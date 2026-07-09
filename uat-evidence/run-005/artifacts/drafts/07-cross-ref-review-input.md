# Cross-ref 审稿包

## 模块清单
```yaml
modules:
  - id: module_001
    name: skills
    tier: core
    storyline_position: 1
    file_count: 10
  - id: module_002
    name: tests
    tier: core
    storyline_position: 2
    file_count: 10
  - id: module_003
    name: [root]
    tier: core
    storyline_position: 3
    file_count: 9
  - id: module_004
    name: .claude-plugin
    tier: minor
    storyline_position: 4
    file_count: 2
  - id: module_005
    name: hooks
    tier: minor
    storyline_position: 5
    file_count: 2
  - id: module_006
    name: .agents
    tier: minor
    storyline_position: 6
    file_count: 1
  - id: module_007
    name: .codex-plugin
    tier: minor
    storyline_position: 7
    file_count: 1
  - id: module_008
    name: .github
    tier: minor
    storyline_position: 8
    file_count: 1

```

## 确定性 cross-ref
```text
# Cross-ref 校验

- 状态: PASS
- 模块数: 8

## 检查项
- 模块草稿标题必须匹配 `05-module-ids.yaml` 中的 ID。
- `[[module_xxx]]` 引用必须能解析到模块清单。
- 单个模块草稿不应出现重复二级章节。

## 问题
- 未发现断裂引用或重复章节。

```

## 覆盖率摘要
```text
# 覆盖率门控

- 状态: PASS
- 核心阈值: 0.80
- 次要阈值: 0.20
- engine: regex-fallback
- tree_sitter_available: false
- tree_sitter_parsed_files: 0
- tree_sitter_queried_files: 0
- tree_sitter_query_symbols: 0
- skipped_large_files: 0

| 模块 ID | tier | 文件数 | 符号覆盖率 | 覆盖状态 |
|---|---|---:|---:|---|
| module_001 | core | 10 | 1.00 | PASS |
| module_002 | core | 10 | 1.00 | PASS |
| module_003 | core | 9 | 1.00 | PASS |
| module_004 | minor | 2 | 1.00 | PASS |
| module_005 | minor | 2 | 1.00 | PASS |
| module_006 | minor | 1 | 1.00 | PASS |
| module_007 | minor | 1 | 1.00 | PASS |
| module_008 | minor | 1 | 1.00 | PASS |

> 覆盖率门控已用确定性符号提取核对模块草稿；tree-sitter 可用时先做串行 parse 与大文件保护记录，业务语义评价可由后续 subagent 复核。

```

## 模块草稿结构
### 06-module-module_001.md
- title: module_001 skills
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_001
- signal_lines:
  - - 模块边界：`skills` 路径组，共 10 个文件。
  - - 分析优先级：核心模块，必须优先核对入口、测试和对外 API。

### 06-module-module_002.md
- title: module_002 tests
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_002
- signal_lines:
  - - 模块边界：`tests` 路径组，共 10 个文件。
  - - 分析优先级：核心模块，必须优先核对入口、测试和对外 API。

### 06-module-module_003.md
- title: module_003 [root]
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_003
- signal_lines:
  - - 模块边界：`[root]` 路径组，共 9 个文件。
  - - 分析优先级：核心模块，必须优先核对入口、测试和对外 API。

### 06-module-module_004.md
- title: module_004 .claude-plugin
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_004
- signal_lines:
  - - 模块边界：`.claude-plugin` 路径组，共 2 个文件。
  - - 分析优先级：次要模块，先轻量确认依赖和辅助职责。

### 06-module-module_005.md
- title: module_005 hooks
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_005
- signal_lines:
  - - 模块边界：`hooks` 路径组，共 2 个文件。
  - - 分析优先级：次要模块，先轻量确认依赖和辅助职责。

### 06-module-module_006.md
- title: module_006 .agents
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_006
- signal_lines:
  - - 模块边界：`.agents` 路径组，共 1 个文件。
  - - 分析优先级：次要模块，先轻量确认依赖和辅助职责。

### 06-module-module_007.md
- title: module_007 .codex-plugin
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_007
- signal_lines:
  - - 模块边界：`.codex-plugin` 路径组，共 1 个文件。
  - - 分析优先级：次要模块，先轻量确认依赖和辅助职责。

### 06-module-module_008.md
- title: module_008 .github
- headings: 角色, 深度分析, 关键文件, 关键路径, 关键符号, MCP 工具/API 表面, 风险与缺口, 证据, 覆盖率明细, Agent 深度分析
- wikilinks: 无
- module_mentions: module_001, module_008
- signal_lines:
  - - 模块边界：`.github` 路径组，共 1 个文件。
  - - 分析优先级：次要模块，先轻量确认依赖和辅助职责。
