#!/usr/bin/env python3
"""Agent execution and scheduling for repo-analyzer.

Extracted from repo_analyzer.py (T05).

``extract_section``/``bullet_excerpt``/``table_cell`` have been moved to
``analyzer_common`` to break the circular dependency between this module
and ``analyzer_reports``. This module now imports them at top level.
"""

import argparse
import json
import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import List, Sequence, Tuple

from analyzer_common import (
    _TOKEN_COLLECTOR,
    bullet_excerpt,
    command_kind,
    degrade_agent_mode,
    extract_section,
    module_rows,
    read_text,
    table_cell,
)
from analyzer_coverage import module_file_paths, module_ids_from_plan
from analyzer_crossref import write_cross_ref_review_packet


def agent_base_command(args: argparse.Namespace, output: Path = None) -> List[str]:
    if args.agent_mode == "codex":
        if output is None:
            raise SystemExit("codex agent 需要分析产物输出目录作为工作目录")
        return [
            "codex",
            "exec",
            "--model",
            args.agent_model,
            "-c",
            f'model_reasoning_effort="{args.agent_reasoning_effort}"',
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


def run_agent_task(output: Path, args: argparse.Namespace, run_id: str, prompt: str, performance: dict = None, progress=None) -> Tuple[bool, str, int]:
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
        degraded = False
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
        except OSError as exc:
            # Binary not found, permission denied, or codex crash before producing output.
            returncode = 127
            stdout = ""
            stderr = f"codex 不可用: {exc}"
            # On the first attempt, degrade immediately rather than retrying.
            if attempt == 1 and args.agent_mode == "codex":
                degrade_agent_mode(args, f"OSError: {exc}")
                degraded = True
        except Exception as exc:  # noqa: BLE001 — broad catch for unexpected codex failures
            returncode = 1
            stdout = ""
            stderr = f"codex 运行异常: {exc}"
            if attempt == 1 and args.agent_mode == "codex":
                degrade_agent_mode(args, f"异常: {exc}")
                degraded = True
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
            "agent_model": args.agent_model,
            "agent_reasoning_effort": args.agent_reasoning_effort,
            "timed_out": timed_out,
            "degraded": degraded,
            "timeout_seconds": timeout,
            "timeout_config_seconds": args.agent_timeout_seconds,
            "tokens_in": 0,
            "tokens_out": 0,
            "tokens_total": 0,
        }
        if returncode == 0:
            message = last_message.read_text(encoding="utf-8", errors="replace") if last_message.exists() else stdout
            (run_dir / "result.md").write_text(message, encoding="utf-8")
            # T05：解析 agent 返回文本中的 <!-- TOKENS: in,out --> 标记。
            token_usage = _TOKEN_COLLECTOR.collect_from(message)
            if token_usage is not None:
                metadata["tokens_in"] = token_usage.tokens_in
                metadata["tokens_out"] = token_usage.tokens_out
                metadata["tokens_total"] = token_usage.tokens_in + token_usage.tokens_out
        # 先完成 token 解析再写 metadata.json 并登记 agent_attempts，确保
        # agent_attempts[] 拷贝已含最新 token 字段（命令模式天然记 0，满足 PRD T06）。
        (attempt_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if performance is not None:
            performance.setdefault("agent_attempts", []).append(dict(metadata))
        if progress is not None:
            progress.agent_progress(run_id, attempt, "OK" if returncode == 0 else "FAIL", round(elapsed, 3))
        if returncode == 0:
            return True, message, attempt
        # If we degraded (codex unavailable), stop retrying and return failure.
        # The orchestrator will skip subsequent agent stages since agent_mode is now deterministic.
        if degraded:
            failure = f"agent task failed (codex degraded to deterministic): {stderr}"
            (run_dir / "result.md").write_text(failure + "\n", encoding="utf-8")
            return False, failure, attempt
    failure = f"agent task failed after {args.agent_max_attempts} attempts"
    (run_dir / "result.md").write_text(failure + "\n", encoding="utf-8")
    return False, failure, args.agent_max_attempts


def module_agent_prompt(module_id: str, root: str, tier: str, output: Path, module_files: List[str]) -> str:
    files = "\n".join(f"- {item}" for item in module_files[:80]) or "- 未识别到模块文件"
    return f"""### MODULE {module_id}
- 模块底稿: {output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"}
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
- 模块清单: {output / "data" / "module-ids.yaml"}
- 模块底稿目录: {output / "diagnostics" / "module-drafts"}
- 主要证据切片: `diagnostics/slices/02-backend.xml`、`diagnostics/slices/04-docs.xml`、`diagnostics/slices/06-tests.xml`、`diagnostics/slices/09-dependencies.xml`、`diagnostics/slices/history-hotspot.txt`

## 模块任务
{module_blocks}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成分析产物；只读取上面列出的分析目录文件。
- 不要写入任何文件，不要修改 .stark-repo-analyzer 目录；只在最终回复中返回 Markdown。
- 不要在分析目录根部直接读取源码路径；源码内容来自 `diagnostics/slices/*.xml` 中的 `<file path="...">`。
- 只基于分析目录中的证据判断，不要编造源码事实。
- 补充业务角色、设计思路、关键数据流、模块协同、架构亮点和风险。
- 每个关键判断必须引用已有证据文件路径。
- 每个模块必须按下面格式输出，方便脚本拆分；不得省略任何模块：

<!-- MODULE_RESULT: module_xxx -->
## Agent 深度分析

...该模块分析...
<!-- END_MODULE_RESULT -->
"""


def module_result_blocks(result: str, module_ids: Sequence[str]) -> dict:
    blocks = {}
    pattern = re.compile(r"<!-- MODULE_RESULT:\s*(module_[0-9]+)\s*-->\s*(.*?)\s*<!-- END_MODULE_RESULT -->", re.S)
    for match in pattern.finditer(result):
        blocks[match.group(1)] = match.group(2).strip()
    return blocks


def append_agent_module_analysis(output: Path, module_id: str, result: str, attempts: int, evidence: str = None) -> None:
    draft = output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"
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
- 模块草稿: {output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"}
- 覆盖率报告: {output / "data" / "coverage.md"}
- 缺失符号: {missing}

## 要求
- 不要写入任何文件，不要修改 .stark-repo-analyzer 目录；只在最终回复中返回要追加的 Markdown。
- 只补充对这些缺失符号的解释，不要改源码。
- 每个缺失符号都必须在输出中以原名出现，便于 coverage gate 重新检测。
- 输出 Markdown，包含标题 `## Agent 覆盖率修复`。
"""


def append_agent_coverage_repair(output: Path, module_id: str, result: str, attempts: int) -> None:
    draft = output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"
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
- 模块草稿: {output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"}
- 独立审稿: {output / "diagnostics" / "cross-ref-agent-review.md"}
- 确定性 cross-ref: {output / "diagnostics" / "cross-ref-checks.md"}
- 模块清单: {output / "data" / "module-ids.yaml"}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成分析产物。
- 不要写入任何文件，不要修改 .stark-repo-analyzer 目录；只在最终回复中返回要追加的 Markdown。
- 只补充能消除审稿指出冲突/不一致的说明，不要改源码。
- 输出 Markdown，包含标题 `## Agent Cross-ref 修复`。
"""


def append_agent_cross_ref_repair(output: Path, module_id: str, result: str, attempts: int) -> None:
    draft = output / "diagnostics" / "module-drafts" / f"module-{module_id}.md"
    body = re.sub(r"(?m)^##\s+Agent Cross-ref 修复\s*", "", result.strip(), count=1).strip()
    with draft.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Agent Cross-ref 修复\n\n"
            f"- attempts: {attempts}\n"
            f"- 证据: `agent-runs/cross-ref-repair-{module_id}/result.md`\n\n"
            f"{body}\n"
            "\n"
        )


def repair_cross_ref_modules(output: Path, args: argparse.Namespace, module_ids: Sequence[str], review: str, summary: dict, performance: dict, progress=None) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    targets = cross_ref_repair_modules(review, module_ids)
    if not targets:
        return []
    issues = []
    repairs = summary.setdefault("cross_ref_repairs", {})
    for module_id in targets:
        ok, result, attempts = run_agent_task(output, args, f"cross-ref-repair-{module_id}", cross_ref_repair_prompt(module_id, output), performance, progress)
        repairs[module_id] = {"status": "PASS" if ok else "FAIL", "attempts": attempts}
        if ok:
            append_agent_cross_ref_repair(output, module_id, result, attempts)
        else:
            issues.append(f"{module_id}: cross-ref 修复 agent 失败")
    return issues


def repair_failed_coverage_modules(output: Path, args: argparse.Namespace, coverage: dict, summary: dict, performance: dict, progress=None) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    issues = []
    repairs = summary.setdefault("repairs", {})
    for module_id, module in coverage["modules"].items():
        if module["status"] == "PASS":
            continue
        ok, result, attempts = run_agent_task(output, args, f"repair-{module_id}", coverage_repair_prompt(module_id, module, output), performance, progress)
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
    (output / "data").mkdir(parents=True, exist_ok=True)
    summary["status"] = "PASS" if not issues and not agent_summary_has_failure(summary) else "FAIL"
    (output / "data" / "agent-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def codex_cross_ref_skip_reason(output: Path, run_id: str) -> str:
    if run_id != "cross-ref-review":
        return ""
    module_ids = module_ids_from_plan(output)
    cross_ref = read_text(output / "diagnostics" / "cross-ref-checks.md", 100_000)
    if len(module_ids) <= 1 and "状态: PASS" in cross_ref:
        return "single module and deterministic cross-ref already PASS"
    return ""


def init_agent_summary(output: Path, args: argparse.Namespace) -> Tuple[List[str], dict]:
    summary = {"mode": args.agent_mode, "max_attempts": args.agent_max_attempts, "modules": {}, "cross_ref": {}}
    if args.agent_mode == "deterministic":
        summary["status"] = "SKIPPED"
        (output / "data").mkdir(parents=True, exist_ok=True)
        (output / "data" / "agent-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [], summary


def run_module_agent_loop(output: Path, args: argparse.Namespace, files: List[Path], repo: Path, summary: dict, performance: dict, progress=None) -> List[str]:
    if args.agent_mode == "deterministic":
        return []
    issues = []
    modules = []
    for index, (module_id, root, _count) in enumerate(module_rows(files, repo), 1):
        tier = "core" if index <= 3 else "minor"
        module_files = module_file_paths(files, repo, root)
        modules.append((module_id, root, tier, module_files))
    ok, result, attempts = run_agent_task(output, args, "modules-batch", modules_batch_agent_prompt(output, modules), performance, progress)
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


def cross_ref_agent_prompt(output: Path) -> str:
    packet = write_cross_ref_review_packet(output)
    return f"""你是一位独立审稿 agent，只读不写源码，请审查分析目录中的模块草稿一致性。

## 输入
- 分析目录: {output}
- 审稿包: {output / "diagnostics" / "cross-ref-review-input.md"}

## 审稿包
{packet}

## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成分析产物；优先只使用上方审稿包。
- 不要写入任何文件，不要修改 .stark-repo-analyzer 目录；只在最终回复中返回 Markdown。
- 检查模块命名、引用、职责边界、重复定义、跨模块协同是否矛盾。
- 如果发现问题，逐条给出证据路径和建议回退模块。
- 如果需要回退模块，必须单独输出一行 `建议回退模块: module_xxx`；没有需要回退的模块时输出 `建议回退模块: 无`。
- 如果未发现问题，也要说明抽查范围。
- 输出 Markdown，包含标题 `## Agent Cross-ref 审稿`。
"""


def run_cross_ref_agent(output: Path, args: argparse.Namespace, summary: dict, performance: dict, run_id: str = "cross-ref-review", progress=None) -> Tuple[List[str], str]:
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
        review_path = output / "diagnostics" / "cross-ref-agent-review.md"
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(result, encoding="utf-8")
        write_agent_summary(output, summary, [])
        return [], result
    issues = []
    ok, result, attempts = run_agent_task(output, args, run_id, cross_ref_agent_prompt(output), performance, progress)
    summary["cross_ref"] = {"status": "PASS" if ok else "FAIL", "attempts": attempts}
    review_path = output / "diagnostics" / "cross-ref-agent-review.md"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(result.strip() + "\n", encoding="utf-8")
    if not ok:
        issues.append("cross-ref-review: agent 审稿失败")
    write_agent_summary(output, summary, issues)
    return issues, result


def agent_insights(output: Path) -> dict:
    try:
        summary = json.loads((output / "data" / "agent-summary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        summary = {}
    mode = summary.get("mode", "deterministic")
    status = summary.get("status", "UNKNOWN")
    modules = []
    for draft in sorted((output / "diagnostics" / "module-drafts").glob("module-*.md")):
        module_id = draft.stem.replace("module-", "", 1)
        section = extract_section(read_text(draft, 500_000), "Agent 深度分析")
        if not section:
            continue
        evidence = sorted(set(re.findall(r"`?((?:agent-runs|diagnostics|data)/[^`\s，,。)]+)`?", section)))
        excerpts = bullet_excerpt(section)
        modules.append(
            {
                "id": module_id,
                "status": summary.get("modules", {}).get(module_id, {}).get("status", "UNKNOWN"),
                "summary": "；".join(excerpts[:2]) if excerpts else "已完成 agent 深度分析，详见模块草稿。",
                "evidence": evidence[:4] or [f"diagnostics/module-drafts/{draft.name}"],
                "draft": f"diagnostics/module-drafts/{draft.name}",
            }
        )
    enabled = mode != "deterministic" and status == "PASS" and bool(modules)
    if not enabled:
        return {
            "enabled": False,
            "mode": mode,
            "status": status,
            "modules": modules,
            "summary_markdown": "",
            "business_markdown": "",
            "learning_markdown": "",
            "tech_lead_completion_line": "当前报告已完成确定性扫描、动态切片、模块候选、对外工具/API 表面和复现入口；需要主观评价的部分可交给后续 subagent 深化。",
            "architecture_assessment_line": "当前版本完成了不依赖 LLM 的确定性分析：类型识别、文件切片、模块候选、对外工具/API 表面、依赖基线、运行命令候选和报告索引。设计优点是可重放、低依赖、证据可追到文件与行号；限制是业务价值排序和架构优劣判断仍属于主观分析，建议由后续 subagent 基于这些底料继续深化。",
            "business_risk_line": "当前报告能确认文件、manifest、工具名和运行入口；市场定位、用户留存和真实搜索质量仍需要人工或 subagent 评审。",
        }

    rows = "\n".join(
        f"| {item['id']} | {item['status']} | {table_cell(item['summary'])} | {', '.join(f'`{ref}`' for ref in item['evidence'])} |"
        for item in modules
    )
    summary_markdown = "\n".join(
        [
            "## Agent 深度分析摘要",
            "",
            f"- agent 模式: {mode}",
            f"- agent 状态: {status}",
            "",
            "| 模块 | 状态 | agent 结论摘要 | 证据 |",
            "|---|---|---|---|",
            rows,
        ]
    )
    business_rows = "\n".join(f"- `{item['id']}`: {item['summary']} 证据: {', '.join(f'`{ref}`' for ref in item['evidence'])}" for item in modules)
    learning_rows = "\n".join(f"{index}. 读 `{item['draft']}` 的 `Agent 深度分析`：{item['summary']}" for index, item in enumerate(modules, 1))
    return {
        "enabled": True,
        "mode": mode,
        "status": status,
        "modules": modules,
        "summary_markdown": summary_markdown,
        "business_markdown": "## Agent insight 摘要\n" + business_rows,
        "learning_markdown": "## Agent insight 学习线索\n" + learning_rows,
        "tech_lead_completion_line": "当前报告已完成确定性扫描、动态切片、模块候选、对外工具/API 表面、复现入口和 agent 模块深度分析；agent 结论已汇入下方摘要。",
        "architecture_assessment_line": "当前版本先用确定性扫描建立可追溯底料，再在 agent 模式下补充业务角色、设计思路、协同关系和风险判断。最终报告已把模块级 agent 结论合并为可复查摘要，关键判断可回到模块草稿和 agent-run 结果核对。",
            "business_risk_line": "agent 已对模块业务角色和风险做深度分析；业务侧应优先复核下方 insight 摘要中的核心模块证据，再决定市场定位、留存和搜索质量等外部验证。",
    }
