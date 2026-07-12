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

printf '\nPhysical baseline integrity gate: '
if [ "$failures" -eq 0 ]; then
  printf 'PASS (P0/P1 integrity and P3 structural checks)\n'
  printf 'Full physical baseline: NOT READY (P2 real invocation and P4 repeatability are not implemented)\n'
  exit 0
else
  printf 'FAIL (%s integrity checks failed)\n' "$failures"
  printf 'Full physical baseline: NOT READY\n'
  exit 1
fi
