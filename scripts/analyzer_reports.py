#!/usr/bin/env python3
"""Report rendering and index for repo-analyzer.

Extracted from repo_analyzer.py (T05).
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from analyzer_common import (
    _LOADER,
    API_SURFACE_LIMIT,
    RENDERER,
    bullet_excerpt,
    extract_section,
    module_rows,
    read_text,
    rel,
    table_cell,
)
from analyzer_checkout import language_counts, readme_summary
from analyzer_metadata import manifest_snippets, command_hints, top_tree
from analyzer_coverage import source_symbols, mcp_tool_names
from analyzer_agent import agent_insights


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
- 证据入口：先读 `data/manifest-card.md` 和 `reports/ANALYSIS_REPORT.business.md`，再按需查看 `diagnostics/slices/04-docs.xml`。

### 业务验证动作
{command_lines}
"""
    if mode == "learning":
        first_module = largest[0]
        return f"""## 6. 学习路径
1. 先读 `reports/README.md` 和 `data/manifest-card.md`，建立项目用途、语言和入口的第一印象。
2. 再读 `data/module-ids.yaml`，把 `{first_module}` 作为第一批学习对象。
3. 接着打开 `diagnostics/module-drafts/module-{first_module}.md`，只看关键符号和 MCP 工具/API 表面。
4. 最后用 `diagnostics/slices/04-docs.xml` 对照文档，用 `diagnostics/slices/02-backend.xml` 对照实现。

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

> 本章由 `reports/STATE_REPORT.md` 中 `failed_modules` 生成；只在存在失败模块时渲染。

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
    slice_names = [filename for filename, _label, _patterns in _LOADER.load(repo_type)] + ["history-hotspot.txt"]
    slice_links = "\n".join(f"- `diagnostics/slices/{name}`" for name in slice_names)
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
- 项目名片：`data/manifest-card.md`
- 主技术报告：`reports/ANALYSIS_REPORT.tech-lead.md`
- 文档切片：`diagnostics/slices/04-docs.xml`
- 依赖切片：`diagnostics/slices/09-dependencies.xml`
- 状态报告：`reports/STATE_REPORT.md`
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
- 你先把它理解成"文档说明能力、manifest 说明安装方式、源码说明真实入口"的三层结构。

## 1. 阅读顺序
1. 打开 `data/manifest-card.md`，只看项目名、文件数、README 前 30 行。
2. 打开 `data/module-ids.yaml`，找到第一个模块 `{first_module}`。
3. 打开 `diagnostics/module-drafts/module-{first_module}.md`，看关键符号和工具/API 表面。
4. 打开 `diagnostics/slices/02-backend.xml`，对照源码里的入口。
5. 最后看 `reports/ANALYSIS_REPORT.tech-lead.md`，把技术判断补齐。

## 2. 本仓库的第一批观察
- README 标题：{readme_title}
- 第一个关键符号：`{first_symbol}`
- 第一个对外工具/API：`{first_tool}`
- 运行命令候选：
{commands}

## 3. 练习题
- 解释 `{first_module}` 为什么被排在模块清单第一位。
- 找到 `{first_tool}` 在源码中的文件和行号。
- 说明 `diagnostics/slices/04-docs.xml` 和 `diagnostics/slices/02-backend.xml` 分别适合回答什么问题。

{audience}

## 7. 证据索引
- 学习入口：`data/manifest-card.md`
- 模块清单：`data/module-ids.yaml`
- 模块草稿：`diagnostics/module-drafts/module-{first_module}.md`
- 代码切片：`diagnostics/slices/02-backend.xml`
- 文档切片：`diagnostics/slices/04-docs.xml`
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
依赖线索见 `diagnostics/slices/09-dependencies.xml`。当前扫描未引入外部依赖解析库，只保留原始 manifest 作为后续判断证据。

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
python3 scripts/repo_analyzer.py {source} --output .stark-repo-analyzer --no-question
```

## 9. 附录
- 类型识别：`data/repo-type.yaml`
- 项目名片：`data/manifest-card.md`
- 覆盖率门控：`data/coverage.md`
- 状态报告：`reports/STATE_REPORT.md`
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
    slice_names = [filename for filename, _label, _patterns in _LOADER.load(repo_type)] + ["history-hotspot.txt"]
    slice_links = "\n".join(f"- `diagnostics/slices/{name}`" for name in slice_names)
    return f"""# {project_name} 分析总览

> 元信息：目标 `{source}`；Repo 类型 `{repo_type}`；报告由确定性 repo-analyzer CLI 生成。

## 0. 读者导航
- 技术负责人：读 `reports/ANALYSIS_REPORT.tech-lead.md`
- 业务负责人：读 `reports/ANALYSIS_REPORT.business.md`
- 学习者：读 `reports/ANALYSIS_REPORT.learning.md`
- 复查证据：读 `data/manifest-card.md`、`data/module-ids.yaml`、`data/coverage.md`、`reports/STATE_REPORT.md`

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
python3 scripts/repo_analyzer.py {source} --output .stark-repo-analyzer --mode all --no-question
```
{failed_section}
"""


def report_data(project_name: str, source: str, repo_type: str, files: List[Path], repo: Path, output: Path, failed_modules: List[dict], research_section: str = "") -> dict:
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
    slice_names = [filename for filename, _label, _patterns in _LOADER.load(repo_type)] + ["history-hotspot.txt"]
    slice_links = "\n".join(f"- `diagnostics/slices/{name}`" for name in slice_names)
    largest = modules[0] if modules else ("module_001", "[root]", len(files))
    first_module = largest[0]
    first_tool = tools[0][0] if tools else "未识别"
    first_symbol = symbols[0][0] if symbols else "未识别"
    insights = agent_insights(output)
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
        "agent_summary": {
            "mode": insights["mode"],
            "status": insights["status"],
            "modules": insights["modules"],
        },
        "agent_insight_summary": insights["summary_markdown"],
        "agent_business_insights": insights["business_markdown"],
        "agent_learning_insights": insights["learning_markdown"],
        "tech_lead_completion_line": insights["tech_lead_completion_line"],
        "architecture_assessment_line": insights["architecture_assessment_line"],
        "business_risk_line": insights["business_risk_line"],
        "research_section": research_section,
    }
    data["audiences"] = {
        mode: {"audience_section": audience_section(mode, repo_type, files, command_list, modules, tools)}
        for mode in ("tech-lead", "business", "learning")
    }
    return data


def write_reports(repo: Path, output: Path, source: str, project_name: str, repo_type: str, files: List[Path], mode: str, failed_modules: List[dict], research_section: str = "") -> None:
    data = report_data(project_name, source, repo_type, files, repo, output, failed_modules, research_section)
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "reports").mkdir(parents=True, exist_ok=True)
    (output / "data" / "report-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rendered = subprocess.run(
        [sys.executable, str(RENDERER), "--template", mode, "--data", str(output / "data"), "--output-dir", str(output / "reports")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if rendered.returncode != 0:
        raise SystemExit(rendered.stderr.strip() or rendered.stdout.strip() or "render_report.py failed")


def write_readme(output: Path, project_name: str, repo_type: str, mode: str) -> None:
    reports_dir = output / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_files = sorted(path.name for path in reports_dir.glob("ANALYSIS_REPORT*.md"))
    links = "\n".join(f"- [{name}]({name})" for name in report_files)
    (output / "reports" / "README.md").write_text(
        f"""# {project_name} 分析索引

提示：本 skill 与 `graphify` 子项目解耦，索引不共享。如需共享请在 shell 层串联。

- Repo 类型: {repo_type}
- 报告模式: {mode}

## 报告
{links}

## 关键产物
- [meta.txt](../data/meta.txt)
- [repo-type.yaml](../data/repo-type.yaml)
- [manifest-card.md](../data/manifest-card.md)
- [module-ids.yaml](../data/module-ids.yaml)
- [cross-ref-checks.md](../diagnostics/cross-ref-checks.md)
- [coverage.md](../data/coverage.md)
- [coverage-symbols.json](../data/coverage-symbols.json)
- [STATE_REPORT.md](STATE_REPORT.md)
- [SLA_REPORT.md](SLA_REPORT.md)
- [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
- [config-effective.json](../data/config-effective.json)
- [report-data.json](../data/report-data.json)
- [agent-summary.json](../data/agent-summary.json)
- [slices/](../diagnostics/slices/)
""",
        encoding="utf-8",
    )
