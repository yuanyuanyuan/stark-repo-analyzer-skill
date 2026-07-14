# Dual-Agent Review · 双角色审查

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义 Worker / Judge / Orchestrator 的职责、基线、独立验证、输出协议与迭代上限 |
| 当前状态 | `active` |
| 当前结论/入口 | 按风险强制或省略 Judge；Judge 不得放宽 real-uat-regression |
| 何时读取 | 必须 Judge 的交付开始前；轻量门需判断是否可省略时 |
| 何时更新 | 角色权限、强制范围、迭代闸门或报告落点变化时 |
| 关联真源 | 触发档位 → [task-quality-gates](../task-quality-gates/README.md)；控制面字段 → [document-control](../document-control/README.md)；UAT 证据上限 → [real-uat-regression](../real-uat-regression/README.md) |

直觉上，Worker 像主刀医生，Judge 像只读的二审，Orchestrator 像复杂手术的调度。类比的边界是：Judge 不获得“顺手改掉”的权力，也不能用审查偏好扩展需求。

## 一、强制范围

### 必须独立 Judge

- 修改产品行为、spec/schema、Graphify gate、输出合同或验收语义；
- 安全、凭据、数据迁移、不可逆操作或真实外部服务；
- 已触发 [完整质量门](../task-quality-gates/README.md)；
- 用户明确要求审查。

### 可省略独立 Judge

局部、可回滚、不改合同的小改动（错别字、索引链接、纯排版、明显单点修复）。Worker 仍须自验，并在最终回复写明“本层可省略 Judge”的理由。

### 与 UAT 的关系

Judge 可以否决假通过声明，**不得**把静态工件、内部控制面直调、中断运行或未跑矩阵的结果抬成 UAT/真实回归通过。产品验收上限只认 real-uat-regression。

## 二、角色

| 角色 | 职责 | 禁止 |
|---|---|---|
| **Worker** | 实现、自验、更新 plan/progress 中属己字段、修改正式文件 | 自审冒充独立 Judge |
| **Judge** | 只读审查任务增量；至少一项与核心风险相关的独立验证；输出固定 verdict | 改代码/文档/计划/配置；跑会改正式树的 formatter；回退用户无关改动 |
| **Orchestrator** | 复杂或并发任务中分派、汇总、控制迭代 | 用调度身份绕过 Judge 权限限制 |

默认调度形态：

- **优先子代理**：当前会话 Agent 作 Worker 后，Orchestrator 必须自行启动**独立、只读** Judge 子代理。尽量不继承 Worker 推理，只交付用户目标、适用规则、工作区基线、任务 diff 与验证证据。
- **fallback 为 `codex exec`**：运行时没有原生子代理时，Orchestrator 自动运行 [`tools/release/run-independent-judge.py`](../../../tools/release/run-independent-judge.py)，它以 `codex exec --sandbox read-only` 发起临时 Judge 并只返回审查区块。
- **复杂/并发**：先由 Orchestrator 分派 Worker 与 Judge；即使存在多个 Worker，也只由未参与实现的 Judge 对任务增量给出 verdict。

用户不应被要求复制 Judge prompt 或手动执行命令。只有无法调度子代理、`codex exec` 不可用、Judge `blocked`，或需要书面豁免时，Orchestrator 才向用户暴露阻塞原因和需要的决定。

## 三、工作区基线

任务开始时记录：

- `git status --short`；
- 预期修改范围；
- 已有且不属于本任务的用户改动。

Worker 只改声明范围；扩展范围前先记 Deviations。Judge 只审相对基线的任务增量，不评价或回退用户无关改动，不用 commit/stash/reset 伪造边界。

## 四、审查标准

Judge 依次使用：

1. 固定底线：用户当前指令、`AGENTS.md`、适用的 `docs/dev-rules/`；
2. 任务验收项：当前 exec plan；小任务则用用户请求、diff 与验证结果。

重点：需求符合度、改动边界、行为正确性、验证证据、文档一致性、未声明偏离。不得擅自扩展需求，或把个人偏好写成阻塞项。

## 五、独立验证

- 至少独立执行一项与核心风险直接相关的验证。
- 代码任务优先重跑针对性测试、lint、typecheck 或复现命令。
- 文档任务检查 diff、链接、术语与规则符合性。
- 高成本、真实网络、付费 API、部署、不可逆验证不自动重复；审查 Worker 的脱敏证据与退出状态。
- 可运行只读命令，以及只写入临时或已忽略目录的测试；不得修改正式文件。

## 六、输出协议

Judge 固定输出：

- `Verdict: pass | revise | blocked`
- 刚性约束违规
- 按严重级别排列的问题
- 缺失验证
- 建议复查范围
- 独立执行的验证及结果

无明确可重复 rubric 时，不要求主观总分。

## 七、迭代与人工闸门

- 默认最多 **3** 轮：`pass` 结束；`revise` 由 Worker 修正后重审；`blocked` 停止自动迭代并交用户。
- 提前人工闸门：同一 major 连续两轮未解；安全风险、不可逆操作或需求冲突；无法获得必要验证证据；三轮仍未通过。
- 大型任务可在该任务 plan 中调整轮数，禁止无限循环。

## 八、报告落点

| 任务类型 | Judge 报告 |
|---|---|
| 轻量门 / 无 plan | 不落盘；最终回复写明 verdict 与独立验证（或省略理由） |
| 完整门 / 有 progress | 原样追加到 `*-progress.md` 的 `Judge Review` 区域 |

只追加且不改变实现或结论的机械转录，可豁免再次审查。若转录同时修改实现、计划内容或审查结论，必须重新审查。

## 九、与 completed 的关系（完整门收口状态机）

完整门或必须独立 Judge 的交付，遵守下列顺序；细则与落点以本节和 document-control 为准，不在根 `AGENTS.md` 展开。

1. 第一刀正式编辑前，plan/progress 写明：`质量门：完整门|轻量门` 与 `独立Judge：必须|可省略`。
2. Worker 自验结束后，只能进入 `awaiting-judge`（plan 状态或 progress 收口阶段）；**禁止**同会话直接标 `completed`。
3. 独立 Judge 在 progress 写入 `### Judge Review` 且 `Verdict: pass`，或记录用户书面豁免（豁免人/豁免项/剩余风险）后，才可考虑 `completed`。
4. 将 plan/roadmap 标为 `completed` 前，必须先跑 `python tools/release/validate-control-plane.py --mode audit`；失败则保持原状态。完整门激活后可用 `--mode bootstrap` 检查启动字段。
5. 无 `Verdict: pass`（或合格豁免）不得 `completed`；“已在 progress 披露流程缺口”不能替代门禁。
6. 轻量门且可省略 Judge：不要求 Judge 报告，但须显式写可省略理由。
7. Judge 由 Orchestrator 自动调度：优先原生只读子代理，缺失时运行 `tools/release/run-independent-judge.py --plan <plan-path>`。输入协议见 [`docs/aiprompts/judge-handoff.md`](../../aiprompts/judge-handoff.md)，不得要求用户手动粘贴。

## 十、机械护栏与 Codex hooks

防呆不只靠自觉，仓库提供两层机械门：

1. **CLI**：`python tools/release/validate-control-plane.py [--mode audit|bootstrap|all]`
   - `audit`：声明完整门/必须 Judge 的 `completed` plan 必须有真实 Judge Review `Verdict: pass` 或结构化豁免。
   - `bootstrap`：`active`/`awaiting-judge` 的完整门 plan 必须声明 `质量门` / `独立Judge` 等启动字段。
2. **Codex hooks**（[`.codex/hooks.json`](../../../.codex/hooks.json) + [`.codex/hooks/control_plane_gate.py`](../../../.codex/hooks/control_plane_gate.py)）：
   - `PreToolUse`（`apply_patch|Edit|Write|Bash`）：拦截把 plan 标成 `completed` 且缺少 pass/豁免的尝试。
   - `PostToolUse`（编辑类）：控制面相关编辑后复审；发现完整门 `awaiting-judge` 时，把自动 Judge 调度义务注入当前 Agent；失败可 `continue: false`。
   - `Stop` / `SubagentStop`：回合结束审计，并再次暴露未调度的 Judge；它们只提醒当前 Agent 调度，绝不伪造 Judge verdict 或改动正式文件。

Hooks 是护栏和调度提醒，不是 Judge，也不能替代独立判断。当前 Agent 收到待审提醒后先创建原生子代理；只有该能力不存在才自动调用 `codex exec` fallback。独立审查输入协议见 [`docs/aiprompts/judge-handoff.md`](../../aiprompts/judge-handoff.md)。项目 hooks 需在 Codex `/hooks` 中审查并 trust 后才会执行。

## 主线总结

有行为或合同风险就上独立 Judge；小修复可省略但要写明理由。Judge 只读、有轮次上限，且永远不能放宽真实 UAT 证据标准。
