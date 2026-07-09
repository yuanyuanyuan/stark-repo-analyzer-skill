#!/usr/bin/env python3
"""Repository checkout and file enumeration for repo-analyzer.

Extracted from repo_analyzer.py (T03).
"""

import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple

from analyzer_common import IGNORE_DIRS, BINARY_SUFFIXES, is_url, read_text, markdown_snippet, rel, run


def checkout_target(target: str) -> Tuple[Path, str, tempfile.TemporaryDirectory]:
    temp = tempfile.TemporaryDirectory(prefix="repo-analyzer-")
    if not is_url(target):
        path = Path(target).expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"目标仓库不存在: {path}")
        return path, str(path), temp

    repo_dir = Path(temp.name) / "repo"
    result = subprocess.run(
        ["git", "clone", "--depth=1", target, str(repo_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip())
    return repo_dir, target, temp


def iter_files(repo: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in BINARY_SUFFIXES:
                continue
            yield path


def parse_project_name(repo: Path) -> str:
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            name = json.loads(read_text(package_json)).get("name")
            if name:
                return str(name)
        except json.JSONDecodeError:
            pass

    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        match = re.search(r'(?m)^name\s*=\s*["\']([^"\']+)["\']', read_text(pyproject))
        if match:
            return match.group(1)

    readme = first_existing(repo, ["README.md", "readme.md", "README.rst"])
    if readme:
        for line in read_text(readme).splitlines():
            title = line.lstrip("#").strip()
            if title:
                return title
    return repo.name


def first_existing(repo: Path, names: List[str]) -> Path:
    for name in names:
        path = repo / name
        if path.exists():
            return path
    return None


def language_counts(files: List[Path]) -> Counter:
    names = Counter()
    mapping = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".c": "C",
        ".h": "C/C++",
        ".cpp": "C++",
        ".cc": "C++",
    }
    for path in files:
        language = mapping.get(path.suffix.lower())
        if language:
            names[language] += 1
    return names


def readme_summary(repo: Path) -> Tuple[str, str]:
    readme = first_existing(repo, ["README.md", "readme.md", "README.rst"])
    if not readme:
        return "未发现 README。", ""
    lines = [line.strip() for line in read_text(readme).splitlines()]
    title = ""
    summary = []
    for line in lines:
        if not title and line.startswith("#"):
            title = line.strip("# ").strip()
            continue
        if line and not line.startswith("#") and len(summary) < 5:
            summary.append(line)
    return title or "未命名项目", "\n".join(f"- {markdown_snippet(line)}" for line in summary) or "README 未提供正文摘要。"


def detect_repo_type(repo: Path, files: List[Path]) -> str:
    relative = {rel(path, repo) for path in files}
    languages = language_counts(files)
    if {"pnpm-workspace.yaml", "lerna.json", "nx.json"} & relative or any("/packages/" in f for f in relative):
        return "monorepo"
    if {".claude", ".codex", ".cursor", ".agents"} & {p.parts[0] for p in (path.relative_to(repo) for path in files if path.relative_to(repo).parts)}:
        return "multi-agent-config"
    if any(name in relative for name in ("AGENTS.md", "CLAUDE.md")) and not languages:
        return "multi-agent-config"
    if any(path.suffix in {".tsx", ".jsx", ".vue", ".svelte"} for path in files):
        return "web-fullstack"
    if languages and set(languages) <= {"C", "C/C++", "C++", "Rust"} and (repo / "Makefile").exists():
        return "embedded-kernel"
    if any(Path(name).name in {"main.py", "cli.py", "index.js", "main.go", "main.rs"} for name in relative):
        return "single-lang-CLI"
    if languages:
        return "single-lang-lib"
    return "single-lang-CLI"
