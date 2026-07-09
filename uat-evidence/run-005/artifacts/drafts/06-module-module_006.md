# module_006 .agents

- 文件数: 1
- 分层: minor

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`.agents` 路径组，共 1 个文件。
- 分析优先级：次要模块，先轻量确认依赖和辅助职责。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `.agents/plugins/marketplace.json`

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
| .agents | 1 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`.agents` 模块是 Agent Skills marketplace 列表入口，用于让 Codex/Cursor/Copilot/Gemini CLI 等 Agent Skills host 通过 marketplace 发现并安装该仓库中的 watch 插件（证据：`slices/05-agent-config.xml`、`slices/04-docs.xml`、`drafts/06-module-module_006.md`）。

**设计思路**：`.agents/plugins/marketplace.json` 是轻量注册表，而不是执行逻辑。它声明 marketplace 名称 `claude-video`、展示名 `watch`、插件源为 GitHub URL，并标注安装可用、认证在安装时处理、分类为 Productivity（证据：`slices/05-agent-config.xml`）。这与项目“一个 self-contained skill folder 被不同宿主复制/链接”的设计一致（证据：`slices/05-agent-config.xml`、`slices/04-docs.xml`）。

**关键数据流**：Agent Skills CLI 或 host marketplace 读取 `.agents/plugins/marketplace.json` → 定位 GitHub repo → 安装 watch plugin/skill → 最终执行仍进入 `skills/watch/SKILL.md` 与 `scripts/watch.py`（证据：`slices/05-agent-config.xml`、`slices/04-docs.xml`）。

**模块协同**：它与 `.codex-plugin` 一起服务非 Claude Code 安装面；与 root README/AGENTS 协同说明 `npx skills add bradautomates/claude-video -g` 的安装路径；与 core skill 协同要求 `skills/watch` 自包含，避免 marketplace 复制时丢失脚本（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**架构亮点**：该模块把多宿主分发能力降到一个小而稳定的 JSON manifest，业务实现不需要感知具体 host。这种分层能降低对单一平台的耦合（证据：`slices/05-agent-config.xml`）。

**主要风险**：manifest 指向 GitHub URL，安装成功依赖远端仓库可达和 host 对该 marketplace schema 的兼容；当前证据不能验证外部 marketplace 实际解析结果（证据：`slices/05-agent-config.xml`）。历史热点仅显示该文件修改 1 次，不能判断其 schema 是否经历过兼容性修正（证据：`slices/12-history-hotspot.txt`）。

