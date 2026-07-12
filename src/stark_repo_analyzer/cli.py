"""Bounded, reproducible run orchestration for the Agent-native skill."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from . import __version__

CODE_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".java", ".js", ".jsx", ".kt", ".m",
    ".mm", ".php", ".py", ".rb", ".rs", ".sh", ".swift", ".ts", ".tsx", ".vue",
}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "target", "dist", "build", "vendor"}
SKIP_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "timeout")


def normalize_input(value: str, work_dir: Path) -> tuple[Path, dict]:
    """Resolve local paths and public repository identifiers without guessing private sources."""
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
        parsed = urlparse(value if "://" in value else "https://github.com/" + value)
        if parsed.scheme != "https" or parsed.hostname not in {"github.com", "gitlab.com", "gitee.com"}:
            raise ValueError("input must be a local path or public GitHub/GitLab/Gitee repository")
        if parsed.username or parsed.password:
            raise ValueError("repository URL must not contain credentials")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError("repository identifier must contain owner and repository")
        safe_url = f"{parsed.scheme}://{parsed.hostname}{parsed.path}"
        clone_source = safe_url if "://" in value else f"https://github.com/{parts[0]}/{parts[1]}.git"
        target = (work_dir / "source").resolve()
        if target.exists():
            raise ValueError(f"clone destination already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        result = run(["git", "clone", "--depth=1", clone_source, str(target)])
        if result.returncode:
            raise RuntimeError("git clone failed: " + (result.stderr.strip() or "unknown error"))
        source_kind = "public-url" if "://" in value else "owner-repo"
    commit = run(["git", "rev-parse", "HEAD"], cwd=target)
    source_commit = commit.stdout.strip() if commit.returncode == 0 else None
    dirty = bool(run(["git", "status", "--porcelain"], cwd=target).stdout.strip()) if source_commit else None
    safe_value = value if source_kind == "local-path" else clone_source
    return target, {
        "kind": source_kind,
        "value": safe_value,
        "resolved_path": str(target),
        "clone_source": clone_source if source_kind != "local-path" else None,
        "source_commit": source_commit,
        "source_dirty": dirty,
    }


def source_files(target: Path) -> list[Path]:
    files = []
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


def size_report(target: Path) -> dict:
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
    return {"files": len(files), "effective_lines": sum(row["lines"] for row in rows), "by_group": dict(sorted(groups.items())), "files_detail": rows}


def collect_context(target: Path) -> dict:
    names = {"README.md", "README.rst", "CONTRIBUTING.md", "ARCHITECTURE.md", "AGENTS.md"}
    documents = []
    urls = []
    for path in sorted(target.iterdir()):
        if path.name in names and path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            documents.append({"path": path.name, "lines": len(text.splitlines()), "excerpt": text[:1200]})
            for raw_url in re.findall(r"https?://[^)\s>]+", text):
                parsed = urlparse(raw_url)
                if parsed.username or parsed.password:
                    continue
                urls.append(urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", "")))
    return {"documents": documents, "external_sources": sorted(set(urls)), "research_status": "agent-research-required"}


def feature_questions(target: Path, sizing: dict, context: dict) -> list[str]:
    extensions = Counter(path.suffix.lower() for path in target.rglob("*") if path.is_file())
    questions = []
    if extensions[".rs"] or extensions[".go"]:
        questions.append("项目把编译期边界和运行时扩展点如何分配？这种取舍对模块演进有什么影响？")
    if extensions[".py"] and (target / "pyproject.toml").exists():
        questions.append("配置、入口和核心执行路径之间的约束是显式声明还是运行时推导？为什么？")
    if any("plugin" in path.name.lower() or "extension" in path.name.lower() for path in target.rglob("*")):
        questions.append("扩展机制如何隔离宿主生命周期和用户代码？失败时谁拥有恢复责任？")
    if sizing["effective_lines"] > 50000:
        questions.append("在 bounded scope 下，哪个核心数据流最能代表系统设计，哪些外围范围必须诚实排除？")
    if not questions:
        questions.append("项目最重要的边界是什么：数据流、生命周期、配置还是扩展？源码中的哪条路径能证明它？")
    if not context["external_sources"]:
        questions.append("未发现可用外部来源；报告是否需要保持离线并把竞品定位标记为未找到？")
    return questions


def doctor(script: Path, phase: str, target: Path, work_dir: Path) -> tuple[int, dict]:
    result = run([str(script), phase, "--target", str(target), "--work-dir", str(work_dir), "--json"])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"phase": phase, "status": {"code": 30, "name": "blocked"}, "failures": [result.stderr.strip() or result.stdout.strip()]}
    return result.returncode, payload


def graphify_extract(target: Path, work_dir: Path, log: list[str]) -> list[dict]:
    """Run the required headless command, retrying only classified transient failures."""
    command = ["graphify", "extract", str(target), "--mode", "deep", "--out", str(work_dir)]
    retries = 0
    attempts = []
    while True:
        started = time.monotonic()
        result = run(command)
        log.append(f"graphify extract exit={result.returncode} elapsed={time.monotonic() - started:.2f}s")
        transient = bool(re.search(r"timeout|timed out|HTTP[ /](429|5[0-9][0-9])|status[=: ]+(429|5[0-9][0-9])", result.stdout + result.stderr, re.I))
        attempts.append({"exit_code": result.returncode, "transient_failure": transient})
        if result.returncode == 0:
            return attempts
        if not transient or retries >= 2:
            raise RuntimeError(f"Graphify extraction failed with exit code {result.returncode}")
        retries += 1
        delay = 2 ** retries
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
            candidates.append(f"- `{node['source_file']}:{node.get('source_location', '?')}` — {node.get('label', node.get('id', 'unknown'))}")
            if node.get("community") is not None:
                communities[str(node["community"])] += 1
    edge_lines = []
    for link in links[:120]:
        if isinstance(link, dict):
            edge_lines.append(f"- `{str(link.get('confidence', 'UNKNOWN')).upper()}` `{link.get('source_file', '?')}:{link.get('source_location', '?')}`: {link.get('source', '?')} -> {link.get('target', '?')} ({link.get('relation', 'unknown')})")
    lines = ["# Graphify Navigation Map", "", f"- Nodes: {len(nodes)}", f"- Edges: {len(links)}", "- Confidence rule: source code adjudicates Graphify relations.", "", "## Communities", ""]
    lines.extend(f"- Community {name}: {count} nodes" for name, count in communities.most_common(40))
    lines.extend(["", "## Report Summary", "", report_path.read_text(encoding="utf-8")[:4000], "", "## Candidate Source Paths", ""])
    lines.extend(candidates[:80] or ["- No source candidates were accepted; post-graph should have failed."])
    lines.extend(["", "## Edge Evidence Samples", ""] + (edge_lines or ["- No edge evidence was accepted; post-graph should have failed."]))
    return "\n".join(lines) + "\n"


def target_graphify_signature(target: Path) -> tuple | None:
    output = target / "graphify-out"
    if not output.exists():
        return None
    return tuple(sorted((str(path.relative_to(output)), path.stat().st_size, path.stat().st_mtime_ns) for path in output.rglob("*") if path.is_file()))


def write_module_plan(work_dir: Path, target: Path, sizing: dict) -> list[str]:
    groups = list(sizing["by_group"])
    plan = ["# Module Analysis Plan", "", "Graphify and size scans provide candidate paths only. The Agent must derive business modules from capabilities, data flow and responsibility before assigning module drafts.", "", "## Candidate Scope", ""]
    plan.extend(f"- `{group}/` — candidate source area; not a business-module conclusion." for group in groups)
    plan.extend(["", "## Narrative", "", "Agent must write the module chain as `module A →[output/constraint]→ module B`, then create one draft per logical module.", ""])
    (work_dir / "drafts" / "05-modules-plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    return []


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


def fuse_report(work_dir: Path, target: Path, metadata: dict, sizing: dict, context: dict, questions: list[str], modules: list[str]) -> None:
    source_commit = metadata["source"]["source_commit"] or "未找到"
    report = ["# 仓库架构分析", "", "## 1. 项目定位", "", f"本次 V1 运行分析 `{target.name}`，源码 commit 为 `{source_commit}`。报告遵循参考 repo-analyzer 流程；生成的结构图只提供导航上下文，不能替代源码阅读。", "", "## 2. 项目全景", "", f"有效源码范围：{sizing['files']} 个文件、{sizing['effective_lines']} 行。分析档位：`standard`。", "", "```mermaid", "flowchart LR", "Input[仓库输入] --> Graph[Graphify 结构证据]", "Graph --> Read[Agent 源码阅读]", "Read --> Validate[交叉验证]", "Validate --> Report[最终报告]", "```", "", "## 3. Graphify 证据边界", "", "见 `drafts/01-graphify-map.md`。`EXTRACTED` 关系必须回到源码验证；`INFERRED` 保持待验证；`AMBIGUOUS` 只能作为风险或疑问。源码裁决冲突。", "", "## 4. 模块分析", ""]
    report.extend(f"### {name}\n\n需要 Agent 在 `drafts/06-module-{name}.md` 写入源码证据；当前候选来自规模扫描和 Graphify 导航地图。\n" for name in modules)
    report.extend(["## 5. 研究与问题", "", "研究状态：" + context["research_status"] + "。", "", "根据本仓库已观察特征生成的问题：", ""])
    report.extend(f"- {question}" for question in questions)
    report.extend(["", "## 6. 限制与覆盖率", "", "静态源码阅读覆盖率、测试覆盖率和运行时验证是三个不同指标。本次运行记录 bounded scope，在模块草稿提供行范围表前不声称已完成覆盖率。", "", "## 证据", "", f"- 源码：`{metadata['source']['resolved_path']}`", f"- Commit：`{source_commit}`", "- Graphify 产物：`graphify-out/graph.json`、`graphify-out/GRAPH_REPORT.md`", "- 外部来源：" + ("、".join(context["external_sources"]) if context["external_sources"] else "未找到"), ""])
    (work_dir / "ANALYSIS_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def finalize(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).expanduser().resolve()
    metadata_path = work_dir / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"cannot read metadata: {type(exc).__name__}", file=sys.stderr)
        return 30
    drafts = sorted((work_dir / "drafts").glob("06-module-*.md"))
    cross_validation = work_dir / "drafts" / "07-cross-validation.md"
    coverage = work_dir / "drafts" / "08-coverage.md"
    failures = []
    if not drafts:
        failures.append("no module analysis drafts")
    if not cross_validation.is_file() or "源码" not in cross_validation.read_text(encoding="utf-8", errors="replace"):
        failures.append("cross-validation draft is missing source adjudication")
    coverage_text = coverage.read_text(encoding="utf-8", errors="replace") if coverage.is_file() else ""
    if not coverage_text or "pending" in coverage_text.lower() or not ("✅" in coverage_text or "PASS" in coverage_text):
        failures.append("coverage draft is not a completed passing table")
    if failures:
        print("finalize blocked: " + "; ".join(failures), file=sys.stderr)
        return 30
    report_path = work_dir / "ANALYSIS_REPORT.md"
    report = report_path.read_text(encoding="utf-8", errors="replace") if report_path.is_file() else "# 仓库架构分析\n"
    report += "\n## Agent 已验证的模块分析\n\n"
    for draft in drafts:
        report += draft.read_text(encoding="utf-8", errors="replace") + "\n\n"
    report += "## 交叉验证记录\n\n" + cross_validation.read_text(encoding="utf-8", errors="replace")
    report += "\n## 覆盖率摘要\n\n" + coverage_text
    report_path.write_text(report, encoding="utf-8")
    metadata["ended_at"] = now()
    metadata["outcome"] = "complete"
    metadata["finalized"] = {"module_drafts": [str(path.relative_to(work_dir)) for path in drafts], "cross_validation": "drafts/07-cross-validation.md", "coverage": "drafts/08-coverage.md"}
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work_dir / "checks.md").write_text(
        "# Run Checks\n\n"
        "| Check | Status | Evidence |\n|---|---|---|\n"
        "| Doctor preflight | PASS | `metadata.json` |\n"
        "| Doctor post-graph | PASS | `metadata.json` |\n"
        "| Source adjudication | PASS | `drafts/07-cross-validation.md` |\n"
        "| Module coverage | PASS | `drafts/08-coverage.md` |\n"
        "| Final report fusion | PASS | `ANALYSIS_REPORT.md` |\n",
        encoding="utf-8",
    )
    return 0


def analyze(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).expanduser().resolve()
    input_path = Path(args.input).expanduser()
    input_candidate = input_path.resolve() if "://" not in args.input and input_path.exists() else None
    if input_candidate and input_candidate.is_dir() and (work_dir == input_candidate or input_candidate in work_dir.parents):
        print("work_dir must be outside target repository", file=sys.stderr)
        return 1
    if work_dir.exists() and not work_dir.is_dir():
        print("work_dir must be a directory", file=sys.stderr)
        return 1
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "drafts").mkdir(exist_ok=True)
    started = now()
    log = [f"run started: {started}", f"tool version: {__version__}"]
    metadata = {"schema_version": 1, "run_id": args.run_id, "started_at": started, "analysis_mode": "standard", "source": {}, "graphify": {}, "tools": {"python": sys.version.split()[0]}, "outcome": "in_progress", "limitations": []}
    try:
        target, source = normalize_input(args.input, work_dir)
        metadata["source"] = source
        doctor_script = find_doctor()
        pre_rc, pre = doctor(doctor_script, "preflight", target, work_dir)
        metadata["graphify"]["preflight"] = pre
        if pre_rc:
            raise RuntimeError("doctor preflight blocked: " + "; ".join(pre.get("failures", [])))
        metadata["graphify"].update({"version": pre.get("graphify", {}).get("version"), "backend": pre.get("graphify", {}).get("backend"), "model": pre.get("graphify", {}).get("model"), "extract_command": "graphify extract <target> --mode deep --out <WORK_DIR>"})
        target_graphify_before = target_graphify_signature(target)
        attempts = graphify_extract(target, work_dir, log)
        target_graphify_after = target_graphify_signature(target)
        if target_graphify_before != target_graphify_after:
            raise RuntimeError("target graphify-out changed during isolated extraction")
        metadata["graphify"]["extract_attempts"] = attempts
        metadata["graphify"]["artifact_paths"] = [
            str(work_dir / "graphify-out" / "graph.json"),
            str(work_dir / "graphify-out" / "GRAPH_REPORT.md"),
        ]
        metadata["graphify"]["target_graphify_out_unchanged"] = True
        post_rc, post = doctor(doctor_script, "post-graph", target, work_dir)
        metadata["graphify"]["post_graph"] = post
        if post_rc:
            raise RuntimeError("doctor post-graph blocked: " + "; ".join(post.get("failures", [])))
        (work_dir / "drafts" / "01-graphify-map.md").write_text(graph_map(work_dir, target), encoding="utf-8")
        sizing = size_report(target)
        context = collect_context(target)
        questions = feature_questions(target, sizing, context)
        (work_dir / "drafts" / "03-plan.md").write_text("# Analysis Plan\n\nAnalysis mode: `standard`.\n\n" + json.dumps(sizing, ensure_ascii=False, indent=2), encoding="utf-8")
        (work_dir / "drafts" / "03-research.md").write_text("# Research Context\n\n" + json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
        (work_dir / "drafts" / "04-questions.md").write_text("# Adaptive Questions\n\n" + "\n".join(f"- {question}" for question in questions) + "\n", encoding="utf-8")
        modules = write_module_plan(work_dir, target, sizing)
        (work_dir / "drafts" / "07-cross-validation.md").write_text(
            "# Cross-Validation\n\n"
            "Graphify relations remain navigation candidates until source paths and line ranges are checked by the Agent. "
            "Source code adjudicates conflicts; unresolved `INFERRED` and `AMBIGUOUS` relations are not conclusions.\n",
            encoding="utf-8",
        )
        (work_dir / "drafts" / "08-coverage.md").write_text(
            "# Coverage Summary\n\n"
            "| Measure | Status | Evidence |\n|---|---|---|\n"
            "| Static source reading | pending Agent module drafts | `06-module-*.md` line tables |\n"
            "| Test coverage | not measured by this workflow | separate test evidence required |\n"
            "| Runtime verification | not measured by this workflow | dynamic trace required |\n",
            encoding="utf-8",
        )
        fuse_report(work_dir, target, metadata, sizing, context, questions, modules)
        metadata["ended_at"] = now()
        metadata["outcome"] = "awaiting-agent-module-analysis"
        metadata["limitations"] = ["Module drafts and final source adjudication remain Agent responsibilities.", "Static reading, tests and runtime validation are not conflated."]
    except Exception as exc:
        metadata["ended_at"] = now()
        metadata["outcome"] = "failed"
        metadata["failure"] = {"class": "configuration-or-execution", "message": str(exc)}
        log.append("FAIL: " + str(exc))
        (work_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (work_dir / "execution-log.md").write_text("# Execution Log\n\n" + "\n\n".join(log) + "\n", encoding="utf-8")
        return 1
    (work_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work_dir / "execution-log.md").write_text("# Execution Log\n\n" + "\n\n".join(log) + "\n", encoding="utf-8")
    (work_dir / "checks.md").write_text(
        "# Run Checks\n\n"
        "| Check | Status | Evidence |\n|---|---|---|\n"
        "| Doctor preflight | PASS | `metadata.json` Graphify preflight payload |\n"
        "| Doctor post-graph | PASS | `metadata.json` Graphify post-graph payload |\n"
        "| Source adjudication | PENDING | `drafts/07-cross-validation.md` |\n"
        "| Module coverage | PENDING | `drafts/08-coverage.md` |\n",
        encoding="utf-8",
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(prog="stark-repo-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze_parser = sub.add_parser("analyze", help="run the bounded V1 orchestration")
    analyze_parser.add_argument("input", help="local path, public URL, or owner/repo")
    analyze_parser.add_argument("--work-dir", required=True, help="writable directory outside target")
    analyze_parser.add_argument("--run-id", default="stark-run")
    analyze_parser.set_defaults(func=analyze)
    finalize_parser = sub.add_parser("finalize", help="fuse verified Agent module drafts into the final report")
    finalize_parser.add_argument("--work-dir", required=True)
    finalize_parser.set_defaults(func=finalize)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
