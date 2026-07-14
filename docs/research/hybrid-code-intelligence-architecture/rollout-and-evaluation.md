# 混合代码智能的评估与 Rollout 计划

状态：仅为研究提案。本文定义如何比较和逐步放量，不授权实现变更，也不构成真实 UAT。

rollout 指“经过分阶段证据门逐步扩大使用范围”，不是功能开发阶段。直觉上像先在试验场、影子环境和少量真实流量中逐级验证；类比的边界是，每一级都有冻结指标和自动回滚条件，不能凭主观感觉升级。

迁移前的完整英文版本保留在
[`docs/archive/research-source/hybrid-code-intelligence-architecture/rollout-and-evaluation.en.md`](../../archive/research-source/hybrid-code-intelligence-architecture/rollout-and-evaluation.en.md)，用于追溯逐项指标。

## 一、要验证的决策

候选 V2 使用 Git `SourceUniverse` 定义语料真源，Graphify `0.9.13 --code-only` 提供常驻本地静态图，确定性算法进行 hotspot 排序，Repomix 提供有界上下文，最终证据由 Agent 直接读取 source range。Serena + 已批准 OSS LSP 只做可选精度解析；Joern 只回答显式 deep-dataflow 问题。

实验只回答一个问题：

> 与 V1 相比，V2 能否降低分析成本、耗时和重复源码阅读，同时不降低模块边界准确性、跨目录流程召回、来源可追溯性和可重复性？

目录结构只是 inventory evidence，不能直接成为模块边界。即使更便宜，只把顶层目录改成 Agent 任务也算实验失败。

## 二、V1 保持不变

在本文全部 V2 gate 通过前，V1 仍是发布和默认路径。V2 工件必须使用独立工作区，不能覆盖、修复或补充 V1 运行；两个路径分析同一固定 commit，并保持目标仓库不变。

V2 失败、超时、不确定或缺少工件时，要启动一次全新、干净的 V1，而不是从部分可信的 V2 partition 继续。不能为了让 V2 更容易胜出而降低 V1 验收口径。

这里的 benchmark、shadow 和 canary 都是实验评估证据，不是“真实 UAT”。真实 UAT 仍必须完整遵守 [`docs/dev-rules/real-uat-regression/README.md`](../../dev-rules/real-uat-regression/README.md)；静态比较、中断运行、复制输出或只有目录形状都不能证明通过。

## 三、对比路径

### Path A：V1 对照组

不做修改地运行当前 V1 standard 流程，保留所有正常工件和失败分类。

### Path B：V2 候选组

1. 固定并记录 source identity。
2. 生成 Git `SourceUniverse` manifest，覆盖 tracked、untracked-not-ignored、dirty identity 和纳入/排除理由。
3. 每次都在本地运行 Graphify `0.9.13 --code-only`，记录为 `graphify-code-only`，禁止 semantic/LLM backend。
4. 与 `SourceUniverse` 对账：`outside_manifest` 阻塞；`missing_from_graph` 必须分类。
5. 根据 manifest、静态图、entrypoint、公开 surface、跨目录 edge、history、unresolved relation 和问题相关性计算确定性 hotspot，并在 Agent 规划前冻结 raw feature 与 ranking。
6. 用明确非空文件列表构建有界 Repomix pack；核心实现、争议 edge 和最终 citation 直接读取 source range。
7. 在最终 Agent 分工前评估 optional precision；Serena 只允许批准的 OSS LSP，ctags/ast-grep 作为声明过的 fallback，无法解析时记录 unresolved。
8. 生成业务/数据流模块和 shared-file ownership matrix，再执行模块分析、交叉验证、覆盖率和报告融合。

Path B 必须同时保存 precision 前后的 graph/hotspot 与模块提案，否则无法测量 precision 的 false positive、false negative 和被丢弃的规划成本。Joern 不进入 standard A/B matrix。

## 四、固定语料与运行矩阵

使用六个固定仓库和 commit：`click`、`httpx`、`ruff`、`codex-plugin-cc`、`claude-code`、`codex`。每个仓库对 Path A 和 Path B 各独立运行两次，总计：

```text
6 repositories x 2 paths x 2 runs = 24 independent runs
```

独立运行要求 fresh work directory，不复用 graph、module plan、draft、summary、prompt cache 或历史裁决；source commit、模式、brief、语言、model policy、工具版本和资源限制保持一致。每个仓库随机化路径顺序，分别记录 run ID、log、metadata 和 manifest。

如果 Path A 被必需 gate 阻塞，要保留真实 blocked 结果，不能用 fixture 或 partial graph 替代。该仓库不能参与成对的完成质量比较，但 availability、time-to-block 和 failure class 仍是有效运维证据。

任何影响 V2 `SourceUniverse` 策略、Graphify 版本/config、对账、hotspot 特征/权重、Repomix 策略、precision 规则、Agent ownership 或评分 rubric 的实质变化，都会使旧 Path B 结果失效，必须重跑完整 24-run matrix。

## 五、Gold Set 与裁决

Gold set 是冻结的参考答案包，不是绝对真理。每个仓库在查看候选结果前冻结：参考模块计划/报告、关键端到端 flow、跨目录边界、合法 shared file、不能直接提升为业务模块的基础设施路径、高影响结论及源码位置、已知限制。

两名独立 reviewer 以匿名随机顺序评审 Path A/B。模块分类为 matched、justified split、justified merge、unsupported 或 omitted；flow edge 记录两端责任、传递合同/数据、源码证据和置信度。争议最终回到固定 commit 的源码裁决，没有来源可定位证据的 prose assertion 不能胜出。

## 六、必需指标

### 质量与准确性

- 业务模块 precision、recall、F1；关键 flow edge recall，跨目录 edge 单列。
- `SourceUniverse` 与 Graphify 对账：expected file、graph file、已分类 `missing_from_graph` 和 `outside_manifest`。
- gold entrypoint、shared file、cross-boundary edge 的 hotspot recall，以及重复运行的 rank correlation。
- unsupported module、基础设施误判、shared-file 边界错误。
- citation 有效性、claim-to-source traceability、交叉验证修正、未解决跨 Agent 冲突和关键遗漏。
- 把静态阅读误写成 runtime/test 结论的次数。

源码阅读覆盖率不是测试覆盖率，两者必须分别报告。

### 成本与时间

- 按阶段/Agent 记录 model input/output token、tool call 和 Agent turn。
- V1 Graphify semantic/deep 调用与 provider cost；V2 code-only 本地计算、图规模，并证明 provider cost 为零。
- optional precision 与 deep-only Joern 成本单列，不能混进 standard。
- Repomix bytes/token、compression ratio 和 over-budget retry。
- 端到端 wall time、首个可用 module plan 时间、inventory、Graphify、对账、ranking、packing、source reading、cross-validation、finalization 和人工裁决时间。

### 重复阅读与协调

把每次源码阅读规范化为 `(commit, path, line interval, agent, phase)`，记录总请求行、唯一行、跨 Agent 重复率、shared file 重读、主 Agent 复读、ownership collision、未分配范围和冲突。重叠 range 必须先做 union，不能按 Agent 重复累加覆盖率。

### Optional Precision 质量

Graphify code-only 在 Path B 中常驻，不属于 escalation。Serena/OSS-LSP、ctags 或 ast-grep 只有在其经源码裁决的结果改变关键模块/流程、修正重要边界、消除同名 symbol 歧义，或解决影响所有权/叙事的动态注册等问题时，才算“materially needed”。

每次决策记录 TP/FP/TN/FN、reason code、当时可见证据、adapter/backend 和 threshold。不能用决策之后才出现的证据倒推合理性。Joern 在 standard 路径中的任何意外调用都是架构违规，不是 TP。

### 可重复性与安全

比较两次运行的 module membership、critical flow edge、Graphify 对账、hotspot rank、precision 决策、source coverage、成本/时间变异、目标树清洁度、越界写入和 failure class。模块名称、成员和关键 edge 是核心结果，不能像物理 normalization 那样排除。

## 七、晋级阈值

阈值必须在首个 scored run 前冻结；看到结果后改阈值会使整个矩阵失效。

### 强制质量门

- 每个完成运行的关键模块/流程遗漏为 0；冻结的跨目录关键 flow recall 为 100%。
- 基础设施目录误判为核心业务模块为 0；重要 claim 的可定位源码证据为 100%。
- 静态证据误标 runtime/test validation 为 0。
- module F1 相比 Path A：aggregate 降幅不超过 0.02，单仓库不超过 0.05。
- high-severity 跨 Agent 冲突不增加。
- `outside_manifest` 为 0，`missing_from_graph` 分类率为 100%。
- 冻结的关键 entrypoint、shared file 和 cross-boundary edge 全部进入裁决后的 hotspot set。
- optional precision FN 为 0；两次决策一致，除非差异可追溯到已记录外部失败。
- standard A/B matrix 中 Joern 调用为 0。

任一失败都自动 no-go，成本节省不能抵消质量失败。

### 可重复性门

- module membership Jaccard >= 0.85；critical flow edge Jaccard >= 0.90，冻结关键 edge 完全一致。
- hotspot top-k rank correlation >= 0.85，且不漏关键 hotspot。
- `outside_manifest` 完全一致，`missing_from_graph` 分类没有无法解释的漂移。
- aggregate source-reading coverage 差异不超过 5 个百分点，除非两次都超过阈值且排除范围一致。
- failure class 不发生无法解释的变化。

### 效率门

质量和可重复性通过后，Path B 还必须达到：median model token 至少降低 20%，median wall time 至少降低 20%，median duplicate-read ratio 至少降低 25%；单仓库成本/耗时回退不超过 10%，除非 V2 恢复了已记录的 V1 blocker；optional precision FP rate <= 25%。

质量通过但效率未通过，仍然不能替代 V1，只能带着证据回到研究阶段。

## 八、Rollout 阶段

### Stage 0：Offline Benchmark

完成并裁决 24-run matrix，V1 不变，候选结果不面向用户。退出条件是指标完整、reviewer 签署、晋级结论可由存储数据复算。

### Stage 1：V2 Shadow

对符合条件的 standard 分析并行运行 V2，但只交付 V1。至少收集 20 组成对完成分析，并覆盖单包库、多包应用和大型 monorepo；blocked pair 仍计入可靠性分母。所有 precision 分歧、对账失败、blocked、低置信 partition 和至少 25% 普通 pair 都要复核。

### Stage 2：Internal Canary

最多把 5% opt-in 内部 standard 分析交给 V2 主结果；前 10 个 canary 并行运行 V1 作为即时 fallback，并明确标记 canary，不得称 UAT。连续 10 个 canary 无关键问题后最多升到 15%；每一级至少保持一个完整 review window。

退出需要至少 30 个完成 canary、与 offline benchmark 相同的质量门、稳定运维指标，以及 analyzer-skill owner 和 acceptance-rule owner 的明确 go 决定。

### Stage 3：Default Consideration

canary 完成不会自动成为默认。还需要更新产品/验收文档、明确 V1 工件兼容策略，并单独执行完整真实 UAT campaign。在真实 UAT 实际完成前，只能说 V2 通过 benchmark/shadow/canary，不能说通过真实 UAT。

## 九、No-Go 与自动回滚

出现关键模块/流程遗漏、precision FN、Graphify 越出 manifest、关键漏图未分类、semantic/backend 调用、standard 中未声明 Joern、基础设施误判、伪造/无效证据、重复计算覆盖率、源码树变更、越界写入、依赖 fixture/partial graph 声称通过，或无法复现 ranking/模块/流程时，停止晋级并保留证据。

canary 中出现一次关键准确性失败、一次 precision FN、一次 source/workspace 边界违规、一次未声明 Joern，或最新 10 个可比 canary 的 p95 耗时/token 高于 V1 超过 20% 时，立即把 V2 allocation 降为 0%，交付或重跑 V1。不得把部分 V2 工件并入 V1；恢复 canary 前必须完成根因审查、冻结新候选并重跑 24-run matrix。

## 十、每次运行必须保存什么

每条运行记录至少包含：path/stage、run ID、固定输入、commit/dirty state、tool/model version、资源限制、外部命令与分类退出、`SourceUniverse` manifest、Graphify code-only 命令/图/config digest/无 semantic backend 证明、语料对账、hotspot raw feature/weight/rank、Repomix 非空文件列表与预算、precision 前后提案、escalation reason/threshold/query、直接 source read、ownership matrix、normalized read interval、草稿/交叉验证/覆盖率/最终报告、时间/token/cost/retry/failure、目标树边界检查和 reviewer 裁决。

不得记录 secret 和私有 provider 配置。Path B 的 Graphify metadata 必须是本地 `graphify-code-only`；出现 provider/backend identity 是失败，不是普通元数据。

## 十一、最终决策报告

报告先展示逐仓库质量，再展示 Graphify 对账与 hotspot、precision 错误、可重复性、成本/时间/重复阅读、失败和限制。必须同时展示两次独立运行，不能只给平均数；deep-only Joern 单独成节，不能混入 standard aggregate。

最终建议只能是：**进入 shadow**、**进入 canary**、**等待更多证据**、**修订后重跑**或**拒绝**。本计划不能得出“已通过真实 UAT”。

## 主线总结

V2 只有在“质量不退步、结果可重复、效率显著提升”三组门全部通过后，才能从 benchmark 逐步进入 shadow 和 canary。每一级都保留 V1、保留失败证据并设置自动回滚；真实 UAT 始终是独立验收，不能被实验数据替代。
