# module_007 .codex-plugin

- 文件数: 1
- 分层: minor

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`.codex-plugin` 路径组，共 1 个文件。
- 分析优先级：次要模块，先轻量确认依赖和辅助职责。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `.codex-plugin/plugin.json`

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
| .codex-plugin | 1 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`.codex-plugin` 是 Codex/agents 安装面的 manifest 模块，作用是把 Agent Skills CLI 指向 `./skills/`，让 watch skill 以 self-contained folder 形式被发现和安装（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`、`drafts/06-module-module_007.md`）。

**设计思路**：它的架构职责是“声明入口，不承载实现”。项目文档明确 `.codex-plugin/plugin.json` 是 Codex/agents manifest，`"skills": "./skills/"` 指向自包含 skill 目录；运行时 path resolution 仍由 `SKILL.md` 基于自身目录完成（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**关键数据流**：Codex 或 Agent Skills CLI 读取 `.codex-plugin/plugin.json` → 发现 `skills/watch/SKILL.md` → 复制/链接整个 `skills/watch` 目录 → 用户调用 `/watch` → `SKILL.md` 启动 `scripts/watch.py`（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**模块协同**：该模块与 core skill 的目录布局强绑定：如果 `SKILL.md` 与 `scripts/` 不再同级，Codex/agents 安装面会复制到不完整 skill。AGENTS 明确禁止把 `SKILL.md` 或 scripts 移回 repo root，这正是在保护 `.codex-plugin` 的安装契约（证据：`slices/05-agent-config.xml`）。发布时它还需要与 `SKILL.md` 和 `.claude-plugin/plugin.json` 版本同步（证据：`slices/04-docs.xml`）。

**架构亮点**：Codex 适配层保持极薄，有助于核心能力在多个 agent runtime 中复用；跨平台差异被限制在 manifest 层，而不是散落到 Python 运行逻辑中（证据：`slices/05-agent-config.xml`）。

**主要风险**：当前可读切片未展开 `.codex-plugin/plugin.json` 的完整 JSON 内容，只能依据 README/AGENTS 判断其职责，不能核对实际字段值和版本号（证据：`drafts/06-module-module_007.md`、`slices/04-docs.xml`、`slices/05-agent-config.xml`）。此外，版本同步缺少当前证据中的自动校验，仍是发布流程风险（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。

