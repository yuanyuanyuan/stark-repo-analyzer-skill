# Repo Analyzer 与 Graphify 简化路线图

状态：`completed`

已完成执行计划：
[`graphify-simplification-plan.md`](../exec-plans/graphify-simplification-plan.md)

## 北极星目标

交付一个忠实保留参考 `repo-analyzer` 分析方法的仓库分析 skill，并将程序化控制面收缩为低侵入的 Graphify 结构证据闸门。Graphify 只负责 code-only 建图、来源规范化、健康验证和导航 map；模块划分、源码阅读、Why > What、覆盖率、交叉验证和最终报告继续由 Agent 流程负责。

用户最终只接收一份 `ANALYSIS_REPORT.md`。Graphify 证据和分析草稿保留在隔离工作区，用于审计，不扩张为第二套正式交付物。

## 目标行为

- 未指定模式时使用 `standard` 并在输入无实质歧义时一键执行。
- 用户明确要求深度分析时使用 `deep`，快速扫描后只进行一轮集中询问。
- 本机存在兼容 Graphify 时执行增强流程；建图开始后的执行或健康门失败必须终止，不能静默回退。
- Graphify 缺失或不兼容时只提供安装指引，由用户选择安装后复检或本次进入无 Graphify 的原版兼容流程。
- Graphify 始终使用 `0.9.13+` code-only 路径，不调用 semantic extraction、provider、模型探测或 semantic chunking。
- Graphify 候选必须回到源码裁决；图谱不能决定最终模块边界或替代源码证据。
- subagent 不可用时必须暂停并取得用户同意，不能自动顺序降级或降低质量门槛。
- 超大型仓库可以使用显式有界范围，但必须披露纳入、排除、理由和覆盖率分母。

## 非目标

- 不恢复 `quick` 模式。
- 不建设独立分析平台、调度服务或新的完整 Python 分析控制面。
- 不把 `analyze`、`finalize`、`validate`、`resume` 作为普通用户产品路径。
- 不把 Graphify semantic/LLM 能力重新引入强制流程。
- 不把六项目完整基线作为日常开发的强制完成条件。
- 不在 Git 中长期保存大型图谱、缓存、完整运行目录或长转录。
- 不删除历史 ADR 来制造从未发生过的设计一致性。

## 权威边界

- 产品术语以 `CONTEXT.md` 为准。
- 产品输入输出合同以 `docs/spec/input-output-contract.md` 为准。
- 当前架构决定以 ADR-0016 至 ADR-0019、ADR-0021 至 ADR-0024 为准。
- 开发与验收声明以 `docs/dev-rules/` 为准。
- 逐文件迁移细节可参考
  [`graphify-simplification-file-plan.md`](../archive/v1-control-plane/graphify-simplification-file-plan.md)，但该文件不是活动控制面。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| G0 控制面收敛 | 建立唯一活动 roadmap、执行计划和进度记录 | 活动入口可从 `AGENTS.md` 唯一定位，旧控制面和执行记忆集中到 `docs/archive/` |
| G1 合同对齐 | 统一 skill、公开规格、README、领域语言与活动 ADR | 静态扫描不存在活动 `quick`、semantic/provider、自动安装、静默降级或旧用户命令语义 |
| G2 薄 Graphify gate | 将 Python 收缩为单一 Graphify gate | 缺失依赖返回 `10`；有效规范化图返回 `0`；执行或健康失败返回 `30`；目标仓库保持只读 |
| G3 Skill 与聚焦验收 | 保留参考 Agent 流程并证明关键分支 | 单元测试、skill 合同检查和聚焦 UAT 覆盖模式、安装选择、健康门和 subagent 降级边界 |
| G4 仓库收敛 | 移除旧控制面和已外置的大型生成证据 | Git 不再跟踪缓存、完整运行目录、`.meta-kim` 或 `__pycache__`，活动文档无失效引用 |
| G5 发布验收 | 在发布前或用户明确要求时执行真实回归 UAT | 按 ADR-0022 和 `docs/dev-rules/real-uat-regression/` 从用户等价入口完成规定流程并保存可核验证据 |

完成状态：G0 至 G4 全部通过，实施主线完成度为 `5/5`。完成证据记录在关联 progress 文档中。

G5 发布验收尚未触发。它不属于 G0-G4 实施完成度；准备发布或用户明确要求时，必须建立新的活动执行计划并按真实 UAT 规则运行，不能把本 roadmap 的 `completed` 状态解释为发布就绪。

## 完成口径

实施主线完成以 G0-G4 五个阶段全部通过为准。G5 是独立的发布就绪门：未触发 G5 时可以声明“实施主线完成、真实回归未执行”，但不能声明发布级真实回归通过。

任何完成状态都必须分别报告：主线阶段、实际执行的验证、未执行的验收、阻塞项和下一刀。百分比只按 G0-G4 或活动计划中的必需任务计算，可选治理和未来扩展不得混入分母。

## 取代关系

本 roadmap 取代以下活动控制用途，但保留其历史内容：

- `docs/archive/v1-control-plane/goals.txt`
- `docs/archive/v1-control-plane/stark-repo-analyzer-v1-implementation.md`
- `docs/archive/v1-control-plane/reimplementation-decomposition.md`

归档的 `tasks.txt` 和旧 Graphify 逐文件方案的执行权由活动 exec plan 取代。
