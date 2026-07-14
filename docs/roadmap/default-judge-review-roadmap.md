# 默认 Judge 审查机制 Roadmap

状态：`completed`

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义默认 Judge 审查机制的目标、非目标、阶段与退出条件；不记录逐文件执行细节 |
| 当前状态 | `completed`；J0-J3 退出条件满足，独立 Judge pass |
| 当前结论/入口 | 先读配对 [exec plan](../exec-plans/default-judge-review-plan.md) 与 [ADR-0026](../adr/0026-default-judge-with-scoped-review-package.md) |
| 何时读取 | 准备改变质量门、Judge 规则、hook 或 fallback 调度器时 |
| 何时更新 | 目标、非目标、阶段或退出条件变化时 |
| 关联真源 | 术语见 `CONTEXT.md`；执行见 plan/progress；实施后的规则以 `docs/dev-rules/` 为准 |

## 北极星目标

让除讨论、只读查询和不留正式交付物的临时探索外的每个 Delivery Task 默认经过独立 Judge，并使 Judge 只基于自动生成的审查包审查本任务增量，避免对脏工作区、历史问题或个人偏好的过拟合。

## 非目标

- 不让 hook 自行生成 verdict、转录结果或标记 `completed`。
- 不把 Judge `pass` 抬高为真实 UAT、发布或外部 marketplace 通过。
- 不自动改写其他仓库；通用经验仅写入 `tools-config-guide`。
- 不根据任务文件数升档模型；Judge 固定 `gpt-5.6-terra` / `medium`。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| J0 合同冻结 | 统一术语、ADR、默认触发与豁免定义 | `CONTEXT.md`、ADR、dev-rules 的定义无冲突 |
| J1 审查包 | 由 Orchestrator 自动捕获基线与范围 | 可为典型正式任务生成完整审查包；缺字段可确定性 `blocked` |
| J2 调度与护栏 | 子代理优先、`codex exec` fallback，hook 只提醒/拦截 | 待审任务只调度一次；已完成任务不误报；无证据 `completed` 被拦截 |
| J3 验证与收口 | 验证范围、模型记录、重审上限与文档 | 单测/夹具、真实只读 fallback、独立 Judge 与控制面校验均有证据 |

## 完成口径

本 roadmap 完成时，默认 Judge 的触发、用户豁免、审查包、阻塞标准、固定模型、三轮上限、调度和验证均被实现并通过独立 Judge。真实 UAT 仍按原有产品规则另行声明。

## 主线总结

本 initiative 把“默认独立审查”做成受范围约束的流程能力，而不是让 Agent 对整个工作树做泛化找错。它已完成：默认 Judge、审查包、固定模型、调度护栏与验证均落地并通过独立 Judge。
