#!/usr/bin/env bash

set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PROJECT=${1:?project name is required}
TARGET=${2:?target repository is required}
GRAPH_FIXTURE=${3:?Graphify fixture directory is required}
WORK_DIR=${4:?output work directory is required}

PYTHONPATH="$ROOT/src" python - "$PROJECT" "$TARGET" "$GRAPH_FIXTURE" "$WORK_DIR" <<'PY'
import json
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from stark_repo_analyzer.cli import analyze, finalize
from stark_repo_analyzer.contracts import validate_run_contract

project, target_value, fixture_value, work_value = sys.argv[1:]
target = Path(target_value).resolve()
fixture = Path(fixture_value).resolve()
work_dir = Path(work_value).resolve()

def fixture_extract(target_path, output_dir, log):
    graph_dir = output_dir / "graphify-out"
    graph_dir.mkdir(parents=True, exist_ok=True)
    for name in ("graph.json", "GRAPH_REPORT.md", "manifest.json"):
        shutil.copy2(fixture / name, graph_dir / name)
    return [{"exit_code": 0, "elapsed_seconds": 0, "transient_failure": False, "fixture": True}]

args = Namespace(input=str(target), work_dir=str(work_dir), run_id=f"fixture-{project}", mode="standard")
with patch("stark_repo_analyzer.cli.graphify_extract", side_effect=fixture_extract):
    result = analyze(args)
if result != 2:
    raise SystemExit(f"analyze handoff failed: {result}")

tasks = json.loads((work_dir / "drafts/06-module-tasks.json").read_text(encoding="utf-8"))
source_path = next(
    path.relative_to(target)
    for path in sorted(target.rglob("*"))
    if path.is_file() and path.suffix in {".py", ".js", ".ts", ".rs", ".go"}
    and not any(part in {".git", "tests", "test", "docs", "node_modules"} for part in path.relative_to(target).parts)
)
for task in tasks:
    path = work_dir / task["output"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {task['id']}\n\n"
        "## Role\nThis verified fixture module owns a bounded architectural responsibility.\n\n"
        "## Why and trade-offs\nThe boundary makes the primary data flow auditable and keeps alternatives explicit.\n\n"
        "```mermaid\nflowchart LR\nInput --> Boundary --> Output\n```\n\n"
        "| File | Lines | Coverage |\n|---|---:|---|\n"
        f"Source evidence: `{source_path}:L1`\n\n"
        f"| {source_path} | 1 | PASS |\n| Total | 1 | PASS |\n",
        encoding="utf-8",
    )
(work_dir / "drafts/06-module-tasks.json").write_text(
    json.dumps([{**task, "status": "completed", "attempts": 1} for task in tasks], indent=2) + "\n",
    encoding="utf-8",
)
(work_dir / "drafts/07-cross-validation.md").write_text(
    "# Cross Validation\n\nSource adjudication confirms the cited boundaries.\n", encoding="utf-8"
)
(work_dir / "drafts/08-insights.md").write_text(
    "# Insights\n\nThe verified fixture preserves the primary design trade-off.\n", encoding="utf-8"
)
(work_dir / "drafts/08-coverage.md").write_text(
    "# Coverage\n\n| Total | Read | Status |\n|---:|---:|---|\n| 1 | 1 | PASS |\n",
    encoding="utf-8",
)
if finalize(Namespace(work_dir=str(work_dir))) != 0:
    raise SystemExit("finalize failed")
summary = validate_run_contract(work_dir, complete=True)
(work_dir / "fixture-summary.json").write_text(
    json.dumps({"project": project, "fixture": str(fixture), "validation": summary}, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, ensure_ascii=False))
PY
