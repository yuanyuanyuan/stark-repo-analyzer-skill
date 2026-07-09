#!/usr/bin/env python3
"""SLA / performance / state / config reports for repo-analyzer.

Extracted from repo_analyzer.py (T05).
"""

import argparse
import json
import time
from pathlib import Path
from typing import List

from analyzer_common import _TOKEN_COLLECTOR
from analyzer_coverage import failed_module_records
from analyzer_config import config_home
from token_reporter import TOKEN_BUDGET, TOKEN_BUDGET_MODE, token_status


def write_state_report(output: Path, coverage: dict, cross_ref_issues: List[str], agent_issues: List[str]) -> List[dict]:
    failed_modules = failed_module_records(coverage)
    (output / "reports").mkdir(parents=True, exist_ok=True)
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
    (output / "reports" / "STATE_REPORT.md").write_text(
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


def write_config_effective(output: Path, args: argparse.Namespace) -> None:
    (output / "data").mkdir(parents=True, exist_ok=True)
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
        "agent_mode_degraded": getattr(args, "_agent_mode_degraded", False),
        "agent_command": args.agent_command,
        "agent_model": args.agent_model,
        "agent_reasoning_effort": args.agent_reasoning_effort,
        "agent_max_attempts": args.agent_max_attempts,
        "agent_timeout_seconds": args.agent_timeout_seconds,
        "config": args.config or str(config_home() / "defaults.yaml"),
        "config_home": str(config_home()),
        # T06：Token 预算与实测用量（ADR-0004 Q2：预算 500K，命令模式=0 显式声明）。
        "token_budget": TOKEN_BUDGET,
        "token_budget_mode": TOKEN_BUDGET_MODE,
        "tokens_in": _TOKEN_COLLECTOR.total_in,
        "tokens_out": _TOKEN_COLLECTOR.total_out,
        "tokens_total": _TOKEN_COLLECTOR.total,
        "token_status": token_status(_TOKEN_COLLECTOR.total),
    }
    (output / "data" / "config-effective.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_mcp_tools(output: Path, tools: List[tuple]) -> None:
    (output / "data").mkdir(parents=True, exist_ok=True)
    data = [{"name": name, "file": file_path, "line": line} for name, file_path, line in tools]
    (output / "data" / "mcp-tools.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_sla_report(output: Path, args: argparse.Namespace, started_at: float, coverage: dict, cross_ref_issues: List[str], agent_issues: List[str]) -> None:
    (output / "reports").mkdir(parents=True, exist_ok=True)
    elapsed_seconds = time.monotonic() - started_at
    failed = [module_id for module_id, item in coverage["modules"].items() if item["status"] != "PASS"]
    status = "PASS" if elapsed_seconds <= args.sla_minutes * 60 and not failed and not cross_ref_issues and not agent_issues else "FAIL"
    (output / "reports" / "SLA_REPORT.md").write_text(
        f"""# SLA 报告

- status: {status}
- budget_minutes: {args.sla_minutes:.2f}
- elapsed_seconds: {elapsed_seconds:.2f}
- resumed: {str(bool(args.resume)).lower()}
- agent_model: {args.agent_model}
- agent_reasoning_effort: {args.agent_reasoning_effort}
- agent_timeout: {"disabled" if args.agent_timeout_seconds <= 0 else "enabled"}
- agent_timeout_seconds: {args.agent_timeout_seconds}
- failed_modules: {len(failed)}
- cross_ref_issues: {len(cross_ref_issues)}
- agent_issues: {len(agent_issues)}
- token_budget: {TOKEN_BUDGET}
- token_usage_total: {_TOKEN_COLLECTOR.total}
- token_status: {token_status(_TOKEN_COLLECTOR.total)}
""",
        encoding="utf-8",
    )


def write_performance_report(output: Path, args: argparse.Namespace, started_at: float, performance: dict) -> None:
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "reports").mkdir(parents=True, exist_ok=True)
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
        # T06：Token 用量汇总（ADR-0004 Q2：预算 500K，命令模式=0）。
        "token_budget": TOKEN_BUDGET,
        "token_budget_mode": TOKEN_BUDGET_MODE,
        "token_usage_in": _TOKEN_COLLECTOR.total_in,
        "token_usage_out": _TOKEN_COLLECTOR.total_out,
        "token_usage_total": _TOKEN_COLLECTOR.total,
        "token_status": token_status(_TOKEN_COLLECTOR.total),
    }
    (output / "data" / "performance-report.json").write_text(json.dumps(performance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    (output / "reports" / "PERFORMANCE_REPORT.md").write_text(
        f"""# 性能诊断报告

> **定位**：本报告是 **事后诊断工具**，不是实时监控面板。它在分析完成后生成，
> 用于回答「这次分析为什么慢」「时间花在了哪里」「agent 子进程成本占比多少」。
> 如果你只需要判断分析是否通过 SLA，请阅读 `reports/SLA_REPORT.md`；
> 如果需要查看产物完整性和覆盖率，请阅读 `reports/STATE_REPORT.md`。

## 如何阅读本报告

1. **先看慢因结论** — 它给出本次分析的主瓶颈定位（agent 子进程 vs repomix/tree-sitter vs 文件规模）。
2. **阶段耗时 Top20** — 按 elapsed 降序排列；如果某阶段远超其他阶段，即为瓶颈。
3. **Agent attempt 耗时 Top20** — 如果 agent_mode 是 codex/command，这里列出每次 agent 调用的耗时、是否超时、工作目录。
4. **Token 用量** — 对比 token_budget 判断是否超预算；command 模式天然记 0，codex 模式从 `<!-- TOKENS: in,out -->` 标记解析。

## 指标

- total_elapsed_seconds: {total_elapsed:.3f}
- agent_mode: {args.agent_mode}
- agent_model: {args.agent_model}
- agent_reasoning_effort: {args.agent_reasoning_effort}
- agent_attempt_count: {len(attempts)}
- agent_total_elapsed_seconds: {agent_total:.3f}
- agent_timeout: {"disabled" if timeout_disabled else "enabled"}
- agent_timeout_seconds: {args.agent_timeout_seconds}
- slowest_stage: {slowest_stage}
- slowest_agent_run_id: {slowest_agent}
- token_budget: {TOKEN_BUDGET}
- token_usage_in: {_TOKEN_COLLECTOR.total_in}
- token_usage_out: {_TOKEN_COLLECTOR.total_out}
- token_usage_total: {_TOKEN_COLLECTOR.total}
- token_status: {token_status(_TOKEN_COLLECTOR.total)}

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
