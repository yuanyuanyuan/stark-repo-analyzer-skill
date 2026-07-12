#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SOURCE_ROOT=${SOURCE_ROOT:-"$ROOT/../stark-repo-analyzer-reference-sources"}
MANIFEST="$ROOT/docs/baseline/source-corpus-manifest.json"
RUN_ROOT="$ROOT/docs/baseline/reference-runs"

failures=0

fail() {
  printf 'FAIL: %s\n' "$1"
  failures=$((failures + 1))
}

pass() {
  printf 'PASS: %s\n' "$1"
}

if ! command -v jq >/dev/null 2>&1; then
  fail "jq is required"
  exit 1
fi

if ! jq empty "$MANIFEST" >/dev/null 2>&1; then
  fail "invalid source manifest: $MANIFEST"
  exit 1
fi

count=$(jq '.repositories | length' "$MANIFEST")
if [ "$count" -eq 6 ]; then
  pass "source manifest contains 6 repositories"
else
  fail "source manifest contains $count repositories; expected 6"
fi

while IFS=$'\t' read -r name commit local_path; do
  source_path="$local_path"
  run_path="$RUN_ROOT/$name"

  if [ ! -d "$source_path/.git" ]; then
    fail "$name source git directory exists"
  else
    actual=$(git -C "$source_path" rev-parse HEAD 2>/dev/null || true)
    if [ "$actual" = "$commit" ]; then
      pass "$name source HEAD is $commit"
    else
      fail "$name source HEAD mismatch: expected $commit, got $actual"
    fi

    if [ -z "$(git -C "$source_path" status --porcelain 2>/dev/null)" ]; then
      pass "$name source worktree is clean"
    else
      fail "$name source worktree is dirty"
    fi
  fi

  for file in metadata.json execution-log.md ANALYSIS_REPORT.md checks.md drafts/08-coverage.md; do
    if [ -f "$run_path/$file" ]; then
      pass "$name artifact exists: $file"
    else
      fail "$name artifact missing: $file"
    fi
  done

  if [ -f "$run_path/metadata.json" ] && jq -e --arg project "$name" --arg commit "$commit" \
    '.project == $project and .commit == $commit and .analysis_mode == "standard" and (.started_at != null) and (.ended_at != null)' \
    "$run_path/metadata.json" >/dev/null 2>&1; then
    pass "$name metadata identifies project, commit, standard mode and timing"
  else
    fail "$name metadata is incomplete"
  fi

  if [ -f "$run_path/ANALYSIS_REPORT.md" ] && grep -Eiq '```mermaid|mermaid' "$run_path/ANALYSIS_REPORT.md"; then
    pass "$name report contains Mermaid architecture evidence"
  else
    fail "$name report has no Mermaid marker"
  fi

  oversized=$(find "$run_path" -type f -size +15k -print -quit 2>/dev/null)
  if [ -z "$oversized" ]; then
    pass "$name artifacts stay below 15KB per file"
  else
    fail "$name artifact exceeds 15KB: $oversized"
  fi
done < <(jq -r '.repositories[] | [.name, .commit, .local_path] | @tsv' "$MANIFEST")

physical_root="$ROOT/docs/baseline/physical-runs"
physical_all=true
graphify_all=true
graphify_passed=0
graphify_blocked=0

check_physical_snapshot() {
  name="$1"
  run_path="$2"
  expected_commit="$3"
  for file in input.md metadata.json execution-log.md ANALYSIS_REPORT.md checks.md drafts/08-coverage.md doctor-preflight.json; do
    if [ -f "$run_path/$file" ]; then
      pass "$name physical artifact exists: $file"
    else
      fail "$name physical artifact missing: $file"
      physical_all=false
    fi
  done

  if jq -e '.phase == "preflight" and .status.code == 0 and (.failures | length == 0)' "$run_path/doctor-preflight.json" >/dev/null 2>&1; then
    pass "$name doctor preflight is ready"
  else
    fail "$name doctor preflight is not ready"
    physical_all=false
  fi

  graph_status=$(jq -r '.graphify.status // "missing"' "$run_path/metadata.json" 2>/dev/null || printf 'missing')
  if [ "$graph_status" = "passed" ]; then
    graphify_passed=$((graphify_passed + 1))
    for file in graphify-out/graph.json graphify-out/GRAPH_REPORT.md graphify-out/manifest.json doctor-post-graph.json; do
      if [ -f "$run_path/$file" ]; then
        pass "$name Graphify artifact exists: $file"
      else
        fail "$name Graphify artifact missing: $file"
        physical_all=false
      fi
    done
    if jq -e '.phase == "post-graph" and .status.code == 0 and (.failures | length == 0)' "$run_path/doctor-post-graph.json" >/dev/null 2>&1; then
      pass "$name doctor post-graph is healthy"
    else
      fail "$name doctor post-graph is blocked"
      physical_all=false
    fi
  elif [ "$graph_status" = "blocked" ] && [ -f "$run_path/graphify-failure.md" ]; then
    pass "$name Graphify blocked run has a failure record"
    graphify_blocked=$((graphify_blocked + 1))
    graphify_all=false
  else
    fail "$name Graphify status is not auditable"
    physical_all=false
  fi

  if [ -f "$run_path/metadata.json" ] && jq -e --arg project "$name" --arg commit "$expected_commit" \
    '.project == $project and .source_head == $commit and .analysis_mode == "standard" and .reference_entrypoint == "codex exec --json" and .input == "input.md" and .exit_status == 0 and (.started_at != null) and (.ended_at != null) and (.source_modified == false)' \
    "$run_path/metadata.json" >/dev/null 2>&1; then
    pass "$name physical metadata identifies clean fixed-head standard run"
  else
    fail "$name physical metadata is incomplete or mismatched"
    physical_all=false
  fi
}

for project in httpx ruff claude-code codex; do
  expected_commit=$(jq -r --arg project "$project" '.repositories[] | select(.name == $project) | .commit' "$MANIFEST")
  check_physical_snapshot "$project" "$physical_root/$project/run-1" "$expected_commit"
  if [ -f "$physical_root/$project/run-1/comparison.md" ]; then
    pass "$project physical comparison report exists"
  else
    fail "$project physical comparison report missing"
    physical_all=false
  fi
done

click_a="$physical_root/click/run-2"
click_b="$physical_root/click/run-3"
click_physical=false
if [ -f "$click_a/metadata.json" ] && [ -f "$click_b/metadata.json" ] \
  && jq -e --arg commit "$(jq -r '.repositories[] | select(.name == "click") | .commit' "$MANIFEST")" \
    '(.source_head == $commit) and (.started_at != null) and (.ended_at != null) and (.reference_entrypoint == "codex exec --json") and (.input == "input.md") and (.exit_status == 0) and (.source_modified == false) and ((.workflow // .analysis_mode) | tostring | test("standard"; "i"))' \
    "$click_a/metadata.json" >/dev/null 2>&1 \
  && jq -e --arg commit "$(jq -r '.repositories[] | select(.name == "click") | .commit' "$MANIFEST")" \
    '(.source_head == $commit) and (.started_at != null) and (.ended_at != null) and (.reference_entrypoint == "codex exec --json") and (.input == "input.md") and (.exit_status == 0) and (.source_modified == false) and ((.workflow // .analysis_mode) | tostring | test("standard"; "i"))' \
    "$click_b/metadata.json" >/dev/null 2>&1 \
  && "$ROOT/acceptance/physical-repeatability-check.sh" "$click_a" "$click_b" --json >/dev/null 2>&1; then
  click_physical=true
  pass "click physical reference runs and repeatability comparison"
else
  fail "click physical reference runs and repeatability comparison"
fi

codex_plugin_physical=false
codex_a="$physical_root/codex-plugin-cc/run-1"
codex_b="$physical_root/codex-plugin-cc/run-2"
if [ -f "$codex_a/metadata.json" ] && [ -f "$codex_b/metadata.json" ] \
  && jq -e --arg commit "$(jq -r '.repositories[] | select(.name == "codex-plugin-cc") | .commit' "$MANIFEST")" \
    '(.source_head == $commit) and (.started_at != null) and (.ended_at != null) and (.reference_entrypoint == "codex exec --json") and (.input == "input.md") and (.exit_status == 0) and (.source_modified == false) and ((.workflow // .analysis_mode) | tostring | test("standard"; "i"))' \
    "$codex_a/metadata.json" >/dev/null 2>&1 \
  && jq -e --arg commit "$(jq -r '.repositories[] | select(.name == "codex-plugin-cc") | .commit' "$MANIFEST")" \
    '(.source_head == $commit) and (.started_at != null) and (.ended_at != null) and (.reference_entrypoint == "codex exec --json") and (.input == "input.md") and (.exit_status == 0) and (.source_modified == false) and ((.workflow // .analysis_mode) | tostring | test("standard"; "i"))' \
    "$codex_b/metadata.json" >/dev/null 2>&1 \
  && "$ROOT/acceptance/physical-repeatability-check.sh" "$codex_a" "$codex_b" --json >/dev/null 2>&1; then
  codex_plugin_physical=true
  pass "codex-plugin-cc physical runs and repeatability comparison"
else
  printf 'INFO: codex-plugin-cc physical runs are pending\n'
fi

printf '\nPhysical baseline integrity gate: '
if [ "$failures" -eq 0 ]; then
  printf 'PASS (P0/P1 integrity and P3 structural checks)\n'
  if [ "$click_physical" = true ] && [ "$codex_plugin_physical" = true ] && [ "$physical_all" = true ]; then
    printf 'P2 physical reference gate: PASS for all 6 projects; P4 PASS for click and codex-plugin-cc\n'
  elif [ "$click_physical" = true ] && [ "$codex_plugin_physical" = true ]; then
    printf 'P2 physical reference gate: PARTIAL (click and codex-plugin-cc P4 PASS; remaining snapshot checks failed)\n'
  else
    printf 'P2 physical reference gate: PARTIAL\n'
  fi
  if [ "$graphify_all" = true ]; then
    printf 'P3 Graphify sidecar gate: PASS for all extended projects\n'
  else
    printf 'P3 Graphify sidecar gate: PARTIAL (%s passed; %s blocked with failure records)\n' "$graphify_passed" "$graphify_blocked"
  fi
  printf 'Full physical baseline: NOT READY (P5 dynamic behavior is pending)\n'
  exit 0
else
  printf 'FAIL (%s integrity checks failed)\n' "$failures"
  printf 'Full physical baseline: NOT READY\n'
  exit 1
fi
