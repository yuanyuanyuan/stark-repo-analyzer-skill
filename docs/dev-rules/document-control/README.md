# 文档控制规则

本规则约束 AI Agent 和人类维护者如何读取、创建和维护 `docs/roadmap/`、`docs/exec-plans/`、`docs/spec/` 与 `docs/adr/`。目标是让上下文恢复足够快，同时避免四类文档互相覆盖或产生两份真源。

直觉上，这四类文档组成一套控制台：roadmap 管方向，plan/progress 管执行，spec 管产品合同，ADR 管决策原因。类比的边界是，它们不是相互复制的四张表；同一事实只能在一个位置作为真源，其他文档通过链接引用。

## 一、Agent 启动时必须执行

1. 先按根 `AGENTS.md` 读取 output style 和 `docs/README.md`。
2. 开发任务读取活动 roadmap、plan 和 progress，只恢复当前阶段、任务 ID、阻塞、验证事实和下一刀。
3. 只有涉及产品行为时，才从 `docs/spec/README.md` 和 `docs/adr/README.md` 选择相关文件。
4. 历史原因只有在当前 ADR 明确引用、当前合同存在冲突或用户要求时才回读；不得默认遍历全部 ADR、`docs/archive/` 或 `tests/baseline/`。
5. 编辑前执行 `git status --short`，区分已有用户修改和本轮拥有的文件。

快速读取不是跳过权威文档。它的含义是按索引选择必要文档，而不是读得更少后自行补全缺失事实。

## 二、四类文档的唯一职责

| 目录 | 唯一负责 | 不得承载 |
|---|---|---|
| `roadmap/` | 为什么做、目标、非目标、阶段、完成边界 | 每日进度、逐文件动作、具体命令 |
| `exec-plans/` | 下一步怎么做、依赖、输出、验证、实际进度 | 新产品合同、架构决定、虚构验收结果 |
| `spec/` | 用户/调用方可依赖的输入、输出、状态、失败和不变量 | 愿景、任务状态、选择某方案的完整历史 |
| `adr/` | 长期技术选择的原因、权衡、影响和取代关系 | 每日执行日志、任务清单、行为合同全文 |

发现同一事实被多处定义且内容不一致时，Agent 必须先识别真源并修复链接或合同，不能选择对当前实现最方便的一份继续。

## 三、创建规则

### Roadmap

只有跨多轮、跨模块、改变产品/架构方向或需要分阶段验收时才创建。先使用 `proposed`，维护者确认后才能设为 `active`；仓库主线最多一份 `active` roadmap。

### Exec Plan

活动 roadmap 需要跨轮执行时，成对创建 `{任务}-plan.md` 与 `{任务}-progress.md`。只有 plan 声明生命周期状态；progress 使用 `文档类型：progress-log` 并继承 plan 状态。

### Spec

输入、输出、默认值、字段、状态、退出码、失败或兼容行为需要成为稳定依赖时创建。机器可读行为需要配套 schema；探索性设想不能提前写成 active spec。

### ADR

存在多个合理方案，并做出了长期影响架构、安全、依赖或验收方式的选择时创建。局部实现和临时排障不创建 ADR。编号连续，正文记录决策、原因、备选、影响与取代关系。

## 四、创建时的强制联动

新建任一活动文档时，必须在同一刀完成：

1. 更新对应目录 README 的当前入口或索引。
2. 添加与上游/下游文档的双向链接：roadmap → plan，plan → roadmap；spec/ADR 按需要互链。
3. 检查是否制造第二份 `active` roadmap、plan 或重复产品合同。
4. 为长文写首屏固定字段：文档角色、状态、当前结论/入口、何时读取、何时更新、关联真源。
5. 运行相对链接检查和状态唯一性检查。

缺少索引或链接的文件可以作为草稿，但不能声明已经成为活动控制面。

## 五、维护规则

| 发生的变化 | 必须维护 |
|---|---|
| 目标、非目标、阶段或退出条件变化 | roadmap；必要时同步 plan |
| 任务顺序、依赖、输出或验证方式变化 | plan |
| 本轮实际完成、失败、验证、阻塞或下一刀变化 | progress，采用追加记录 |
| 输入、输出、默认值、字段、失败或兼容语义变化 | spec、schema、测试；有新权衡时同步 ADR |
| 长期架构选择发生变化 | 新 ADR、旧 ADR 的 superseded 标记、ADR 索引、活动 roadmap |

不得用以下方式维护：

- 用 roadmap 的目标描述代替 spec 中的可测试行为；
- 用 plan 的“完成”状态代替 progress 中的验证证据；
- 回写历史 progress，把失败改成成功；
- 直接重写 accepted ADR，使旧决策看起来从未存在；
- 复制当前阶段、百分比或下一刀到多个 README，造成状态漂移。

## 六、Agent 每刀收尾检查

跨轮或控制面相关任务结束前，Agent 必须逐项检查：

1. 本轮修改是否回挂到活动任务 ID。
2. plan 状态与 progress 的实际证据是否一致。
3. 产品行为变化是否同步 spec/schema/test，架构原因是否需要 ADR。
4. 新建、取代或改状态的文档是否更新目录索引和双向链接。
5. 是否误改 `docs/archive/`、`tests/baseline/` 或第三方参考内容。
6. 实际运行了哪些验证，哪些未运行；不得提高声明级别。
7. 是否保留了唯一活动 roadmap、唯一活动 plan 和唯一产品合同入口。

## 七、冲突处理

权威层发生冲突时，按问题类型处理，不采用简单的“后写覆盖先写”：

- 方向冲突：回到活动 roadmap，由维护者确认目标。
- 产品行为冲突：回到 spec；如果新行为尚未被授权，先停止实现。
- 架构理由冲突：检查当前 ADR 及取代关系，必要时新建 ADR。
- 执行状态冲突：以 progress 中可核验事实为准，再修正 plan 快照。
- 验收声明冲突：以 `docs/dev-rules/` 的适用规则为上限。

无法判断哪份文档有效时，Agent 必须明确暴露冲突并请求决策，不能静默选择。


## 八、质量门与双角色审查字段

本仓库 **不** 使用外仓那种“单文件 exec-plan 兼进度与 Judge”的格式。Task Quality Gates 与 Dual-Agent Review 的内容必须写入现有控制面：

| 内容 | 落点 |
|---|---|
| 目标关、启动关（Blindspot、关键假设）、工作区基线 | `{task}-plan.md` |
| Deviations、Worker 验证、Boundary Check、Judge Review、最终结果 | `{task}-progress.md` 追加 |
| 轻量门小任务 | 不建 plan；验证与 Judge（或省略理由）写在最终回复 |

完整门与轻量门的触发条件见
[`../task-quality-gates/README.md`](../task-quality-gates/README.md)。
Worker/Judge 权限与迭代见
[`../dual-agent-review/README.md`](../dual-agent-review/README.md)。

### completed 与 Judge

默认 Judge、审查包、固定模型与阻塞标准以 [dual-agent-review](../dual-agent-review/README.md) 与 ADR-0026 为准；本节只规定它们如何落入 plan/progress 生命周期。


- 触发完整门，或属于必须 Judge 的改动：progress 中需有 `Verdict: pass`，或用户书面豁免（含豁免人、豁免项、剩余风险），才可将 plan 标为 `completed`。
- Worker 自验结束的合法中间态是 `awaiting-judge`（写在 plan 状态或 progress 收口阶段）；**不得**用“已在 progress 披露流程缺口”代替 pass/豁免。
- 省略 Judge 仅接受当前任务用户书面豁免（豁免人/豁免项/剩余风险）；Agent 不得自免。历史“可省略”措辞若仍出现，不得解释为 Agent 可自行跳过默认 Judge。
- 机械校验：`python tools/release/validate-control-plane.py --mode audit`。完整门激活字段检查用 `--mode bootstrap`。Codex hooks 在编辑/停止时触发同一护栏。
- Judge `pass` 不自动等于真实回归 UAT 通过；产品/gate 变更的证据上限仍是
  [`../real-uat-regression/README.md`](../real-uat-regression/README.md)。

### 归档

`completed` / `superseded` **不** 因质量门规则而强制移出 `docs/exec-plans/`。
仅在被明确取代、或维护者决定归档历史控制面时移入 `docs/archive/`，并同步目录索引。

### 最终回复最低字段

Delivery Task 收口时，最终回复至少说明：

1. 主线目标是否完成；
2. 关键改动；
3. Worker 验证（实际跑了什么）；
4. Judge verdict，或“本层可省略 Judge”的理由；
5. 未验证项、剩余风险与下一步。

完成度百分比仅在验收项可计数时使用，并注明口径。

## 主线总结

Agent 先通过索引选择最少但足够的权威文档，再按四类职责工作。新文档必须接入索引和链接，行为变化必须同步 spec，长期选择必须通过 ADR，跨轮事实必须追加到 progress。质量门与 Judge 写入 plan/progress，不另起状态机；快速阅读的前提不是省略规则，而是让规则具有稳定入口和唯一真源。
