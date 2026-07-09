#!/usr/bin/env python3
"""Shared constants, global state, and utility functions for repo-analyzer modules.

This module is the foundation dependency for all other analyzer_* modules.
It contains:
- Constants: IGNORE_DIRS, BINARY_SUFFIXES, GENERATED_DIRS, REPOMIX_BINARY, etc.
- Shared state: _LOADER (RepoTypeLoader singleton), _TOKEN_COLLECTOR (TokenCollector singleton)
- Utility functions: run, markdown_snippet, rel, read_text, init_performance, timed_stage,
  clean_output, prepare_output, is_url, command_kind
- Shared text helpers (moved here to break circular dependencies):
  module_rows, extract_section, bullet_excerpt, table_cell, degrade_agent_mode
"""

import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from repo_types_loader import RepoTypeLoader
from token_reporter import TokenCollector

# ---------------------------------------------------------------------------
# Shared singletons
# ---------------------------------------------------------------------------

# 切片维度加载器（T02）：取代内嵌 SLICES，配置外置到 config/repo-types.yaml。
_LOADER = RepoTypeLoader()

# Token 用量收集器（T05/T06）：跨 agent 运行累计用量，供 SLA/PERFORMANCE/CONFIG_EFFECTIVE 报告。
_TOKEN_COLLECTOR = TokenCollector()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

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
    ".stark-repo-analyzer",
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

GENERATED_DIRS = {"reports", "data", "diagnostics", "logs", "acceptance", "agent-runs"}
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


# ---------------------------------------------------------------------------
# Shared text helpers (moved here to break circular dependencies)
# ---------------------------------------------------------------------------

def module_rows(files: List[Path], repo: Path) -> List[Tuple[str, str, int]]:
    """Group files by top-level directory and return module rows.

    Returns a list of (module_id, root_name, file_count) tuples sorted by
    file count descending, capped at 8 entries.
    """
    groups: Counter = Counter()
    for path in files:
        relative = path.relative_to(repo)
        root = relative.parts[0] if len(relative.parts) > 1 else "[root]"
        groups[root] += 1
    return [(f"module_{index:03d}", name, count) for index, (name, count) in enumerate(groups.most_common(8), 1)]


def extract_section(text: str, heading: str) -> str:
    """Extract the content under a ``## heading`` until the next ``##`` or EOF."""
    match = re.search(rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)", text)
    return match.group(1).strip() if match else ""


def bullet_excerpt(text: str, limit: int = 4) -> List[str]:
    """Extract up to *limit* meaningful bullet-point excerpts from Markdown text."""
    priority: List[str] = []
    fallback: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("```", "<!--")):
            continue
        if stripped.startswith(("#", "|")):
            continue
        if stripped.startswith(("-", "*")):
            stripped = stripped[1:].strip()
        if re.match(r"(?i)^(attempts?|证据|evidence)\s*[:：]", stripped):
            continue
        stripped = re.sub(r"\*\*([^*]+)\*\*", r"\1", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if not stripped:
            continue
        target = priority if re.match(r"^(业务角色|设计思路|关键数据流|模块协同|架构亮点|主要风险|风险|职责)\s*[:：]", stripped) else fallback
        target.append(stripped)
        if len(priority) >= limit:
            break
    return (priority + fallback)[:limit]


def table_cell(value: str) -> str:
    """Sanitize a value for safe embedding in a Markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def degrade_agent_mode(args, reason: str) -> None:
    """Degrade agent_mode from codex/command to deterministic after a failure.

    Sets ``args.agent_mode = "deterministic"``, ``args._agent_mode_degraded = True``
    and prints a WARN to stderr. Idempotent: only degrades if not already deterministic.
    """
    if getattr(args, "agent_mode", "deterministic") == "deterministic":
        return
    args.agent_mode = "deterministic"
    args._agent_mode_degraded = True
    print(f"WARN: codex 不可用（{reason}），自动降级到 deterministic 模式，继续运行确定性流程", file=sys.stderr)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def run(cmd: Sequence[str], cwd: Path) -> str:
    """Run a command and return stdout (or stderr on failure)."""
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()


def init_performance() -> dict:
    """Initialize the performance tracking dict."""
    return {"stages": [], "agent_attempts": []}


@contextmanager
def timed_stage(performance: dict, name: str):
    """Context manager that records stage timing into the performance dict."""
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


class LogWriter:
    """T10: Writes a structured run log to ``logs/run-YYYYMMDD-HHMMSS-{pid}.md``.

    The filename includes PID to avoid concurrent runs overwriting each other.
    Entries are flushed to disk after every stage/agent entry (not just at summary
    time), and an atexit handler ensures the log is written even on failure paths.
    """

    def __init__(self, output_dir: Path):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.log_path = output_dir / "logs" / f"run-{timestamp}-{os.getpid()}.md"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list = []
        self._finalized = False
        atexit.register(self._atexit_flush)

    def _render(self, total_elapsed: float = 0.0, stage_count: int = 0, agent_count: int = 0) -> str:
        stage_lines = "\n".join(line for kind, line in self._entries if kind == "stage")
        agent_lines = "\n".join(line for kind, line in self._entries if kind == "agent")
        return (
            f"# Run Log\n\n"
            f"- total_elapsed: {total_elapsed:.3f}s\n"
            f"- stages: {stage_count}\n"
            f"- agent_attempts: {agent_count}\n\n"
            f"## Stages\n\n"
            f"| Stage | Elapsed | Status |\n|---|---|---|\n"
            f"{stage_lines}\n\n"
            f"## Agent Attempts\n\n"
            f"| Run | Attempt | Status | Elapsed |\n|---|---|---|---|\n"
            f"{agent_lines}\n"
        )

    def stage_entry(self, name: str, elapsed: float, status: str) -> None:
        self._entries.append(("stage", f"| {name} | {elapsed:.3f}s | {status} |"))
        self.flush_pending()

    def agent_entry(self, run_id: str, attempt: int, status: str, elapsed: float) -> None:
        self._entries.append(("agent", f"| agent:{run_id} | {attempt} | {status} | {elapsed:.3f}s |"))
        self.flush_pending()

    def flush_pending(self) -> None:
        """Write current entries to disk immediately (incremental, not final)."""
        if self._finalized:
            return
        stage_count = sum(1 for kind, _ in self._entries if kind == "stage")
        agent_count = sum(1 for kind, _ in self._entries if kind == "agent")
        self.log_path.write_text(self._render(0.0, stage_count, agent_count), encoding="utf-8")

    def flush(self, total_elapsed: float, stage_count: int, agent_count: int) -> None:
        """Write the final complete log with summary metrics."""
        self._finalized = True
        self.log_path.write_text(self._render(total_elapsed, stage_count, agent_count), encoding="utf-8")

    def _atexit_flush(self) -> None:
        """Ensure the log is written even if the process exits unexpectedly."""
        if not self._finalized and self._entries:
            stage_count = sum(1 for kind, _ in self._entries if kind == "stage")
            agent_count = sum(1 for kind, _ in self._entries if kind == "agent")
            self.log_path.write_text(self._render(0.0, stage_count, agent_count), encoding="utf-8")


class ProgressReporter:
    """T10: Progress reporter that replaces timed_stage with ``[N/M]`` display."""

    def __init__(self, performance: dict, total: int, log_writer: "LogWriter | None" = None):
        self._performance = performance
        self._total = total
        self._current = 0
        self._log = log_writer

    def add_stages(self, count: int) -> None:
        """Increase the total stage count when conditional stages will run."""
        self._total += count

    @contextmanager
    def stage(self, name: str):
        self._current += 1
        label = f"[{self._current}/{self._total}]" if self._total > 0 else f"[{self._current}]"
        print(f"  {label} {name} ...", file=sys.stderr, flush=True)
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
            elapsed = round(time.monotonic() - started, 3)
            self._performance.setdefault("stages", []).append(
                {"name": name, "elapsed_seconds": elapsed, "status": status, "error": error[:500]}
            )
            if self._log:
                self._log.stage_entry(name, elapsed, status)
            print(f"  {label} {name} -> {status} ({elapsed:.3f}s)", file=sys.stderr, flush=True)

    def agent_progress(self, run_id: str, attempt: int, status: str, elapsed: float) -> None:
        """Print and log an agent attempt result."""
        label = f"[{self._current}/{self._total}]"
        print(f"  {label} agent:{run_id} attempt {attempt} -> {status} ({elapsed:.3f}s)", file=sys.stderr, flush=True)
        if self._log:
            self._log.agent_entry(run_id, attempt, status, elapsed)

    def summary(self, total_elapsed: float) -> None:
        """Print final summary line and flush the log."""
        stage_count = len(self._performance.get("stages", []))
        agent_count = len(self._performance.get("agent_attempts", []))
        print(f"\n  done: {stage_count} stages, {agent_count} agent attempts, {total_elapsed:.1f}s total", file=sys.stderr)
        if self._log:
            self._log.flush(total_elapsed, stage_count, agent_count)


def clean_output(path: Path) -> None:
    """Remove and recreate the output directory."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def prepare_output(path: Path, resume: bool) -> None:
    """Prepare the output directory: clean fully or selectively for resume mode.

    When ``resume=True`` only known generated files are removed (never
    ``shutil.rmtree`` on a whole directory). User-authored files inside
    ``reports/``, ``data/``, ``diagnostics/`` etc. are preserved, as are
    historical log files.
    """
    if not resume:
        clean_output(path)
        return
    path.mkdir(parents=True, exist_ok=True)
    # Known generated files — precise paths only, no directory-level rmtree.
    generated_files = {
        # data/
        "data/meta.txt",
        "data/repo-type.yaml",
        "data/manifest-card.md",
        "data/question-answers.md",
        "data/research.md",
        "data/module-ids.yaml",
        "data/modules-plan.md",
        "data/coverage.md",
        "data/coverage-failure.md",
        "data/expected-symbols.json",
        "data/coverage-symbols.json",
        "data/mcp-tools.json",
        "data/performance-report.json",
        "data/config-effective.json",
        "data/report-data.json",
        "data/agent-summary.json",
        # reports/
        "reports/ANALYSIS_REPORT.md",
        "reports/ANALYSIS_REPORT.tech-lead.md",
        "reports/ANALYSIS_REPORT.business.md",
        "reports/ANALYSIS_REPORT.learning.md",
        "reports/README.md",
        "reports/STATE_REPORT.md",
        "reports/SLA_REPORT.md",
        "reports/PERFORMANCE_REPORT.md",
        # diagnostics/
        "diagnostics/cross-ref-checks.md",
        "diagnostics/cross-ref-review-input.md",
        "diagnostics/cross-ref-agent-review.md",
        # acceptance/
        "acceptance/check.sh",
        "acceptance/04-link.sh",
        "acceptance/05-mermaid-judge.sh",
        "acceptance/llm-judge.sh",
        "acceptance/panorama.mmd",
        "acceptance/panorama.svg",
    }
    for item in generated_files:
        target = path / item
        if target.exists() and target.is_file():
            target.unlink()
    # Generated file patterns inside subdirectories — remove only matching
    # files/dirs, preserving user-authored content.
    _clear_generated_patterns(path)


def _clear_generated_patterns(path: Path) -> None:
    """Remove known generated file patterns inside output subdirectories.

    This never calls ``shutil.rmtree`` on a top-level generated directory;
    it only removes specific generated files and run subdirectories.
    """
    # diagnostics/slices/* — generated slice files
    slices_dir = path / "diagnostics" / "slices"
    if slices_dir.is_dir():
        for item in slices_dir.iterdir():
            if item.is_file():
                item.unlink()
    # diagnostics/module-drafts/module-*.md — generated module drafts
    drafts_dir = path / "diagnostics" / "module-drafts"
    if drafts_dir.is_dir():
        for item in drafts_dir.glob("module-*.md"):
            if item.is_file():
                item.unlink()
    # agent-runs/* — each subdirectory is a generated agent run
    agent_runs_dir = path / "agent-runs"
    if agent_runs_dir.is_dir():
        for item in agent_runs_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
    # logs/run-*.md — only clear logs from previous runs that match our pattern.
    # Historical logs with different naming are preserved.
    logs_dir = path / "logs"
    if logs_dir.is_dir():
        for item in logs_dir.glob("run-*.md"):
            if item.is_file():
                item.unlink()


def is_url(value: str) -> bool:
    """Check if the value is a git URL."""
    return value.startswith("https://") or value.startswith("http://") or value.startswith("git@")


def command_kind(command: Sequence[str]) -> str:
    """Classify a command for metadata recording."""
    if not command:
        return "unknown"
    if len(command) >= 2 and command[0] == "codex" and command[1] == "exec":
        return "codex exec"
    return Path(command[0]).name


def markdown_snippet(text: str) -> str:
    """Sanitize text for safe embedding in Markdown."""
    return text.replace("```", "'''").replace("](#", "](\\#").replace("[[", "[ [").replace("]]", "] ]")


def rel(path: Path, repo: Path) -> str:
    """Return the path relative to repo as a POSIX string."""
    return path.relative_to(repo).as_posix()


def read_text(path: Path, limit: int = 200_000) -> str:
    """Read text from a file with a byte limit, returning empty string on error."""
    try:
        data = path.read_bytes()[:limit]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""
