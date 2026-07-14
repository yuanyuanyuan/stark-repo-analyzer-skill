# 仓库 Agent 规则

本文件只承载 AI 协作的仓库级硬规则。产品行为、命令细节、任务进度和长篇提示词必须下沉到对应文档，不能堆在这里。

`AGENTS.md` 是 Agent 打开仓库后的首读入口，必须保留在仓库根目录，不能移入 `docs/`。

## Graphify 路由

The project knowledge graph lives under `graphify-out/` when generated, with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed Graphify skill or these instructions before doing anything else.

Rules:

- For codebase questions, first run `graphify query "<question>"` when `graphify-out/graph.json` exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than `GRAPH_REPORT.md` or raw grep output.
- Dirty `graphify-out/` files are expected after hooks or incremental updates; dirty graph files are not a reason to skip Graphify. Only skip Graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation instead of raw source browsing.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 启动顺序

打开本仓库后，按以下顺序建立上下文：

1. **先读 [`docs/dev-rules/output-style/README.md`](docs/dev-rules/output-style/README.md)**：后续回复、文档编写和代码注释都必须遵守其中的语言与表达规则。
2. 阅读 [`docs/README.md`](docs/README.md)，理解文档分层、职责和权威边界。
3. 阅读 [`docs/dev-rules/document-control/README.md`](docs/dev-rules/document-control/README.md)，按任务类型选择文档，并遵守创建、维护、索引和冲突处理规则。
4. 开发交付任务开始前，阅读 [`docs/dev-rules/task-quality-gates/README.md`](docs/dev-rules/task-quality-gates/README.md)，判断轻量门或完整门；属于必须 Judge 的改动时，再读 [`docs/dev-rules/dual-agent-review/README.md`](docs/dev-rules/dual-agent-review/README.md)。
5. 执行开发任务时，先从 [`docs/roadmap/README.md`](docs/roadmap/README.md) 和
   [`docs/exec-plans/README.md`](docs/exec-plans/README.md) 确认是否存在 `active` 控制面。
   当前 Graphify 简化实施主线已经完成，最近记录是
   [roadmap](docs/roadmap/graphify-simplification-roadmap.md)、
   [执行计划](docs/exec-plans/graphify-simplification-plan.md)和
   [进度记录](docs/exec-plans/graphify-simplification-progress.md)；不能把 `completed` 文档当作新的执行授权。
6. 编辑前执行 `git status --short`，保留用户已有改动，并在其基础上工作。
7. 涉及产品行为时，先读 `CONTEXT.md`、[`docs/spec/README.md`](docs/spec/README.md) 和
   [`docs/adr/README.md`](docs/adr/README.md)，再按索引只读取相关合同和当前有效 ADR；不要默认全量读取历史 ADR。
8. 涉及 analyzer skill、Graphify gate、输出合同或验收语义时，编辑前必须阅读
   [`docs/dev-rules/real-uat-regression/README.md`](docs/dev-rules/real-uat-regression/README.md)。

不要根据熟悉的文件名或目录名自行推断权威性。`docs/archive/` 下的归档和 `tests/baseline/` 下的外部证据索引默认都不是活动权威，除非活动 roadmap 或 plan 明确重新引入。

## Output Style 路由

- 面向用户的回复和本仓库维护性文档默认使用中文，专业术语、命令、标识符和必要的原文名称可以保留英文。
- 根 `README.md` 是英文产品入口，`README.zh.md` 是中文版本；这是维护性文档默认中文规则的明确例外，修改产品说明时必须同步两份文件的行为合同。
- 解释复杂概念或编写需要帮助读者理解的文档时，必须使用“渐进式陪跑教学”：先降低术语门槛，再逐步给出准确边界，不能通过牺牲技术深度换取表面易懂。
- 代码注释必须使用英文；面向用户的错误消息、测试 fixture 和产品输出不属于代码注释。
- 完整写作方法、文档适用范围和例外只以
  [`docs/dev-rules/output-style/README.md`](docs/dev-rules/output-style/README.md) 为准。本节只负责让 Agent 在开始其他工作前加载该规则。

## 文档边界

- `docs/roadmap/` 定义一项工作的原因、目标结果、非目标、阶段和验收边界。
- `docs/exec-plans/` 定义活动工作的执行顺序、验证和跨轮交接状态。
- `docs/aiprompts/` 存放可复用的操作指引；Prompt 不是产品合同，不能覆盖本文件、活动 roadmap 或验收规则。
- `docs/dev-rules/` 存放可执行的开发、协作和验收规则。
- 产品行为属于 `skills/repo-analyzer/`、`docs/spec/`、`CONTEXT.md` 和仍然有效的 ADR。

## 文档控制硬规则

- Agent 必须先从目录 README 选择最短阅读路径，不得把全量扫描历史 ADR、archive 或 baseline 当作默认启动步骤。
- 新建 roadmap、plan、spec 或 ADR 时，必须同时更新对应目录 README 的当前入口或索引；没有被索引的活动文档视为未接入控制面。
- roadmap/plan 的状态、spec 的行为合同和 ADR 的取代关系发生变化时，必须在同一刀同步相关链接和索引。
- roadmap 不能替代 spec，plan/progress 不能替代验收证据，ADR 不能替代实现计划；发现冲突时先修正权威文档，再继续实现。
- 跨多轮工作每刀结束时必须更新 progress；只记录实际完成和实际验证，不能把计划、文件存在或静态扫描写成验收通过。

详细创建条件、维护动作和收尾检查以
[`docs/dev-rules/document-control/README.md`](docs/dev-rules/document-control/README.md) 为准。

最近完成的仓库实施主线由
[`docs/roadmap/graphify-simplification-roadmap.md`](docs/roadmap/graphify-simplification-roadmap.md)
和
[`docs/exec-plans/graphify-simplification-plan.md`](docs/exec-plans/graphify-simplification-plan.md)
共同记录；完成证据位于
[`docs/exec-plans/graphify-simplification-progress.md`](docs/exec-plans/graphify-simplification-progress.md)。
当前没有 `active` roadmap 或 plan。准备发布并触发 G5 真实回归，或开始新的跨多轮工作时，必须先建立新的活动执行控制面；不能直接续写已完成计划。
被取代的 V1 控制面和执行记录位于 `docs/archive/`，只能作为历史输入，不能指导当前执行。

## 主线控制

如果工作预计跨越多轮、涉及多个模块、属于迁移，或会改变产品/验收合同，编辑前必须：

1. 确认活动 roadmap 和执行计划。
2. 说明当前主目标、所处阶段和下一刀动作。
3. 如果缺少活动文档，先建立或迁移控制面，再开始实现。

小型且局部的修复不要求新建 roadmap 或执行计划。

长任务进行期间，要在执行记录中持续写入已完成动作、准确的验证结果、阻塞和下一刀。旁支问题只有在直接阻塞当前交付、会让新行为成为假配置/假入口，或用户明确要求时才处理。清理或重构前，先说明它如何直接帮助当前主线。

## 验收与收口

任何影响 analyzer skill、Graphify gate、输出合同或验收语义的变更，都必须遵守
[`docs/dev-rules/real-uat-regression/README.md`](docs/dev-rules/real-uat-regression/README.md)。

- 不得把静态工件、内部控制面直调、聚焦 UAT 或中断运行称为真实 UAT 通过。
- 不能为了提前收口，把必需验收门改称可选验证。
- Delivery Task 必须按 [`task-quality-gates`](docs/dev-rules/task-quality-gates/README.md) 选择轻量门或完整门；必须 Judge 时遵守 [`dual-agent-review`](docs/dev-rules/dual-agent-review/README.md)。
- 开发任务结束时，必须报告：主线目标是否完成、关键改动、Worker 验证、Judge verdict 或可省略理由、剩余阻塞/未验证项与下一刀。
- 只有明确分母时才使用完成度百分比，例如按 roadmap 阶段或 plan 必需任务计算；不得把主观百分比当作验收证据。
- Judge `pass` 不等于真实回归 UAT 通过。
