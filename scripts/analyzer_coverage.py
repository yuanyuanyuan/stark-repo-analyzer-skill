#!/usr/bin/env python3
"""Symbol extraction and coverage gating for repo-analyzer.

Extracted from repo_analyzer.py (T04).
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Sequence, Tuple

from analyzer_common import (
    SOURCE_SYMBOL_LIMIT,
    API_SURFACE_LIMIT,
    TREE_SITTER_CHUNK_BYTES,
    SYMBOL_SUFFIXES,
    TREE_SITTER_QUERIES,
    module_rows,
    read_text,
    rel,
)


def source_symbols(repo: Path, files: List[Path], limit: int = SOURCE_SYMBOL_LIMIT) -> List[Tuple[str, str, str]]:
    symbols = []
    seen = set()
    patterns = [
        re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", re.MULTILINE),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(", re.MULTILINE),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*async\s*(?:\(|[A-Za-z_$])", re.MULTILINE),
        re.compile(r"^\s*([A-Za-z_$][\w$]*)\s*:\s*(?:async\s+)?(?:function\s*)?\(", re.MULTILINE),
        re.compile(r"^\s*async\s+([A-Za-z_$][\w$]*)\s*\(", re.MULTILINE),
        re.compile(r"^\s*def\s+([A-Za-z_][\w]*)\s*\(", re.MULTILINE),
        re.compile(r"^\s*class\s+([A-Za-z_][\w]*)\s*[:(]", re.MULTILINE),
    ]
    for path in files:
        if path.suffix.lower() not in SYMBOL_SUFFIXES:
            continue
        text = read_text(path, 200_000)
        for pattern in patterns:
            for match in pattern.finditer(text):
                item = (match.group(1), rel(path, repo), str(text[: match.start()].count("\n") + 1))
                if item in seen:
                    continue
                seen.add(item)
                symbols.append(item)
                if len(symbols) >= limit:
                    return symbols
    return symbols


def tree_sitter_query_symbols(binary: str, path: Path, repo: Path, query_text: str) -> Tuple[List[Tuple[str, str, str]], str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".scm", delete=False) as handle:
        handle.write(query_text)
        query_path = Path(handle.name)
    try:
        result = subprocess.run([binary, "query", str(query_path), str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    finally:
        query_path.unlink(missing_ok=True)
    if result.returncode != 0:
        return [], (result.stderr or result.stdout).strip()
    symbols = []
    text = read_text(path, 200_000)
    lines = text.splitlines()
    for match in re.finditer(r"(?:pattern:\s*\d+,\s*)?capture:\s*name\s*,\s*start:\s*\((\d+),\s*(\d+)\)", result.stdout):
        row = int(match.group(1))
        column = int(match.group(2))
        if row >= len(lines):
            continue
        candidate = re.match(r"[A-Za-z_$][\w$]*", lines[row][column:])
        if not candidate:
            continue
        symbols.append((candidate.group(0), rel(path, repo), str(row + 1)))
    return symbols, ""


def tree_sitter_scan(repo: Path, files: List[Path], limit: int) -> Tuple[List[Tuple[str, str, str]], dict]:
    binary = shutil.which("tree-sitter")
    meta = {
        "engine": "regex-fallback",
        "tree_sitter_available": bool(binary),
        "tree_sitter_version": "",
        "scanned_files": 0,
        "parsed_files": 0,
        "queried_files": 0,
        "query_symbols": 0,
        "skipped_large_files": [],
        "parse_failures": [],
        "query_failures": [],
    }
    if not binary:
        meta["reason"] = "tree-sitter CLI not found"
        return source_symbols(repo, files, limit), meta

    version = subprocess.run([binary, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    meta["tree_sitter_version"] = (version.stdout or version.stderr).strip()
    symbols = []
    seen = set()
    candidates = [path for path in files if path.suffix.lower() in SYMBOL_SUFFIXES]
    meta["scanned_files"] = len(candidates)
    for path in candidates:
        if path.stat().st_size >= TREE_SITTER_CHUNK_BYTES:
            meta["skipped_large_files"].append(rel(path, repo))
            continue
        parsed = subprocess.run([binary, "parse", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if parsed.returncode == 0:
            meta["parsed_files"] += 1
            query = TREE_SITTER_QUERIES.get(path.suffix.lower())
            if query:
                queried, error = tree_sitter_query_symbols(binary, path, repo, query)
                if error:
                    if len(meta["query_failures"]) < 20:
                        meta["query_failures"].append({"file": rel(path, repo), "error": error.splitlines()[:1]})
                else:
                    meta["queried_files"] += 1
                    for item in queried:
                        if item in seen:
                            continue
                        seen.add(item)
                        symbols.append(item)
                        if len(symbols) >= limit:
                            meta["engine"] = "tree-sitter-query"
                            meta["query_symbols"] = len(symbols)
                            return symbols, meta
        elif len(meta["parse_failures"]) < 20:
            meta["parse_failures"].append({"file": rel(path, repo), "error": parsed.stderr.strip().splitlines()[:1]})
    meta["query_symbols"] = len(symbols)
    if symbols:
        meta["engine"] = "tree-sitter-query"
        return symbols, meta
    meta["engine"] = "tree-sitter+regex"
    meta["reason"] = "tree-sitter query produced no symbols; regex fallback used"
    return source_symbols(repo, files, limit), meta


def mcp_tool_names(repo: Path, files: List[Path], limit: int = API_SURFACE_LIMIT) -> List[Tuple[str, str, str]]:
    tools = []
    seen = set()
    pattern = re.compile(r"\bname\s*:\s*['\"](ai_[A-Za-z0-9_$-]+)['\"]")
    for path in files:
        if path.suffix.lower() not in {".js", ".ts", ".mjs", ".cjs"}:
            continue
        text = read_text(path, 300_000)
        for match in pattern.finditer(text):
            item = (match.group(1), rel(path, repo), str(text[: match.start()].count("\n") + 1))
            if item in seen:
                continue
            seen.add(item)
            tools.append(item)
            if len(tools) >= limit:
                return tools
    return tools


def module_file_paths(files: List[Path], repo: Path, root: str) -> List[str]:
    paths = []
    for path in files:
        relative = rel(path, repo)
        if (root == "[root]" and "/" not in relative) or relative.startswith(f"{root}/"):
            paths.append(relative)
    return sorted(paths)


def module_ids_from_plan(output: Path) -> List[str]:
    modules_text = read_text(output / "data" / "module-ids.yaml", 100_000)
    return re.findall(r"(?m)^\s*- id: (module_[0-9]+)", modules_text)


def symbol_coverage(
    output: Path,
    files: List[Path],
    repo: Path,
    core_threshold: float,
    minor_threshold: float,
    coverage_engine: str,
) -> dict:
    if coverage_engine == "regex":
        symbols = source_symbols(repo, files, 10_000)
        engine_meta = {"engine": "regex", "tree_sitter_available": bool(shutil.which("tree-sitter"))}
    else:
        symbols, engine_meta = tree_sitter_scan(repo, files, 10_000)
    rows = module_rows(files, repo)
    draft_dir = output / "diagnostics" / "module-drafts"
    result = {
        "thresholds": {"core": core_threshold, "minor": minor_threshold},
        "engine": engine_meta,
        "modules": {},
    }
    for index, (module_id, root, count) in enumerate(rows, 1):
        tier = "core" if index <= 3 else "minor"
        expected = [
            {"name": name, "file": file_path, "line": line}
            for name, file_path, line in symbols
            if (root == "[root]" and "/" not in file_path) or file_path.startswith(f"{root}/")
        ]
        draft_text = read_text(draft_dir / f"module-{module_id}.md", 500_000)
        covered = sorted({item["name"] for item in expected if re.search(rf"\b{re.escape(item['name'])}\b", draft_text)})
        missing = sorted({item["name"] for item in expected} - set(covered))
        ratio = 1.0 if not expected else len(covered) / len({item["name"] for item in expected})
        threshold = core_threshold if tier == "core" else minor_threshold
        result["modules"][module_id] = {
            "root": root,
            "tier": tier,
            "file_count": count,
            "expected_symbols": expected,
            "covered_symbols": covered,
            "missing_symbols": missing,
            "coverage_ratio": round(ratio, 4),
            "threshold": threshold,
            "status": "PASS" if ratio >= threshold else "FAIL",
        }
    return result


def write_coverage(output: Path, files: List[Path], repo: Path, core_threshold: float, minor_threshold: float, coverage_engine: str) -> dict:
    (output / "data").mkdir(parents=True, exist_ok=True)
    rows = module_rows(files, repo)
    coverage = symbol_coverage(output, files, repo, core_threshold, minor_threshold, coverage_engine)
    expected_symbols = []
    for module_id, item in coverage["modules"].items():
        for symbol in item["expected_symbols"]:
            expected_symbols.append({"module": module_id, **symbol})
    (output / "data" / "expected-symbols.json").write_text(json.dumps({"engine": coverage["engine"], "symbols": expected_symbols}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "data" / "coverage-symbols.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failed = [module_id for module_id, item in coverage["modules"].items() if item["status"] != "PASS"]
    engine = coverage["engine"]
    lines = [
        "# 覆盖率门控",
        "",
        f"- 状态: {'PASS' if not failed else 'FAIL'}",
        f"- 核心阈值: {core_threshold:.2f}",
        f"- 次要阈值: {minor_threshold:.2f}",
        f"- engine: {engine.get('engine', 'unknown')}",
        f"- tree_sitter_available: {str(bool(engine.get('tree_sitter_available'))).lower()}",
        f"- tree_sitter_parsed_files: {engine.get('parsed_files', 0)}",
        f"- tree_sitter_queried_files: {engine.get('queried_files', 0)}",
        f"- tree_sitter_query_symbols: {engine.get('query_symbols', 0)}",
        f"- skipped_large_files: {len(engine.get('skipped_large_files', []))}",
        "",
        "| 模块 ID | tier | 文件数 | 符号覆盖率 | 覆盖状态 |",
        "|---|---|---:|---:|---|",
    ]
    for module_id, _name, _count in rows:
        item = coverage["modules"][module_id]
        lines.append(f"| {module_id} | {item['tier']} | {item['file_count']} | {item['coverage_ratio']:.2f} | {item['status']} |")
    lines.extend(["", "> 覆盖率门控已用确定性符号提取核对模块草稿；tree-sitter 可用时先做串行 parse 与大文件保护记录，业务语义评价可由后续 subagent 复核。"])
    (output / "data" / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if failed:
        failure_lines = ["# 覆盖率失败明细", ""]
        for module_id in failed:
            item = coverage["modules"][module_id]
            failure_lines.append(f"## {module_id}")
            failure_lines.append(f"- 覆盖率: {item['coverage_ratio']:.2f}")
            failure_lines.append(f"- 阈值: {item['threshold']:.2f}")
            failure_lines.append(f"- 缺失符号: {', '.join(item['missing_symbols'][:30]) or '无'}")
            failure_lines.append("")
        (output / "data" / "coverage-failure.md").write_text("\n".join(failure_lines), encoding="utf-8")
    return coverage


def failed_module_records(coverage: dict) -> List[dict]:
    failed_modules = []
    for module_id, item in coverage["modules"].items():
        if item["status"] != "PASS":
            failed_modules.append(
                {
                    "id": module_id,
                    "tier": item["tier"],
                    "attempts": 1,
                    "last_error": "COVERAGE_FAILED",
                    "missing_symbols_count": len(item["missing_symbols"]),
                    "coverage_ratio": item["coverage_ratio"],
                    "suggested_recovery": f"补充 diagnostics/module-drafts/module-{module_id}.md 中缺失符号说明后重跑 acceptance",
                }
            )
    return failed_modules
