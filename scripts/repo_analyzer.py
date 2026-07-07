#!/usr/bin/env python3
"""Deterministic repo-analyzer entrypoint."""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
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
    "analysis",
    "analysis-final",
    "analysis-judge",
    "analysis-judge-final",
    "analysis-novice-final",
    "graphify-out",
    "uat-evidence",
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

GENERATED_DIRS = {"slices", "drafts", "acceptance", "agent-runs"}
REPOMIX_BINARY = "npx"
RENDERER = Path(__file__).resolve().with_name("render_report.py")
SOURCE_SYMBOL_LIMIT = 400
API_SURFACE_LIMIT = 1_000
TREE_SITTER_CHUNK_BYTES = 5 * 1024 * 1024
SYMBOL_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs"}
CONFIG_HOME_ENV = "REPO_ANALYZER_CONFIG_HOME"
TREE_SITTER_QUERIES = {
    ".py": """
(function_definition name: (identifier) @name)
(class_definition name: (identifier) @name)
""",
    ".js": """
(function_declaration name: (identifier) @name)
(lexical_declaration (variable_declarator name: (identifier) @name))
(variable_declaration (variable_declarator name: (identifier) @name))
(method_definition name: (property_identifier) @name)
(class_declaration name: (identifier) @name)
""",
    ".jsx": """
(function_declaration name: (identifier) @name)
(lexical_declaration (variable_declarator name: (identifier) @name))
(variable_declaration (variable_declarator name: (identifier) @name))
(method_definition name: (property_identifier) @name)
(class_declaration name: (identifier) @name)
""",
    ".ts": """
(function_declaration name: (identifier) @name)
(lexical_declaration (variable_declarator name: (identifier) @name))
(variable_declaration (variable_declarator name: (identifier) @name))
(method_definition name: (property_identifier) @name)
(class_declaration name: (type_identifier) @name)
""",
    ".tsx": """
(function_declaration name: (identifier) @name)
(lexical_declaration (variable_declarator name: (identifier) @name))
(variable_declaration (variable_declarator name: (identifier) @name))
(method_definition name: (property_identifier) @name)
(class_declaration name: (type_identifier) @name)
""",
    ".go": """
(function_declaration name: (identifier) @name)
(method_declaration name: (field_identifier) @name)
(type_declaration (type_spec name: (type_identifier) @name))
""",
    ".rs": """
(function_item name: (identifier) @name)
(struct_item name: (type_identifier) @name)
(enum_item name: (type_identifier) @name)
(trait_item name: (type_identifier) @name)
""",
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


def init_performance() -> dict:
    return {"stages": [], "agent_attempts": []}


@contextmanager
def timed_stage(performance: dict, name: str):
    started = time.monotonic()
    status = "PASS"
    error = ""
    try:
        yield
    except Exception as exc:
        status = "FAIL"
        error = str(exc)
        raise
    finally:
        performance.setdefault("stages", []).append(
            {
                "name": name,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "status": status,
                "error": error[:500],
            }
        )


def clean_output(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def prepare_output(path: Path, resume: bool) -> None:
    if not resume:
        clean_output(path)
        return
    path.mkdir(parents=True, exist_ok=True)
    generated_files = {
        "00-meta.txt",
        "02a-repo-type.yaml",
        "02a-manifest-card.md",
        "03-question-answers.md",
        "05-module-ids.yaml",
        "08-coverage.md",
        "08-coverage-failure.md",
        "expected-symbols.json",
        "coverage-symbols.json",
        "mcp-tools.json",
        "STATE_REPORT.md",
        "SLA_REPORT.md",
        "PERFORMANCE_REPORT.md",
        "PERFORMANCE_REPORT.json",
        "CONFIG_EFFECTIVE.json",
        "REPORT_DATA.json",
        "AGENT_SUMMARY.json",
        "ANALYSIS_REPORT.md",
        "ANALYSIS_REPORT.tech-lead.md",
        "ANALYSIS_REPORT.business.md",
        "ANALYSIS_REPORT.learning.md",
        "README.md",
    }
    for item in generated_files:
        target = path / item
        if target.exists():
            target.unlink()
    for item in GENERATED_DIRS:
        target = path / item
        if target.exists():
            shutil.rmtree(target)


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


def config_home() -> Path:
    return Path(os.environ.get(CONFIG_HOME_ENV, "~/.config/repo-analyzer")).expanduser()


def parse_scalar(value: str):
    value = value.strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def parse_simple_yaml(text: str) -> dict:
    result = {}
    current = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            if value.strip():
                result[key] = parse_scalar(value)
                current = None
            else:
                result[key] = [] if key == "extends" else {}
                current = key
            continue
        if current == "extends" and raw.strip().startswith("- "):
            result[current].append(parse_scalar(raw.strip()[2:]))
        elif current and ":" in raw:
            key, value = raw.strip().split(":", 1)
            result[current][key.strip()] = parse_scalar(value)
    return result


def merge_config(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def flatten_config(config: dict) -> dict:
    flat = dict(config)
    if isinstance(config.get("target_coverage"), dict):
        flat["target_coverage_core"] = config["target_coverage"].get("core", flat.get("target_coverage_core"))
        flat["target_coverage_minor"] = config["target_coverage"].get("minor", flat.get("target_coverage_minor"))
    if isinstance(config.get("sla_budget"), dict):
        flat["sla_minutes"] = config["sla_budget"].get("minutes", flat.get("sla_minutes"))
    return flat


def load_config_file(path: Path, seen=None) -> dict:
    seen = seen or set()
    config_path = path.expanduser().resolve()
    if config_path in seen:
        raise SystemExit(f"配置文件继承循环: {config_path}")
    if not config_path.exists():
        return {}
    seen.add(config_path)
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text) if config_path.suffix == ".json" else parse_simple_yaml(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"配置文件读取失败: {config_path}: {exc}") from exc
    merged = {}
    for parent in config.get("extends", []) if isinstance(config.get("extends"), list) else []:
        merged = merge_config(merged, load_config_file(Path(str(parent)), seen))
    return merge_config(merged, config)


def load_config(path: str) -> dict:
    explicit = Path(path).expanduser() if path else config_home() / "defaults.yaml"
    return flatten_config(load_config_file(explicit))


def env_config() -> dict:
    mapping = {
        "REPO_ANALYZER_MODE": ("mode", str),
        "REPO_ANALYZER_NO_QUESTION": ("no_question", bool_config),
        "REPO_ANALYZER_OFFLINE": ("offline", bool_config),
        "REPO_ANALYZER_TARGET_COVERAGE_CORE": ("target_coverage_core", float),
        "REPO_ANALYZER_TARGET_COVERAGE_MINOR": ("target_coverage_minor", float),
        "REPO_ANALYZER_SLA_BUDGET_MINUTES": ("sla_minutes", float),
        "REPO_ANALYZER_COVERAGE_ENGINE": ("coverage_engine", str),
        "REPO_ANALYZER_AGENT_MODE": ("agent_mode", str),
        "REPO_ANALYZER_AGENT_COMMAND": ("agent_command", str),
        "REPO_ANALYZER_AGENT_MAX_ATTEMPTS": ("agent_max_attempts", int),
        "REPO_ANALYZER_AGENT_TIMEOUT_SECONDS": ("agent_timeout_seconds", int),
    }
    result = {}
    for name, (key, cast) in mapping.items():
        if name in os.environ:
            result[key] = cast(os.environ[name])
    return result


def last_session_path() -> Path:
    return config_home() / "last-session.json"


def load_last_session(use_last_pref: bool) -> dict:
    path = last_session_path()
    if not use_last_pref or not path.exists():
        return {}
    if time.time() - path.stat().st_mtime > 30 * 24 * 60 * 60:
        path.unlink()
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("flags_used", {})
    except (OSError, json.JSONDecodeError):
        return {}


def bool_config(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def set_if_default(args: argparse.Namespace, key: str, value) -> None:
    defaults = {
        "mode": "tech-lead",
        "no_question": False,
        "offline": False,
        "coverage_engine": "auto",
        "agent_mode": "deterministic",
        "agent_command": "",
    }
    if getattr(args, key) == defaults.get(key):
        setattr(args, key, value)


def apply_config_values(args: argparse.Namespace, config: dict, force: bool = False) -> None:
    if not config:
        return
    if "mode" in config:
        setattr(args, "mode", str(config["mode"])) if force else set_if_default(args, "mode", str(config["mode"]))
    if "no_question" in config:
        setattr(args, "no_question", bool_config(config["no_question"])) if force else set_if_default(args, "no_question", bool_config(config["no_question"]))
    if "offline" in config:
        setattr(args, "offline", bool_config(config["offline"])) if force else set_if_default(args, "offline", bool_config(config["offline"]))
    if "target_coverage_core" in config and (force or args.target_coverage_core is None):
        args.target_coverage_core = float(config["target_coverage_core"])
    if "target_coverage_minor" in config and (force or args.target_coverage_minor is None):
        args.target_coverage_minor = float(config["target_coverage_minor"])
    if "sla_minutes" in config and (force or args.sla_minutes is None):
        args.sla_minutes = float(config["sla_minutes"])
    if "coverage_engine" in config:
        setattr(args, "coverage_engine", str(config["coverage_engine"])) if force else set_if_default(args, "coverage_engine", str(config["coverage_engine"]))
    if "agent_mode" in config:
        setattr(args, "agent_mode", str(config["agent_mode"])) if force else set_if_default(args, "agent_mode", str(config["agent_mode"]))
    if "agent_command" in config:
        setattr(args, "agent_command", str(config["agent_command"])) if force else set_if_default(args, "agent_command", str(config["agent_command"]))
    if "agent_max_attempts" in config and (force or args.agent_max_attempts is None):
        args.agent_max_attempts = int(config["agent_max_attempts"])
    if "agent_timeout_seconds" in config and (force or args.agent_timeout_seconds is None):
        args.agent_timeout_seconds = int(config["agent_timeout_seconds"])


def save_last_session(args: argparse.Namespace) -> None:
    path = last_session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flags_used": {
            "mode": args.mode,
            "no_question": bool(args.no_question),
            "offline": bool(args.offline),
            "coverage_engine": args.coverage_engine,
            "agent_mode": args.agent_mode,
            "agent_command": args.agent_command,
            "agent_max_attempts": args.agent_max_attempts,
            "agent_timeout_seconds": args.agent_timeout_seconds,
            "resume": bool(args.resume),
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def apply_config(args: argparse.Namespace) -> argparse.Namespace:
    apply_config_values(args, load_config(args.config))
    apply_config_values(args, load_last_session(args.use_last_pref))
    apply_config_values(args, env_config(), force=True)
    args.target_coverage_core = 0.8 if args.target_coverage_core is None else args.target_coverage_core
    args.target_coverage_minor = 0.2 if args.target_coverage_minor is None else args.target_coverage_minor
    args.sla_minutes = 30.0 if args.sla_minutes is None else args.sla_minutes
    args.agent_max_attempts = 3 if args.agent_max_attempts is None else args.agent_max_attempts
    args.agent_timeout_seconds = 0 if args.agent_timeout_seconds is None else args.agent_timeout_seconds
    return args


def command_kind(command: Sequence[str]) -> str:
    if not command:
        return "unknown"
    if len(command) >= 2 and command[0] == "codex" and command[1] == "exec":
        return "codex exec"
    return Path(command[0]).name


def markdown_snippet(text: str) -> str:
    return text.replace("```", "'''").replace("](#", "](\\#").replace("[[", "[ [").replace("]]", "] ]")


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
    return title or "未命名项目", "\n".join(f"- {markdown_snippet(line)}" for line in summary) or "README 未提供正文摘要。"


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
    modules_text = read_text(output / "05-module-ids.yaml", 100_000)
    return re.findall(r"(?m)^\s*- id: (module_[0-9]+)", modules_text)


def risk_lines(module_files: List[str], root_symbols: List[Tuple[str, str, str]], root_tools: List[Tuple[str, str, str]]) -> List[str]:
    risks = []
    has_tests = any(re.search(r"(^|/)(tests?|__tests__)/|test|spec", item, re.I) for item in module_files)
    has_docs = any(Path(item).name.lower().startswith("readme") or "/docs/" in item for item in module_files)
    if not has_tests:
        risks.append("缺少可见测试文件，变更该模块前应先补最小回归验证。")
    if root_tools and not has_docs:
        risks.append("该模块暴露对外工具/API，但同组文档信号较弱，使用说明可能不足。")
    if len(root_symbols) > 20:
        risks.append("公开符号较多，后续人工深挖应优先确认职责边界是否过宽。")
    if not risks:
        risks.append("未发现明显结构性风险；后续重点核对业务语义是否与 README 承诺一致。")
    return risks


def module_agent_prompt(module_id: str, root: str, tier: str, output: Path, module_files: List[str]) -> str:
    files = "\n".join(f"- {item}" for item in module_files[:80]) or "- 未识别到模块文件"
    return f"""### MODULE {module_id}
- 模块底稿: {output / "drafts" / f"06-module-{module_id}.md"}
- 模块分组: {root}
- 模块层级: {tier}
- 需在 repomix 切片中核对的源码路径:
{files}
"""


def modules_batch_agent_prompt(output: Path, modules: List[Tuple[str, str, str, List[str]]]) -> str:
    module_blocks = "\n".join(module_agent_prompt(module_id, root, tier, output, module_files) for module_id, root, tier, module_files in modules)
    return f"""你是一位资深架构师，请基于已生成的 repomix 切片和模块底稿，对所有模块做判断型深度分析。

## 输入
- 分析目录: {output}
- 模块清单: {output / "05-module-ids.yaml"}
- 模块底稿目录: {output / "drafts"}
- 主要证据切片: `slices/02-backend.xml`、`slices/04-docs.xml`、`slices/06-tests.xml`、`slices/09-dependencies.xml`、`slices/12-history-hotspot.txt`

## 模块任务
{module_blocks}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成 analysis；只读取上面列出的分析目录文件。
- 不要写入任何文件，不要修改 analysis 目录；只在最终回复中返回 Markdown。
- 不要在分析目录根部直接读取源码路径；源码内容来自 `slices/*.xml` 中的 `<file path="...">`。
- 只基于分析目录中的证据判断，不要编造源码事实。
- 补充业务角色、设计思路、关键数据流、模块协同、架构亮点和风险。
- 每个关键判断必须引用已有证据文件路径。
- 每个模块必须按下面格式输出，方便脚本拆分；不得省略任何模块：

<!-- MODULE_RESULT: module_xxx -->
## Agent 深度分析

...该模块分析...
<!-- END_MODULE_RESULT -->
"""


def draft_outline(path: Path) -> str:
    text = read_text(path, 120_000)
    title_match = re.search(r"(?m)^#\s+(.+)$", text)
    title = title_match.group(1).strip() if title_match else path.name
    headings = re.findall(r"(?m)^##\s+(.+)$", text)
    wikilinks = sorted(set(re.findall(r"\[\[(module_[0-9]+)\]\]", text)))
    mentions = sorted(set(re.findall(r"\bmodule_[0-9]+\b", text)))
    signal_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- 模块边界", "- 分析优先级", "- 业务角色", "- 设计思路", "- 关键数据流", "- 职责", "- 风险")):
            signal_lines.append(stripped)
        if len(signal_lines) >= 12:
            break
    return "\n".join(
        [
            f"### {path.name}",
            f"- title: {title}",
            f"- headings: {', '.join(headings) or '无'}",
            f"- wikilinks: {', '.join(wikilinks) or '无'}",
            f"- module_mentions: {', '.join(mentions) or '无'}",
            "- signal_lines:",
            *[f"  - {line}" for line in signal_lines],
        ]
    )


def write_cross_ref_review_packet(output: Path) -> str:
    packet = "\n\n".join(
        [
            "# Cross-ref 审稿包",
            "## 模块清单\n```yaml\n" + read_text(output / "05-module-ids.yaml", 120_000) + "\n```",
            "## 确定性 cross-ref\n```text\n" + read_text(output / "drafts" / "07-cross-ref-checks.md", 120_000) + "\n```",
            "## 覆盖率摘要\n```text\n" + read_text(output / "08-coverage.md", 120_000) + "\n```",
            "## 模块草稿结构\n" + "\n\n".join(draft_outline(path) for path in sorted((output / "drafts").glob("06-module-*.md"))),
        ]
    )
    packet_path = output / "drafts" / "07-cross-ref-review-input.md"
    packet_path.write_text(packet + "\n", encoding="utf-8")
    return packet


def cross_ref_agent_prompt(output: Path) -> str:
    packet = write_cross_ref_review_packet(output)
    return f"""你是一位独立审稿 agent，只读不写源码，请审查分析目录中的模块草稿一致性。

## 输入
- 分析目录: {output}
- 审稿包: {output / "drafts" / "07-cross-ref-review-input.md"}

## 审稿包
{packet}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成 analysis；优先只使用上方审稿包。
- 不要写入任何文件，不要修改 analysis 目录；只在最终回复中返回 Markdown。
- 检查模块命名、引用、职责边界、重复定义、跨模块协同是否矛盾。
- 如果发现问题，逐条给出证据路径和建议回退模块。
- 如果需要回退模块，必须单独输出一行 `建议回退模块: module_xxx`；没有需要回退的模块时输出 `建议回退模块: 无`。
- 如果未发现问题，也要说明抽查范围。
- 输出 Markdown，包含标题 `## Agent Cross-ref 审稿`。
"""


def agent_base_command(args: argparse.Namespace, output: Path = None) -> List[str]:
    if args.agent_mode == "codex":
        if output is None:
            raise SystemExit("codex agent 需要 analysis 输出目录作为工作目录")
        return [
            "codex",
            "exec",
            "-c",
            'model_reasoning_effort="low"',
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "-C",
            str(output),
            "-",
        ]
    if args.agent_mode == "command":
        if not args.agent_command:
            raise SystemExit("--agent-mode command 需要提供 --agent-command")
        return shlex.split(args.agent_command)
    raise SystemExit(f"未知 agent 模式: {args.agent_mode}")


def run_agent_task(output: Path, args: argparse.Namespace, run_id: str, prompt: str, performance: dict = None) -> Tuple[bool, str, int]:
    run_dir = output / "agent-runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    command = agent_base_command(args, output)
    last_message = run_dir / "last-message.md"
    if args.agent_mode == "codex":
        command = command[:-1] + ["--output-last-message", str(last_message), "-"]
    timeout = args.agent_timeout_seconds if args.agent_timeout_seconds and args.agent_timeout_seconds > 0 else None
    for attempt in range(1, args.agent_max_attempts + 1):
        attempt_dir = run_dir / f"attempt-{attempt}"
        attempt_dir.mkdir()
        started = time.monotonic()
        timed_out = False
        try:
            result = subprocess.run(
                command,
                input=prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            returncode = result.returncode
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            returncode = 124
            stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
            stderr = f"agent timeout after {args.agent_timeout_seconds}s"
        elapsed = time.monotonic() - started
        (attempt_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
        (attempt_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
        metadata = {
            "run_id": run_id,
            "attempt": attempt,
            "returncode": returncode,
            "elapsed_seconds": round(elapsed, 3),
            "command": command,
            "command_kind": command_kind(command),
            "cwd": str(output.resolve()) if args.agent_mode == "codex" else str(Path.cwd()),
            "timed_out": timed_out,
            "timeout_seconds": timeout,
            "timeout_config_seconds": args.agent_timeout_seconds,
        }
        (attempt_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if performance is not None:
            performance.setdefault("agent_attempts", []).append(dict(metadata))
        if returncode == 0:
            message = last_message.read_text(encoding="utf-8", errors="replace") if last_message.exists() else stdout
            (run_dir / "result.md").write_text(message, encoding="utf-8")
            return True, message, attempt
    failure = f"agent task failed after {args.agent_max_attempts} attempts"
    (run_dir / "result.md").write_text(failure + "\n", encoding="utf-8")
    return False, failure, args.agent_max_attempts


def module_result_blocks(result: str, module_ids: Sequence[str]) -> dict:
    blocks = {}
    pattern = re.compile(r"<!-- MODULE_RESULT:\s*(module_[0-9]+)\s*-->\s*(.*?)\s*<!-- END_MODULE_RESULT -->", re.S)
    for match in pattern.finditer(result):
        blocks[match.group(1)] = match.group(2).strip()
    return blocks


def append_agent_module_analysis(output: Path, module_id: str, result: str, attempts: int, evidence: str = None) -> None:
    draft = output / "drafts" / f"06-module-{module_id}.md"
    body = re.sub(r"(?m)^##\s+Agent 深度分析\s*", "", result.strip(), count=1).strip()
    evidence = evidence or f"agent-runs/module-{module_id}/result.md"
    with draft.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Agent 深度分析\n\n"
            f"- attempts: {attempts}\n"
            f"- 证据: `{evidence}`\n\n"
            f"{body}\n"
            "\n"
        )


def coverage_repair_prompt(module_id: str, module: dict, output: Path) -> str:
    missing = ", ".join(module.get("missing_symbols", [])[:40]) or "无"
    return f"""你是一位模块分析修复 agent，请补齐 `{module_id}` 覆盖率门控缺失的符号说明。

## 输入
- 分析目录: {output}
- 模块草稿: {output / "drafts" / f"06-module-{module_id}.md"}
- 覆盖率报告: {output / "08-coverage.md"}
- 缺失符号: {missing}

## 要求
- 不要写入任何文件，不要修改 analysis 目录；只在最终回复中返回要追加的 Markdown。
- 只补充对这些缺失符号的解释，不要改源码。
- 每个缺失符号都必须在输出中以原名出现，便于 coverage gate 重新检测。
- 输出 Markdown，包含标题 `## Agent 覆盖率修复`。
"""


def append_agent_coverage_repair(output: Path, module_id: str, result: str, attempts: int) -> None:
    draft = output / "drafts" / f"06-module-{module_id}.md"
    body = re.sub(r"(?m)^##\s+Agent 覆盖率修复\s*", "", result.strip(), count=1).strip()
    with draft.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Agent 覆盖率修复\n\n"
            f"- attempts: {attempts}\n"
            f"- 证据: `agent-runs/repair-{module_id}/result.md`\n\n"
            f"{body}\n"
            "\n"
        )


def cross_ref_repair_modules(review: str, known_module_ids: Sequence[str]) -> List[str]:
    known = set(known_module_ids)
    explicit = []
    saw_explicit_decision = False
    for line in review.splitlines():
        match = re.search(r"建议回退模块\s*[:：]\s*(.+)", line)
        if not match:
            continue
        saw_explicit_decision = True
        value = match.group(1)
        if re.search(r"\b(?:无|none|no)\b", value, re.I):
            continue
        explicit.extend(re.findall(r"module_[0-9]+", value))
    if saw_explicit_decision:
        return sorted({module_id for module_id in explicit if module_id in known})

    if not re.search(r"冲突|矛盾|断裂|重复|回退|修复|不一致|FAIL|failed", review, re.I):
        return []
    return sorted({module_id for module_id in re.findall(r"module_[0-9]+", review) if module_id in known})


def cross_ref_repair_prompt(module_id: str, output: Path) -> str:
    return f"""你是一位模块草稿修复 agent，请根据独立 cross-ref 审稿意见修复 `{module_id}` 的分析草稿。

## 输入
- 分析目录: {output}
- 模块草稿: {output / "drafts" / f"06-module-{module_id}.md"}
- 独立审稿: {output / "drafts" / "07-cross-ref-agent-review.md"}
- 确定性 cross-ref: {output / "drafts" / "07-cross-ref-checks.md"}
- 模块清单: {output / "05-module-ids.yaml"}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成 analysis。
- 不要写入任何文件，不要修改 analysis 目录；只在最终回复中返回要追加的 Markdown。
- 只补充能消除审稿指出冲突/不一致的说明，不要改源码。
- 输出 Markdown，包含标题 `## Agent Cross-ref 修复`。
"""


def append_agent_cross_ref_repair(output: Path, module_id: str, result: str, attempts: int) -> None:
    draft = output / "drafts" / f"06-module-{module_id}.md"
    body = re.sub(r"(?m)^##\s+Agent Cross-ref 修复\s*", "", result.strip(), count=1).strip()
    with draft.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Agent Cross-ref 修复\n\n"
            f"- attempts: {attempts}\n"
            f"- 证据: `agent-runs/cross-ref-repair-{module_id}/result.md`\n\n"
            f"{body}\n"
            "\n"
        )


def repair_cross_ref_modules(output: Path, args: argparse.Namespace, module_ids: Sequence[str], review: str, summary: dict, performance: dict) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    targets = cross_ref_repair_modules(review, module_ids)
    if not targets:
        return []
    issues = []
    repairs = summary.setdefault("cross_ref_repairs", {})
    for module_id in targets:
        ok, result, attempts = run_agent_task(output, args, f"cross-ref-repair-{module_id}", cross_ref_repair_prompt(module_id, output), performance)
        repairs[module_id] = {"status": "PASS" if ok else "FAIL", "attempts": attempts}
        if ok:
            append_agent_cross_ref_repair(output, module_id, result, attempts)
        else:
            issues.append(f"{module_id}: cross-ref 修复 agent 失败")
    return issues


def repair_failed_coverage_modules(output: Path, args: argparse.Namespace, coverage: dict, summary: dict, performance: dict) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    issues = []
    repairs = summary.setdefault("repairs", {})
    for module_id, module in coverage["modules"].items():
        if module["status"] == "PASS":
            continue
        ok, result, attempts = run_agent_task(output, args, f"repair-{module_id}", coverage_repair_prompt(module_id, module, output), performance)
        repairs[module_id] = {"status": "PASS" if ok else "FAIL", "attempts": attempts}
        if ok:
            append_agent_coverage_repair(output, module_id, result, attempts)
        else:
            issues.append(f"{module_id}: coverage 修复 agent 失败")
    return issues


def agent_summary_has_failure(summary: dict) -> bool:
    for item in summary.get("modules", {}).values():
        if item.get("status") != "PASS":
            return True
    for item in summary.get("repairs", {}).values():
        if item.get("status") != "PASS":
            return True
    for item in summary.get("cross_ref_repairs", {}).values():
        if item.get("status") != "PASS":
            return True
    cross_ref = summary.get("cross_ref", {})
    return bool(cross_ref) and cross_ref.get("status") not in {"", "PASS"}


def write_agent_summary(output: Path, summary: dict, issues: List[str]) -> None:
    summary["status"] = "PASS" if not issues and not agent_summary_has_failure(summary) else "FAIL"
    (output / "AGENT_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def codex_cross_ref_skip_reason(output: Path, run_id: str) -> str:
    if run_id != "cross-ref-review":
        return ""
    module_ids = module_ids_from_plan(output)
    cross_ref = read_text(output / "drafts" / "07-cross-ref-checks.md", 100_000)
    if len(module_ids) <= 1 and "状态: PASS" in cross_ref:
        return "single module and deterministic cross-ref already PASS"
    return ""


def init_agent_summary(output: Path, args: argparse.Namespace) -> Tuple[List[str], dict]:
    summary = {"mode": args.agent_mode, "max_attempts": args.agent_max_attempts, "modules": {}, "cross_ref": {}}
    if args.agent_mode == "deterministic":
        summary["status"] = "SKIPPED"
        (output / "AGENT_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [], summary


def run_module_agent_loop(output: Path, args: argparse.Namespace, files: List[Path], repo: Path, summary: dict, performance: dict) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    issues = []
    modules = []
    for index, (module_id, root, _count) in enumerate(module_rows(files, repo), 1):
        tier = "core" if index <= 3 else "minor"
        module_files = module_file_paths(files, repo, root)
        modules.append((module_id, root, tier, module_files))
    ok, result, attempts = run_agent_task(output, args, "modules-batch", modules_batch_agent_prompt(output, modules), performance)
    blocks = module_result_blocks(result, [module_id for module_id, _root, _tier, _files in modules]) if ok else {}
    for module_id, _root, _tier, _files in modules:
        has_block = module_id in blocks
        summary["modules"][module_id] = {"status": "PASS" if ok and has_block else "FAIL", "attempts": attempts}
        if ok and has_block:
            append_agent_module_analysis(output, module_id, blocks[module_id], attempts, "agent-runs/modules-batch/result.md")
        else:
            issues.append(f"{module_id}: agent 深度分析失败")
    write_agent_summary(output, summary, issues)
    return issues


def run_cross_ref_agent(output: Path, args: argparse.Namespace, summary: dict, performance: dict, run_id: str = "cross-ref-review") -> Tuple[List[str], str]:
    if args.agent_mode == "deterministic":
        return [], ""
    skip_reason = codex_cross_ref_skip_reason(output, run_id) if args.agent_mode == "codex" else ""
    if skip_reason:
        result = (
            "## Agent Cross-ref 审稿\n\n"
            "- status: SKIPPED_SINGLE_MODULE\n"
            f"- reason: {skip_reason}\n"
            "- deterministic_cross_ref: PASS\n"
            "\n建议回退模块: 无\n"
        )
        summary["cross_ref"] = {"status": "PASS", "attempts": 0, "skipped": skip_reason}
        (output / "drafts" / "07-cross-ref-agent-review.md").write_text(result, encoding="utf-8")
        write_agent_summary(output, summary, [])
        return [], result
    issues = []
    ok, result, attempts = run_agent_task(output, args, run_id, cross_ref_agent_prompt(output), performance)
    summary["cross_ref"] = {"status": "PASS" if ok else "FAIL", "attempts": attempts}
    review_path = output / "drafts" / "07-cross-ref-agent-review.md"
    review_path.write_text(result.strip() + "\n", encoding="utf-8")
    if not ok:
        issues.append("cross-ref-review: agent 审稿失败")
    write_agent_summary(output, summary, issues)
    return issues, result


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
        module_files = module_file_paths(files, repo, root)
        symbol_lines = "\n".join(f"- `{name}` ({file_path}:{line})" for name, file_path, line in root_symbols) or "- 未识别到公开符号"
        tool_lines = "\n".join(f"- `{name}` ({file_path}:{line})" for name, file_path, line in root_tools[:40]) or "- 未识别到 MCP 工具"
        file_lines = "\n".join(f"- `{item}`" for item in module_files[:20]) or "- 未识别到模块文件"
        path_lines = "\n".join(
            f"- 从 `{file_path}:{line}` 的 `{name}` 开始核对调用链。" for name, file_path, line in (root_tools or root_symbols)[:8]
        ) or "- 先从模块文件清单逐个确认入口。"
        risk_text = "\n".join(f"- {line}" for line in risk_lines(module_files, root_symbols, root_tools))
        (drafts / f"06-module-{module_id}.md").write_text(
            f"""# {module_id} {root}

- 文件数: {count}
- 分层: {"core" if index <= 3 else "minor"}

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`{root}` 路径组，共 {count} 个文件。
- 分析优先级：{"核心模块，必须优先核对入口、测试和对外 API。" if index <= 3 else "次要模块，先轻量确认依赖和辅助职责。"}
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
{file_lines}

## 关键路径
{path_lines}

## 关键符号
{symbol_lines}

## MCP 工具/API 表面
{tool_lines}

## 风险与缺口
{risk_text}

## 证据
- 模块 ID 来源：`05-module-ids.yaml`
- 代码切片：`slices/02-backend.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 历史热点：`slices/12-history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| {root} | {count} | deterministic deep scan |
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
    readme_head = markdown_snippet("\n".join(read_text(readme).splitlines()[:30])) if readme else "未发现 README。"
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
    run_repomix_slice(repo, output / "slices" / filename, label, patterns)


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


def write_cross_ref(output: Path) -> List[str]:
    drafts = output / "drafts"
    module_text = (output / "05-module-ids.yaml").read_text(encoding="utf-8", errors="replace")
    module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", module_text)
    valid_ids = set(module_ids)
    issues = []
    seen_titles = set()
    for draft in sorted(drafts.glob("06-module-*.md")):
        text = draft.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"^#\s+(module_[0-9]+)", text)
        module_id = title_match.group(1) if title_match else draft.stem.replace("06-module-", "")
        if module_id not in valid_ids:
            issues.append(f"{draft.name}: 未在 05-module-ids.yaml 中登记")
        for ref in re.findall(r"\[\[(module_[0-9]+)\]\]", text):
            if ref not in valid_ids:
                issues.append(f"{draft.name}: 断裂引用 {ref}")
        for heading in re.findall(r"(?m)^##\s+(.+)$", text):
            key = heading.strip().lower()
            if (module_id, key) in seen_titles:
                issues.append(f"{draft.name}: 重复章节 {heading}")
            seen_titles.add((module_id, key))
    lines = [
        "# Cross-ref 校验",
        "",
        f"- 状态: {'PASS' if not issues else 'FAIL'}",
        f"- 模块数: {len(module_ids)}",
        "",
        "## 检查项",
        "- 模块草稿标题必须匹配 `05-module-ids.yaml` 中的 ID。",
        "- `[[module_xxx]]` 引用必须能解析到模块清单。",
        "- 单个模块草稿不应出现重复二级章节。",
        "",
        "## 问题",
    ]
    lines.extend(f"- {issue}" for issue in issues)
    if not issues:
        lines.append("- 未发现断裂引用或重复章节。")
    (drafts / "07-cross-ref-checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return issues


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
    draft_dir = output / "drafts"
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
        draft_text = read_text(draft_dir / f"06-module-{module_id}.md", 500_000)
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
    rows = module_rows(files, repo)
    coverage = symbol_coverage(output, files, repo, core_threshold, minor_threshold, coverage_engine)
    expected_symbols = []
    for module_id, item in coverage["modules"].items():
        for symbol in item["expected_symbols"]:
            expected_symbols.append({"module": module_id, **symbol})
    (output / "expected-symbols.json").write_text(json.dumps({"engine": coverage["engine"], "symbols": expected_symbols}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "coverage-symbols.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    (output / "08-coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if failed:
        failure_lines = ["# 覆盖率失败明细", ""]
        for module_id in failed:
            item = coverage["modules"][module_id]
            failure_lines.append(f"## {module_id}")
            failure_lines.append(f"- 覆盖率: {item['coverage_ratio']:.2f}")
            failure_lines.append(f"- 阈值: {item['threshold']:.2f}")
            failure_lines.append(f"- 缺失符号: {', '.join(item['missing_symbols'][:30]) or '无'}")
            failure_lines.append("")
        (output / "08-coverage-failure.md").write_text("\n".join(failure_lines), encoding="utf-8")
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
                    "suggested_recovery": f"补充 drafts/06-module-{module_id}.md 中缺失符号说明后重跑 acceptance",
                }
            )
    return failed_modules


def write_state_report(output: Path, coverage: dict, cross_ref_issues: List[str], agent_issues: List[str]) -> List[dict]:
    failed_modules = failed_module_records(coverage)
    yaml_items = "\n".join(
        "\n".join(
            [
                f"  - id: {item['id']}",
                f"    tier: {item['tier']}",
                f"    attempts: {item['attempts']}",
                f"    last_error: {item['last_error']}",
                f"    coverage_ratio: {item['coverage_ratio']}",
                f"    missing_symbols_count: {item['missing_symbols_count']}",
                f"    suggested_recovery: {item['suggested_recovery']}",
            ]
        )
        for item in failed_modules
    )
    failed_yaml = "[]" if not failed_modules else "\n" + yaml_items
    status = "PASS_DETERMINISTIC_ACCEPTANCE" if not failed_modules and not cross_ref_issues else "FAILED_DETERMINISTIC_ACCEPTANCE"
    (output / "STATE_REPORT.md").write_text(
        f"""---
failed_modules: {failed_yaml}
---

# 状态报告

- 当前状态: {status}
- 失败模块: {len(failed_modules)}
- Cross-ref 问题: {len(cross_ref_issues)}
- Agent 问题: {len(agent_issues)}
- 下一步: 如需主观架构评价，使用 subagent 基于当前产物复核。
""",
        encoding="utf-8",
    )
    return failed_modules


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


def failed_modules_section(failed_modules: List[dict]) -> str:
    if not failed_modules:
        return ""
    rows = "\n".join(
        f"| {item['id']} | {item['tier']} | {item['attempts']} | {item['last_error']} | {item['coverage_ratio']:.2f} | {item['suggested_recovery']} |"
        for item in failed_modules
    )
    details = "\n\n".join(
        "\n".join(
            [
                f"### {item['id']}",
                f"- tier: {item['tier']}",
                f"- attempts: {item['attempts']}",
                f"- last_error: {item['last_error']}",
                f"- coverage_ratio: {item['coverage_ratio']:.2f}",
                f"- missing_symbols_count: {item['missing_symbols_count']}",
                f"- suggested_recovery: {item['suggested_recovery']}",
            ]
        )
        for item in failed_modules
    )
    return f"""
## §9 未完成模块明细

> 本章由 `STATE_REPORT.md` 中 `failed_modules` 生成；只在存在失败模块时渲染。

| 模块 ID | tier | 失败次数 | 最后错误 | 覆盖率 | 建议恢复 |
|---|---|---:|---|---:|---|
{rows}

## 失败详情
{details}
"""


def report_body(project_name: str, source: str, repo_type: str, files: List[Path], repo: Path, mode: str, failed_modules: List[dict] = None) -> str:
    failed_modules = failed_modules or []
    failed_section = failed_modules_section(failed_modules)
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
    tools = mcp_tool_names(repo, files, API_SURFACE_LIMIT)
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
{failed_section}
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
{failed_section}
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
{failed_section}
"""


def overview_report_body(project_name: str, source: str, repo_type: str, files: List[Path], repo: Path, failed_modules: List[dict] = None) -> str:
    failed_modules = failed_modules or []
    failed_section = failed_modules_section(failed_modules)
    language_line = ", ".join(f"{name}({count})" for name, count in language_counts(files).most_common()) or "未识别"
    modules = module_rows(files, repo)
    module_table = "\n".join(f"| {module_id} | {name} | {count} |" for module_id, name, count in modules[:8])
    readme_title, readme_points = readme_summary(repo)
    commands = "\n".join(f"- `{command}`" for command in command_hints(repo, files))
    tools = mcp_tool_names(repo, files, API_SURFACE_LIMIT)
    tool_lines = "\n".join(f"- `{name}` (`{file_path}:{line}`)" for name, file_path, line in tools) or "- 未识别到 MCP 工具/API 名称"
    slice_names = [filename for filename, _label, _patterns in SLICES[repo_type]] + ["12-history-hotspot.txt"]
    slice_links = "\n".join(f"- `slices/{name}`" for name in slice_names)
    return f"""# {project_name} 分析总览

> 元信息：目标 `{source}`；Repo 类型 `{repo_type}`；报告由确定性 repo-analyzer CLI 生成。

## 0. 读者导航
- 技术负责人：读 `ANALYSIS_REPORT.tech-lead.md`
- 业务负责人：读 `ANALYSIS_REPORT.business.md`
- 学习者：读 `ANALYSIS_REPORT.learning.md`
- 复查证据：读 `02a-manifest-card.md`、`05-module-ids.yaml`、`08-coverage.md`、`STATE_REPORT.md`

## 1. 总览摘要
- 项目识别名：{readme_title}
- 主要语言：{language_line}
- 文件总数：{len(files)}

README 摘要：
{readme_points}

## 2. 架构地图
```mermaid
flowchart TD
  A[目标仓库] --> B[类型识别]
  B --> C[动态切片]
  C --> D[模块清单]
  D --> E[三份受众报告]
```

## 3. 核心模块
| 模块 ID | 路径/分组 | 文件数 |
|---|---|---:|
{module_table or '| module_001 | [root] | 0 |'}

## 4. API 与运行入口
### 对外工具/API 表面
{tool_lines}

### 运行命令候选
{commands}

## 5. 证据切片
{slice_links}

## 6. 复现方法
```bash
python3 scripts/repo_analyzer.py {source} --output analysis --mode all --no-question
```
{failed_section}
"""


def report_data(project_name: str, source: str, repo_type: str, files: List[Path], repo: Path, failed_modules: List[dict]) -> dict:
    languages = language_counts(files)
    language_line = ", ".join(f"{name}({count})" for name, count in languages.most_common()) or "未识别"
    modules = module_rows(files, repo)
    module_table = "\n".join(f"| {module_id} | {name} | {count} |" for module_id, name, count in modules) or "| module_001 | [root] | 0 |"
    readme_title, readme_points = readme_summary(repo)
    manifests = manifest_snippets(repo)
    manifest_section = "\n\n".join(f"### {name}\n```text\n{text}\n```" for name, text in manifests) or "未发现常见依赖 manifest。"
    manifest_names = ", ".join(name for name, _text in manifests) or "未发现"
    command_list = command_hints(repo, files)
    commands = "\n".join(f"- `{command}`" for command in command_list)
    tree = "\n".join(f"- `{item}`" for item in top_tree(repo, files, 40))
    symbols = source_symbols(repo, files, 30)
    symbol_lines = "\n".join(f"- `{name}` (`{file_path}:{line}`)" for name, file_path, line in symbols) or "- 未识别到代码符号"
    tools = mcp_tool_names(repo, files, API_SURFACE_LIMIT)
    tool_lines = "\n".join(f"- `{name}` (`{file_path}:{line}`)" for name, file_path, line in tools) or "- 未识别到 MCP 工具/API 名称"
    tool_summary = "\n".join(f"- {name}" for name, _file_path, _line in tools[:20]) or "- 未识别到对外工具/API"
    slice_names = [filename for filename, _label, _patterns in SLICES[repo_type]] + ["12-history-hotspot.txt"]
    slice_links = "\n".join(f"- `slices/{name}`" for name in slice_names)
    largest = modules[0] if modules else ("module_001", "[root]", len(files))
    first_module = largest[0]
    first_tool = tools[0][0] if tools else "未识别"
    first_symbol = symbols[0][0] if symbols else "未识别"
    data = {
        "project_name": project_name,
        "source": source,
        "repo_type": repo_type,
        "file_count": len(files),
        "readme_title": readme_title,
        "readme_points": readme_points,
        "language_line": language_line,
        "module_table": module_table,
        "symbol_lines": symbol_lines,
        "tool_lines": tool_lines,
        "tool_summary": tool_summary,
        "tool_count": len(tools),
        "command_count": len(command_list),
        "commands": commands,
        "manifest_section": manifest_section,
        "manifest_names": manifest_names,
        "slice_links": slice_links,
        "tree": tree,
        "largest_root": largest[1],
        "largest_count": largest[2],
        "first_module": first_module,
        "first_tool": first_tool,
        "first_symbol": first_symbol,
        "failed_section": failed_modules_section(failed_modules),
    }
    data["audiences"] = {
        mode: {"audience_section": audience_section(mode, repo_type, files, command_list, modules, tools)}
        for mode in ("tech-lead", "business", "learning")
    }
    return data


def write_reports(repo: Path, output: Path, source: str, project_name: str, repo_type: str, files: List[Path], mode: str, failed_modules: List[dict]) -> None:
    data = report_data(project_name, source, repo_type, files, repo, failed_modules)
    (output / "REPORT_DATA.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rendered = subprocess.run(
        [sys.executable, str(RENDERER), "--template", mode, "--data", str(output)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if rendered.returncode != 0:
        raise SystemExit(rendered.stderr.strip() or rendered.stdout.strip() or "render_report.py failed")


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
- [drafts/07-cross-ref-checks.md](drafts/07-cross-ref-checks.md)
- [08-coverage.md](08-coverage.md)
- [coverage-symbols.json](coverage-symbols.json)
- [STATE_REPORT.md](STATE_REPORT.md)
- [SLA_REPORT.md](SLA_REPORT.md)
- [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
- [CONFIG_EFFECTIVE.json](CONFIG_EFFECTIVE.json)
- [REPORT_DATA.json](REPORT_DATA.json)
- [AGENT_SUMMARY.json](AGENT_SUMMARY.json)
- [slices/](slices/)
""",
        encoding="utf-8",
    )


def write_config_effective(output: Path, args: argparse.Namespace) -> None:
    config = {
        "mode": args.mode,
        "no_question": bool(args.no_question),
        "offline": bool(args.offline),
        "resume": bool(args.resume),
        "use_last_pref": bool(args.use_last_pref),
        "save_pref": bool(args.save_pref),
        "target_coverage_core": args.target_coverage_core,
        "target_coverage_minor": args.target_coverage_minor,
        "sla_minutes": args.sla_minutes,
        "coverage_engine": args.coverage_engine,
        "agent_mode": args.agent_mode,
        "agent_command": args.agent_command,
        "agent_max_attempts": args.agent_max_attempts,
        "agent_timeout_seconds": args.agent_timeout_seconds,
        "config": args.config or str(config_home() / "defaults.yaml"),
        "config_home": str(config_home()),
    }
    (output / "CONFIG_EFFECTIVE.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_mcp_tools(output: Path, tools: List[Tuple[str, str, str]]) -> None:
    data = [{"name": name, "file": file_path, "line": line} for name, file_path, line in tools]
    (output / "mcp-tools.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_sla_report(output: Path, args: argparse.Namespace, started_at: float, coverage: dict, cross_ref_issues: List[str], agent_issues: List[str]) -> None:
    elapsed_seconds = time.monotonic() - started_at
    failed = [module_id for module_id, item in coverage["modules"].items() if item["status"] != "PASS"]
    status = "PASS" if elapsed_seconds <= args.sla_minutes * 60 and not failed and not cross_ref_issues and not agent_issues else "FAIL"
    (output / "SLA_REPORT.md").write_text(
        f"""# SLA 报告

- status: {status}
- budget_minutes: {args.sla_minutes:.2f}
- elapsed_seconds: {elapsed_seconds:.2f}
- resumed: {str(bool(args.resume)).lower()}
- agent_timeout: {"disabled" if args.agent_timeout_seconds <= 0 else "enabled"}
- agent_timeout_seconds: {args.agent_timeout_seconds}
- failed_modules: {len(failed)}
- cross_ref_issues: {len(cross_ref_issues)}
- agent_issues: {len(agent_issues)}
""",
        encoding="utf-8",
    )


def write_performance_report(output: Path, args: argparse.Namespace, started_at: float, performance: dict) -> None:
    total_elapsed = round(time.monotonic() - started_at, 3)
    stages = sorted(performance.get("stages", []), key=lambda item: item.get("elapsed_seconds", 0), reverse=True)
    attempts = sorted(performance.get("agent_attempts", []), key=lambda item: item.get("elapsed_seconds", 0), reverse=True)
    agent_total = round(sum(item.get("elapsed_seconds", 0) for item in attempts), 3)
    timeout_disabled = args.agent_timeout_seconds <= 0
    slowest_stage = stages[0]["name"] if stages else "none"
    slowest_agent = attempts[0]["run_id"] if attempts else "none"
    performance["summary"] = {
        "total_elapsed_seconds": total_elapsed,
        "agent_total_elapsed_seconds": agent_total,
        "agent_attempt_count": len(attempts),
        "slowest_stage": slowest_stage,
        "slowest_agent_run_id": slowest_agent,
        "agent_timeout_enabled": not timeout_disabled,
        "diagnosis": (
            "deterministic-only; no agent subprocess cost observed"
            if not attempts
            else "agent subprocess/model fixed cost dominates; do not hide it with default timeout"
        ),
    }
    (output / "PERFORMANCE_REPORT.json").write_text(json.dumps(performance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stage_rows = "\n".join(
        f"| {item['name']} | {item['elapsed_seconds']:.3f} | {item['status']} |"
        for item in stages[:20]
    ) or "| 无 | 0.000 | PASS |"
    agent_rows = "\n".join(
        f"| {item['run_id']} | {item['attempt']} | {item['command_kind']} | {item['elapsed_seconds']:.3f} | {item['timed_out']} | `{item['cwd']}` |"
        for item in attempts[:20]
    ) or "| 无 | 0 | none | 0.000 | false | `n/a` |"
    conclusion = (
        "本次未运行 agent 子进程；如果仍慢，应优先查看 repomix、tree-sitter 或文件规模。"
        if not attempts
        else "本次慢点应优先从 agent 子进程启动、模型推理固定成本和子会话数量定位；默认 timeout 已关闭，不能把限时当成根因修复。"
    )
    (output / "PERFORMANCE_REPORT.md").write_text(
        f"""# 性能诊断报告

- total_elapsed_seconds: {total_elapsed:.3f}
- agent_mode: {args.agent_mode}
- agent_attempt_count: {len(attempts)}
- agent_total_elapsed_seconds: {agent_total:.3f}
- agent_timeout: {"disabled" if timeout_disabled else "enabled"}
- agent_timeout_seconds: {args.agent_timeout_seconds}
- slowest_stage: {slowest_stage}
- slowest_agent_run_id: {slowest_agent}

## 慢因结论

{conclusion}

## 阶段耗时 Top20

| 阶段 | 秒 | 状态 |
|---|---:|---|
{stage_rows}

## Agent attempt 耗时 Top20

| run_id | attempt | command | 秒 | timed_out | cwd |
|---|---:|---|---:|---|---|
{agent_rows}
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
import json
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


def strip_fenced_code(text):
    return re.sub(r"(?ms)^```.*?^```", "", text)


required = [
    "00-meta.txt",
    "02a-repo-type.yaml",
    "02a-manifest-card.md",
    "03-question-answers.md",
    "05-module-ids.yaml",
    "08-coverage.md",
    "expected-symbols.json",
    "coverage-symbols.json",
    "mcp-tools.json",
    "STATE_REPORT.md",
    "SLA_REPORT.md",
    "PERFORMANCE_REPORT.md",
    "PERFORMANCE_REPORT.json",
    "CONFIG_EFFECTIVE.json",
    "REPORT_DATA.json",
    "AGENT_SUMMARY.json",
    "ANALYSIS_REPORT.md",
    "README.md",
    "drafts/07-cross-ref-checks.md",
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
performance_report = read("PERFORMANCE_REPORT.md")
check("failed_modules tracked", "failed_modules: []" in state)
check("state final", "PASS_DETERMINISTIC_ACCEPTANCE" in state and "PASS_WITH_DETERMINISTIC_BASELINE" not in state)
check("coverage final", "状态: PASS" in coverage and "待 LLM" not in coverage)
check("coverage engine recorded", "engine:" in coverage and "tree_sitter_available:" in coverage)
check("cross-ref pass", "状态: PASS" in read("drafts/07-cross-ref-checks.md"))
check("sla pass", "status: PASS" in read("SLA_REPORT.md"))
check("performance diagnostic present", "慢因结论" in performance_report and "阶段耗时 Top20" in performance_report)
check("timeout not default fix", "agent_timeout: disabled" in performance_report or "agent_timeout: enabled" in performance_report)

try:
    expected_data = json.loads(read("expected-symbols.json"))
    check("expected symbols json parse", isinstance(expected_data.get("symbols"), list) and "engine" in expected_data)
except json.JSONDecodeError:
    check("expected symbols json parse", False)

try:
    coverage_data = json.loads(read("coverage-symbols.json"))
except json.JSONDecodeError:
    coverage_data = {"modules": {}}
    check("coverage json parse", False)

try:
    agent_summary = json.loads(read("AGENT_SUMMARY.json"))
    check("agent summary json parse", isinstance(agent_summary, dict) and "mode" in agent_summary and "status" in agent_summary)
    if agent_summary.get("mode") != "deterministic":
        check("agent summary pass", agent_summary.get("status") == "PASS")
except json.JSONDecodeError:
    agent_summary = {}
    check("agent summary json parse", False)
try:
    performance = json.loads(read("PERFORMANCE_REPORT.json"))
    check("performance json parse", isinstance(performance.get("stages"), list) and "summary" in performance)
except json.JSONDecodeError:
    performance = {}
    check("performance json parse", False)
for module_id, item in coverage_data.get("modules", {}).items():
    draft_text = read(f"drafts/06-module-{module_id}.md")
    threshold = float(item.get("threshold", 0))
    expected = item.get("expected_symbols", [])
    covered_now = []
    for symbol in expected:
        name = symbol.get("name", "")
        ok = bool(name) and re.search(rf"\\b{re.escape(name)}\\b", draft_text)
        check(f"coverage symbol:{module_id}:{name}", ok)
        if ok:
            covered_now.append(name)
    ratio = 1.0 if not expected else len(set(covered_now)) / max(1, len({symbol.get("name", "") for symbol in expected if symbol.get("name")}))
    check(f"coverage gate:{module_id}", ratio >= threshold, f"{ratio:.2f}/{threshold:.2f}")

failed_blocks = re.findall(r"(?m)^  - id: (module_[0-9]+)\\n((?:    .+\\n)+)", state)
for module_id, block in failed_blocks:
    check(
        f"failed module schema:{module_id}",
        all(field in block for field in ["tier:", "attempts:", "last_error:", "coverage_ratio:", "missing_symbols_count:", "suggested_recovery:"]),
    )

markdown_files = [path for path in root.glob("*.md") if path.is_file()]
claim_files = [
    path
    for path in root.rglob("*")
    if path.is_file()
    and "acceptance" not in path.relative_to(root).parts
    and (path.name.startswith("ANALYSIS_REPORT") or path.name in {"08-coverage.md", "STATE_REPORT.md", "SLA_REPORT.md"})
]
claim_text = "\\n".join(path.read_text(encoding="utf-8", errors="replace") for path in claim_files)
markdown_text = "\\n".join(strip_fenced_code(path.read_text(encoding="utf-8", errors="replace")) for path in markdown_files)
main_report = read("ANALYSIS_REPORT.md")
check("failed section absent on pass", "§9 未完成模块明细" not in main_report)
try:
    tools = sorted(item["name"] for item in json.loads(read("mcp-tools.json")))
except (json.JSONDecodeError, KeyError, TypeError):
    tools = []
    check("mcp tools json parse", False)
check("api surface count", not tools or all(tool in main_report for tool in tools), f"{len(tools)} tools")

slice_refs = sorted(set(re.findall(r"slices/[A-Za-z0-9_.-]+", main_report)))
check("slice refs exist", bool(slice_refs) and all((root / ref).exists() for ref in slice_refs))

draft_refs = sorted(set(re.findall(r"drafts/[A-Za-z0-9_.-]+", main_report)))
check("draft refs exist", all((root / ref).exists() for ref in draft_refs))

readme = read("README.md")
local_links = [link for link in re.findall(r"\\[[^\\]]+\\]\\(([^)#][^)]+)\\)", readme) if not link.startswith(("http://", "https://"))]
check("readme links exist", all((root / link).exists() for link in local_links))

wiki_refs = set(re.findall(r"\\[\\[([^\\]]+)\\]\\]", markdown_text))
valid_wiki = set(module_ids)
check("wikilinks valid", all(ref in valid_wiki for ref in wiki_refs), ",".join(sorted(wiki_refs - valid_wiki)))

for md in markdown_files:
    text = md.read_text(encoding="utf-8", errors="replace")
    structural_text = strip_fenced_code(text)
    headings = set()
    for heading in re.findall(r"(?m)^#+\\s+(.+)$", structural_text):
        slug = re.sub(r"[^a-z0-9\\u4e00-\\u9fff -]", "", heading.lower()).strip().replace(" ", "-")
        if slug:
            headings.add(slug)
    anchors = [anchor[1:] for anchor in re.findall(r"\\(#[^)]+\\)", structural_text)]
    check(f"anchors:{md.name}", all(anchor in headings for anchor in anchors))

report_names = ["tech-lead", "business", "learning"]
reports = {name: read(f"ANALYSIS_REPORT.{name}.md") for name in report_names}
if all(reports.values()):
    check("main report distinct", all(main_report != report for report in reports.values()))
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
check("no placeholder claims", not any(term in claim_text for term in ["待 LLM 深度分析补全", "PASS_WITH_DETERMINISTIC_BASELINE", "骨架/待补全"]))

sys.exit(1 if failures else 0)
PY
""",
        encoding="utf-8",
    )
    check.chmod(0o755)


def analyze(args: argparse.Namespace) -> Path:
    args = apply_config(args)
    started_at = time.monotonic()
    performance = init_performance()
    with timed_stage(performance, "checkout-target"):
        repo, source, temp = checkout_target(args.target)
    try:
        output = Path(args.output).expanduser().resolve()
        with timed_stage(performance, "prepare-output"):
            prepare_output(output, args.resume)
        with timed_stage(performance, "scan-files"):
            files = sorted(iter_files(repo), key=lambda path: rel(path, repo))
        with timed_stage(performance, "classify-repo"):
            project_name = parse_project_name(repo)
            repo_type = detect_repo_type(repo, files)
            dimensions = SLICES[repo_type]

        with timed_stage(performance, "write-meta"):
            write_meta(repo, output, source, files)
            write_repo_type(output, repo_type, project_name, dimensions)
            write_manifest_card(repo, output, source, project_name, repo_type, files)
            write_question_answers(output, args.no_question, args.mode)
        with timed_stage(performance, "repomix-slices"):
            write_slices(repo, output, repo_type, files)
        with timed_stage(performance, "module-drafts"):
            write_module_plan(repo, output, files)
            write_module_drafts(repo, output, files)
        with timed_stage(performance, "cross-ref-deterministic-initial"):
            cross_ref_issues = write_cross_ref(output)
        with timed_stage(performance, "agent-init"):
            agent_issues, agent_summary = init_agent_summary(output, args)
        with timed_stage(performance, "agent-modules-batch"):
            agent_issues.extend(run_module_agent_loop(output, args, files, repo, agent_summary, performance))
        with timed_stage(performance, "cross-ref-deterministic-after-agent"):
            cross_ref_issues = write_cross_ref(output)
        with timed_stage(performance, "coverage-initial"):
            coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
        if args.agent_mode != "deterministic" and any(item["status"] != "PASS" for item in coverage["modules"].values()):
            with timed_stage(performance, "agent-coverage-repair"):
                agent_issues.extend(repair_failed_coverage_modules(output, args, coverage, agent_summary, performance))
            with timed_stage(performance, "cross-ref-deterministic-after-coverage-repair"):
                cross_ref_issues = write_cross_ref(output)
            with timed_stage(performance, "coverage-after-repair"):
                coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
            with timed_stage(performance, "agent-summary-after-coverage-repair"):
                write_agent_summary(output, agent_summary, agent_issues)
        with timed_stage(performance, "agent-cross-ref-review"):
            review_issues, review_text = run_cross_ref_agent(output, args, agent_summary, performance)
        agent_issues.extend(review_issues)
        if args.agent_mode != "deterministic":
            module_ids = [module_id for module_id, _root, _count in module_rows(files, repo)]
            with timed_stage(performance, "agent-cross-ref-repair"):
                repair_issues = repair_cross_ref_modules(output, args, module_ids, review_text, agent_summary, performance)
            if repair_issues or agent_summary.get("cross_ref_repairs"):
                agent_issues.extend(repair_issues)
                with timed_stage(performance, "cross-ref-deterministic-after-cross-ref-repair"):
                    cross_ref_issues = write_cross_ref(output)
                with timed_stage(performance, "coverage-after-cross-ref-repair"):
                    coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
                with timed_stage(performance, "agent-cross-ref-review-final"):
                    review_issues, _review_text = run_cross_ref_agent(output, args, agent_summary, performance, "cross-ref-review-final")
                agent_issues.extend(review_issues)
        with timed_stage(performance, "state-report"):
            failed_modules = write_state_report(output, coverage, cross_ref_issues, agent_issues)
        with timed_stage(performance, "render-reports"):
            write_reports(repo, output, source, project_name, repo_type, files, args.mode, failed_modules)
        with timed_stage(performance, "write-index-and-config"):
            write_readme(output, project_name, repo_type, args.mode)
            write_config_effective(output, args)
            write_mcp_tools(output, mcp_tool_names(repo, files, API_SURFACE_LIMIT))
        with timed_stage(performance, "sla-report"):
            write_sla_report(output, args, started_at, coverage, cross_ref_issues, agent_issues)
        with timed_stage(performance, "performance-report"):
            write_performance_report(output, args, started_at, performance)
        with timed_stage(performance, "acceptance-script"):
            write_acceptance(output)
        if args.save_pref:
            with timed_stage(performance, "save-last-session"):
                save_last_session(args)
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
    parser.add_argument("--config", default="", help="JSON 配置文件路径，支持 mode/no_question/coverage/SLA 默认值")
    parser.add_argument("--resume", action="store_true", help="复用输出目录，清理本工具生成文件但保留用户手写文件")
    parser.add_argument("--target-coverage-core", type=float, default=None, help="核心模块符号覆盖率阈值")
    parser.add_argument("--target-coverage-minor", type=float, default=None, help="次要模块符号覆盖率阈值")
    parser.add_argument("--coverage-engine", choices=["auto", "regex"], default="auto", help="覆盖率符号引擎；auto 会在可用时记录 tree-sitter parse 结果")
    parser.add_argument("--sla-minutes", type=float, default=None, help="本次分析 SLA 分钟预算")
    parser.add_argument("--agent-mode", choices=["deterministic", "codex", "command"], default="deterministic", help="判断型模块分析模式；codex/command 会执行外部 agent")
    parser.add_argument("--agent-command", default="", help="--agent-mode command 时使用的命令，prompt 通过 stdin 传入")
    parser.add_argument("--agent-max-attempts", type=int, default=None, help="agent 失败重试次数，默认 3")
    parser.add_argument("--agent-timeout-seconds", type=int, default=None, help="agent 子进程超时秒数；0 表示不启用，默认 0")
    parser.add_argument("--use-last-pref", action="store_true", help="读取配置目录中的 last-session.json 作为默认偏好")
    parser.add_argument("--save-pref", action="store_true", help="运行成功后保存本次非敏感偏好到 last-session.json")
    return parser


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    output = analyze(args)
    print(f"分析完成: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
