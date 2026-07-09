#!/usr/bin/env python3
"""Deterministic repo-analyzer entrypoint.

Slimmed down from 2746 lines to < 200 lines (T05).
All logic extracted to analyzer_* modules; this file is pure orchestration.
"""

import argparse
import time
from pathlib import Path
from typing import Sequence

from analyzer_common import (
    _TOKEN_COLLECTOR, init_performance, prepare_output, rel,
    ProgressReporter, LogWriter, module_rows,
)
from analyzer_config import apply_config, save_last_session
from analyzer_checkout import checkout_target, iter_files, parse_project_name, detect_repo_type
from analyzer_common import _LOADER
from analyzer_slicing import write_slices
from analyzer_metadata import write_meta, write_repo_type, write_manifest_card, write_question_answers, write_research
from analyzer_modules import write_module_plan, write_module_drafts
from analyzer_coverage import write_coverage, mcp_tool_names, API_SURFACE_LIMIT
from analyzer_crossref import write_cross_ref
from analyzer_agent import (
    init_agent_summary, run_module_agent_loop, run_cross_ref_agent,
    repair_failed_coverage_modules, repair_cross_ref_modules, write_agent_summary,
    run_agent_task, append_agent_cross_ref_repair, cross_ref_repair_modules,
)
from analyzer_reports import write_reports, write_readme, report_data
from analyzer_reporting import write_config_effective, write_mcp_tools, write_sla_report, write_performance_report, write_state_report
from analyzer_acceptance import write_acceptance
from analyzer_preflight import preflight_check, count_stages


def analyze(args: argparse.Namespace) -> Path:
    args = apply_config(args)
    preflight_check(args)
    started_at = time.monotonic()
    performance = init_performance()
    _TOKEN_COLLECTOR.reset()
    progress = ProgressReporter(performance, count_stages(args))
    output = Path(args.output).expanduser().resolve()
    progress._log = LogWriter(output)
    with progress.stage("checkout-target"):
        repo, source, temp = checkout_target(args.target)
    try:
        with progress.stage("prepare-output"):
            prepare_output(output, args.resume)
            for subdir in ("reports", "data", "diagnostics", "diagnostics/module-drafts", "diagnostics/slices", "logs", "acceptance", "agent-runs"):
                (output / subdir).mkdir(parents=True, exist_ok=True)
        with progress.stage("scan-files"):
            files = sorted(iter_files(repo), key=lambda path: rel(path, repo))
        with progress.stage("classify-repo"):
            project_name = parse_project_name(repo)
            repo_type = detect_repo_type(repo, files)
            dimensions = _LOADER.load(repo_type)
        with progress.stage("write-meta"):
            write_meta(repo, output, source, files)
            write_repo_type(output, repo_type, project_name, dimensions)
            write_manifest_card(repo, output, source, project_name, repo_type, files)
            write_question_answers(output, args.no_question, args.mode)
        with progress.stage("repomix-slices"):
            write_slices(repo, output, repo_type, files)
        with progress.stage("module-drafts"):
            write_module_plan(repo, output, files)
            write_module_drafts(repo, output, files)
        with progress.stage("cross-ref-deterministic-initial"):
            cross_ref_issues = write_cross_ref(output)
        with progress.stage("agent-init"):
            agent_issues, agent_summary = init_agent_summary(output, args)
        with progress.stage("agent-modules-batch"):
            agent_issues.extend(run_module_agent_loop(output, args, files, repo, agent_summary, performance, progress))
        with progress.stage("cross-ref-deterministic-after-agent"):
            cross_ref_issues = write_cross_ref(output)
        with progress.stage("coverage-initial"):
            coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
        if args.agent_mode != "deterministic" and any(item["status"] != "PASS" for item in coverage["modules"].values()):
            progress.add_stages(4)
            with progress.stage("agent-coverage-repair"):
                agent_issues.extend(repair_failed_coverage_modules(output, args, coverage, agent_summary, performance, progress))
            with progress.stage("cross-ref-deterministic-after-coverage-repair"):
                cross_ref_issues = write_cross_ref(output)
            with progress.stage("coverage-after-repair"):
                coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
            with progress.stage("agent-summary-after-coverage-repair"):
                write_agent_summary(output, agent_summary, agent_issues)
        with progress.stage("agent-cross-ref-review"):
            review_issues, review_text = run_cross_ref_agent(output, args, agent_summary, performance, progress=progress)
        agent_issues.extend(review_issues)
        if args.agent_mode != "deterministic":
            module_ids = [module_id for module_id, _root, _count in module_rows(files, repo)]
            repair_targets = cross_ref_repair_modules(review_text, module_ids)
            if repair_targets:
                progress.add_stages(3)
            with progress.stage("agent-cross-ref-repair"):
                repair_issues = repair_cross_ref_modules(output, args, module_ids, review_text, agent_summary, performance, progress)
            if repair_issues or agent_summary.get("cross_ref_repairs"):
                agent_issues.extend(repair_issues)
                with progress.stage("cross-ref-deterministic-after-cross-ref-repair"):
                    cross_ref_issues = write_cross_ref(output)
                with progress.stage("coverage-after-cross-ref-repair"):
                    coverage = write_coverage(output, files, repo, args.target_coverage_core, args.target_coverage_minor, args.coverage_engine)
                with progress.stage("agent-cross-ref-review-final"):
                    review_issues, _review_text = run_cross_ref_agent(output, args, agent_summary, performance, "cross-ref-review-final", progress)
                agent_issues.extend(review_issues)
        with progress.stage("state-report"):
            failed_modules = write_state_report(output, coverage, cross_ref_issues, agent_issues)
        research_section = ""
        if args.research:
            with progress.stage("external-research"):
                research_section = write_research(output, args.offline)
        with progress.stage("render-reports"):
            write_reports(repo, output, source, project_name, repo_type, files, args.mode, failed_modules, research_section)
        with progress.stage("write-index-and-config"):
            write_readme(output, project_name, repo_type, args.mode)
            write_config_effective(output, args)
            write_mcp_tools(output, mcp_tool_names(repo, files, API_SURFACE_LIMIT))
        with progress.stage("sla-report"):
            write_sla_report(output, args, started_at, coverage, cross_ref_issues, agent_issues)
        with progress.stage("performance-report"):
            write_performance_report(output, args, started_at, performance)
        with progress.stage("acceptance-script"):
            write_acceptance(output)
        if args.save_pref:
            with progress.stage("save-last-session"):
                save_last_session(args)
        progress.summary(time.monotonic() - started_at)
        return output
    finally:
        temp.cleanup()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="分析一个 git 仓库并生成分析产物。")
    parser.add_argument("target", help="本地仓库路径或 git URL")
    parser.add_argument("--output", default=".stark-repo-analyzer", help="分析产物目录")
    parser.add_argument("--mode", choices=["tech-lead", "business", "learning", "all"], default="tech-lead")
    parser.add_argument("--no-question", action="store_true", help="跳过交互问题，使用默认值")
    parser.add_argument("--offline", action="store_true", help="离线模式；不访问 Web（外部调研阶段将 SKIP）")
    parser.add_argument("--research", action="store_true", help="启用外部调研阶段（T07）；默认关闭，离线环境自动 SKIP")
    parser.add_argument("--config", default="", help="JSON 配置文件路径，支持 mode/no_question/coverage/SLA 默认值")
    parser.add_argument("--resume", action="store_true", help="复用输出目录，清理本工具生成文件但保留用户手写文件")
    parser.add_argument("--target-coverage-core", type=float, default=None, help="核心模块符号覆盖率阈值")
    parser.add_argument("--target-coverage-minor", type=float, default=None, help="次要模块符号覆盖率阈值")
    parser.add_argument("--coverage-engine", choices=["auto", "regex"], default="auto", help="覆盖率符号引擎；auto 会在可用时记录 tree-sitter parse 结果")
    parser.add_argument("--sla-minutes", type=float, default=None, help="本次分析 SLA 分钟预算")
    parser.add_argument("--agent-mode", choices=["deterministic", "codex", "command"], default="codex", help="判断型模块分析模式；codex/command 会执行外部 agent；codex 不可用时自动降级 deterministic")
    parser.add_argument("--agent-command", default="", help="--agent-mode command 时使用的命令，prompt 通过 stdin 传入")
    parser.add_argument("--agent-model", default="", help="--agent-mode codex 时传给 codex exec 的模型，默认 5.4")
    parser.add_argument("--agent-reasoning-effort", default="", help="--agent-mode codex 时传给 codex exec 的推理级别，默认 medium")
    parser.add_argument("--agent-max-attempts", type=int, default=None, help="agent 失败重试次数，默认 3")
    parser.add_argument("--agent-timeout-seconds", type=int, default=None, help="agent 子进程超时秒数；0 表示不启用，默认 0")
    parser.add_argument("--use-last-pref", action="store_true", help="读取配置目录中的 last-session.json 作为默认偏好")
    parser.add_argument("--save-pref", action="store_true", help="运行成功后保存本次非敏感偏好到 last-session.json")
    return parser


def _ensure_gitignore(output: Path) -> bool:
    """REQ-01: Ensure the output directory is git-ignored in the parent repo.

    If the parent directory is a git repo (has ``.git``) and its ``.gitignore``
    does not already list the output directory, append the entry. Returns True
    if a new entry was added (or ``.gitignore`` was created).
    """
    parent = output.parent
    if not (parent / ".git").exists():
        return False
    entry = output.name + "/"
    gitignore = parent / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.strip() == entry or line.strip() == output.name:
                return False
        gitignore.write_text(content.rstrip() + "\n" + entry + "\n", encoding="utf-8")
        return True
    gitignore.write_text(entry + "\n", encoding="utf-8")
    return True


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    output = analyze(args)
    print(f"分析完成: {output}")
    gitignore_updated = _ensure_gitignore(output)
    if gitignore_updated:
        print(f"提示：产物已输出到 {output.name}/，已自动追加到 .gitignore")
    else:
        print(f"提示：产物已输出到 {output.name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
