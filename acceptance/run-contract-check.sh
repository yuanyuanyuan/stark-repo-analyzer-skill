#!/usr/bin/env bash

set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
RUN_DIR="${1:-}"

if [ -n "$RUN_DIR" ]; then
  PYTHONPATH="$ROOT/src" python -m stark_repo_analyzer.cli validate --work-dir "$RUN_DIR" --complete
  exit $?
fi

failures=0
fail() { printf 'FAIL: %s\n' "$1"; failures=$((failures + 1)); }
pass() { printf 'PASS: %s\n' "$1"; }

for run in "$ROOT"/docs/baseline/reference-runs/*; do
  [ -d "$run" ] || continue
  name=$(basename "$run")
  for file in metadata.json execution-log.md ANALYSIS_REPORT.md checks.md drafts/08-coverage.md; do
    if [ -s "$run/$file" ]; then pass "$name has $file"; else fail "$name missing $file"; fi
  done
  if jq empty "$run/metadata.json" >/dev/null 2>&1; then pass "$name metadata is valid JSON"; else fail "$name metadata is invalid JSON"; fi
  if grep -Eiq 'mermaid' "$run/ANALYSIS_REPORT.md"; then pass "$name report has Mermaid evidence"; else fail "$name report has no Mermaid evidence"; fi
  if grep -Eiq '覆盖率|coverage' "$run/drafts/08-coverage.md"; then pass "$name coverage draft exists"; else fail "$name coverage draft has no coverage marker"; fi
done

"$ROOT/acceptance/physical-baseline-check.sh" >/dev/null || fail "physical baseline check"
"$ROOT/acceptance/doctor-self-test.sh" >/dev/null || fail "doctor self-test"

printf '\nRun contract check: '
if [ "$failures" -eq 0 ]; then printf 'PASS\n'; exit 0; fi
printf 'FAIL (%s)\n' "$failures"
exit 1
