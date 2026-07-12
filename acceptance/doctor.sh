#!/usr/bin/env bash

# Deterministic Graphify gate for the repo-analyzer workflow.
# It never invokes extraction and never prints secret values.
set -u

EXIT_READY=0
EXIT_BOOTSTRAP=10
EXIT_CONFIGURATION=20
EXIT_BLOCKED=30

usage() {
  printf '%s\n' "Usage: $0 preflight|post-graph --target <repo> --work-dir <dir> [--json]" >&2
}

[ "$#" -ge 1 ] || { usage; exit "$EXIT_BLOCKED"; }
phase="$1"
shift
target=""
work_dir=""
json_output=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || { usage; exit "$EXIT_BLOCKED"; }
      target="$2"
      shift 2
      ;;
    --work-dir)
      [ "$#" -ge 2 ] || { usage; exit "$EXIT_BLOCKED"; }
      work_dir="$2"
      shift 2
      ;;
    --json)
      json_output=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit "$EXIT_BLOCKED"
      ;;
  esac
done

case "$phase" in
  preflight|post-graph) ;;
  *) usage; exit "$EXIT_BLOCKED" ;;
esac

if [ -z "$target" ] || [ -z "$work_dir" ]; then
  usage
  exit "$EXIT_BLOCKED"
fi

# Resolve existing paths without creating anything. Doctor is read-only.
target=$(cd "$target" 2>/dev/null && pwd -P) || target=$(printf '%s' "$target" | sed 's:/*$::')
work_dir=$(cd "$work_dir" 2>/dev/null && pwd -P) || work_dir=$(printf '%s' "$work_dir" | sed 's:/*$::')

status="$EXIT_READY"
failures=""
warnings=""
python_ok=false
graphify_ok=false
version=""
backend=""
model=""

record_failure() {
  code="$1"
  message="$2"
  failures="$failures"$'\n'"$message"
  if [ "$code" -gt "$status" ]; then
    status="$code"
  fi
}

record_warning() {
  warnings="$warnings"$'\n'"$1"
}

if [ ! -d "$target" ] || [ ! -r "$target" ]; then
  record_failure "$EXIT_BLOCKED" "target is missing or unreadable"
fi

if [ ! -d "$work_dir" ] || [ ! -w "$work_dir" ]; then
  record_failure "$EXIT_BLOCKED" "work_dir is missing or not writable"
fi

if [ -d "$target" ] && [ -d "$work_dir" ]; then
  case "$work_dir/" in
    "$target/"*) record_failure "$EXIT_BLOCKED" "work_dir must be outside target repository" ;;
  esac
  if [ "$target" = "$work_dir" ]; then
    record_failure "$EXIT_BLOCKED" "work_dir must differ from target repository"
  fi
fi

if [ "$phase" = "preflight" ]; then
  if command -v python >/dev/null 2>&1 && python -c 'import graphify' >/dev/null 2>&1; then
    python_ok=true
  else
    record_failure "$EXIT_BOOTSTRAP" "Graphify Python import is unavailable"
  fi

  if command -v graphify >/dev/null 2>&1; then
    graphify_ok=true
    version=$(graphify --version 2>/dev/null | sed -n '1p' | tr -d '\r')
    [ -n "$version" ] || record_failure "$EXIT_BOOTSTRAP" "Graphify version probe failed"
    if ! graphify extract --help >/dev/null 2>&1; then
      record_failure "$EXIT_BOOTSTRAP" "Graphify headless extract capability is unavailable"
    fi
  else
    record_failure "$EXIT_BOOTSTRAP" "Graphify CLI is unavailable"
  fi

  if [ "$python_ok" = true ]; then
    # Delegate provider priority to Graphify; only public identifiers are returned.
    resolver=$(python - <<'PY'
import sys
try:
    from graphify.llm import _default_model_for_backend, detect_backend
    selected = detect_backend()
    model = _default_model_for_backend(selected) if selected else ""
    print(f"{selected or ''}\t{model}")
except Exception as exc:
    print(f"ERROR\t{type(exc).__name__}")
    sys.exit(1)
PY
    )
    resolver_status=$?
    if [ "$resolver_status" -eq 0 ] && [[ "$resolver" != ERROR$'\t'* ]]; then
      IFS=$'\t' read -r backend model <<< "$resolver"
      [ -n "$backend" ] || record_failure "$EXIT_CONFIGURATION" "Graphify found no usable LLM backend"
    else
      record_failure "$EXIT_CONFIGURATION" "Graphify LLM auto-detection failed"
    fi
  fi
fi

if [ "$phase" = "post-graph" ]; then
  graph_dir="$work_dir/graphify-out"
  graph_json="$graph_dir/graph.json"
  graph_report="$graph_dir/GRAPH_REPORT.md"

  [ -f "$graph_json" ] || record_failure "$EXIT_BLOCKED" "graphify-out/graph.json is missing"
  [ -r "$graph_json" ] || record_failure "$EXIT_BLOCKED" "graphify-out/graph.json is unreadable"
  [ -f "$graph_report" ] || record_failure "$EXIT_BLOCKED" "graphify-out/GRAPH_REPORT.md is missing"
  [ -r "$graph_report" ] || record_failure "$EXIT_BLOCKED" "graphify-out/GRAPH_REPORT.md is unreadable"

  if [ -f "$graph_json" ] && [ -f "$graph_report" ]; then
    graph_result=$(python - "$graph_json" "$graph_report" "$target" <<'PY'
import json
import re
import sys
from pathlib import Path

graph_path, report_path, target_path = map(Path, sys.argv[1:])
target = target_path.resolve()
errors = []

try:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
except Exception as exc:
    print("ERROR\tinvalid graph.json: " + type(exc).__name__)
    raise SystemExit(0)

if not isinstance(graph, dict):
    errors.append("graph.json root is not an object")
    graph = {}
nodes = graph.get("nodes", [])
links = graph.get("links", graph.get("edges", []))
if not isinstance(nodes, list):
    errors.append("graph nodes are not an array")
    nodes = []
if not isinstance(links, list):
    errors.append("graph links are not an array")
    links = []
if not nodes:
    errors.append("graph has zero nodes")
if not links:
    errors.append("graph has zero edges")

def valid_source(item):
    if not isinstance(item, dict):
        return False
    source_file = item.get("source_file")
    source_location = item.get("source_location")
    if not isinstance(source_file, str) or not source_file.strip():
        return False
    if not isinstance(source_location, str) or not re.search(r"L[0-9]+", source_location):
        return False
    candidate = Path(source_file)
    if candidate.is_absolute():
        try:
            resolved = candidate.resolve()
            resolved.relative_to(target)
        except ValueError:
            return False
    elif ".." in candidate.parts:
        return False
    else:
        resolved = (target / candidate).resolve()
        try:
            resolved.relative_to(target)
        except ValueError:
            return False
    if not resolved.is_file():
        return False
    return True

node_sources = sum(bool(valid_source(item)) for item in nodes)
link_sources = sum(bool(valid_source(item)) for item in links)
if node_sources == 0:
    errors.append("graph has no locatable node source references")
if link_sources == 0:
    errors.append("graph has no locatable edge source references")

try:
    report = report_path.read_text(encoding="utf-8")
except Exception as exc:
    report = ""
    errors.append("report cannot be read: " + type(exc).__name__)

match = re.search(r"([0-9][0-9,]*) nodes?\s*[·|/]\s*([0-9][0-9,]*) edges?", report)
if not match:
    match = re.search(r"([0-9][0-9,]*) nodes?.{0,12}([0-9][0-9,]*) edges?", report)
if not match:
    errors.append("GRAPH_REPORT.md has no node/edge summary")
else:
    report_nodes = int(match.group(1).replace(",", ""))
    report_links = int(match.group(2).replace(",", ""))
    if report_nodes != len(nodes) or report_links != len(links):
        errors.append("GRAPH_REPORT.md counts do not match graph.json")

extracted = sum(
    bool(isinstance(item, dict)
    and str(item.get("confidence", "")).upper() == "EXTRACTED"
    and valid_source(item))
    for item in links
)
print("OK\t{}\t{}\t{}\t{}\t{}".format(
    len(nodes), len(links), node_sources, link_sources, extracted
))
for error in errors:
    print("ERROR\t" + error)
PY
    )
    graph_nodes=""
    graph_links=""
    extracted=""
    while IFS=$'\t' read -r kind value rest; do
      if [ "$kind" = "ERROR" ]; then
        if [ -n "$rest" ]; then message="$value $rest"; else message="$value"; fi
        record_failure "$EXIT_BLOCKED" "$message"
      elif [ "$kind" = "OK" ]; then
        graph_nodes="$value"
        IFS=$'\t' read -r graph_links _ _ extracted <<< "$rest"
      fi
    done <<< "$graph_result"

    case "$(basename "$target")" in
      click)
        if ! printf '%s\n' "$graph_result" | awk -F '\t' '$1 == "OK" && $6 + 0 > 0 { found=1 } END { exit(found ? 0 : 1) }'; then
          record_failure "$EXIT_BLOCKED" "click graph has no locatable EXTRACTED edge"
        fi
        ;;
    esac
  fi
fi

export DOCTOR_PHASE="$phase"
export DOCTOR_STATUS="$status"
export DOCTOR_TARGET="$target"
export DOCTOR_WORK_DIR="$work_dir"
export DOCTOR_GRAPHIFY_OK="$graphify_ok"
export DOCTOR_VERSION="$version"
export DOCTOR_BACKEND="$backend"
export DOCTOR_MODEL="$model"
export DOCTOR_FAILURES="$failures"
export DOCTOR_WARNINGS="$warnings"

python - <<'PY'
import json
import os

def lines(name):
    return [line for line in os.environ.get(name, "").splitlines() if line]

code = int(os.environ["DOCTOR_STATUS"])
result = {
    "schema_version": 1,
    "phase": os.environ["DOCTOR_PHASE"],
    "status": {
        "code": code,
        "name": {0: "ready", 10: "bootstrap_required", 20: "user_configuration_required", 30: "blocked"}.get(code, "unknown"),
    },
    "target": os.environ["DOCTOR_TARGET"],
    "work_dir": os.environ["DOCTOR_WORK_DIR"],
    "graphify": {
        "cli_available": os.environ["DOCTOR_GRAPHIFY_OK"] == "true",
        "version": os.environ["DOCTOR_VERSION"] or None,
        "backend": os.environ["DOCTOR_BACKEND"] or None,
        "model": os.environ["DOCTOR_MODEL"] or None,
    },
    "failures": lines("DOCTOR_FAILURES"),
    "warnings": lines("DOCTOR_WARNINGS"),
}
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
PY

if [ "$json_output" = false ]; then
  name="unknown"
  case "$status" in
    0) name="ready" ;;
    10) name="bootstrap_required" ;;
    20) name="user_configuration_required" ;;
    30) name="blocked" ;;
  esac
  printf 'doctor %s: %s\n' "$phase" "$name"
  [ -n "$version" ] && printf 'Graphify: %s\n' "$version"
  [ -n "$backend" ] && printf 'LLM: %s (%s)\n' "$backend" "$model"
  while IFS= read -r failure; do
    [ -n "$failure" ] && printf 'FAIL: %s\n' "$failure"
  done <<< "$failures"
  while IFS= read -r warning; do
    [ -n "$warning" ] && printf 'WARN: %s\n' "$warning"
  done <<< "$warnings"
fi

exit "$status"
