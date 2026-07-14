# ADR-0026：默认 Judge 使用范围受限的审查包

状态：`accepted`

## 决策

对除纯讨论、只读查询和不留正式交付物的临时探索外的 Delivery Task，默认要求独立 Judge。只有用户在当前任务中的明确书面豁免可省略，并记录豁免人、范围和剩余风险。

Judge 必须以 Orchestrator 自动生成、Worker 补充事实的审查包为输入。审查包包含目标/验收、启动基线、拥有文件、排除的用户改动、Worker 验证和阻塞标准。缺字段时 Judge 返回 `blocked: insufficient review package`，不得扫描范围外内容推断任务边界。

Judge 在 Worker 自验准备收口时只启动一次；子代理优先，`codex exec` 是 fallback。两条路径固定 `gpt-5.6-terra` / `medium`，最多三轮重审。hook 仅负责提醒与无证据状态拦截，不能产生 verdict 或修改控制面。

## 原因

按风险决定是否审查会让小改动长期逃过独立检查；默认 Judge 把独立性变成可预测的交付成本。与此同时，缺少任务基线与范围的泛化审查会对脏工作树、历史问题或风格偏好过拟合，因此必须先限定审查证据。

## 备选方案

- 保持风险触发、允许 Agent 自行省略 Judge：成本较低，但标准随 Agent 判断漂移。
- 让 hook 自动发起 Judge 并标记完成：自动化更强，但合并了调度、判断和状态权限，审计性差。
- 仅传 plan/progress 让 Judge 自行探索：输入最少，但无法可靠区分任务增量与工作区噪声。
- 按风险升档模型：可能提升部分审查深度，但增加策略复杂度；当前 `gpt-5.6-terra` / `medium` 已被维护者确认足够。

## 影响

- 正式交付的延迟与推理成本上升，但豁免变得显式、可审计。
- Orchestrator 需要在任务开始和收口时维护审查包，而不是将上下文负担交给用户。
- dev-rules、hook 和 fallback 需要实现对应边界，并增加 dirty-worktree 与范围夹具。
- Judge pass 不改变真实 UAT、发布或外部安装的证据等级。

## 取代关系

不取代现有 ADR；它细化 Task Quality Gates 与 Dual-Agent Review 的默认审查策略。

## 修订记录

- 2026-07-14：澄清 fallback 沙箱与独立验证义务。Judge 角色仍禁止改正式树；`run-independent-judge.py` 使用 `workspace-write` 仅覆盖验证侧写（临时目录 / pytest basetemp / 可忽略缓存），以便重跑廉价本地测试。禁止以「只读沙箱写不了临时目录」为由采信 Worker 的 pytest 等结果并 `pass`；细则见 `docs/dev-rules/dual-agent-review/` 第六节与 `docs/aiprompts/judge-handoff.md`。
