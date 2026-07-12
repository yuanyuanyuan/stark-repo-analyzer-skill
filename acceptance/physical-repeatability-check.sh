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
import re
import sys
from pathlib import Path

left = Path(sys.argv[1])
right = Path(sys.argv[2])
json_output = sys.argv[3] == "true"
required = [
    "input.md",
    "metadata.json",
    "execution-log.md",
    "ANALYSIS_REPORT.md",
    "checks.md",
    "drafts/08-coverage.md",
    "graphify-out/graph.json",
    "graphify-out/GRAPH_REPORT.md",
    "graphify-out/manifest.json",
]
failures = []

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

def metadata_summary(metadata):
    source = metadata.get("source", {})
    if not source:
        source = {
            "source_commit": metadata.get("source_head"),
            "source_path": metadata.get("source_tree"),
        }
    coverage = metadata.get("static_reading_coverage")
    if not coverage:
        total = metadata.get("effective_source_lines")
        read = metadata.get("read_source_lines")
        coverage = {
            "total_lines": total,
            "read_lines": read,
            "percentage": metadata.get("coverage_percent"),
            "status": "passed" if metadata.get("coverage_percent") is not None else None,
        }
    mode = metadata.get("analysis_mode") or metadata.get("workflow")
    if mode and mode != "standard" and "standard" in str(mode).lower():
        mode = "standard"
    failure = metadata.get("failure", {}).get("class")
    return {
        "source_commit": source.get("source_commit") or source.get("commit"),
        "source_path": source.get("resolved_path") or source.get("source_path"),
        "analysis_mode": mode,
        "effective_source_lines": coverage.get("total_lines"),
        "read_source_lines": coverage.get("read_lines"),
        "coverage_ratio": (
            coverage.get("read_lines") / coverage.get("total_lines")
            if coverage.get("read_lines") is not None and coverage.get("total_lines")
            else None
        ),
        "coverage_percent": coverage.get("percentage"),
        "coverage_status": coverage.get("status"),
        "failure_class": failure,
    }

for base in (left, right):
    for name in required:
        if not (base / name).is_file():
            failures.append(f"missing artifact: {base / name}")

if failures:
    result = {
        "schema_version": 1,
        "runs": [str(left), str(right)],
        "status": "fail",
        "failures": failures,
        "comparison_basis": [
            "required artifact presence, including fixed input snapshots",
            "source commit and standard mode",
            "overall static coverage totals and threshold status",
            "failure classification",
            "normalized graph structure and source references",
            "machine-level verification status; prose, timestamps and run-specific limitation wording are excluded",
        ],
    }
    if json_output:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print("repeatability: fail")
        for failure in failures:
            print("FAIL: " + failure)
    sys.exit(30)

def file_digest(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()

if file_digest(left / "input.md") != file_digest(right / "input.md"):
    failures.append("fixed input snapshot differs")

left_metadata = read_json(left / "metadata.json")
right_metadata = read_json(right / "metadata.json")
if left_metadata is not None and right_metadata is not None:
    left_summary = metadata_summary(left_metadata)
    right_summary = metadata_summary(right_metadata)
    for key in ("source_commit", "analysis_mode", "coverage_percent", "coverage_status"):
        if left_summary.get(key) != right_summary.get(key):
            failures.append(f"stable metadata differs: {key}")
    left_ratio = left_summary.get("coverage_ratio")
    right_ratio = right_summary.get("coverage_ratio")
    if left_ratio is None or right_ratio is None or abs(left_ratio - right_ratio) > 0.01:
        failures.append("coverage ratio differs by more than one percentage point")
    if left_summary.get("source_commit") != right_summary.get("source_commit"):
        failures.append("source commit differs")
    if left_summary.get("analysis_mode") != "standard" or right_summary.get("analysis_mode") != "standard":
        failures.append("analysis mode is not standard")
    left_failure = left_summary.get("failure_class")
    right_failure = right_summary.get("failure_class")
    if left_failure != right_failure:
        failures.append("failure classification differs")

if graph_signature(left / "graphify-out/graph.json") != graph_signature(right / "graphify-out/graph.json"):
    failures.append("normalized graph structure or source references differ")

def verification_status(base):
    coverage = (base / "drafts/08-coverage.md").read_text(encoding="utf-8", errors="replace")
    checks = (base / "checks.md").read_text(encoding="utf-8", errors="replace")
    return {
        "coverage_pass": bool(re.search(r"(?:全部达标|达标|PASS|✅)", coverage)),
        "checks_fail": bool(re.search(r"\bFAIL\b|status.?[:=].?fail", checks, re.I)),
    }

left_verification = verification_status(left)
right_verification = verification_status(right)
if left_verification != right_verification:
    failures.append("stable verification status differs")
if not left_verification["coverage_pass"] or not right_verification["coverage_pass"]:
    failures.append("coverage threshold status is not passing in both runs")

result = {
    "schema_version": 1,
    "runs": [str(left), str(right)],
    "status": "pass" if not failures else "fail",
    "failures": failures,
    "comparison_basis": [
        "source commit and standard mode",
        "overall static coverage totals and threshold status",
        "failure classification",
        "normalized graph structure and source references",
        "machine-level verification status; prose, timestamps and run-specific limitations are excluded",
    ],
}
if json_output:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
else:
    print(f"repeatability: {result['status']}")
    for failure in failures:
        print("FAIL: " + failure)
sys.exit(0 if not failures else 30)
PY
