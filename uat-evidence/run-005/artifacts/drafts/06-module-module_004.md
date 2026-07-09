# module_004 .claude-plugin

- 文件数: 2
- 分层: minor

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`.claude-plugin` 路径组，共 2 个文件。
- 分析优先级：次要模块，先轻量确认依赖和辅助职责。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `.claude-plugin/marketplace.json`
- `.claude-plugin/plugin.json`

## 关键路径
- 先从模块文件清单逐个确认入口。

## 关键符号
- 未识别到公开符号

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 风险与缺口
- 缺少可见测试文件，变更该模块前应先补最小回归验证。

## 证据
- 模块 ID 来源：`05-module-ids.yaml`
- 代码切片：`slices/02-backend.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 历史热点：`slices/12-history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| .claude-plugin | 2 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`.claude-plugin` 是 Claude Code 安装面的适配模块，负责把同一个 `/watch` skill 暴露到 Claude Code plugin/marketplace 体系中。该角色来自项目结构说明：`.claude-plugin/` 包含 `plugin.json` 与 `marketplace.json`，用于 Claude Code plugin 和 local marketplace（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`、`drafts/06-module-module_004.md`）。

**设计思路**：该模块不是业务逻辑，而是分发元数据。核心设计是让 Claude Code 安装路径与 self-contained `skills/watch` 运行模型保持一致：文档强调产品 contract 在 `skills/watch/SKILL.md`，Claude Code 只是安装面之一，不能把实现绑定到 Claude Code 专属变量（证据：`slices/05-agent-config.xml`）。

**关键数据流**：用户通过 `/plugin marketplace add bradautomates/claude-video` 和 `/plugin install watch@claude-video` 安装，Claude Code plugin 元数据把仓库中的 watch skill 暴露给宿主；实际运行仍回到 `skills/watch/SKILL.md` 和 `scripts/watch.py`（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**模块协同**：它与 `hooks` 模块协同提供 Claude Code 专属体验：plugin 负责安装入口，SessionStart hook 负责首次/部分配置时的一行状态提示（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。它还与 root/release 协同，发布规则要求 `.claude-plugin/plugin.json` 版本与 `SKILL.md`、`.codex-plugin/plugin.json` 同步（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**架构亮点**：将 Claude Code 适配隔离在 `.claude-plugin`，而不是污染核心 `skills/watch`，有利于保持核心 skill 对 Codex/Cursor/其他 Agent Skills host 的可移植性（证据：`slices/05-agent-config.xml`）。

**主要风险**：当前可读切片没有展开 `.claude-plugin/marketplace.json` 和 `.claude-plugin/plugin.json` 的完整内容，只能确认其存在与职责，不能判断字段、版本号、路径指向是否正确（证据：`drafts/06-module-module_004.md`、`slices/04-docs.xml`、`slices/05-agent-config.xml`）。另外，版本同步是文档规则，当前证据未显示 CI 自动检查该规则（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。

