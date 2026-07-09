#!/usr/bin/env python3
"""Repomix slice generation for repo-analyzer.

Extracted from repo_analyzer.py (T03).
"""

import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import List, Sequence

from analyzer_common import IGNORE_DIRS, GENERATED_DIRS, BINARY_SUFFIXES, REPOMIX_BINARY, _LOADER, run, read_text, rel


def repomix_ignore_glob() -> str:
    patterns = []
    for dirname in sorted(IGNORE_DIRS | GENERATED_DIRS):
        patterns.append(f"**/{dirname}/**")
    for suffix in sorted(BINARY_SUFFIXES):
        patterns.append(f"**/*{suffix}")
    return ",".join(patterns)


def repomix_include_glob(patterns: Sequence[str]) -> str:
    expanded = []
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        candidates = [normalized]
        if normalized.startswith("*.") or normalized.endswith("*") or "/" not in normalized:
            candidates.append(f"**/{normalized}")
        if normalized.endswith("/*"):
            base = normalized[:-2]
            candidates.extend([f"{base}/**", f"**/{base}/**"])
        elif "/" in normalized and not normalized.startswith("**/"):
            candidates.append(f"**/{normalized}")
        for item in candidates:
            if item not in expanded:
                expanded.append(item)
    return ",".join(expanded)


def run_repomix_slice(repo: Path, output_file: Path, label: str, patterns: Sequence[str]) -> None:
    if not shutil.which(REPOMIX_BINARY):
        raise SystemExit("缺少 repomix 执行入口：未找到 npx，无法按 PLAN 使用 repomix 生成切片")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    command = [
        REPOMIX_BINARY,
        "--yes",
        "repomix",
        ".",
        "--style",
        "xml",
        "--parsable-style",
        "--include",
        repomix_include_glob(patterns),
        "--ignore",
        repomix_ignore_glob(),
        "--output",
        str(output_file),
        "--quiet",
    ]
    result = subprocess.run(command, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise SystemExit(f"repomix 切片失败: {label} -> {output_file.name}: {detail}")


def write_slice(repo: Path, output: Path, filename: str, label: str, patterns: Sequence[str], files: List[Path]) -> None:
    run_repomix_slice(repo, output / "diagnostics" / "slices" / filename, label, patterns)


def write_history(repo: Path, output: Path) -> None:
    history = run(["git", "log", "--name-only", "--pretty=format:"], repo)
    counts = Counter(
        line.strip()
        for line in history.splitlines()
        if line.strip() and not any(part in IGNORE_DIRS for part in Path(line.strip()).parts)
    )
    lines = ["# 变更历史热点", "", "## 累计修改次数 Top50"]
    if counts:
        for path, count in counts.most_common(50):
            lines.append(f"- {count} {path}")
    else:
        lines.append("- 无历史热点数据")
    lines.extend(["", "## 最近 30 天提交", run(["git", "log", "--since=30 days ago", "--pretty=format:%h | %ad | %s", "--date=short"], repo) or "无"])
    (output / "diagnostics" / "slices" / "history-hotspot.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_slices(repo: Path, output: Path, repo_type: str, files: List[Path]) -> None:
    slices_dir = output / "diagnostics" / "slices"
    slices_dir.mkdir(parents=True, exist_ok=True)
    dimensions = _LOADER.load(repo_type)
    for filename, label, patterns in dimensions:
        write_slice(repo, output, filename, label, patterns, files)
    write_history(repo, output)
