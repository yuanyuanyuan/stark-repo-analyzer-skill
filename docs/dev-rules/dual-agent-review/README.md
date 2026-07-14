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

默认形态：

- **小交付**：当前会话 Agent 作 Worker；收尾启动**独立** Judge 会话，尽量不继承 Worker 推理，只接收用户目标、适用规则、工作区基线、任务 diff 与验证证据。
- **复杂/并发**：先由 Orchestrator 分派 Worker 与 Judge。

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

## 九、与 completed 的关系

- 完整门或必须 Judge 的改动：无 `Verdict: pass`（或用户书面豁免并记入 progress）不得将 plan 标为 `completed`。
- 轻量门且可省略 Judge：不要求 Judge 即可收口。
- 用户豁免必须记录：谁豁免、豁免哪条、剩余风险。

## 主线总结

有行为或合同风险就上独立 Judge；小修复可省略但要写明理由。Judge 只读、有轮次上限，且永远不能放宽真实 UAT 证据标准。
