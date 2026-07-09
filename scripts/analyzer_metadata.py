#!/usr/bin/env python3
"""Repository metadata and project manifest card for repo-analyzer.

Extracted from repo_analyzer.py (T03).
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Sequence, Tuple

from analyzer_common import (
    _LOADER,
    BINARY_SUFFIXES,
    run,
    read_text,
    markdown_snippet,
    rel,
)
from analyzer_checkout import first_existing, language_counts, readme_summary
from ask_user_adapters import ask_user as _ask_user, build_questions, ensure_defaults_file


def manifest_snippets(repo: Path) -> List[Tuple[str, str]]:
    names = ["package.json", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "go.mod", "Cargo.toml"]
    snippets = []
    for name in names:
        path = repo / name
        if path.exists():
            text = markdown_snippet("\n".join(read_text(path, 40_000).splitlines()[:80]))
            snippets.append((name, text))
    return snippets


def command_hints(repo: Path, files: List[Path]) -> List[str]:
    relative = {rel(path, repo) for path in files}
    hints = []
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(read_text(package_json)).get("scripts", {})
            for name in ("start", "dev", "test", "build"):
                if name in scripts:
                    hints.append(f"npm run {name}")
        except json.JSONDecodeError:
            pass
    if "main.py" in relative:
        hints.append("python main.py")
    if "cli.py" in relative:
        hints.append("python cli.py")
    if "go.mod" in relative:
        hints.append("go run .")
    if "Cargo.toml" in relative:
        hints.append("cargo run")
    return hints or ["未从常见入口识别到运行命令"]


def top_tree(repo: Path, files: List[Path], limit: int = 80) -> List[str]:
    entries = sorted(rel(path, repo) for path in files)
    return entries[:limit]


def write_meta(repo: Path, output: Path, source: str, files: List[Path]) -> None:
    extensions = Counter(path.suffix or "[no-ext]" for path in files)
    lines = [
        "# 元数据",
        "",
        f"- 目标: {source}",
        f"- HEAD: {run(['git', 'rev-parse', '--short', 'HEAD'], repo) or 'unknown'}",
        "",
        "## 最近提交",
        run(["git", "log", "-1", "--pretty=fuller"], repo) or "无 git 提交信息",
        "",
        "## 文件扩展名 Top20",
    ]
    for suffix, count in extensions.most_common(20):
        lines.append(f"- {suffix}: {count}")
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "data" / "meta.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_repo_type(output: Path, repo_type: str, project_name: str, dimensions: List[Tuple[str, str, Sequence[str]]]) -> None:
    lines = [
        f"project_name: {project_name}",
        f"repo_type: {repo_type}",
        f"dimension_count: {len(dimensions) + 1}",
        "dimensions:",
    ]
    for filename, label, _patterns in dimensions:
        lines.append(f"  - file: {filename}")
        lines.append(f"    label: {label}")
    lines.append("  - file: history-hotspot.txt")
    lines.append("    label: 变更历史热点")
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "data" / "repo-type.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _git_head_info(repo: Path) -> Tuple[str, str, str]:
    """Return (short_hash, commit_date, commit_author) for HEAD."""
    short = run(["git", "rev-parse", "--short", "HEAD"], repo) or "unknown"
    date = run(["git", "log", "-1", "--format=%ci", "HEAD"], repo) or "unknown"
    author = run(["git", "log", "-1", "--format=%an", "HEAD"], repo) or "unknown"
    return short, date, author


def _git_remote_url(repo: Path) -> str:
    """Return the first fetch remote URL, or '未配置'."""
    url = run(["git", "remote", "get-url", "origin"], repo)
    return url.strip() if url and url.strip() else "未配置"


def _estimate_loc(files: List[Path]) -> int:
    """Estimate total lines of code across text files (capped for speed)."""
    total = 0
    for path in files:
        if path.suffix in BINARY_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            total += text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        except (OSError, UnicodeDecodeError):
            continue
    return total


def _binary_file_count(files: List[Path]) -> int:
    """Count files with known binary suffixes."""
    return sum(1 for f in files if f.suffix in BINARY_SUFFIXES)


def _dependency_summary(repo: Path) -> str:
    """Summarize dependencies from common manifest files."""
    deps: List[str] = []
    pkg = repo / "package.json"
    if pkg.exists():
        try:
            data = json.loads(read_text(pkg))
            for key in ("dependencies", "devDependencies"):
                items = data.get(key, {})
                if items:
                    names = ", ".join(sorted(items.keys())[:20])
                    deps.append(f"{key}({len(items)}): {names}")
        except (json.JSONDecodeError, OSError):
            pass
    req = repo / "requirements.txt"
    if req.exists():
        lines = [ln.strip() for ln in read_text(req).splitlines() if ln.strip() and not ln.startswith("#")]
        if lines:
            deps.append(f"requirements.txt({len(lines)}): {', '.join(lines[:20])}")
    pyproj = repo / "pyproject.toml"
    if pyproj.exists():
        text = read_text(pyproj)
        m = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.DOTALL)
        if m:
            items = [ln.strip().strip('"').strip("'") for ln in m.group(1).splitlines() if ln.strip() and not ln.strip().startswith("#")]
            deps.append(f"pyproject.toml({len(items)}): {', '.join(items[:20])}")
    return "\n".join(f"- {d}" for d in deps) if deps else "- 未检测到依赖清单"


def _top_level_dirs(repo: Path, files: List[Path]) -> List[str]:
    """Return sorted unique top-level directory names."""
    dirs = set()
    for path in files:
        try:
            rel_path = path.relative_to(repo)
        except ValueError:
            continue
        if len(rel_path.parts) > 1:
            dirs.add(rel_path.parts[0])
    return sorted(dirs)[:30]


def _license_detect(repo: Path) -> str:
    """Detect license from common license files."""
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"):
        path = repo / name
        if path.exists():
            text = read_text(path)[:500]
            if "MIT" in text:
                return f"MIT (检测到 {name})"
            if "Apache" in text:
                return f"Apache (检测到 {name})"
            if "BSD" in text:
                return f"BSD (检测到 {name})"
            if "GPL" in text:
                return f"GPL (检测到 {name})"
            return f"自定义/其他 (检测到 {name})"
    return "未检测到许可证文件"


def _file_size_stats(files: List[Path]) -> Tuple[int, float]:
    """Return (total_bytes, avg_bytes) across all files."""
    total = 0
    for path in files:
        try:
            total += path.stat().st_size
        except OSError:
            continue
    avg = total / len(files) if files else 0.0
    return total, avg


def write_manifest_card(repo: Path, output: Path, source: str, project_name: str, repo_type: str, files: List[Path]) -> None:
    readme = first_existing(repo, ["README.md", "readme.md", "README.rst"])
    readme_head = markdown_snippet("\n".join(read_text(readme).splitlines()[:30])) if readme else "未发现 README。"
    languages = ", ".join(f"{name}({count})" for name, count in language_counts(files).most_common()) or "未识别"

    # 新增字段（T07：5KB→10KB 扩展）
    head_short, head_date, head_author = _git_head_info(repo)
    remote_url = _git_remote_url(repo)
    total_loc = _estimate_loc(files)
    binary_count = _binary_file_count(files)
    dep_summary = _dependency_summary(repo)
    top_dirs = _top_level_dirs(repo, files)
    license_info = _license_detect(repo)
    total_bytes, avg_bytes = _file_size_stats(files)
    hints = command_hints(repo, files)
    tree_snapshot = top_tree(repo, files, 60)

    # Issue 6: Priority-based truncation instead of blind card[:10_000].
    # Fields are written in priority order; each field has a max length.
    # If adding a field would exceed the 10KB budget, it is skipped entirely
    # (no half-field truncation).
    CARD_BUDGET = 10_000
    sections: List[Tuple[str, str, int]] = [
        # (title, body, max_body_length)
        ("基本信息", _format_basic_info(project_name, source, repo_type, languages, len(files)), 500),
        ("Git 信息", _format_git_info(head_short, head_date, head_author, remote_url), 500),
        ("代码规模", _format_code_scale(total_loc, binary_count, total_bytes, avg_bytes), 400),
        ("许可证", f"- {license_info}", 200),
        ("顶层目录", "\n".join(f"- {d}" for d in top_dirs) or "- (无子目录)", 800),
        ("依赖摘要", dep_summary, 1500),
        ("运行命令", "\n".join(f"- {h}" for h in hints), 500),
        ("顶层文件快照", "\n".join(f"- {item}" for item in tree_snapshot), 1500),
        ("README 前 30 行", f"```text\n{readme_head[:4000]}\n```", 4000),
    ]

    parts: List[str] = ["# 10KB 项目名片\n"]
    for title, body, max_body in sections:
        body = body[:max_body]
        section_text = f"\n## {title}\n{body}\n"
        # Check if adding this section would exceed the budget.
        if len("\n".join(parts)) + len(section_text) > CARD_BUDGET:
            continue
        parts.append(section_text)

    card = "\n".join(parts)
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "data" / "manifest-card.md").write_text(card + "\n", encoding="utf-8")


def _format_basic_info(project_name: str, source: str, repo_type: str, languages: str, file_count: int) -> str:
    return "\n".join([
        f"- 项目名: {project_name}",
        f"- 目标: {source}",
        f"- Repo 类型: {repo_type}",
        f"- 主要语言: {languages}",
        f"- 文件数: {file_count}",
    ])


def _format_git_info(head_short: str, head_date: str, head_author: str, remote_url: str) -> str:
    return "\n".join([
        f"- HEAD: {head_short}",
        f"- 提交时间: {head_date}",
        f"- 提交者: {head_author}",
        f"- 远程仓库: {remote_url}",
    ])


def _format_code_scale(total_loc: int, binary_count: int, total_bytes: int, avg_bytes: float) -> str:
    return "\n".join([
        f"- 估计总行数 (LOC): {total_loc:,}",
        f"- 二进制文件数: {binary_count}",
        f"- 文件总大小: {total_bytes:,} bytes",
        f"- 平均文件大小: {avg_bytes:.0f} bytes",
    ])


def write_question_answers(output: Path, no_question: bool, mode: str) -> None:
    # T04：首次运行自动生成 defaults.yaml；交互不可用/超时/未知运行时降级到默认值。
    ensure_defaults_file()
    questions = build_questions()
    answers = _ask_user(questions, no_question=no_question, mode_default=mode)
    priority = (answers.get("priority") or ["architecture"])[0]
    audience = (answers.get("audience") or [mode])[0]
    usage = answers.get("usage_assumptions") or []
    future = answers.get("future_extensions") or []
    source = "默认值（--no-question）" if no_question else "运行时交互 / 默认值退化"
    path = output / "data" / "question-answers.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# 自适应问题答案

- 来源: {source}
- 优先方向: {priority}
- 报告受众: {audience}
- 用法假设: {json.dumps(usage, ensure_ascii=False)}
- 未来扩展: {json.dumps(future, ensure_ascii=False)}
""",
        encoding="utf-8",
    )


def write_research(output: Path, offline: bool) -> str:
    """运行外部调研阶段（T07）。默认关闭；离线或联网受限时自动 SKIP，不抛异常。

    写入 ``data/research.md``，并返回用于报告模板 ``{{ research_section }}`` 的 Markdown 片段。
    """
    research_path = output / "data" / "research.md"
    research_path.parent.mkdir(parents=True, exist_ok=True)
    if offline:
        content = "# 外部调研\n\n- status: SKIP\n- 原因: 离线模式（--offline），不访问外部 Web\n"
        section = "## 外部调研\n\n- 状态: SKIP（离线模式，未访问外部 Web）\n"
    else:
        # 在线调研：当前运行环境未内置联网源；统一降级为 SKIP，保证主流程不中断。
        content = "# 外部调研\n\n- status: SKIP\n- 原因: 当前运行环境未配置在线调研源（联网受限）\n"
        section = "## 外部调研\n\n- 状态: SKIP（未配置在线调研源）\n"
    research_path.write_text(content, encoding="utf-8")
    return section
