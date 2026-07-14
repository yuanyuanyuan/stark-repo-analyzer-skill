# V1 执行与证据边界

**记录日期：** 2026-07-13
**状态：** 已基于现有文档整理；不是新的 UAT 运行结果。
**范围：** `stark-repo-analyzer-skill` V1 的 Graphify 结构证据、物理基线与验收表述。

## 可复用经验

### 1. 图谱产物必须隔离，且健康检查是分析前提

**经验：** Graphify 的输出只能写入本次分析工作目录；在正式分析前后都要执行 doctor。空图、缺少可定位来源或不完整报告不能作为结构证据，也不能靠手写报告补足。

**为什么：** 目标仓库污染会破坏“只读分析”承诺；仅有 `graph.json` 或 `GRAPH_REPORT.md` 也不能证明图谱可用。

**证据：**

- [执行记录：问题 1 与问题 2](../goal-execution-record.md#1-graphify-output-could-cross-the-source-boundary)
- [真实 UAT 规则：必备证据与禁止假通过](../../../dev-rules/real-uat-regression/README.md)
- [doctor 实现](../../../../acceptance/doctor.sh)

**适用范围：** 所有通过本项目 skill 执行的源码分析。
**反例/边界：** `graphify-out/` 目录存在本身不构成通过；必须以 doctor 的实际结果和保存的运行证据为准。

### 2. Graphify 用于导航，源码负责裁决

**经验：** 将图谱关系按 `EXTRACTED`、`INFERRED`、`AMBIGUOUS` 区分：核心路径的 `EXTRACTED` 仍须回到源码核对；`INFERRED` 只可作为待验证项；`AMBIGUOUS` 只可作为风险或问题。

**为什么：** 图谱能缩短定位时间，但不能替代对源码行为、边界和冲突的判断。

**证据：**

- [目标：Graphify 与源码裁决边界](../../v1-control-plane/stark-repo-analyzer-v1-implementation.md#graphify-and-doctor-boundaries)
- [真实 UAT 规则：禁止假通过](../../../dev-rules/real-uat-regression/README.md)

**适用范围：** 分析报告中的架构关系、模块协作与风险结论。
**反例/边界：** 这不是运行时测试覆盖率，也不能推导动态行为正确性。

### 3. 失败运行必须保留失败分类，不能被后续文字“修复”

**经验：** 当 Graphify 长时间运行但未生成验收所需的图谱和报告时，分类应保持为中断/失败。不得用手写、fixture 或参考输出替代真实运行产物；恢复路径也必须保存原始证据链。

**为什么：** 结果可审计比“凑齐一份报告”更重要。否则后续比较无法区分真实产物、恢复产物和人工补写内容。

**证据：**

- [执行记录：恢复路径与原始证据](../goal-execution-record.md#3-resume-needed-to-preserve-raw-graphify-evidence)
- [执行记录：Ruff 语义提取失败](../goal-execution-record.md#4-ruff-repeatedly-stalled-during-semantic-extraction)
- [真实 UAT 规则：禁止假通过](../../../dev-rules/real-uat-regression/README.md)

**适用范围：** 所有 physical run、重试和 `resume`。
**反例/边界：** 记录了失败原因不等于已经定位根因；本项目对 Ruff 的既有记录明确拒绝无证据地归因到特定 HTTP、模型或内存问题。

### 4. code-only 是独立证据模式，不能替代未完成的语义模式

**经验：** Ruff 的 code-only 续跑可以证明静态 AST/代码关系产物及其 doctor 检查通过，但不能追溯性地将语义提取标成成功，也不构成与语义 run-1 的 P4 可重复性通过。

**为什么：** 两种模式的提取能力、失败面和输出含义不同；混合比较会夸大结论。

**证据：**

- [执行记录：Ruff code-only continuation](../goal-execution-record.md#7-ruff-code-only-continuation)
- [V1 目标状态与未完成边界](../../v1-control-plane/stark-repo-analyzer-v1-implementation.md#status)

**适用范围：** `graphify-code-only` 标记的运行与报告。
**反例/边界：** code-only 不是语义 Graphify 的等价替代，也不是 P5 动态验证。

### 5. 物理运行证据、报告深度与项目完成状态必须分开表述

**经验：** `physical-runs/` 可以证明固定输入下真实入口调用和产物谱系；它不自动证明与 `reference-runs/` 报告同等深度。P4 需要同一固定输入的两次独立快照和通过的比较；在此之前，不得宣称可重复性通过。当前 V1 总体仍不完整。

**为什么：** 固定输入的执行成功、报告语义质量、隔离性和重复性是不同维度；将它们合并成“项目已完成”会制造假通过。

**证据：**

- [执行记录：报告保真度差异](../goal-execution-record.md#7-physical-baseline-report-depth-differs-from-reference-reports)
- [物理基线：当前证据边界](../../../baseline/physical-baseline.md#current-evidence-boundary)
- [V1 目标状态](../../v1-control-plane/stark-repo-analyzer-v1-implementation.md#status)
- [真实 UAT 规则：P2/P4 证据](../../../dev-rules/real-uat-regression/README.md)

**适用范围：** 发布判断、基线比较与对外/对内进度报告。
**反例/边界：** P5 已明确不在 V1 范围内；这不表示已经完成动态验证。

## 当前待验证观察

1. HTTPX、Claude Code 与 Codex 已有 run-2 快照，但现有记录不支持 P4 通过声明；目标输出隔离问题也仍需按既有规则处理。
2. Ruff 的语义提取失败原因已定位到“语义提取阶段”，但没有足够证据归因到某个具体外部服务故障。
3. 后续任何“V1 ready”结论应先复核 `docs/goals/stark-repo-analyzer-v1-implementation.md`、物理基线和真实 UAT 规则，而不是仅查看目录是否存在。

## 维护动作

当一次任务产生可复用结论时，新增一张经验卡并至少填写：结论、为什么、证据、适用范围、反例/边界。仅有原始会话记录时，先保留为观察，待仓库证据或真实运行结果支持后再升级为经验。
