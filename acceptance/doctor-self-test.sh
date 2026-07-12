#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DOCTOR="$ROOT/acceptance/doctor.sh"
TARGET="$ROOT"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

failures=0
fail() {
  printf 'FAIL: %s\n' "$1"
  failures=$((failures + 1))
}
pass() {
  printf 'PASS: %s\n' "$1"
}

mkdir -p "$TMP/run-a/graphify-out" "$TMP/run-b/graphify-out"
cp "$ROOT/graphify-out/graph.json" "$ROOT/graphify-out/GRAPH_REPORT.md" "$TMP/run-a/graphify-out/"
cp "$ROOT/graphify-out/graph.json" "$ROOT/graphify-out/GRAPH_REPORT.md" "$TMP/run-b/graphify-out/"

set +e
"$DOCTOR" post-graph --target "$TARGET" --work-dir "$TMP/run-a" --json >"$TMP/a.json"
rc_a=$?
"$DOCTOR" post-graph --target "$TARGET" --work-dir "$TMP/run-b" --json >"$TMP/b.json"
rc_b=$?
set -e
[ "$rc_a" -eq 0 ] || fail "independent valid graph run A passes"
[ "$rc_b" -eq 0 ] || fail "independent valid graph run B passes"
set +e
python - "$TMP/a.json" "$TMP/b.json" <<'PY'
import json
import sys

def normalized(path):
    data = json.load(open(path))
    data.pop("work_dir", None)
    return data

raise SystemExit(0 if normalized(sys.argv[1]) == normalized(sys.argv[2]) else 1)
PY
normalized_rc=$?
set -e
if [ "$normalized_rc" -eq 0 ]; then
  pass "two valid post-graph classifications are structurally identical"
else
  fail "two valid post-graph classifications differ"
fi

python - "$TMP/run-a/graphify-out/graph.json" <<'PY'
import json
import sys
path = sys.argv[1]
data = json.load(open(path))
data["nodes"] = []
data["links"] = []
json.dump(data, open(path, "w"))
PY
set +e
"$DOCTOR" post-graph --target "$TARGET" --work-dir "$TMP/run-a" --json >/dev/null
rc_empty=$?
set -e
[ "$rc_empty" -eq 30 ] && pass "empty graph is rejected with blocked status" || fail "empty graph is rejected with blocked status"

set +e
"$DOCTOR" preflight --target "$TARGET" --work-dir "$TARGET" --json >/dev/null
rc_isolation=$?
set -e
[ "$rc_isolation" -eq 30 ] && pass "workdir inside target is rejected" || fail "workdir inside target is rejected"

set +e
DEEPSEEK_API_KEY="doctor-self-test-secret" "$DOCTOR" preflight --target "$TARGET" --work-dir "$TMP/run-b" --json >"$TMP/preflight.json"
rc_preflight=$?
set -e
[ "$rc_preflight" -eq 0 ] || fail "preflight resolves Graphify backend"
if grep -Fq "doctor-self-test-secret" "$TMP/preflight.json"; then
  fail "doctor output contains a secret value"
else
  pass "doctor output does not contain secret values"
fi
python -m json.tool "$TMP/preflight.json" >/dev/null 2>&1 || fail "preflight JSON is valid"

printf '\nDoctor self-test: '
if [ "$failures" -eq 0 ]; then
  printf 'PASS\n'
  exit 0
fi
printf 'FAIL (%s)\n' "$failures"
exit 1
