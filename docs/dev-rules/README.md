# dev-rules · 开发与验收规则目录

本目录存放本仓库 **dev 侧** 可执行规则（agent/人共用的操作与验收口径），与产品 skill 正文、CLI 实现并列维护。

## 目录约定

| 路径 | 用途 |
|---|---|
| [`output-style/`](output-style/) | 回复、维护性文档和代码注释的语言与渐进式表达规则；Agent 启动后必须先读 |
| [`document-control/`](document-control/) | roadmap、exec plan、spec、ADR 的读取、创建、维护、索引和冲突处理规则；Agent 启动后必须读 |
| [`task-quality-gates/`](task-quality-gates/) | 按风险触发的任务质量门：Delivery Task、轻量/完整门、四关与控制面落点 |
| [`dual-agent-review/`](dual-agent-review/) | Worker → Judge（及 Orchestrator）审查协议、`awaiting-judge`/completed 状态机、校验脚本与 Codex hooks 护栏 |
| [`real-uat-regression/`](real-uat-regression/) | 区分开发期聚焦 UAT 与发布级真实回归，覆盖模式、Graphify 选择、健康门和 subagent 同意边界 |
| [`code-map/`](code-map/) | 本仓库代码地图真源、更新触发、无影响声明与提醒 hook 行为 |
| [`pre-release-security-scan/`](pre-release-security-scan/) | 公开发版前强制密钥/敏感资料扫描（工作树 + 全 git 历史）；与真实回归 UAT 并列且互不替代 |
| [`version-release/`](version-release/) | 公开版本发布总规则：SOP 顺序、元数据/tag/Release、检查清单、纠正发版与 tag/main 语义；编排安全扫描与 Judge |
| [`domain-language.md`](domain-language.md) | 领域语言和 ADR 使用约束 |
| （后续）其它 dev 规则 | 新增时在本 README 登记一行，保持「一类规则一个子目录」 |

## 权威与同步

1. **操作入口**：根目录 [`AGENTS.md`](../../AGENTS.md) 只做导航路由，必须先指向 `output-style/`，随后加载 `document-control/`；开发交付再按风险加载 `task-quality-gates/` 与（如需）`dual-agent-review/`，并按变更类型继续路由到本目录的其他规则。细则正文在本目录，不在 `AGENTS.md` 复写。
2. **控制面机械护栏**（实现位于仓库工具与 hooks，规则解释在 `dual-agent-review/` / `document-control/`）：
   - CLI：`python tools/release/validate-control-plane.py [--mode audit|bootstrap|all]`
   - Codex hooks：`.codex/hooks.json` + `.codex/hooks/control_plane_gate.py`（PreToolUse / PostToolUse / Stop / SubagentStop）；代码地图提醒：`.codex/hooks/code_map_gate.py`（PostToolUse edit + Stop，仅 systemMessage）
3. **产品契约细节**：skill 工作流与质量门语义仍以 `skills/repo-analyzer/` 与 `docs/spec/` 为准；本目录写 **如何跑回归、场景矩阵、证据目录、禁止假通过**，以及开发协作门禁。
4. **变更联动（强制）**：当 **代码、skill、gate、需求/Issue/ticket** 发生会改变分析行为或验收语义的变更时，**必须同步更新**本目录对应规则（至少 `real-uat-regression/`），并在 PR 中写明规则 diff 或「规则无影响」理由。禁止只改实现不改回归规则，或只改规则不改实现却声称已验收。协作门禁（质量门、双角色审查）变更时同步 `task-quality-gates/`、`dual-agent-review/` 与 `document-control/` 中的落点说明。

## 命名

- 目录与文件使用英文 kebab-case；正文默认中文。
- 对外正式测试名：**真实UAT回归测试**（标签 `real-uat-regression`）。
