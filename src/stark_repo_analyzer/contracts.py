"""Run-contract helpers shared by the CLI and acceptance tests.

The skill is agent-led, but its filesystem contract must be deterministic.  This
module validates the boundary between the programmatic control plane and the
Agent-owned module drafts without attempting to judge prose quality.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_DRAFTS = (
    "01-graphify-map.md",
    "03-research.md",
    "03-plan.md",
    "05-modules-plan.md",
    "07-cross-validation.md",
    "08-insights.md",
    "08-coverage.md",
)

REQUIRED_ROOT_FILES = (
    "input.md",
    "metadata.json",
    "execution-log.md",
    "ANALYSIS_REPORT.md",
    "checks.md",
)


class ContractError(ValueError):
    """Raised when a run cannot satisfy the V1 output contract."""


def validate_output_manifest(manifest: Any) -> None:
    """Validate the stable fields declared by output-manifest-schema.json."""

    if not isinstance(manifest, dict):
        raise ContractError("manifest root must be an object")
    required = {"schema_version", "status", "analysis_mode", "files"}
    if not required.issubset(manifest):
        raise ContractError("manifest is missing required fields")
    if manifest["schema_version"] != 1 or manifest["analysis_mode"] != "standard":
        raise ContractError("manifest schema version or analysis mode is invalid")
    if manifest["status"] not in {"awaiting-agent-module-analysis", "complete"}:
        raise ContractError("manifest status is invalid")
    if not isinstance(manifest["files"], list):
        raise ContractError("manifest files must be an array")
    for item in manifest["files"]:
        if not isinstance(item, dict) or not {"path", "bytes", "sha256"}.issubset(item):
            raise ContractError("manifest file entry is incomplete")
        if not isinstance(item["path"], str) or not item["path"]:
            raise ContractError("manifest file path is invalid")
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ContractError("manifest file path is invalid")
        if isinstance(item["bytes"], bool) or not isinstance(item["bytes"], int) or item["bytes"] < 0:
            raise ContractError("manifest file byte count is invalid")
        if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise ContractError("manifest file hash is invalid")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coverage_marker(text: str) -> bool:
    return bool(
        re.search(
            r"(?:合计|total|aggregate).{0,160}(?:✅|PASS|达标)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
    )


def validate_module_draft(path: Path, *, source_root: Path | None = None) -> dict[str, Any]:
    """Validate the mechanical portions of one Agent module draft."""

    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        raise ContractError(f"empty module draft: {path.name}")
    if "```mermaid" not in text.lower() and "mermaid" not in text.lower():
        raise ContractError(f"module draft has no Mermaid evidence: {path.name}")
    if not re.search(r"(?:覆盖率|coverage)", text, re.IGNORECASE):
        raise ContractError(f"module draft has no coverage table: {path.name}")
    if not _coverage_marker(text):
        raise ContractError(f"module draft coverage is not marked passed: {path.name}")
    if not re.search(r"(?:文件|file).{0,160}(?:行|line)", text, re.IGNORECASE | re.DOTALL):
        raise ContractError(f"module draft has no file/line evidence table: {path.name}")
    required_sections = ("为什么", "Why", "权衡", "trade-off", "角色", "role")
    if not any(marker in text for marker in required_sections):
        raise ContractError(f"module draft lacks design-reasoning evidence: {path.name}")
    if source_root is not None:
        references = re.findall(r"(?<![\w/])((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+):L?(\d+)(?:-L?(\d+))?", text)
        if not references:
            raise ContractError(f"module draft has no source path/line reference: {path.name}")
        locatable = False
        for reference, first, last in references:
            source_path = source_root / reference
            if not source_path.is_file():
                continue
            line_count = len(source_path.read_text(encoding="utf-8", errors="replace").splitlines())
            if int(first) <= line_count and (not last or int(last) <= line_count):
                locatable = True
                break
        if not locatable:
            raise ContractError(f"module draft source references are not locatable: {path.name}")
    return {
        "path": str(path.relative_to(path.parents[1])),
        "bytes": path.stat().st_size,
        "coverage_marked_pass": True,
    }


def validate_run_contract(work_dir: Path, *, complete: bool = False) -> dict[str, Any]:
    """Return an auditable artifact summary or raise ``ContractError``."""

    missing = [name for name in REQUIRED_ROOT_FILES if not (work_dir / name).is_file()]
    missing.extend(
        f"drafts/{name}"
        for name in REQUIRED_DRAFTS
        if not (work_dir / "drafts" / name).is_file()
    )
    graph_files = (work_dir / "graphify-out" / "graph.json", work_dir / "graphify-out" / "GRAPH_REPORT.md")
    missing.extend(str(path.relative_to(work_dir)) for path in graph_files if not path.is_file())
    missing.extend(name for name in ("doctor-preflight.json", "doctor-post-graph.json") if not (work_dir / name).is_file())
    if missing:
        raise ContractError("missing run artifacts: " + ", ".join(missing))

    try:
        metadata = json.loads((work_dir / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"metadata.json is invalid: {type(exc).__name__}") from exc
    if metadata.get("analysis_mode") != "standard":
        raise ContractError("V1 only supports standard analysis mode")
    source = metadata.get("source", {})
    if not source.get("source_commit"):
        raise ContractError("metadata does not record source commit")
    try:
        doctor_pre = json.loads((work_dir / "doctor-preflight.json").read_text(encoding="utf-8"))
        doctor_post = json.loads((work_dir / "doctor-post-graph.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"doctor-post-graph.json is invalid: {type(exc).__name__}") from exc
    if doctor_pre.get("phase") != "preflight" or doctor_pre.get("status", {}).get("code") != 0:
        raise ContractError("doctor preflight did not pass")
    expected_target = source.get("resolved_path")
    for doctor_name, doctor in (("preflight", doctor_pre), ("post-graph", doctor_post)):
        if expected_target and doctor.get("target") != expected_target:
            raise ContractError(f"doctor {doctor_name} target does not match metadata")
        if doctor.get("work_dir"):
            doctor_work_dir = Path(doctor["work_dir"])
            try:
                workspace_matches = doctor_work_dir.samefile(work_dir)
            except OSError:
                workspace_matches = doctor_work_dir.resolve() == work_dir.resolve()
            if not workspace_matches:
                raise ContractError(f"doctor {doctor_name} workspace does not match run")
    if doctor_post.get("phase") != "post-graph" or doctor_post.get("status", {}).get("code") != 0:
        raise ContractError("doctor post-graph did not pass")
    if doctor_post.get("failures"):
        raise ContractError("doctor post-graph contains failures")
    health = doctor_post.get("graphify", {}).get("health") or {}
    nodes = int(health.get("nodes", 0))
    links = int(health.get("edges", 0))
    if not nodes or not links or int(health.get("node_source_references", 0)) <= 0 or int(health.get("edge_source_references", 0)) <= 0:
        raise ContractError("Graphify graph health is empty")
    manifest_path = work_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            validate_output_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContractError(f"manifest.json is invalid: {type(exc).__name__}") from exc

    modules = sorted((work_dir / "drafts").glob("06-module-*.md"))
    if complete and not modules:
        raise ContractError("no Agent module drafts found")
    task_manifest_path = work_dir / "drafts" / "06-module-tasks.json"
    tasks: list[dict[str, Any]] = []
    if complete and not task_manifest_path.is_file():
        raise ContractError("module task manifest is missing")
    if complete:
        try:
            raw_tasks = json.loads(task_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContractError(f"module task manifest is invalid: {type(exc).__name__}") from exc
        if not isinstance(raw_tasks, list) or not raw_tasks:
            raise ContractError("module task manifest must contain tasks")
        for task in raw_tasks:
            if not isinstance(task, dict) or not isinstance(task.get("output"), str):
                raise ContractError("module task manifest contains an invalid output")
            if task.get("status") not in {"pending", "running", "completed", "failed"}:
                raise ContractError("module task manifest contains an invalid status")
            if complete and task.get("status") != "completed":
                raise ContractError("module task manifest contains an incomplete task")
            output = Path(task["output"])
            if output.is_absolute() or output.parts[:1] != ("drafts",):
                raise ContractError("module task output must stay under drafts/")
            tasks.append(task)
        expected = {task["output"] for task in tasks}
        actual = {str(path.relative_to(work_dir)) for path in modules}
        missing_modules = sorted(expected - actual)
        if missing_modules:
            raise ContractError("module drafts missing for tasks: " + ", ".join(missing_modules))
    source_root = Path(source["resolved_path"]) if source.get("resolved_path") else None
    module_results = [validate_module_draft(path, source_root=source_root) for path in modules]
    cross = (work_dir / "drafts" / "07-cross-validation.md").read_text(encoding="utf-8", errors="replace")
    if complete and not any(marker in cross for marker in ("源码", "source", "Source")):
        raise ContractError("cross-validation draft has no source adjudication")
    coverage = (work_dir / "drafts" / "08-coverage.md").read_text(encoding="utf-8", errors="replace")
    if complete and not _coverage_marker(coverage):
        raise ContractError("coverage summary is not marked passed")
    if complete and "pending" in coverage.lower():
        raise ContractError("coverage summary still contains pending status")

    return {
        "schema_version": 1,
        "work_dir": str(work_dir),
        "source_commit": source["source_commit"],
        "analysis_mode": metadata["analysis_mode"],
        "graph": {"nodes": nodes, "edges": links},
        "module_drafts": module_results,
        "module_tasks": len(tasks),
        "complete": complete,
        "input_sha256": sha256_file(work_dir / "input.md") if (work_dir / "input.md").is_file() else None,
    }


def write_output_manifest(work_dir: Path, *, status: str, validation: dict[str, Any]) -> Path:
    """Write a stable manifest without embedding transient report prose."""

    files = []
    for path in sorted(work_dir.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        files.append(
            {
                "path": str(path.relative_to(work_dir)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "schema_version": 1,
        "status": status,
        "source_commit": validation.get("source_commit"),
        "analysis_mode": validation.get("analysis_mode", "standard"),
        "graph": validation.get("graph"),
        "files": files,
    }
    validate_output_manifest(manifest)
    path = work_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
