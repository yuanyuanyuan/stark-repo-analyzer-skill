"""Thin deterministic Graphify gate for the Agent-owned analysis workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Sequence

EXIT_READY = 0
EXIT_DEPENDENCY_UNAVAILABLE = 10
EXIT_BLOCKED = 30
STATUS_FILENAME = "graphify-gate-status.json"
RAW_GRAPH = "raw-code-only-graph.json"
RAW_REPORT = "raw-code-only-GRAPH_REPORT.md"
NORMALIZED_GRAPH = "graph.json"
NORMALIZED_REPORT = "GRAPH_REPORT.md"
NAVIGATION_MAP = "drafts/01-graphify-map.md"
GRAPHIFY_MIN_VERSION = (0, 9, 13)
GRAPHIFY_EXTRACT_OPTIONS = ("--code-only", "--no-cluster")
TRANSIENT_FAILURE = re.compile(
    r"(?:timeout|timed out|HTTP[ /](?:429|5[0-9][0-9])|status[=: ]+(?:429|5[0-9][0-9]))",
    re.IGNORECASE,
)


class RunFailure(RuntimeError):
    """The gate stopped at a declared failure boundary."""

    def __init__(
        self,
        message: str,
        *,
        failure_class: str = "graphify-gate",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_class = failure_class
        self.details = details or {}


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "process timeout")


def graphify_cli() -> str:
    return os.environ.get("GRAPHIFY_CLI", "graphify")


def classify_stream(value: str) -> str:
    if not value.strip():
        return "empty"
    if re.search(r"HTTP[ /]429|status[=: ]+429", value, re.IGNORECASE):
        return "http-429"
    if re.search(r"HTTP[ /]5[0-9][0-9]|status[=: ]+5[0-9][0-9]", value, re.IGNORECASE):
        return "http-5xx"
    if re.search(r"timeout|timed out", value, re.IGNORECASE):
        return "timeout"
    return "non-empty"


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", value)
    return tuple(int(part) for part in match.groups()) if match else (0, 0, 0)


def _doctor_payload(
    phase: str,
    target: Path,
    work_dir: Path,
    code: int,
    *,
    version: str | None = None,
    failures: list[str] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "phase": phase,
        "status": {
            "code": code,
            "name": {
                EXIT_READY: "ready",
                EXIT_DEPENDENCY_UNAVAILABLE: "dependency-unavailable",
                EXIT_BLOCKED: "blocked",
            }.get(code, "blocked"),
        },
        "target": str(target),
        "work_dir": str(work_dir),
        "graphify": {
            "version": version,
            "extraction_mode": "code-only",
        },
        "failures": failures or [],
    }


def _preflight(target: Path, work_dir: Path) -> tuple[int, dict[str, object]]:
    failures: list[str] = []
    if not target.is_dir() or not os.access(target, os.R_OK):
        failures.append("target is missing or unreadable")
    if not work_dir.is_dir() or not os.access(work_dir, os.W_OK):
        failures.append("work_dir is missing or not writable")
    if work_dir == target or target in work_dir.parents:
        failures.append("work_dir must be outside target repository")
    if failures:
        return EXIT_BLOCKED, _doctor_payload(
            "preflight", target, work_dir, EXIT_BLOCKED, failures=failures
        )

    executable = graphify_cli()
    if shutil.which(executable) is None:
        message = "Graphify CLI is unavailable"
        return EXIT_DEPENDENCY_UNAVAILABLE, _doctor_payload(
            "preflight",
            target,
            work_dir,
            EXIT_DEPENDENCY_UNAVAILABLE,
            failures=[message],
        )
    version_result = run([executable, "--version"], timeout=30)
    version = version_result.stdout.strip().splitlines()[0] if version_result.stdout.strip() else None
    help_result = run([executable, "--help"], timeout=30)
    extract_help = run([executable, "extract", "--help"], timeout=30)
    dependency_failures = []
    if version_result.returncode != 0 or version is None:
        dependency_failures.append("Graphify version probe failed")
    elif _version_tuple(version) < GRAPHIFY_MIN_VERSION:
        dependency_failures.append("Graphify version is older than 0.9.13")
    if help_result.returncode != 0 or "--code-only" not in help_result.stdout:
        dependency_failures.append("Graphify code-only extraction capability is unavailable")
    if extract_help.returncode != 0:
        dependency_failures.append("Graphify headless extract capability is unavailable")
    code = EXIT_DEPENDENCY_UNAVAILABLE if dependency_failures else EXIT_READY
    return code, _doctor_payload(
        "preflight", target, work_dir, code, version=version, failures=dependency_failures
    )


def _post_graph(target: Path, work_dir: Path) -> tuple[int, dict[str, object]]:
    graph_dir = work_dir / "graphify-out"
    required = (NORMALIZED_GRAPH, NORMALIZED_REPORT, RAW_GRAPH, RAW_REPORT)
    failures = [f"graphify-out/{name} is missing" for name in required if not (graph_dir / name).is_file()]
    if failures:
        return EXIT_BLOCKED, _doctor_payload(
            "post-graph", target, work_dir, EXIT_BLOCKED, failures=failures
        )
    try:
        graph = json.loads((graph_dir / NORMALIZED_GRAPH).read_text(encoding="utf-8"))
        report = (graph_dir / NORMALIZED_REPORT).read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"Graphify normalized artifacts are invalid: {type(exc).__name__}")
        return EXIT_BLOCKED, _doctor_payload(
            "post-graph", target, work_dir, EXIT_BLOCKED, failures=failures
        )
    if not isinstance(graph, dict):
        failures.append("graph.json root is not an object")
        graph = {}
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    if not isinstance(nodes, list) or not nodes:
        failures.append("graph has zero nodes")
        nodes = []
    if not isinstance(links, list) or not links:
        failures.append("graph has zero edges")
        links = []
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    linked_ids = {
        endpoint
        for link in links
        if isinstance(link, dict)
        for endpoint in (link.get("source"), link.get("target"))
    }
    line_count_cache: dict[Path, int] = {}
    source_nodes = [
        node for node in nodes if _normalized_source_item(node, target, line_count_cache) is not None
    ]
    symbol_nodes = [
        node
        for node in nodes
        if isinstance(node, dict) and not node.get("source_file") and node.get("id") in linked_ids
    ]
    valid_links = [
        link
        for link in links
        if _normalized_source_item(link, target, line_count_cache) is not None
        and isinstance(link, dict)
        and link.get("source") in node_ids
        and link.get("target") in node_ids
    ]
    if not source_nodes or len(source_nodes) + len(symbol_nodes) != len(nodes):
        failures.append("graph contains invalid or missing node source references")
    if not valid_links or len(valid_links) != len(links):
        failures.append("graph contains invalid or missing edge source references")
    report_match = re.search(r"([0-9][0-9,]*) nodes?\s*[·|/]\s*([0-9][0-9,]*) edges?", report)
    if report_match is None:
        failures.append("GRAPH_REPORT.md has no node/edge summary")
    elif (
        int(report_match.group(1).replace(",", "")) != len(nodes)
        or int(report_match.group(2).replace(",", "")) != len(links)
    ):
        failures.append("GRAPH_REPORT.md counts do not match graph.json")
    code = EXIT_BLOCKED if failures else EXIT_READY
    return code, _doctor_payload("post-graph", target, work_dir, code, failures=failures)


def doctor(phase: str, target: Path, work_dir: Path) -> tuple[int, dict[str, object]]:
    if phase == "preflight":
        return _preflight(target, work_dir)
    if phase == "post-graph":
        return _post_graph(target, work_dir)
    return EXIT_BLOCKED, _doctor_payload(
        phase, target, work_dir, EXIT_BLOCKED, failures=["unknown Graphify gate phase"]
    )


def graphify_extract(target: Path, work_dir: Path, log: list[str]) -> list[dict[str, object]]:
    command = [
        graphify_cli(),
        "extract",
        str(target),
        *GRAPHIFY_EXTRACT_OPTIONS,
        "--out",
        str(work_dir),
    ]
    retries = 0
    attempts: list[dict[str, object]] = []
    while True:
        started = time.monotonic()
        environment = os.environ.copy()
        environment["GRAPHIFY_OUT"] = str((work_dir / "graphify-out").resolve())
        result = run(command, cwd=work_dir, env=environment)
        elapsed = round(time.monotonic() - started, 2)
        combined = result.stdout + "\n" + result.stderr
        transient = bool(
            result.returncode not in (0, 124) and TRANSIENT_FAILURE.search(combined)
        )
        attempts.append(
            {
                "command": shlex.join(command),
                "exit_code": result.returncode,
                "elapsed_seconds": elapsed,
                "transient_failure": transient,
                "stdout_class": classify_stream(result.stdout),
                "stderr_class": classify_stream(result.stderr),
            }
        )
        log.append(f"graphify extract exit={result.returncode} elapsed={elapsed}s transient={transient}")
        if result.returncode == 0:
            return attempts
        if not transient or retries >= 2:
            failure_class = "graphify-transient-exhausted" if transient else "graphify-execution"
            raise RunFailure(
                f"Graphify extraction failed with exit code {result.returncode}",
                failure_class=failure_class,
            )
        retries += 1
        time.sleep(2**retries)


def _failure_message(payload: dict[str, object], fallback: str) -> str:
    failures = payload.get("failures")
    if isinstance(failures, list):
        messages = [item for item in failures if isinstance(item, str) and item.strip()]
        if messages:
            return "; ".join(messages)
    return fallback


def _base_status(target: Path, work_dir: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "code": EXIT_BLOCKED,
        "outcome": "blocked",
        "stage": "preflight",
        "target": str(target),
        "work_dir": str(work_dir),
        "graphify": {
            "version": None,
            "extraction_mode": "code-only",
        },
        "artifacts": [],
        "failure": None,
    }


def _write_status(work_dir: Path, status: dict[str, object]) -> None:
    path = work_dir / STATUS_FILENAME
    path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _existing_failure_artifacts(work_dir: Path) -> list[str]:
    graph_dir = work_dir / "graphify-out"
    artifacts = [
        f"graphify-out/{name}"
        for name in (RAW_GRAPH, RAW_REPORT)
        if (graph_dir / name).is_file()
    ]
    if (work_dir / NAVIGATION_MAP).is_file():
        artifacts.append(NAVIGATION_MAP)
    return artifacts


def _complete(
    work_dir: Path,
    status: dict[str, object],
    *,
    code: int,
    outcome: str,
    stage: str,
    failure_class: str | None = None,
    message: str | None = None,
) -> dict[str, object]:
    status["code"] = code
    status["outcome"] = outcome
    status["stage"] = stage
    status["failure"] = (
        {"class": failure_class, "message": message}
        if failure_class is not None and message is not None
        else None
    )
    _write_status(work_dir, status)
    return status


def source_tree_signature(target: Path) -> tuple[tuple[str, int, int, int], ...]:
    """Capture target metadata without following repository internals under .git."""

    if not target.is_dir():
        raise RunFailure("target is missing or is not a directory", failure_class="invalid-input")
    entries: list[tuple[str, int, int, int]] = []
    try:
        for path in target.rglob("*"):
            relative = path.relative_to(target)
            if ".git" in relative.parts:
                continue
            metadata = path.lstat()
            entries.append((relative.as_posix(), metadata.st_mode, metadata.st_size, metadata.st_mtime_ns))
    except OSError as exc:
        raise RunFailure(
            f"target source boundary could not be inspected: {type(exc).__name__}",
            failure_class="source-boundary-inspection",
        ) from exc
    return tuple(sorted(entries))


def ensure_source_unchanged(
    target: Path,
    before: tuple[tuple[str, int, int, int], ...],
    *,
    phase: str,
    target_graphify_existed: bool,
) -> None:
    after = source_tree_signature(target)
    if after == before:
        return
    unexpected_graphify = target / "graphify-out"
    if not target_graphify_existed and unexpected_graphify.is_dir():
        shutil.rmtree(unexpected_graphify)
    raise RunFailure(
        f"source repository changed during {phase}",
        failure_class="source-boundary-violation",
    )


def _resolve_source_file(source_file: str, target: Path) -> tuple[Path | None, str | None]:
    candidate = Path(source_file)
    target = target.resolve()
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            return resolved, resolved.relative_to(target).as_posix() if resolved.is_file() else None
        except ValueError:
            return None, None
    if ".." in candidate.parts:
        return None, None

    direct = (target / candidate).resolve()
    try:
        direct.relative_to(target)
    except ValueError:
        return None, None
    if direct.is_file():
        return direct, candidate.as_posix()

    if candidate.parts and candidate.parts[0] == target.name and len(candidate.parts) > 1:
        normalized = Path(*candidate.parts[1:])
        resolved = (target / normalized).resolve()
        try:
            resolved.relative_to(target)
        except ValueError:
            return None, None
        if resolved.is_file():
            return resolved, normalized.as_posix()
    return None, None


def _normalized_source_item(
    item: object,
    target: Path,
    line_count_cache: dict[Path, int],
) -> dict[str, object] | None:
    if not isinstance(item, dict):
        return None
    source_file = item.get("source_file")
    location = item.get("source_location")
    match = re.search(r"L(\d+)(?:-L?(\d+))?", location or "") if isinstance(location, str) else None
    if not isinstance(source_file, str) or not source_file.strip() or match is None:
        return None
    resolved, normalized_source = _resolve_source_file(source_file, target)
    if resolved is None or normalized_source is None:
        return None
    line_count = line_count_cache.get(resolved)
    if line_count is None:
        line_count = len(resolved.read_text(encoding="utf-8", errors="replace").splitlines())
        line_count_cache[resolved] = line_count
    first = int(match.group(1))
    last = int(match.group(2) or match.group(1))
    if not 1 <= first <= last <= line_count:
        return None
    normalized = dict(item)
    normalized["source_file"] = normalized_source
    return normalized


def normalize_graphify_artifacts(target: Path, work_dir: Path) -> dict[str, object]:
    """Retain raw code-only artifacts and write a source-locatable normalized pair."""

    graph_dir = work_dir / "graphify-out"
    graph_path = graph_dir / NORMALIZED_GRAPH
    report_path = graph_dir / NORMALIZED_REPORT
    raw_graph_path = graph_dir / RAW_GRAPH
    raw_report_path = graph_dir / RAW_REPORT
    raw_pair_exists = raw_graph_path.is_file() and raw_report_path.is_file()
    if (raw_graph_path.exists() or raw_report_path.exists()) and not raw_pair_exists:
        raise RunFailure("Graphify raw artifact pair is incomplete", failure_class="graphify-artifact")
    source_graph_path = raw_graph_path if raw_pair_exists else graph_path
    source_report_path = raw_report_path if raw_pair_exists else report_path
    try:
        raw_graph = json.loads(source_graph_path.read_text(encoding="utf-8"))
        raw_report = source_report_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        raise RunFailure(
            f"Graphify report artifacts are invalid: {type(exc).__name__}",
            failure_class="graphify-artifact",
        ) from exc
    if not isinstance(raw_graph, dict):
        raise RunFailure("Graphify graph root is not an object", failure_class="graphify-artifact")
    nodes = raw_graph.get("nodes", [])
    links = raw_graph.get("links", raw_graph.get("edges", []))
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise RunFailure("Graphify nodes or links are not arrays", failure_class="graphify-artifact")

    if not raw_pair_exists:
        shutil.copy2(graph_path, raw_graph_path)
        shutil.copy2(report_path, raw_report_path)

    line_count_cache: dict[Path, int] = {}
    valid_nodes = [
        normalized
        for node in nodes
        if (normalized := _normalized_source_item(node, target, line_count_cache)) is not None
    ]
    valid_node_ids = {node.get("id") for node in valid_nodes}
    symbol_nodes = [
        dict(node)
        for node in nodes
        if isinstance(node, dict) and not node.get("source_file") and node.get("id") is not None
    ]
    symbol_node_ids = {node.get("id") for node in symbol_nodes}
    allowed_node_ids = valid_node_ids | symbol_node_ids
    valid_links = [
        normalized
        for link in links
        if (normalized := _normalized_source_item(link, target, line_count_cache)) is not None
        and normalized.get("source") in allowed_node_ids
        and normalized.get("target") in allowed_node_ids
    ]
    used_symbol_ids = {
        endpoint
        for link in valid_links
        for endpoint in (link.get("source"), link.get("target"))
        if endpoint in symbol_node_ids
    }
    retained_symbol_nodes = [node for node in symbol_nodes if node.get("id") in used_symbol_ids]
    normalized_graph = {
        "nodes": valid_nodes + retained_symbol_nodes,
        "links": valid_links,
        "normalization": {
            "raw_nodes": len(nodes),
            "raw_edges": len(links),
            "source_locatable_nodes": len(valid_nodes),
            "source_locatable_edges": len(valid_links),
            "dropped_nodes": len(nodes) - len(valid_nodes) - len(retained_symbol_nodes),
            "dropped_edges": len(links) - len(valid_links),
            "raw_report": RAW_REPORT,
        },
    }
    if not valid_nodes or not valid_links:
        raise RunFailure(
            "Graphify normalization produced no source-locatable nodes and relationships",
            failure_class="graphify-artifact",
        )

    graph_path.write_text(json.dumps(normalized_graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "# Graphify 规范化源码证据\n\n"
        f"- Summary: {len(normalized_graph['nodes'])} nodes · {len(valid_links)} edges.\n"
        f"- Raw Graphify graph: {len(nodes)} nodes · {len(links)} edges.\n"
        f"- 已过滤 {normalized_graph['normalization']['dropped_nodes']} 个节点和 "
        f"{normalized_graph['normalization']['dropped_edges']} 条关系。\n"
        f"- 原始报告保留在 `{RAW_REPORT}`，原始图保留在 `{RAW_GRAPH}`。\n\n"
        + raw_report[:4000],
        encoding="utf-8",
    )
    return {
        "raw_artifacts": [f"graphify-out/{RAW_GRAPH}", f"graphify-out/{RAW_REPORT}"],
        "normalized_artifacts": [f"graphify-out/{NORMALIZED_GRAPH}", f"graphify-out/{NORMALIZED_REPORT}"],
        "raw_graph": {"nodes": len(nodes), "edges": len(links)},
        "normalized_graph": {"nodes": len(normalized_graph["nodes"]), "edges": len(valid_links)},
        "normalization": normalized_graph["normalization"],
    }


def graphify_postprocess(target: Path, work_dir: Path, log: list[str]) -> dict[str, object]:
    graph_dir = work_dir / "graphify-out"
    command = [graphify_cli(), "cluster-only", str(work_dir), "--no-label", "--no-viz"]
    environment = os.environ.copy()
    environment["GRAPHIFY_OUT"] = str(graph_dir.resolve())
    started = time.monotonic()
    result = run(command, cwd=work_dir, env=environment)
    summary = {
        "command": shlex.join(command),
        "exit_code": result.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "no_label": True,
        "no_viz": True,
        "stdout_class": classify_stream(result.stdout),
        "stderr_class": classify_stream(result.stderr),
    }
    log.append(f"graphify cluster-only exit={result.returncode} no-label=true no-viz=true")
    if result.returncode != 0:
        raise RunFailure(
            "Graphify report generation failed",
            failure_class="graphify-report-generation",
            details={"cluster_only": summary},
        )
    normalized = normalize_graphify_artifacts(target, work_dir)
    normalized["cluster_only"] = summary
    return normalized


def write_graph_map(work_dir: Path, target: Path) -> str:
    graph_path = work_dir / "graphify-out" / NORMALIZED_GRAPH
    report_path = work_dir / "graphify-out" / NORMALIZED_REPORT
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        report = report_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        raise RunFailure(
            f"Graphify navigation map inputs are invalid: {type(exc).__name__}",
            failure_class="graphify-artifact",
        ) from exc
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    links = graph.get("links", []) if isinstance(graph, dict) else []
    communities = Counter(
        str(node["community"])
        for node in nodes
        if isinstance(node, dict) and node.get("community") is not None
    )
    candidates = [
        f"- `{node['source_file']}:{node.get('source_location', '?')}`：{node.get('label', node.get('id', 'unknown'))}"
        for node in nodes
        if isinstance(node, dict) and node.get("source_file")
    ]
    relations = [
        f"- `{str(link.get('confidence', 'UNKNOWN')).upper()}` "
        f"`{link.get('source_file', '?')}:{link.get('source_location', '?')}`："
        f"{link.get('source', '?')} -> {link.get('target', '?')} ({link.get('relation', 'unknown')})"
        for link in links[:120]
        if isinstance(link, dict)
    ]
    lines = [
        "# Graphify 导航 Map",
        "",
        f"- 节点：{len(nodes)}",
        f"- 关系：{len(links)}",
        f"- 目标仓库：`{target}`",
        "- 证据边界：Graphify 只提供导航候选，最终结论由源码裁决。",
        "",
        "## Community",
        "",
        *(f"- Community {name}：{count} 个节点" for name, count in communities.most_common(40)),
        "",
        "## 规范化报告摘要",
        "",
        report[:4000],
        "",
        "## 候选源码路径",
        "",
        *(candidates[:80] or ["- 没有可用候选；post-graph 本应阻断。"]),
        "",
        "## 关系证据样本",
        "",
        *(relations or ["- 没有可用关系；post-graph 本应阻断。"]),
        "",
    ]
    map_path = work_dir / NAVIGATION_MAP
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text("\n".join(lines), encoding="utf-8")
    return NAVIGATION_MAP


def run_gate(target: Path | str, work_dir: Path | str) -> dict[str, object]:
    """Run the Graphify gate and return its machine-readable terminal status."""

    target_path = Path(target).expanduser().resolve()
    work_path = Path(work_dir).expanduser().resolve()
    status = _base_status(target_path, work_path)
    stage = "preflight"

    try:
        if work_path == target_path or target_path in work_path.parents:
            raise ValueError("work_dir must be outside target repository")
        work_path.mkdir(parents=True, exist_ok=True)
        source_before = source_tree_signature(target_path)
        target_graphify_existed = (target_path / "graphify-out").exists()
        preflight_code, preflight = doctor("preflight", target_path, work_path)
        ensure_source_unchanged(
            target_path,
            source_before,
            phase="Graphify preflight",
            target_graphify_existed=target_graphify_existed,
        )
        graphify = preflight.get("graphify")
        if isinstance(graphify, dict):
            version = graphify.get("version")
            if isinstance(version, str) and version.strip():
                status["graphify"]["version"] = version

        if preflight_code != EXIT_READY:
            if preflight_code == EXIT_DEPENDENCY_UNAVAILABLE:
                return _complete(
                    work_path,
                    status,
                    code=EXIT_DEPENDENCY_UNAVAILABLE,
                    outcome="dependency-unavailable",
                    stage=stage,
                    failure_class="graphify-dependency",
                    message=_failure_message(preflight, "Graphify is unavailable or incompatible"),
                )
            return _complete(
                work_path,
                status,
                code=EXIT_BLOCKED,
                outcome="blocked",
                stage=stage,
                failure_class="doctor-preflight",
                message=_failure_message(preflight, "Graphify preflight failed"),
            )

        log: list[str] = []
        stage = "extract"
        graphify_extract(target_path, work_path, log)
        ensure_source_unchanged(
            target_path,
            source_before,
            phase="Graphify extraction",
            target_graphify_existed=target_graphify_existed,
        )

        stage = "postprocess"
        artifact_summary = graphify_postprocess(target_path, work_path, log)
        ensure_source_unchanged(
            target_path,
            source_before,
            phase="Graphify postprocess",
            target_graphify_existed=target_graphify_existed,
        )
        artifacts: list[str] = []
        for key in ("raw_artifacts", "normalized_artifacts"):
            values = artifact_summary.get(key)
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str) and value not in artifacts:
                        artifacts.append(value)
        status["artifacts"] = artifacts

        stage = "post-graph"
        post_graph_code, post_graph = doctor("post-graph", target_path, work_path)
        ensure_source_unchanged(
            target_path,
            source_before,
            phase="Graphify post-graph validation",
            target_graphify_existed=target_graphify_existed,
        )
        if post_graph_code != EXIT_READY:
            return _complete(
                work_path,
                status,
                code=EXIT_BLOCKED,
                outcome="blocked",
                stage=stage,
                failure_class="doctor-post-graph",
                message=_failure_message(post_graph, "Graphify post-graph validation failed"),
            )

        stage = "navigation-map"
        navigation_map = write_graph_map(work_path, target_path)
        status["artifacts"].append(navigation_map)
        ensure_source_unchanged(
            target_path,
            source_before,
            phase="Graphify navigation map generation",
            target_graphify_existed=target_graphify_existed,
        )
        return _complete(
            work_path,
            status,
            code=EXIT_READY,
            outcome="ready",
            stage="complete",
        )
    except Exception as exc:
        failure_class = exc.failure_class if isinstance(exc, RunFailure) else "graphify-gate"
        if not status["artifacts"]:
            status["artifacts"] = _existing_failure_artifacts(work_path)
        status["failure"] = {"class": failure_class, "message": str(exc)}
        status["code"] = EXIT_BLOCKED
        status["outcome"] = "blocked"
        status["stage"] = stage
        try:
            _write_status(work_path, status)
        except OSError:
            pass
        return status


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stark-repo-analyzer-graphify-gate")
    parser.add_argument("--target", required=True, help="source repository kept read-only by the gate")
    parser.add_argument("--work-dir", required=True, help="writable directory outside the source repository")
    args = parser.parse_args(argv)
    status = run_gate(args.target, args.work_dir)
    print(json.dumps(status, ensure_ascii=False, sort_keys=True))
    return int(status["code"])


if __name__ == "__main__":
    raise SystemExit(main())
