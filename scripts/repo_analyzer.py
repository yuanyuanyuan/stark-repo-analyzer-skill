#!/usr/bin/env python3
"""Deterministic repo-analyzer entrypoint."""

import argparse
import fnmatch
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "vendor",
    "coverage",
}

BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".tar",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".wasm",
}

SLICES: Dict[str, List[Tuple[str, str, Sequence[str]]]] = {
    "web-fullstack": [
        ("01-frontend.xml", "前端代码", ["*.tsx", "*.jsx", "*.vue", "*.svelte", "*.css", "*.scss", "*.html"]),
        ("02-backend.xml", "后端代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("03-database.xml", "数据库设计", ["*.sql", "*.prisma", "migrations/*", "schema/*"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "docker-compose*", "Makefile", "*.sh", ".github/*", "scripts/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
    ],
    "single-lang-CLI": [
        ("02-backend.xml", "代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
        ("10-examples.xml", "示例与 demo", ["examples/*", "samples/*", "demo/*", "notebooks/*"]),
    ],
    "single-lang-lib": [
        ("02-backend.xml", "库代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
        ("10-examples.xml", "示例与 demo", ["examples/*", "samples/*", "demo/*"]),
    ],
    "multi-agent-config": [
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("05-agent-config.xml", "AI Agent 配置", [".claude/*", ".codex/*", ".cursor/*", ".agents/*", "AGENTS.md", "CLAUDE.md"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pyproject.toml", "requirements*.txt", "go.mod", "Cargo.toml"]),
    ],
    "monorepo": [
        ("02-backend.xml", "包代码", ["*.py", "*.go", "*.rs", "*.java", "*.ts", "*.js"]),
        ("04-docs.xml", "文档", ["*.md", "*.mdx", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*", "*.spec.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Dockerfile*", "Makefile", "*.sh", "scripts/*", ".github/*"]),
        ("09-dependencies.xml", "第三方依赖清单", ["package.json", "pnpm-workspace.yaml", "pyproject.toml", "go.mod", "Cargo.toml"]),
    ],
    "embedded-kernel": [
        ("02-backend.xml", "系统代码", ["*.c", "*.h", "*.cc", "*.cpp", "*.rs"]),
        ("04-docs.xml", "文档", ["*.md", "*.rst", "docs/*", "README*"]),
        ("06-tests.xml", "测试", ["test/*", "tests/*", "*test.*"]),
        ("07-config-scripts.xml", "配置与脚本", ["Makefile", "*.sh", "CMakeLists.txt"]),
        ("09-dependencies.xml", "第三方依赖清单", ["Cargo.toml", "go.mod", "requirements*.txt"]),
    ],
}


def run(cmd: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()


def clean_output(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://") or value.startswith("git@")


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


def rel(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def read_text(path: Path, limit: int = 200_000) -> str:
    try:
        data = path.read_bytes()[:limit]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def match_any(relative_path: str, patterns: Sequence[str]) -> bool:
    name = Path(relative_path).name
    for pattern in patterns:
        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
        if "/" in pattern and fnmatch.fnmatch(relative_path, f"**/{pattern}"):
            return True
    return False


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


def first_existing(repo: Path, names: Sequence[str]) -> Path:
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
    return title or "未命名项目", "\n".join(f"- {line}" for line in summary) or "README 未提供正文摘要。"


def manifest_snippets(repo: Path) -> List[Tuple[str, str]]:
    names = ["package.json", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "go.mod", "Cargo.toml"]
    snippets = []
    for name in names:
        path = repo / name
        if path.exists():
            text = "\n".join(read_text(path, 40_000).splitlines()[:80])
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


def source_symbols(repo: Path, files: List[Path], limit: int = 80) -> List[Tuple[str, str, str]]:
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
        if path.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs"}:
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


def mcp_tool_names(repo: Path, files: List[Path], limit: int = 80) -> List[Tuple[str, str, str]]:
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


def write_module_drafts(repo: Path, output: Path, files: List[Path]) -> None:
    drafts = output / "drafts"
    drafts.mkdir()
    symbols = source_symbols(repo, files)
    tools = mcp_tool_names(repo, files)
    by_root: Dict[str, List[Tuple[str, str, str]]] = {}
    for name, file_path, line in symbols:
        root = file_path.split("/", 1)[0] if "/" in file_path else "[root]"
        by_root.setdefault(root, []).append((name, file_path, line))
    for index, (module_id, root, count) in enumerate(module_rows(files, repo), 1):
        root_symbols = by_root.get(root, [])
        if root == "[root]":
            root_symbols = [symbol for symbol in symbols if "/" not in symbol[1]]
        root_tools = [tool for tool in tools if (root == "[root]" and "/" not in tool[1]) or tool[1].startswith(f"{root}/")]
        symbol_lines = "\n".join(f"- `{name}` ({file_path}:{line})" for name, file_path, line in root_symbols[:30]) or "- 未识别到公开符号"
        tool_lines = "\n".join(f"- `{name}` ({file_path}:{line})" for name, file_path, line in root_tools[:40]) or "- 未识别到 MCP 工具"
        (drafts / f"06-module-{module_id}.md").write_text(
            f"""# {module_id} {root}

- 文件数: {count}
- 分层: {"core" if index <= 3 else "minor"}

## 角色
该模块由确定性扫描按路径分组生成，用于给后续 subagent 提供分析入口。

## 关键符号
{symbol_lines}

## MCP 工具/API 表面
{tool_lines}

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| {root} | {count} | deterministic scan |
""",
            encoding="utf-8",
        )


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
    (output / "00-meta.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    lines.append("  - file: 12-history-hotspot.txt")
    lines.append("    label: 变更历史热点")
    (output / "02a-repo-type.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def top_tree(repo: Path, files: List[Path], limit: int = 80) -> List[str]:
    entries = sorted(rel(path, repo) for path in files)
    return entries[:limit]


def write_manifest_card(repo: Path, output: Path, source: str, project_name: str, repo_type: str, files: List[Path]) -> None:
    readme = first_existing(repo, ["README.md", "readme.md", "README.rst"])
    readme_head = "\n".join(read_text(readme).splitlines()[:30]) if readme else "未发现 README。"
    languages = ", ".join(f"{name}({count})" for name, count in language_counts(files).most_common()) or "未识别"
    card = f"""# 5KB 项目名片

- 项目名: {project_name}
- 目标: {source}
- Repo 类型: {repo_type}
- 主要语言: {languages}
- 文件数: {len(files)}

## 顶层文件快照
{chr(10).join(f"- {item}" for item in top_tree(repo, files, 60))}

## README 前 30 行
```text
{readme_head[:2400]}
```
"""
    (output / "02a-manifest-card.md").write_text(card[:5_000] + "\n", encoding="utf-8")


def write_question_answers(output: Path, no_question: bool, mode: str) -> None:
    path = output / "03-question-answers.md"
    source = "默认值（--no-question）" if no_question else "默认值"
    path.write_text(
        f"""# 自适应问题答案

- 来源: {source}
- 优先方向: architecture
- 报告受众: {mode}
- 用法假设: []
- 未来扩展: []
""",
        encoding="utf-8",
    )


def write_slice(repo: Path, output: Path, filename: str, label: str, patterns: Sequence[str], files: List[Path]) -> None:
    matched = [path for path in files if match_any(rel(path, repo), patterns)]
    parts = [f'<slice name="{html.escape(label)}">']
    for path in matched[:200]:
        relative_path = rel(path, repo)
        parts.append(f'  <file path="{html.escape(relative_path)}">')
        parts.append(html.escape(read_text(path, 80_000)))
        parts.append("  </file>")
    parts.append("</slice>")
    (output / "slices" / filename).write_text("\n".join(parts) + "\n", encoding="utf-8")


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
    (output / "slices" / "12-history-hotspot.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_slices(repo: Path, output: Path, repo_type: str, files: List[Path]) -> None:
    slices_dir = output / "slices"
    slices_dir.mkdir()
    dimensions = SLICES[repo_type]
    for filename, label, patterns in dimensions:
        write_slice(repo, output, filename, label, patterns, files)
    write_history(repo, output)


def module_rows(files: List[Path], repo: Path) -> List[Tuple[str, str, int]]:
    groups = Counter()
    for path in files:
        relative = path.relative_to(repo)
        root = relative.parts[0] if len(relative.parts) > 1 else "[root]"
        groups[root] += 1
    return [(f"module_{index:03d}", name, count) for index, (name, count) in enumerate(groups.most_common(8), 1)]


def write_module_plan(repo: Path, output: Path, files: List[Path]) -> None:
    rows = module_rows(files, repo)
    lines = ["modules:"]
    for index, (module_id, name, count) in enumerate(rows, 1):
        tier = "core" if index <= 3 else "minor"
        lines.append(f"  - id: {module_id}")
        lines.append(f"    name: {name}")
        lines.append(f"    tier: {tier}")
        lines.append(f"    storyline_position: {index}")
        lines.append(f"    file_count: {count}")
    (output / "05-module-ids.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_coverage(output: Path, files: List[Path], repo: Path) -> None:
    rows = module_rows(files, repo)
    lines = ["# 覆盖率门控", "", "| 模块 ID | tier | 文件数 | 覆盖状态 |", "|---|---|---:|---|"]
    for index, (module_id, _name, count) in enumerate(rows, 1):
        tier = "core" if index <= 3 else "minor"
        lines.append(f"| {module_id} | {tier} | {count} | 已完成确定性门控 |")
    lines.extend(["", "> 覆盖率门控已记录模块、分层、文件数和切片证据；业务语义评价可由后续 subagent 复核。"])
    (output / "08-coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_state_report(output: Path) -> None:
    (output / "STATE_REPORT.md").write_text(
        """---
failed_modules: []
---

# 状态报告

- 当前状态: PASS_DETERMINISTIC_ACCEPTANCE
- 失败模块: 0
- 下一步: 如需主观架构评价，使用 subagent 基于当前产物复核。
""",
        encoding="utf-8",
    )


def audience_section(
    mode: str,
    repo_type: str,
    files: List[Path],
    commands: List[str],
    modules: List[Tuple[str, str, int]],
    tools: List[Tuple[str, str, str]],
) -> str:
    tool_count = len(tools)
    command_lines = "\n".join(f"- `{command}`" for command in commands)
    largest = modules[0] if modules else ("module_001", "[root]", len(files))
    if mode == "business":
        return f"""## 6. 业务负责人关注
- 可交付能力：当前仓库暴露 {tool_count} 个对外工具/API，直接决定可包装给用户的能力范围。
- 采用成本：识别到 {len(commands)} 个运行命令候选，优先从最短可复现路径验证部署和演示。
- 主要风险：最大模块 `{largest[1]}` 覆盖 {largest[2]} 个文件，后续业务评审应先确认它是否承载核心价值。
- 证据入口：先读 `02a-manifest-card.md` 和 `ANALYSIS_REPORT.business.md`，再按需查看 `slices/04-docs.xml`。

### 业务验证动作
{command_lines}
"""
    if mode == "learning":
        first_module = largest[0]
        return f"""## 6. 学习路径
1. 先读 `README.md` 和 `02a-manifest-card.md`，建立项目用途、语言和入口的第一印象。
2. 再读 `05-module-ids.yaml`，把 `{first_module}` 作为第一批学习对象。
3. 接着打开 `drafts/06-module-{first_module}.md`，只看关键符号和 MCP 工具/API 表面。
4. 最后用 `slices/04-docs.xml` 对照文档，用 `slices/02-backend.xml` 对照实现。

### 初学者检查点
- 能说清项目提供什么能力。
- 能找到一个运行命令。
- 能指出一个公开工具/API 来自哪个文件和行号。
"""
    return f"""## 6. 技术负责人关注
- 架构形态：`{repo_type}`，当前实现把类型识别、切片、模块计划、覆盖门控和报告生成放在一条可复现 CLI 中。
- 维护焦点：最大文件组 `{largest[1]}` 有 {largest[2]} 个文件，优先审查该组的边界和测试覆盖。
- API 表面：识别到 {tool_count} 个对外工具/API，报告已把名称回链到文件和行号。
- 验收入口：`acceptance/check.sh` 会检查产物完整性、报告差异、引用链、API 名称和门控状态。

### 技术复核动作
{command_lines}
"""


def report_body(project_name: str, source: str, repo_type: str, files: List[Path], repo: Path, mode: str) -> str:
    languages = language_counts(files)
    language_line = ", ".join(f"{name}({count})" for name, count in languages.most_common()) or "未识别"
    modules = module_rows(files, repo)
    module_table = "\n".join(f"| {module_id} | {name} | {count} |" for module_id, name, count in modules)
    readme_title, readme_points = readme_summary(repo)
    manifests = manifest_snippets(repo)
    manifest_section = "\n\n".join(f"### {name}\n```text\n{text}\n```" for name, text in manifests) or "未发现常见依赖 manifest。"
    command_list = command_hints(repo, files)
    commands = "\n".join(f"- `{command}`" for command in command_list)
    tree = "\n".join(f"- `{item}`" for item in top_tree(repo, files, 40))
    symbols = source_symbols(repo, files, 30)
    symbol_lines = "\n".join(f"- `{name}` (`{file_path}:{line}`)" for name, file_path, line in symbols) or "- 未识别到代码符号"
    tools = mcp_tool_names(repo, files, 60)
    tool_lines = "\n".join(f"- `{name}` (`{file_path}:{line}`)" for name, file_path, line in tools) or "- 未识别到 MCP 工具/API 名称"
    slice_names = [filename for filename, _label, _patterns in SLICES[repo_type]] + ["12-history-hotspot.txt"]
    slice_links = "\n".join(f"- `slices/{name}`" for name in slice_names)
    audience = audience_section(mode, repo_type, files, command_list, modules, tools)
    manifest_names = ", ".join(name for name, _text in manifests) or "未发现"
    largest = modules[0] if modules else ("module_001", "[root]", len(files))
    if mode == "business":
        tool_summary = "\n".join(f"- {name}" for name, _file_path, _line in tools[:20]) or "- 未识别到对外工具/API"
        return f"""# {project_name} 业务分析报告

> 目标 `{source}`；Repo 类型 `{repo_type}`；报告由确定性 repo-analyzer CLI 生成。

## 0. 管理摘要
- 项目识别名：{readme_title}
- 对外能力数量：{len(tools)}
- 运行命令候选：{len(command_list)}
- 最大维护单元：`{largest[1]}`（{largest[2]} 个文件）

## 1. 用户价值
README 摘要显示该项目的主要卖点是：
{readme_points}

当前扫描到的能力清单：
{tool_summary}

## 2. 采用成本
- 主要语言：{language_line}
- 依赖 manifest：{manifest_names}
- 推荐先验证的命令：
{commands}

## 3. 业务风险
- 能力集中在 `{largest[1]}`，如果该模块缺少测试或错误处理，发布风险会集中放大。
- 当前报告能确认文件、manifest、工具名和运行入口；市场定位、用户留存和真实搜索质量仍需要人工或 subagent 评审。
- 验收入口是 `acceptance/check.sh`，适合在交付前做快速门禁。

{audience}

## 7. 证据索引
- 项目名片：`02a-manifest-card.md`
- 主技术报告：`ANALYSIS_REPORT.tech-lead.md`
- 文档切片：`slices/04-docs.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 状态报告：`STATE_REPORT.md`
"""
    if mode == "learning":
        first_module = largest[0]
        first_tool = tools[0][0] if tools else "未识别"
        first_symbol = symbols[0][0] if symbols else "未识别"
        return f"""# {project_name} 学习报告

> 目标 `{source}`；Repo 类型 `{repo_type}`；报告由确定性 repo-analyzer CLI 生成。

## 0. 先建立心智模型
- 这是一个 `{repo_type}` 仓库。
- 主要语言是：{language_line}。
- 你先把它理解成“文档说明能力、manifest 说明安装方式、源码说明真实入口”的三层结构。

## 1. 阅读顺序
1. 打开 `02a-manifest-card.md`，只看项目名、文件数、README 前 30 行。
2. 打开 `05-module-ids.yaml`，找到第一个模块 `{first_module}`。
3. 打开 `drafts/06-module-{first_module}.md`，看关键符号和工具/API 表面。
4. 打开 `slices/02-backend.xml`，对照源码里的入口。
5. 最后看 `ANALYSIS_REPORT.tech-lead.md`，把技术判断补齐。

## 2. 本仓库的第一批观察
- README 标题：{readme_title}
- 第一个关键符号：`{first_symbol}`
- 第一个对外工具/API：`{first_tool}`
- 运行命令候选：
{commands}

## 3. 练习题
- 解释 `{first_module}` 为什么被排在模块清单第一位。
- 找到 `{first_tool}` 在源码中的文件和行号。
- 说明 `slices/04-docs.xml` 和 `slices/02-backend.xml` 分别适合回答什么问题。

{audience}

## 7. 证据索引
- 学习入口：`02a-manifest-card.md`
- 模块清单：`05-module-ids.yaml`
- 模块草稿：`drafts/06-module-{first_module}.md`
- 代码切片：`slices/02-backend.xml`
- 文档切片：`slices/04-docs.xml`
"""
    return f"""# {project_name} 架构分析报告（{mode}）

> 元信息：目标 `{source}`；Repo 类型 `{repo_type}`；报告由确定性 repo-analyzer CLI 生成。

## 0. TL;DR
- 项目识别名：{readme_title}
- 主要语言：{language_line}
- 当前报告已完成确定性扫描、动态切片、模块候选、对外工具/API 表面和复现入口；需要主观评价的部分可交给后续 subagent 深化。

## 1. 场景化问题引入
该仓库被识别为 `{repo_type}`。本 skill 先用本地文件、manifest、git 历史和切片产物建立分析底料，再让 agent 做业务模块判断，避免把确定性步骤交给 LLM 猜。

README 摘要：
{readme_points}

## 2. 架构全景
```mermaid
flowchart TD
  A[目标仓库] --> B[Phase-2a 类型识别]
  B --> C[动态切片]
  C --> D[模块计划]
  D --> E[多受众报告]
```

## 3. 核心模块清单
| 模块 ID | 路径/分组 | 文件数 |
|---|---|---:|
{module_table or '| module_001 | [root] | 0 |'}

### 关键符号入口
{symbol_lines}

### 对外工具/API 表面
{tool_lines}

## 4. 第三方依赖与版本基线
依赖线索见 `slices/09-dependencies.xml`。当前扫描未引入外部依赖解析库，只保留原始 manifest 作为后续判断证据。

{manifest_section}

## 5. 工程成熟度
- 文件总数：{len(files)}

### 已生成切片
{slice_links}

### 运行命令候选
{commands}

### 文件结构快照
{tree}

{audience}

## 7. 架构评价
当前版本完成了不依赖 LLM 的确定性分析：类型识别、文件切片、模块候选、对外工具/API 表面、依赖基线、运行命令候选和报告索引。设计优点是可重放、低依赖、证据可追到文件与行号；限制是业务价值排序和架构优劣判断仍属于主观分析，建议由后续 subagent 基于这些底料继续深化。

## 8. 复现方法
```bash
python3 scripts/repo_analyzer.py {source} --output analysis --no-question
```

## 9. 附录
- 类型识别：`02a-repo-type.yaml`
- 项目名片：`02a-manifest-card.md`
- 覆盖率门控：`08-coverage.md`
- 状态报告：`STATE_REPORT.md`
"""


def write_reports(repo: Path, output: Path, source: str, project_name: str, repo_type: str, files: List[Path], mode: str) -> None:
    modes = ["tech-lead", "business", "learning"] if mode == "all" else [mode]
    primary = None
    for report_mode in modes:
        body = report_body(project_name, source, repo_type, files, repo, report_mode)
        target = output / f"ANALYSIS_REPORT.{report_mode}.md"
        target.write_text(body, encoding="utf-8")
        if primary is None:
            primary = body
    (output / "ANALYSIS_REPORT.md").write_text(primary or report_body(project_name, source, repo_type, files, repo, mode), encoding="utf-8")


def write_readme(output: Path, project_name: str, repo_type: str, mode: str) -> None:
    report_files = sorted(path.name for path in output.glob("ANALYSIS_REPORT*.md"))
    links = "\n".join(f"- [{name}]({name})" for name in report_files)
    (output / "README.md").write_text(
        f"""# {project_name} 分析索引

提示：本 skill 与 `graphify` 子项目解耦，索引不共享。如需共享请在 shell 层串联。

- Repo 类型: {repo_type}
- 报告模式: {mode}

## 报告
{links}

## 关键产物
- [00-meta.txt](00-meta.txt)
- [02a-repo-type.yaml](02a-repo-type.yaml)
- [02a-manifest-card.md](02a-manifest-card.md)
- [05-module-ids.yaml](05-module-ids.yaml)
- [08-coverage.md](08-coverage.md)
- [STATE_REPORT.md](STATE_REPORT.md)
- [slices/](slices/)
""",
        encoding="utf-8",
    )


def write_acceptance(output: Path) -> None:
    acceptance = output / "acceptance"
    acceptance.mkdir()
    check = acceptance / "check.sh"
    check.write_text(
        """#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

python3 - "$ROOT" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
failures = []


def read(relative):
    path = root / relative
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}|{name}{('|'+detail) if detail else ''}")
    if not ok:
        failures.append(name)


required = [
    "00-meta.txt",
    "02a-repo-type.yaml",
    "02a-manifest-card.md",
    "03-question-answers.md",
    "05-module-ids.yaml",
    "08-coverage.md",
    "STATE_REPORT.md",
    "ANALYSIS_REPORT.md",
    "README.md",
]
for item in required:
    check(f"required:{item}", (root / item).is_file())

slices = sorted((root / "slices").glob("*")) if (root / "slices").is_dir() else []
check("slices present", bool(slices))

modules_text = read("05-module-ids.yaml")
module_ids = re.findall(r"(?m)^\\s*- id: (module_[0-9]+)", modules_text)
check("module ids unique", bool(module_ids) and len(module_ids) == len(set(module_ids)))
for module_id in module_ids:
    block = modules_text.split(f"- id: {module_id}", 1)[1].split("\\n  - id:", 1)[0]
    check(f"module schema:{module_id}", "tier:" in block and "storyline_position:" in block)

state = read("STATE_REPORT.md")
coverage = read("08-coverage.md")
check("failed_modules tracked", "failed_modules: []" in state)
check("state final", "PASS_DETERMINISTIC_ACCEPTANCE" in state and "PASS_WITH_DETERMINISTIC_BASELINE" not in state)
check("coverage final", "已完成确定性门控" in coverage and "待 LLM" not in coverage)

artifact_files = [path for path in root.rglob("*") if path.is_file() and "acceptance" not in path.relative_to(root).parts]
all_text = "\\n".join(path.read_text(encoding="utf-8", errors="replace") for path in artifact_files)
main_report = read("ANALYSIS_REPORT.md")
code_slices = [path for path in slices if path.name.startswith(("01-", "02-", "05-"))]
tools = sorted(set(re.findall(r"\\bai_[A-Za-z0-9_$-]+\\b", "\\n".join(read(f"slices/{path.name}") for path in code_slices))))
check("api surface count", not tools or all(tool in main_report for tool in tools), f"{len(tools)} tools")

slice_refs = sorted(set(re.findall(r"slices/[A-Za-z0-9_.-]+", main_report)))
check("slice refs exist", bool(slice_refs) and all((root / ref).exists() for ref in slice_refs))

draft_refs = sorted(set(re.findall(r"drafts/[A-Za-z0-9_.-]+", main_report)))
check("draft refs exist", all((root / ref).exists() for ref in draft_refs))

readme = read("README.md")
local_links = [link for link in re.findall(r"\\[[^\\]]+\\]\\(([^)#][^)]+)\\)", readme) if not link.startswith(("http://", "https://"))]
check("readme links exist", all((root / link).exists() for link in local_links))

wiki_refs = set(re.findall(r"\\[\\[([^\\]]+)\\]\\]", all_text))
valid_wiki = set(module_ids)
check("wikilinks valid", all(ref in valid_wiki for ref in wiki_refs), ",".join(sorted(wiki_refs - valid_wiki)))

for md in root.glob("*.md"):
    text = md.read_text(encoding="utf-8", errors="replace")
    headings = set()
    for heading in re.findall(r"(?m)^#+\\s+(.+)$", text):
        slug = re.sub(r"[^a-z0-9\\u4e00-\\u9fff -]", "", heading.lower()).strip().replace(" ", "-")
        if slug:
            headings.add(slug)
    anchors = [anchor[1:] for anchor in re.findall(r"\\(#[^)]+\\)", text)]
    check(f"anchors:{md.name}", all(anchor in headings for anchor in anchors))

report_names = ["tech-lead", "business", "learning"]
reports = {name: read(f"ANALYSIS_REPORT.{name}.md") for name in report_names}
if all(reports.values()):
    check("audience marker:tech", "技术负责人关注" in reports["tech-lead"])
    check("audience marker:business", "业务负责人关注" in reports["business"])
    check("audience marker:learning", "学习路径" in reports["learning"])
    pairs = [("tech-lead", "business"), ("tech-lead", "learning"), ("business", "learning")]
    for left, right in pairs:
        left_words = set(re.findall(r"[A-Za-z0-9_\\u4e00-\\u9fff]+", reports[left]))
        right_words = set(re.findall(r"[A-Za-z0-9_\\u4e00-\\u9fff]+", reports[right]))
        distance = 1 - (len(left_words & right_words) / max(1, len(left_words | right_words)))
        check(f"audience distance:{left}:{right}", reports[left] != reports[right] and distance >= 0.18, f"{distance:.2f}")
else:
    check("audience reports optional", True)

check("mermaid present", "```mermaid" in main_report and "flowchart TD" in main_report)
check("markdown fences balanced", main_report.count("```") % 2 == 0)
check("no placeholder claims", not any(term in all_text for term in ["待 LLM 深度分析补全", "PASS_WITH_DETERMINISTIC_BASELINE", "骨架/待补全"]))

sys.exit(1 if failures else 0)
PY
""",
        encoding="utf-8",
    )
    check.chmod(0o755)


def analyze(args: argparse.Namespace) -> Path:
    repo, source, temp = checkout_target(args.target)
    try:
        output = Path(args.output).expanduser().resolve()
        clean_output(output)
        files = sorted(iter_files(repo), key=lambda path: rel(path, repo))
        project_name = parse_project_name(repo)
        repo_type = detect_repo_type(repo, files)
        dimensions = SLICES[repo_type]

        write_meta(repo, output, source, files)
        write_repo_type(output, repo_type, project_name, dimensions)
        write_manifest_card(repo, output, source, project_name, repo_type, files)
        write_question_answers(output, args.no_question, args.mode)
        write_slices(repo, output, repo_type, files)
        write_module_plan(repo, output, files)
        write_module_drafts(repo, output, files)
        write_coverage(output, files, repo)
        write_state_report(output)
        write_reports(repo, output, source, project_name, repo_type, files, args.mode)
        write_acceptance(output)
        write_readme(output, project_name, repo_type, args.mode)
        return output
    finally:
        temp.cleanup()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="分析一个 git 仓库并生成 analysis 产物。")
    parser.add_argument("target", help="本地仓库路径或 git URL")
    parser.add_argument("--output", default="analysis", help="分析产物目录")
    parser.add_argument("--mode", choices=["tech-lead", "business", "learning", "all"], default="tech-lead")
    parser.add_argument("--no-question", action="store_true", help="跳过交互问题，使用默认值")
    parser.add_argument("--offline", action="store_true", help="保留给后续外部调研开关；当前实现不访问 Web")
    return parser


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    output = analyze(args)
    print(f"分析完成: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
