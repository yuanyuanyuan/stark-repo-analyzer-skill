#!/usr/bin/env python3
"""Module plan and drafts for repo-analyzer.

Extracted from repo_analyzer.py (T04).

``module_rows`` has been moved to ``analyzer_common`` to break the circular
dependency between this module and ``analyzer_coverage``. Both modules now
import it from common, and this module can safely use a top-level import
of ``source_symbols``/``mcp_tool_names``/``module_file_paths`` from coverage.
"""

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from analyzer_common import module_rows, read_text, rel
from analyzer_coverage import source_symbols, mcp_tool_names, module_file_paths


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
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "data" / "module-ids.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def write_module_drafts(repo: Path, output: Path, files: List[Path]) -> None:
    drafts = output / "diagnostics" / "module-drafts"
    drafts.mkdir(parents=True, exist_ok=True)
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
        (drafts / f"module-{module_id}.md").write_text(
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
- 模块 ID 来源：`data/module-ids.yaml`
- 代码切片：`diagnostics/slices/02-backend.xml`
- 依赖切片：`diagnostics/slices/09-dependencies.xml`
- 历史热点：`diagnostics/slices/history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| {root} | {count} | deterministic deep scan |
""",
            encoding="utf-8",
        )
