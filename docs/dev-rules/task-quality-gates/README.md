# Task Quality Gates · 任务质量门

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义按风险触发的目标、假设、偏离和交付边界检查；不负责 roadmap/plan 生命周期真源 |
| 当前状态 | `active` |
| 当前结论/入口 | 轻量门 vs 完整门两档；Delivery Task 默认独立 Judge + 审查包；完整门字段写入 plan/progress |
| 何时读取 | 任何 Delivery Task 开始前判断档位；完整门或高风险交付执行前必读 |
| 何时更新 | 触发条件、四关定义或与控制面落点关系变化时 |
| 关联真源 | 控制面生命周期 → [document-control](../document-control/README.md)；审查协议 → [dual-agent-review](../dual-agent-review/README.md)；产品验收上限 → [real-uat-regression](../real-uat-regression/README.md) |

本规则解决的是“这项交付要过哪些思考与记录关口”，不是“仓库里有没有 active roadmap”。生命周期状态、索引和 plan/progress 拆分仍以 document-control 与 `docs/exec-plans/` 为准。

## 一、Delivery Task

满足任一条件即为 **Delivery Task（交付任务）**：

- 创建、修改或删除仓库中的正式文件；
- 产生需要保留的计划、报告、设计或验证证据；
- 修改数据库、部署环境、GitHub、云资源等外部状态；
- 执行会形成正式结论并被后续工作依赖的代码库审查。

不属于交付任务：纯讨论、只读查询、临时探索且不形成正式交付物。一旦结论写入 plan、ADR、Issue 或仓库文件，即转为交付任务。

## 二、两档触发

质量门按**风险**触发，不按改动文件数量机械触发。

### 轻量门

适用：局部、明确、可回滚、不改产品/验收合同的小修改。

必须：

- Worker 自验，并在最终回复写清验证结果；
- 默认独立 Judge（审查包协议见 [dual-agent-review](../dual-agent-review/README.md)）；仅用户当前任务书面豁免可省略；
- 不强制创建 roadmap / plan / progress。

### 完整门

满足任一条件时，执行前必须留下完整记录：

- 修改产品契约、schema、信封、缓存语义或 CLI/Skill 外部行为；
- 涉及安全、凭据、数据迁移、不可逆操作或真实外部服务；
- 跨模块且步骤存在前后依赖；
- 关键假设无法从代码或权威文档直接确认；
- 用户明确要求盲点扫描、假设验证或边界检查。

完整门与控制面：

| 情形 | 必须创建/使用 |
|---|---|
| 同时跨多轮、跨模块主线或改变产品/架构方向 | 活动或拟议中的 roadmap + `{task}-plan.md` + `{task}-progress.md` |
| 高风险但单轮可收口 | 可只建 plan/progress，不强制 roadmap |
| 仅轻量门 | 不建控制面文件 |

禁止为质量门再发明第三套计划格式或单文件“源仓库式 exec-plan”替代 plan/progress。

## 三、四个关口

### 目标关

记录目标、非目标和可验证完成条件。完成条件必须是可观察结果，而不是“已处理”“已沟通”等过程状态。

完整门时写入 `*-plan.md`。

### 启动关

执行 **Blindspot Pass（盲点扫描）**：列出可能遗漏的利益相关方、状态、失败路径和约束。记录关键假设、置信度，以及低置信度假设的快速验证方式。低置信且会改变方案的假设必须先验证再大规模实现。

完整门时写入 `*-plan.md`（含工作区基线：`git status --short`、预期范围、用户既有改动）。

### 执行关

仅在实际偏离原计划时记录 **Deviations**；每项包含触发原因、取舍、影响范围，以及下次应提前确认的事项。无偏离时明确写“无”。

完整门时追加到 `*-progress.md`。

### 收尾关

执行 **Boundary Check（边界检查）**：结果适用范围、失效条件、降级或回退，并附 Worker 与（若需要）Judge 的验证证据。

完整门时追加到 `*-progress.md`。触及 analyzer / Graphify gate / 输出合同 / 验收语义时，证据级别不得超过 [real-uat-regression](../real-uat-regression/README.md)。

## 四、边界示例

- 修改一个拼写错误并保存：Delivery Task；轻量门；默认仍要 Judge，除非用户书面豁免。
- 修改 Graphify gate 失败语义：Delivery Task；完整门；必须 Judge；聚焦或真实 UAT 按 real-uat-regression。
- 只读检查代码并在对话中回答：非 Delivery Task。
- 讨论尚未决定是否实施的想法：非 Delivery Task；写入 plan/ADR 后转为交付任务。

## 五、与流水线的关系

Delivery Task 默认 Judge。完整门 + 审查包 +（若适用）UAT 规则同时生效时，顺序为：

1. 目标关 / 启动关
2. 工作区基线（进入审查包）
3. Worker 实现与自验
4. 收尾关预检（Boundary Check、Worker 证据）并生成/补全审查包
5. 进入 `awaiting-judge` 后，Orchestrator 只调度一次独立 Judge
6. 仅当变更触及产品/gate/验收语义时，按 real-uat-regression 执行聚焦 UAT 或（发布宣称时）真实回归
7. 满足 document-control 的终态条件后才升级状态

Judge `pass` 不等于真实回归 UAT 通过。

## 主线总结

先判断是不是 Delivery Task，再选轻量门或完整门。Delivery Task 默认独立 Judge，并用审查包限定范围；完整门把四关写进 plan/progress，不另起状态机；产品是否“验过”仍以 real-uat-regression 为上限。
