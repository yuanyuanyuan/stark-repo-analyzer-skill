"""Reproducible control-plane orchestration for the Agent-native skill.

The Python entrypoint owns deterministic work: input normalization, Graphify
gating, sizing, adaptive context, task manifests, and final artifact checks.
Agent-owned module reading remains in Markdown drafts so the reference skill's
reasoning and subagent responsibilities are preserved.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from . import __version__
from .contracts import ContractError, validate_run_contract, write_output_manifest


CODE_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".java", ".js", ".jsx", ".kt", ".m",
    ".mm", ".php", ".py", ".rb", ".rs", ".sh", ".swift", ".ts", ".tsx", ".vue",
}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "target", "dist", "build", "vendor"}
SKIP_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock"}
PUBLIC_HOSTS = {"github.com", "gitlab.com", "gitee.com"}
TRANSIENT_FAILURE = re.compile(
    r"(?:timeout|timed out|HTTP[ /](?:429|5[0-9][0-9])|status[=: ]+(?:429|5[0-9][0-9]))",
    re.IGNORECASE,
)


class RunFailure(RuntimeError):
    """An analysis run stopped at a declared failure boundary."""

    def __init__(self, message: str, *, failure_class: str = "configuration-or-execution") -> None:
        super().__init__(message)
        self.failure_class = failure_class


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    """Run a command without invoking a shell or exposing environment secrets."""

    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "timeout")


def _git_output(target: Path, args: list[str]) -> str | None:
    result = run(["git", "-C", str(target), *args])
    return result.stdout.strip() if result.returncode == 0 else None


def source_status(target: Path) -> dict[str, object]:
    return {
        "head": _git_output(target, ["rev-parse", "HEAD"]),
        "porcelain": _git_output(target, ["status", "--porcelain"]) or "",
    }


def normalize_input(value: str, work_dir: Path) -> tuple[Path, dict[str, object]]:
    """Resolve a local path or public repository identifier without credentials."""

    candidate = Path(value).expanduser()
    clone_source = value
    if candidate.exists():
        target = candidate.resolve()
        if not target.is_dir():
            raise ValueError("local input is not a directory")
        if not (target / ".git").exists():
            raise ValueError("local input must be a Git repository so its source commit can be recorded")
        source_kind = "local-path"
    else:
        raw_url = value if "://" in value else "https://github.com/" + value
        parsed = urlparse(raw_url)
        if parsed.scheme != "https" or parsed.hostname not in PUBLIC_HOSTS:
            raise ValueError("input must be a public HTTPS GitHub/GitLab/Gitee repository")
        if parsed.username or parsed.password:
            raise ValueError("repository URL must not contain credentials")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError("repository identifier must contain owner and repository")
        owner, repository = parts[0], parts[1].removesuffix(".git")
        if not owner or not repository:
            raise ValueError("repository identifier contains an empty owner or repository")
        safe_url = urlunparse((parsed.scheme, parsed.netloc, f"/{owner}/{repository}.git", "", "", ""))
        clone_source = safe_url
        target = (work_dir / "source").resolve()
        if target.exists():
            raise ValueError(f"clone destination already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        result = run(["git", "clone", "--depth=1", clone_source, str(target)])
        if result.returncode:
            raise RunFailure(
                "git clone failed: " + (result.stderr.strip() or "unknown error"),
                failure_class="source-acquisition",
            )
        source_kind = "public-url" if "://" in value else "owner-repo"

    status = source_status(target)
    if not status["head"]:
        raise ValueError("source repository HEAD could not be resolved")
    return target, {
        "kind": source_kind,
        "value": value if source_kind == "local-path" else clone_source,
        "resolved_path": str(target),
        "clone_source": clone_source if source_kind != "local-path" else None,
        "source_commit": status["head"],
        "source_dirty": bool(status["porcelain"]),
        "source_status_before": status,
    }


def source_files(target: Path) -> list[Path]:
    files: list[Path] = []
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        relative = path.relative_to(target)
        if any(part in SKIP_PARTS for part in relative.parts) or path.name in SKIP_NAMES:
            continue
        if any(part.lower() in {"tests", "test", "examples", "docs"} for part in relative.parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def size_report(target: Path) -> dict[str, object]:
    files = source_files(target)
    groups: defaultdict[str, int] = defaultdict(int)
    rows = []
    for path in files:
        try:
            lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            lines = 0
        relative = path.relative_to(target)
        group = relative.parts[0] if len(relative.parts) > 1 else "root"
        groups[group] += lines
        rows.append({"file": str(relative), "lines": lines, "group": group})
    total = sum(row["lines"] for row in rows)
    return {
        "files": len(files),
        "effective_lines": total,
        "by_group": dict(sorted(groups.items())),
        "files_detail": rows,
        "mode": "standard",
        "thresholds": {"core_percent": 60, "secondary_percent": 30},
        "bounded": total > 50_000,
    }


def collect_context(target: Path) -> dict[str, object]:
    """Collect local context; external research stays Agent-owned and explicit."""

    names = {"README.md", "README.rst", "CONTRIBUTING.md", "ARCHITECTURE.md", "AGENTS.md"}
    candidates = [path for path in target.iterdir() if path.is_file() and path.name in names]
    for directory_name in ("docs", "architecture", "design"):
        directory = target / directory_name
        if directory.is_dir():
            candidates.extend(sorted(directory.rglob("*.md"))[:20])
    documents = []
    urls = []
    for path in sorted(set(candidates))[:40]:
        text = path.read_text(encoding="utf-8", errors="replace")
        documents.append({"path": str(path.relative_to(target)), "lines": len(text.splitlines()), "excerpt": text[:1200]})
        for raw_url in re.findall(r"https?://[^)\s>]+", text):
            parsed = urlparse(raw_url)
            if parsed.username or parsed.password:
                continue
            urls.append(urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", "")))
    return {
        "documents": documents,
        "external_sources": sorted(set(urls)),
        "research_status": "agent-research-required",
        "offline_reason": "The control plane records candidates; external search/crawl belongs to the Agent runtime.",
    }


def _adaptive_questions(target: Path, sizing: dict[str, object], context: dict[str, object]) -> list[dict[str, str]]:
    extensions = Counter(path.suffix.lower() for path in target.rglob("*") if path.is_file())
    questions: list[dict[str, str]] = []

    def add(question_id: str, question: str, evidence: str) -> None:
        questions.append({"id": question_id, "question": question, "evidence": evidence})

    if extensions[".rs"] or extensions[".go"]:
        add("compile-runtime-boundary", "项目如何分配编译期边界与运行时扩展点？这种取舍如何影响模块演进？", "Rust/Go source extensions")
    if extensions[".py"] and (target / "pyproject.toml").exists():
        add("configuration-execution", "配置、入口和核心执行路径之间的约束是显式声明还是运行时推导？为什么？", "pyproject.toml and Python source")
    if any("plugin" in path.name.lower() or "extension" in path.name.lower() for path in target.rglob("*")):
        add("extension-boundary", "扩展机制如何隔离宿主生命周期和用户代码？失败时谁拥有恢复责任？", "plugin/extension paths")
    if bool(sizing.get("bounded", int(sizing.get("effective_lines", 0)) > 50_000)):
        add("bounded-core", "在 bounded scope 下，哪个核心数据流最能代表系统设计，哪些外围范围必须诚实排除？", "effective source size exceeds 50,000 lines")
    if not questions:
        add("primary-boundary", "项目最重要的边界是什么：数据流、生命周期、配置还是扩展？源码中的哪条路径能证明它？", "no stronger feature signal")
    if not context["external_sources"]:
        add("offline-research", "没有发现可用外部来源；报告是否需要保持离线并把竞品定位标记为未找到？", "no local documentation URLs")
    return questions


def feature_questions(target: Path, sizing: dict[str, object], context: dict[str, object]) -> list[str]:
    """Backward-compatible question API used by small integrations and tests."""

    return [item["question"] for item in _adaptive_questions(target, sizing, context)]


def doctor(script: Path, phase: str, target: Path, work_dir: Path) -> tuple[int, dict[str, object]]:
    result = run([str(script), phase, "--target", str(target), "--work-dir", str(work_dir), "--json"])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "phase": phase,
            "status": {"code": 30, "name": "blocked"},
            "failures": [result.stderr.strip() or result.stdout.strip() or "doctor returned invalid JSON"],
        }
        return 30, payload
    status = payload.get("status", {})
    return int(status.get("code", result.returncode or 30)), payload


def target_graphify_signature(target: Path) -> tuple | None:
    output = target / "graphify-out"
    if not output.exists():
        return None
    return tuple(
        sorted(
            (str(path.relative_to(output)), path.stat().st_size, path.stat().st_mtime_ns)
            for path in output.rglob("*")
            if path.is_file()
        )
    )


def cleanup_created_target_graphify(target: Path, before: tuple | None, after: tuple | None, log: list[str]) -> None:
    if before is None and after is not None:
        output = target / "graphify-out"
        shutil.rmtree(output)
        log.append("removed Graphify output unexpectedly created inside the target repository")
        raise RunFailure("Graphify wrote into the target repository", failure_class="source-boundary-violation")
    if before != after:
        raise RunFailure("target graphify-out changed during isolated extraction", failure_class="source-boundary-violation")


def ensure_source_unchanged(target: Path, before: dict[str, object], *, phase: str) -> dict[str, object]:
    after = source_status(target)
    if after != before:
        raise RunFailure(
            f"source repository changed during {phase}",
            failure_class="source-boundary-violation",
        )
    return after


def graphify_extract(target: Path, work_dir: Path, log: list[str]) -> list[dict[str, object]]:
    """Run Graphify with retries limited to classified transient failures."""

    command = ["graphify", "extract", str(target), "--mode", "deep", "--out", str(work_dir)]
    retries = 0
    attempts: list[dict[str, object]] = []
    while True:
        started = time.monotonic()
        result = run(command)
        elapsed = round(time.monotonic() - started, 2)
        combined = result.stdout + "\n" + result.stderr
        transient = bool(result.returncode != 0 and TRANSIENT_FAILURE.search(combined))
        attempts.append({"exit_code": result.returncode, "elapsed_seconds": elapsed, "transient_failure": transient})
        log.append(f"graphify extract exit={result.returncode} elapsed={elapsed}s transient={transient}")
        if result.returncode == 0:
            return attempts
        if not transient or retries >= 2:
            failure_class = "graphify-transient-exhausted" if transient else "graphify-execution"
            raise RunFailure(f"Graphify extraction failed with exit code {result.returncode}", failure_class=failure_class)
        retries += 1
        delay = 2**retries
        log.append(f"transient Graphify failure; retry {retries}/2 after {delay}s")
        time.sleep(delay)


def graph_map(work_dir: Path, target: Path) -> str:
    graph_path = work_dir / "graphify-out" / "graph.json"
    report_path = work_dir / "graphify-out" / "GRAPH_REPORT.md"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    candidates = []
    communities = Counter()
    for node in nodes:
        if isinstance(node, dict) and node.get("source_file"):
            candidates.append(
                f"- `{node['source_file']}:{node.get('source_location', '?')}` — {node.get('label', node.get('id', 'unknown'))}"
            )
            if node.get("community") is not None:
                communities[str(node["community"])] += 1
    edge_lines = []
    for link in links[:120]:
        if isinstance(link, dict):
            edge_lines.append(
                f"- `{str(link.get('confidence', 'UNKNOWN')).upper()}` "
                f"`{link.get('source_file', '?')}:{link.get('source_location', '?')}`: "
                f"{link.get('source', '?')} -> {link.get('target', '?')} ({link.get('relation', 'unknown')})"
            )
    lines = [
        "# Graphify Navigation Map",
        "",
        f"- Nodes: {len(nodes)}",
        f"- Edges: {len(links)}",
        "- Target: `" + str(target) + "`",
        "- Confidence rule: source code adjudicates Graphify relations.",
        "",
        "## Communities",
        "",
    ]
    lines.extend(f"- Community {name}: {count} nodes" for name, count in communities.most_common(40))
    lines.extend(["", "## Report Summary", "", report_path.read_text(encoding="utf-8")[:4000], "", "## Candidate Source Paths", ""])
    lines.extend(candidates[:80] or ["- No source candidates were accepted; post-graph should have failed."])
    lines.extend(["", "## Edge Evidence Samples", ""] + (edge_lines or ["- No edge evidence was accepted; post-graph should have failed."]))
    return "\n".join(lines) + "\n"


def _safe_module_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "root"


def write_module_plan(work_dir: Path, sizing: dict[str, object], questions: list[dict[str, str]]) -> list[dict[str, object]]:
    groups = list(sizing["by_group"])
    modules: list[dict[str, object]] = []
    for index, group in enumerate(groups, start=1):
        module_id = f"module-{index:02d}-{_safe_module_id(group)}"
        modules.append(
            {
                "id": module_id,
                "candidate_scope": f"{group}/" if group != "root" else "repository root",
                "type": "candidate-core-or-secondary",
                "business_module_required": True,
                "reason": "Directory is only a navigation candidate; Agent must derive the business boundary from data flow and responsibility.",
                "output": f"drafts/06-module-{module_id}.md",
                "questions": [item["id"] for item in questions],
                "owner": "Agent",
                "status": "pending",
                "attempts": 0,
                "isolation": f"one-draft-path:{module_id}",
                "failure": None,
            }
        )
    lines = [
        "# Module Analysis Plan",
        "",
        "Graphify and size scans provide candidate paths only. The Agent must derive business modules from capabilities, data flow and responsibility before assigning module drafts.",
        "",
        "## Narrative",
        "",
        "The report must use a data-flow, layer, or problem-driven narrative and state each transition as an output/constraint from one module to the next.",
        "",
        "## Candidate Tasks",
        "",
    ]
    lines.extend(f"{i}. `{module['id']}` — `{module['candidate_scope']}`; {module['reason']}" for i, module in enumerate(modules, start=1))
    lines.extend(["", "## Agent Requirements", "", "- One independent Agent task per core business module.", "- All secondary modules may be assigned to one secondary task.", "- Every draft must include source paths/lines, Mermaid, Why > What trade-offs and a final coverage table.", ""])
    (work_dir / "drafts" / "05-modules-plan.md").write_text("\n".join(lines), encoding="utf-8")
    (work_dir / "drafts" / "06-module-tasks.json").write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return modules


def write_input_snapshot(work_dir: Path, value: str, target: Path, metadata: dict[str, object]) -> None:
    lines = [
        "# Physical Analysis Run Input",
        "",
        "```yaml",
        f"run_id: {metadata['run_id']}",
        "input:",
        f"  kind: {metadata['source']['kind']}",
        f"  value: {value}",
        "analysis_mode: standard",
        "graphify:",
        "  extraction_mode: deep",
        "  backend: auto-detect",
        "  output: <WORK_DIR>/graphify-out",
        f"workspace: {work_dir}",
        "```",
        "",
        f"Resolved source: `{target}`",
        f"Source HEAD: `{metadata['source']['source_commit']}`",
        "",
        "The target is read-only. External research, tests and runtime behavior must be recorded as performed or not performed; they must not be inferred from static source reading.",
        "",
    ]
    (work_dir / "input.md").write_text("\n".join(lines), encoding="utf-8")


def write_plan(work_dir: Path, sizing: dict[str, object], context: dict[str, object], questions: list[dict[str, str]]) -> None:
    group_lines = [f"- `{name}`: {lines:,} effective lines" for name, lines in sizing["by_group"].items()]
    plan = [
        "# Analysis Plan",
        "",
        "- Analysis mode: `standard`",
        f"- Effective source: {sizing['files']:,} files / {sizing['effective_lines']:,} lines",
        f"- Bounded scope required: `{sizing['bounded']}`",
        "- Core threshold: 60%; secondary threshold: 30%",
        "",
        "## Size by Candidate Area",
        "",
        *group_lines,
        "",
        "## Required Sequence",
        "",
        "Input -> Graphify/doctor -> sizing -> local research -> adaptive questions -> module plan -> Agent module drafts -> source adjudication -> coverage gate -> report fusion.",
        "",
        "## Research Boundary",
        "",
        f"- Local documents inspected: {len(context['documents'])}",
        f"- URL candidates: {len(context['external_sources'])}",
        f"- Control-plane research status: `{context['research_status']}`",
        "",
        "## Adaptive Questions",
        "",
    ]
    plan.extend(f"- `{item['id']}` ({item['evidence']}): {item['question']}" for item in questions)
    (work_dir / "drafts" / "03-plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    (work_dir / "drafts" / "03-research.md").write_text(
        "# Research Context\n\n"
        "## Local Evidence\n\n"
        + "\n".join(f"- `{doc['path']}` ({doc['lines']} lines): {doc['excerpt'][:240].replace(chr(10), ' ')}" for doc in context["documents"])
        + "\n\n## External Research\n\n"
        + f"Status: `{context['research_status']}`. {context['offline_reason']}\n"
        + ("Candidate URLs:\n" + "\n".join(f"- {url}" for url in context["external_sources"]) if context["external_sources"] else "No external URLs were found in local context; Agent research may be required.")
        + "\n",
        encoding="utf-8",
    )


def fuse_initial_report(work_dir: Path, target: Path, metadata: dict[str, object], sizing: dict[str, object], context: dict[str, object], questions: list[dict[str, str]], modules: list[dict[str, object]]) -> None:
    source_commit = metadata["source"]["source_commit"] or "未找到"
    lines = [
        "# 仓库架构分析",
        "",
        "## 1. 场景与项目定位",
        "",
        f"本次 V1 运行分析 `{target.name}`，固定源码 commit 为 `{source_commit}`。最终报告必须从具体使用场景出发，说明现有方案的不足，再解释源码如何解决问题。",
        "",
        "当前阶段由 Agent 完成项目文档/外部研究、模块源码阅读和 Why > What 叙事；本文件是可审计的报告骨架，不把 Graphify 结构候选误写成结论。",
        "",
        "## 2. 项目全景",
        "",
        f"有效源码范围为 {sizing['files']:,} 个文件、{sizing['effective_lines']:,} 行；V1 分析档位为 `standard`。候选目录只用于组织 Agent 阅读，业务模块边界必须由数据流和职责确认。",
        "",
        "```mermaid",
        "flowchart LR",
        "Input[Local path or public repository] --> Normalize[Resolve source commit]",
        "Normalize --> Doctor[Doctor preflight]",
        "Doctor --> Graph[Graphify deep structure evidence]",
        "Graph --> Read[Agent source reading]",
        "Read --> Validate[Cross-validation and coverage gate]",
        "Validate --> Report[Single final report]",
        "```",
        "",
        "## 3. Graphify 证据边界",
        "",
        "Graphify map is navigation context only. `EXTRACTED` relations require source verification; `INFERRED` remains pending verification; `AMBIGUOUS` is only a risk/question. Source code adjudicates graph conflicts, and all conflicts belong in `drafts/07-cross-validation.md`.",
        "",
        "## 4. Report Structure and Module Tasks",
        "",
        "The Agent must replace candidate areas with business modules and write one draft per core module. The expected task manifest is `drafts/06-module-tasks.json`.",
        "",
    ]
    lines.extend(f"- `{module['id']}`: candidate `{module['candidate_scope']}` -> `{module['output']}`" for module in modules)
    lines.extend(
        [
            "",
            "## 5. Adaptive Questions",
            "",
        ]
    )
    lines.extend(f"- **{item['id']}**: {item['question']}" for item in questions)
    lines.extend(
        [
            "",
            "## 6. Evidence and Limitations",
            "",
            f"- Source: `{metadata['source']['resolved_path']}`",
            f"- Commit: `{source_commit}`",
            "- Graphify: `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `drafts/01-graphify-map.md`",
            f"- Local context documents: {len(context['documents'])}; external research status: `{context['research_status']}`",
            "- Static reading coverage, test coverage and runtime verification must remain separate metrics.",
            "- Unread code, unavailable tools, bounded scope and unperformed research must be stated explicitly.",
            "",
        ]
    )
    (work_dir / "ANALYSIS_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def write_checks(work_dir: Path, rows: list[tuple[str, str, str]]) -> None:
    text = ["# Run Checks", "", "| Check | Status | Evidence |", "|---|---|---|"]
    text.extend(f"| {name} | {status} | `{evidence}` |" for name, status, evidence in rows)
    (work_dir / "checks.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def _draft_heading(path: Path, text: str) -> str:
    title = path.stem.removeprefix("06-module-").replace("-", " ").title()
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip() or title
        lines = lines[1:]
    return f"### {title}\n\n" + "\n".join(lines).strip() + "\n"


def finalize(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).expanduser().resolve()
    metadata_path = work_dir / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read metadata: {type(exc).__name__}", file=sys.stderr)
        return 30

    failures: list[str] = []
    source = metadata.get("source", {})
    source_path = source.get("resolved_path")
    if source_path and source.get("source_status_before"):
        target = Path(source_path)
        if not target.is_dir() or source_status(target) != source["source_status_before"]:
            failures.append("source repository changed after analyze")
    graphify = metadata.get("graphify", {})
    if graphify.get("preflight", {}).get("status", {}).get("code") != 0:
        failures.append("doctor preflight did not pass")
    if graphify.get("post_graph", {}).get("status", {}).get("code") != 0:
        failures.append("doctor post-graph did not pass")
    try:
        validation = validate_run_contract(work_dir, complete=True)
    except ContractError as exc:
        failures.append(str(exc))
        validation = None
    if failures:
        write_checks(work_dir, [("Finalization", "FAIL", "; ".join(failures))])
        print("finalize blocked: " + "; ".join(failures), file=sys.stderr)
        return 30
    assert validation is not None

    base = (work_dir / "ANALYSIS_REPORT.md").read_text(encoding="utf-8", errors="replace")
    modules = sorted((work_dir / "drafts").glob("06-module-*.md"))
    research = (work_dir / "drafts" / "03-research.md").read_text(encoding="utf-8", errors="replace")
    plan = (work_dir / "drafts" / "03-plan.md").read_text(encoding="utf-8", errors="replace")
    cross = (work_dir / "drafts" / "07-cross-validation.md").read_text(encoding="utf-8", errors="replace")
    insights = (work_dir / "drafts" / "08-insights.md").read_text(encoding="utf-8", errors="replace")
    sections = [base.rstrip(), "", "## 6. 调研与执行计划", "", research.rstrip(), "", plan.rstrip(), "", "## 7. 深度模块分析", ""]
    sections.extend(_draft_heading(path, path.read_text(encoding="utf-8", errors="replace")) for path in modules)
    sections.extend(["## 8. 交叉验证与评价", "", cross.rstrip(), "", insights.rstrip(), ""])
    report = "\n".join(sections)
    if "```mermaid" not in report.lower():
        failures.append("final report has no Mermaid diagram")
    if failures:
        write_checks(work_dir, [("Finalization", "FAIL", "; ".join(failures))])
        print("finalize blocked: " + "; ".join(failures), file=sys.stderr)
        return 30
    (work_dir / "ANALYSIS_REPORT.md").write_text(report, encoding="utf-8")
    metadata["ended_at"] = now()
    metadata["outcome"] = "complete"
    metadata["finalized"] = {
        "module_drafts": [str(path.relative_to(work_dir)) for path in modules],
        "cross_validation": "drafts/07-cross-validation.md",
        "insights": "drafts/08-insights.md",
        "coverage": "drafts/08-coverage.md",
    }
    metadata["output_manifest"] = "manifest.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_checks(
        work_dir,
        [
            ("Doctor preflight", "PASS", "metadata.json"),
            ("Doctor post-graph", "PASS", "metadata.json"),
            ("Source adjudication", "PASS", "drafts/07-cross-validation.md"),
            ("Module coverage", "PASS", "drafts/08-coverage.md"),
            ("Final report fusion", "PASS", "ANALYSIS_REPORT.md"),
        ],
    )
    validation = validate_run_contract(work_dir, complete=True)
    write_output_manifest(work_dir, status="complete", validation=validation)
    return 0


def analyze(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).expanduser().resolve()
    input_path = Path(args.input).expanduser()
    input_candidate = input_path.resolve() if "://" not in args.input and input_path.exists() else None
    if input_candidate and input_candidate.is_dir() and (work_dir == input_candidate or input_candidate in work_dir.parents):
        print("work_dir must be outside target repository", file=sys.stderr)
        return 30
    if args.mode != "standard":
        print("V1 supports only standard analysis mode", file=sys.stderr)
        return 30
    if work_dir.exists() and not work_dir.is_dir():
        print("work_dir must be a directory", file=sys.stderr)
        return 30
    work_dir.mkdir(parents=True, exist_ok=True)
    if any(work_dir.iterdir()):
        print("work_dir must be empty for a new analysis", file=sys.stderr)
        return 30
    (work_dir / "drafts").mkdir(exist_ok=True)
    started = now()
    metadata: dict[str, object] = {
        "schema_version": 1,
        "run_id": args.run_id,
        "started_at": started,
        "analysis_mode": "standard",
        "source": {},
        "graphify": {},
        "tools": {"python": sys.version.split()[0]},
        "outcome": "in_progress",
        "limitations": [],
    }
    log = [f"run started: {started}", f"tool version: {__version__}", f"input: {args.input}"]
    try:
        target, source = normalize_input(args.input, work_dir)
        metadata["source"] = source
        write_input_snapshot(work_dir, args.input, target, metadata)
        doctor_script = find_doctor()
        pre_rc, pre = doctor(doctor_script, "preflight", target, work_dir)
        (work_dir / "doctor-preflight.json").write_text(json.dumps(pre, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        metadata["graphify"]["preflight"] = pre
        if pre_rc != 0:
            raise RunFailure("doctor preflight blocked", failure_class=f"doctor-{pre.get('status', {}).get('name', 'blocked')}")
        graphify = metadata["graphify"]
        graphify.update(
            {
                "version": pre.get("graphify", {}).get("version"),
                "backend": pre.get("graphify", {}).get("backend"),
                "model": pre.get("graphify", {}).get("model"),
                "extract_command": "graphify extract <target> --mode deep --out <WORK_DIR>",
            }
        )
        before = target_graphify_signature(target)
        attempts = graphify_extract(target, work_dir, log)
        after = target_graphify_signature(target)
        cleanup_created_target_graphify(target, before, after, log)
        metadata["source"]["source_status_after_graphify"] = ensure_source_unchanged(
            target,
            metadata["source"]["source_status_before"],
            phase="Graphify extraction",
        )
        graphify["extract_attempts"] = attempts
        graphify["target_graphify_out_unchanged"] = True
        graphify["artifact_paths"] = ["graphify-out/graph.json", "graphify-out/GRAPH_REPORT.md"]
        post_rc, post = doctor(doctor_script, "post-graph", target, work_dir)
        (work_dir / "doctor-post-graph.json").write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        graphify["post_graph"] = post
        if post_rc != 0:
            raise RunFailure("doctor post-graph blocked", failure_class="doctor-post-graph")
        (work_dir / "drafts" / "01-graphify-map.md").write_text(graph_map(work_dir, target), encoding="utf-8")
        sizing = size_report(target)
        context = collect_context(target)
        questions = _adaptive_questions(target, sizing, context)
        write_plan(work_dir, sizing, context, questions)
        modules = write_module_plan(work_dir, sizing, questions)
        (work_dir / "drafts" / "07-cross-validation.md").write_text(
            "# Cross-Validation\n\n"
            "Graphify relations remain navigation candidates until source paths and line ranges are checked by the Agent. "
            "Source code adjudicates conflicts; unresolved `INFERRED` and `AMBIGUOUS` relations are not conclusions.\n",
            encoding="utf-8",
        )
        (work_dir / "drafts" / "08-insights.md").write_text(
            "# Architecture Insights\n\n"
            "The Agent must write system-level design philosophy, trade-offs, redesign suggestions and residual risks here after module validation.\n",
            encoding="utf-8",
        )
        (work_dir / "drafts" / "08-coverage.md").write_text(
            "# Coverage Summary\n\n"
            "| Measure | Status | Evidence |\n|---|---|---|\n"
            "| Static source reading | pending Agent module drafts | `drafts/06-module-*.md` line tables |\n"
            "| Test coverage | not measured by this workflow | separate test evidence required |\n"
            "| Runtime verification | not measured by this workflow | dynamic trace required |\n",
            encoding="utf-8",
        )
        fuse_initial_report(work_dir, target, metadata, sizing, context, questions, modules)
        metadata["source"]["source_status_after"] = ensure_source_unchanged(
            target,
            metadata["source"]["source_status_before"],
            phase="analysis",
        )
        metadata["ended_at"] = now()
        metadata["outcome"] = "awaiting-agent-module-analysis"
        metadata["limitations"] = [
            "Agent module drafts and final source adjudication remain required.",
            "External research, tests and runtime behavior are not inferred from static reading.",
        ]
        log.append("control plane completed; awaiting Agent-owned module drafts")
        write_checks(
            work_dir,
            [
                ("Doctor preflight", "PASS", "metadata.json"),
                ("Graphify extraction", "PASS", "metadata.json"),
                ("Doctor post-graph", "PASS", "metadata.json"),
                ("Source adjudication", "PENDING", "drafts/07-cross-validation.md"),
                ("Module coverage", "PENDING", "drafts/08-coverage.md"),
            ],
        )
    except Exception as exc:
        metadata["ended_at"] = now()
        metadata["outcome"] = "failed"
        failure_class = exc.failure_class if isinstance(exc, RunFailure) else "configuration-or-execution"
        metadata["failure"] = {"class": failure_class, "message": str(exc)}
        log.append(f"FAIL class={failure_class}: {exc}")
        write_checks(work_dir, [("Run", "FAIL", f"{failure_class}: {exc}")])
        (work_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (work_dir / "execution-log.md").write_text("# Execution Log\n\n" + "\n\n".join(log) + "\n", encoding="utf-8")
        return 30
    (work_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work_dir / "execution-log.md").write_text("# Execution Log\n\n" + "\n\n".join(log) + "\n", encoding="utf-8")
    try:
        validation = validate_run_contract(work_dir, complete=False)
        write_output_manifest(work_dir, status="awaiting-agent-module-analysis", validation=validation)
    except ContractError as exc:
        log.append(f"manifest validation pending: {exc}")
        (work_dir / "execution-log.md").write_text("# Execution Log\n\n" + "\n\n".join(log) + "\n", encoding="utf-8")
    return 2


def find_doctor() -> Path:
    candidates = [
        Path.cwd() / "acceptance" / "doctor.sh",
        Path(__file__).resolve().parents[2] / "acceptance" / "doctor.sh",
        Path(__file__).resolve().parent / "doctor.sh",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("acceptance/doctor.sh is not installed or available from the current checkout")


def validate_command(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).expanduser().resolve()
    try:
        result = validate_run_contract(work_dir, complete=args.complete)
    except ContractError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 30
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="stark-repo-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze_parser = sub.add_parser("analyze", help="run the bounded V1 orchestration")
    analyze_parser.add_argument("input", help="local path, public URL, or owner/repo")
    analyze_parser.add_argument("--work-dir", required=True, help="writable directory outside target")
    analyze_parser.add_argument("--run-id", default="stark-run")
    analyze_parser.add_argument("--mode", choices=("standard",), default="standard")
    analyze_parser.set_defaults(func=analyze)
    finalize_parser = sub.add_parser("finalize", help="fuse verified Agent module drafts into the final report")
    finalize_parser.add_argument("--work-dir", required=True)
    finalize_parser.set_defaults(func=finalize)
    validate_parser = sub.add_parser("validate", help="validate a run workspace contract")
    validate_parser.add_argument("--work-dir", required=True)
    validate_parser.add_argument("--complete", action="store_true")
    validate_parser.set_defaults(func=validate_command)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
