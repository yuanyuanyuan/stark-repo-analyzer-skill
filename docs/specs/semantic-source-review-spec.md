# 风险驱动的源码语义抽查规格

## Problem Statement

Evidence-First v2 已能机械验证关键单元是否具有 `file:line` 锚点和实质设计判断，但只能验证字段形状，不能确认源码是否真的支持该判断。错误、错位或装饰性的锚点仍可能被计入覆盖率并进入最终报告，使“可审计”退化成“格式正确”。用户需要一种成本受预算约束、可追溯、不会恢复 v1 全量阅读的源码语义抽查机制。

## Solution

在 Phase 7 增加风险驱动的 Semantic Source Review。模块分析完成后，由主 Agent 或串行运行中的独立复核阶段重新读取被抽样关键单元的源码 span，对照当前锚点和设计判断，记录源码实际表达的事实，并只把得到 `supported` 结论的抽查计入质量门。

语义抽查记录进入 core 模块的机器可读 Evidence Matrix。现有 `gate` 作为唯一测试与放行 seam，机械检查抽查记录是否引用当前 analyzed unit、锚点和判断是否与 coverage 记录一致、源码观察是否存在、verdict 是否为 `supported`，以及当前模式是否达到抽样预算。gate 不尝试理解源码语义，也不引入 LLM judge。

当抽查发现判断只被部分支持或不被支持时，Agent 必须修正判断或把单元降级为 unanalyzed / open question，再重新抽样；未解决的语义抽查不得进入最终合成。

## User Stories

1. 作为架构报告读者，我希望抽样锚点确实支持对应设计判断，从而不会被格式正确但语义错误的证据误导。
2. 作为分析使用者，我希望语义抽查集中在影响最大的结论上，从而不恢复全量源码阅读成本。
3. 作为快速模式使用者，我希望只抽查少量全局高风险结论，从而保留快速分析的成本边界。
4. 作为标准模式使用者，我希望每个 core 模块至少有一个设计判断被独立复核，从而避免单个模块完全依赖原分析者自证。
5. 作为深度模式使用者，我希望每个 core 模块的角色、主流程和关键权衡得到代表性复核，从而提高深度报告的可信度。
6. 作为维护者，我希望抽查记录引用稳定 unit ID，从而可以追溯到 coverage 分母中的具体单元。
7. 作为维护者，我希望抽查锚点和判断与当前 coverage 记录完全一致，从而防止复核后又悄悄替换结论。
8. 作为维护者，我希望抽查记录包含源码实际表达的观察，从而让人类可以复核 Agent 的 verdict。
9. 作为维护者，我希望 gate 对缺失、错位和未支持的抽查记录给出逐项失败原因和关联 unit，从而可以直接修复。
10. 作为分析 Agent，我希望抽查失败时有明确处理路径，从而知道应修正判断、降低覆盖状态还是保留开放问题。
11. 作为无 subagent 运行时的使用者，我希望在模块分析完成后以独立串行复核 pass 执行相同要求，从而不降低质量标准。
12. 作为有 subagent 运行时的使用者，我希望主 Agent 优先复核其他 Agent 产出的判断，从而减少同一推理过程的确认偏差。
13. 作为报告读者，我希望未解决的 partial / unsupported 判断不会出现在确定性叙事中。
14. 作为发布维护者，我希望该机制复用现有 Evidence Matrix、coverage 和 gate 工件，从而不增加新的 CLI 或固定 drafts 文件体系。
15. 作为测试维护者，我希望通过 gate 的公开输入输出验证行为，而不是测试内部抽样函数或命令拼装。
16. 作为审计者，我希望 quick、standard、deep 的抽样数量和范围可从工件中检查，从而证明模式差异不是只改名称。

## Implementation Decisions

- 最高公共测试 seam 是现有 `repo-analyzer gate`：输入 coverage、core Evidence Matrix 和报告草稿，输出逐项 gate 结果与最终合成决定。
- 每个 core Evidence Matrix 增加 `semantic_reviews` 数组。每条记录表达 stable unit ID、当前锚点、当前设计判断、源码观察和 verdict；这些是 gate 与人工审计所需的最小字段。
- 只有 `verdict: supported` 的记录满足语义抽查。partial 或 unsupported 必须先修正判断、降级单元或转为开放问题，再产生与当前状态一致的新抽查记录。
- gate 确认记录引用 analyzed unit，且抽查中的 anchor 与 judgment 必须逐值匹配 coverage 中当前字段；孤立、过期或重复记录不计数。
- gate 只验证抽查契约和预算，不判断自然语言是否正确。源码语义判断仍由 Agent 完成，不增加 LLM judge、外部 API 或私有服务。
- quick 模式抽查全局影响最高的 2–3 个 analyzed unit；优先覆盖跨模块、引用不完整、风险相关或影响最终批判性评价的判断。
- standard 模式每个 core 模块至少抽查 1 个 analyzed unit。
- deep 模式每个 core 模块至少抽查 3 个代表性 analyzed unit；单元不足时抽查该模块全部 analyzed unit。
- 有 subagent 时，主 Agent 优先复核模块 Agent 的判断；无 subagent 时，在模块分析结束后开启独立串行复核 pass，并继续记录 `parallelism: degraded`。
- 抽查失败时，最终报告、Matrix 和 coverage 必须保持一致；被降级的单元仍留在分母中，不得通过删除单元解决。
- 现有质量报告新增独立的 semantic source review 检查项，列出模式阈值、已满足数量、失败原因和关联 unit。
- 分析哲学不变：Why > What、风险抽样、跨模块验证和叙事分析继续由模型完成。

## Testing Decisions

- 测试只经过 `gate` CLI 及其机器可读报告观察行为，不直接测试内部 helper。
- 使用现有代表性 JavaScript fixture 和 coverage / Matrix 工件模式，扩展语义抽查数据。
- 覆盖缺少 `semantic_reviews`、未知 unit ID、非 analyzed unit、锚点不一致、判断不一致、空源码观察、非 supported verdict 和重复抽样。
- 在同一 fixture 上验证 quick、standard、deep 的抽样预算差异。
- 验证任何未解决 semantic review 都阻止最终合成，并在质量报告中给出 unit 证据。
- 验证修正判断或降级单元、重新抽样后可以通过 gate，且未覆盖单元仍保留在分母中。
- 增加端到端人工可读 fixture：故意提供与源码不符的设计判断，确认复核流程会打回；修正后完整 v2 工件链可放行。
- 沿用现有测试原则：断言外部工件与退出状态，不断言内部命令或函数调用顺序。

## Out of Scope

- 恢复 v1 的固定 drafts 文件体系。
- 对所有 analyzed unit 做全量语义复核。
- 使用 LLM judge 自动给设计判断打分。
- 让确定性 gate 自行解释源码或判断自然语言真实性。
- 强制用户确认报告大纲、无限轮次提问或恢复固定等待时长。
- 恢复 Star、Fork、贡献者等非架构元数据为必填项。
- 新增外部服务、API key、daemon 或 graphify 硬依赖。
- 改变关键单元分母、覆盖率阈值或 Why > What 分析哲学。

## Further Notes

这一机制降低的是“锚点掺水”风险，不提供数学意义上的真实性证明。它通过独立复核 pass、风险优先抽样、稳定 unit 对齐和可审计源码观察，提高发现错位结论的概率，同时保持 v2 的注意力预算。

固定文件数量、固定等待分钟数和固定写入分块不是本规格的质量目标；运行时可以根据自身能力处理这些可靠性细节。
