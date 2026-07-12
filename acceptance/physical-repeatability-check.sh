#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: $0 <run-a> <run-b> [--json]" >&2
}
[ "$#" -ge 2 ] || { usage; exit 30; }
run_a="$1"
run_b="$2"
json=false
if [ "$#" -ge 3 ] && [ "$3" = "--json" ]; then
  json=true
fi

python - "$run_a" "$run_b" "$json" <<'PY'
import json
import sys
from pathlib import Path

left = Path(sys.argv[1])
right = Path(sys.argv[2])
json_output = sys.argv[3] == "true"
required = [
    "metadata.json",
    "execution-log.md",
    "ANALYSIS_REPORT.md",
    "checks.md",
    "drafts/08-coverage.md",
    "graphify-out/graph.json",
    "graphify-out/GRAPH_REPORT.md",
]
failures = []

def scrub(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in {"run_id", "started_at", "ended_at", "work_dir"}:
                continue
            if key == "artifact_paths" and isinstance(item, list):
                result[key] = ["/".join(Path(path).parts[-2:]) for path in item]
            else:
                result[key] = scrub(item)
        return result
    if isinstance(value, list):
        return [scrub(item) for item in value]
    return value

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"invalid JSON: {path}: {type(exc).__name__}")
        return None

def graph_signature(path):
    graph = read_json(path)
    if not isinstance(graph, dict):
        return None
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    def node_key(item):
        if not isinstance(item, dict):
            return repr(item)
        return tuple(sorted((key, str(item.get(key, ""))) for key in ("id", "label", "source_file", "source_location", "community")))
    def link_key(item):
        if not isinstance(item, dict):
            return repr(item)
        return tuple(sorted((key, str(item.get(key, ""))) for key in ("source", "target", "relation", "confidence", "source_file", "source_location")))
    return {
        "nodes": sorted(node_key(item) for item in nodes),
        "links": sorted(link_key(item) for item in links),
        "node_count": len(nodes),
        "link_count": len(links),
    }

for base in (left, right):
    for name in required:
        if not (base / name).is_file():
            failures.append(f"missing artifact: {base / name}")

left_metadata = read_json(left / "metadata.json")
right_metadata = read_json(right / "metadata.json")
if left_metadata is not None and right_metadata is not None:
    if scrub(left_metadata) != scrub(right_metadata):
        failures.append("normalized metadata differs")
    left_source = left_metadata.get("source", {})
    right_source = right_metadata.get("source", {})
    if left_source.get("source_commit") != right_source.get("source_commit"):
        failures.append("source commit differs")
    if left_metadata.get("analysis_mode") != "standard" or right_metadata.get("analysis_mode") != "standard":
        failures.append("analysis mode is not standard")
    left_failure = left_metadata.get("failure", {}).get("class")
    right_failure = right_metadata.get("failure", {}).get("class")
    if left_failure != right_failure:
        failures.append("failure classification differs")

if graph_signature(left / "graphify-out/graph.json") != graph_signature(right / "graphify-out/graph.json"):
    failures.append("normalized graph structure or source references differ")

for name in ("drafts/08-coverage.md", "checks.md"):
    left_text = " ".join((left / name).read_text(encoding="utf-8", errors="replace").split()) if (left / name).is_file() else ""
    right_text = " ".join((right / name).read_text(encoding="utf-8", errors="replace").split()) if (right / name).is_file() else ""
    if left_text != right_text:
        failures.append(f"normalized verification record differs: {name}")

result = {
    "schema_version": 1,
    "runs": [str(left), str(right)],
    "status": "pass" if not failures else "fail",
    "failures": failures,
}
if json_output:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
else:
    print(f"repeatability: {result['status']}")
    for failure in failures:
        print("FAIL: " + failure)
sys.exit(0 if not failures else 30)
PY
