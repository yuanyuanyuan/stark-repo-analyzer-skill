# Tickets: v1.2 Evidence Plan

为 repo-analyzer 的 v1.2 Evidence Plan 计划层增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.2-evidence-plan.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 Evidence Plan 的最小行为契约

**What to build:** repo-analyzer 明确知道 Evidence Plan 是模块深读前的轻量 Markdown 计划，字段包含模块、架构问题、候选证据范围、必需证据类型、风险路径和预期判断范围；同时保留 v1.1 源码锚点要求，并明确不引入 CLI、JSON schema、自动生成或 Evidence Matrix。

**Blocked by:** None — can start immediately.

- [x] Evidence Plan 被描述为模块深读前的计划层产物，而不是新的工具链产物。
- [x] 最小字段包含模块、架构问题、候选文件或入口、必需证据类型、风险路径和预期判断范围。
- [x] 明确继承源码锚点要求，并排除 CLI、JSON schema、自动生成和 Evidence Matrix。

## 把 Evidence Plan 嵌入模块规划阶段

**What to build:** 主 agent 在启动 subagent 前，能在现有模块规划草稿里为每个核心模块产出 Evidence Plan；用户可以先看到每个模块要回答什么问题、准备查哪些候选入口、边界在哪里，而不是只看到模块清单或文件列表。

**Blocked by:** 确立 Evidence Plan 的最小行为契约.

- [x] 模块规划阶段要求为每个核心模块先写 Evidence Plan。
- [x] Evidence Plan 可以嵌入现有模块规划草稿，不新增复杂产物链。
- [x] Evidence Plan 必须包含架构问题，不能退化成文件列表。

## 让 subagent 按模块 Evidence Plan 深读源码

**What to build:** 每个 subagent 的任务输入都包含对应模块的 Evidence Plan，使 subagent 围绕架构问题、候选证据、风险路径和预期判断范围阅读源码；不同模块的阅读范围更清楚，减少重复盲读。

**Blocked by:** 把 Evidence Plan 嵌入模块规划阶段.

- [x] 核心模块 subagent prompt 引用对应模块的 Evidence Plan。
- [x] subagent prompt 使用 Evidence Plan 限定阅读目标、候选证据和风险路径。
- [x] 分工说明强调减少重复盲读，而不是要求扩大阅读范围。

## 让模块草稿回应 Evidence Plan

**What to build:** subagent 草稿不只是补源码锚点，而是要明确回应 Evidence Plan 中的问题；如果候选文件不足、风险路径未验证或判断范围需要收窄，草稿需要标出限制或开放问题。

**Blocked by:** 让 subagent 按模块 Evidence Plan 深读源码.

- [x] 模块草稿必须回应 Evidence Plan 中的架构问题。
- [x] 候选证据不足时，草稿将相关内容降级为限制、假设或开放问题。
- [x] 草稿保留 v1.1 的源码锚点要求，不把无锚点内容写成确定性结论。

## 补齐 v1.2 人工验收清单

**What to build:** 维护者可以用代表性仓库手工验收 v1.2：检查核心模块启动前是否都有 Evidence Plan、计划是否包含架构问题而不只是文件列表、subagent 草稿是否回应计划、候选范围是否降低无目的阅读，并且不要求 Markdown 格式逐字一致。

**Blocked by:** 让模块草稿回应 Evidence Plan.

- [x] 验收清单覆盖核心模块启动前是否存在 Evidence Plan。
- [x] 验收清单检查 Evidence Plan 是否包含架构问题，而不仅是候选文件。
- [x] 验收清单检查 subagent 草稿是否回应 Evidence Plan。
- [x] 验收标准只要求字段语义完整，不要求 Markdown 格式逐字一致。

## 同步用户文档中的 v1.2 工作流说明

**What to build:** README/中文 README 或同类用户入口能说明 v1.2 的新增行为：分析会先形成模块 Evidence Plan，再分配 subagent 深读；用户理解这是计划层增强，不是新工具链或质量门。

**Blocked by:** 补齐 v1.2 人工验收清单.

- [x] 用户文档说明模块 Evidence Plan 会出现在 subagent 深读之前。
- [x] 用户文档说明 Evidence Plan 是轻量 Markdown 计划层增强。
- [x] 用户文档不暗示已引入新 CLI、JSON schema、Evidence Matrix 或硬质量门。

---

# Tickets: v1.3 Evidence Matrix

为 repo-analyzer 的 v1.3 Evidence Matrix 增量拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.3-evidence-matrix.to-spec.md`，并参考 `docs/specs/evidence-first-repo-analyzer-spec.slim.md` 中 Evidence-First Pipeline 的长期方向。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 v1.3 Evidence Matrix 的最小行为契约

**What to build:** repo-analyzer 明确把 Evidence Matrix 定义为核心模块草稿里的 Markdown 证据结构，字段包含模块角色、入口点、核心数据结构、主流程、跨模块依赖、关键设计决策、风险点、源码证据、开放问题；同时明确它必须回应 v1.2 Evidence Plan、继承 v1.1 源码锚点要求，并且 v1.3 不引入 JSON、自动 gate 或新 CLI。

**Blocked by:** None — can start immediately.

- [x] Evidence Matrix 被描述为核心模块草稿中的 Markdown 证据结构，而不是新的机器可读产物。
- [x] 最小字段包含模块角色、入口点、核心数据结构、主流程、跨模块依赖、关键设计决策、风险点、源码证据和开放问题。
- [x] 明确 Evidence Matrix 必须回应 v1.2 Evidence Plan 中的问题，并继承源码锚点要求。
- [x] 明确 v1.3 不引入 JSON、自动 quality gate、新 CLI 或 `module-evidence` 产物。

## 让核心模块 subagent 先产出 Evidence Matrix

**What to build:** 每个核心模块 subagent 的任务输入和输出约束都要求草稿先写 Evidence Matrix，再写叙事分析；用户能在模块草稿里稳定看到结构化证据，而不是只看到散文式模块分析。

**Blocked by:** 确立 v1.3 Evidence Matrix 的最小行为契约.

- [x] 核心模块 subagent prompt 要求先写 Evidence Matrix，再写叙事分析。
- [x] Evidence Matrix 要求覆盖最小字段，并以字段语义完整为准，不绑定具体 Markdown 排版。
- [x] 草稿中的关键判断必须带源码锚点，无证据内容必须降级为限制、假设或开放问题。
- [x] 草稿必须显式回应对应 Evidence Plan 中的架构问题。

## 让 Evidence Matrix 覆盖次要模块的简化路径

**What to build:** 次要模块批量分析不被迫使用完整核心模块矩阵，但仍保留简化 Evidence Matrix，至少表达职责、入口或涉及文件、关键证据、风险或开放问题；这样 v1.3 覆盖“次要模块可以简化”的决策，不把它误实现成全量硬要求。

**Blocked by:** 确立 v1.3 Evidence Matrix 的最小行为契约.

- [x] 次要模块分析说明支持简化 Evidence Matrix。
- [x] 简化矩阵至少保留职责、入口或涉及文件、关键证据、风险或开放问题。
- [x] 次要模块的特别判断仍需源码锚点，无锚点内容降级为观察或假设。
- [x] 文档明确简化路径只适用于次要模块，不能削弱核心模块要求。

## 在交叉验证阶段检查 Evidence Matrix 缺口

**What to build:** 主 agent 在最终合成前能逐个检查模块草稿是否包含 Evidence Matrix、必需字段是否语义完整、源码证据是否有锚点、开放问题是否保留，并把缺口反馈给对应草稿，而不是直接合成最终报告。

**Blocked by:** 让核心模块 subagent 先产出 Evidence Matrix; 让 Evidence Matrix 覆盖次要模块的简化路径.

- [x] 交叉验证阶段检查每个核心模块草稿是否包含 Evidence Matrix。
- [x] 交叉验证阶段检查 Evidence Matrix 是否覆盖所有必需字段。
- [x] 交叉验证阶段检查源码证据字段是否包含锚点。
- [x] 交叉验证阶段检查开放问题是否被保留，而不是静默丢弃。
- [x] 缺口处理方式是补充草稿或降级结论，不是直接进入最终合成。

## 用 Evidence Matrix 支撑最终报告合成

**What to build:** 主 agent 合成最终报告时，能基于各模块 Evidence Matrix 对比模块角色、入口、主流程、跨模块依赖、风险和开放问题，发现冲突或缺口，并避免把未验证内容写成确定性结论。

**Blocked by:** 在交叉验证阶段检查 Evidence Matrix 缺口.

- [x] 最终报告合成步骤要求先对比各模块 Evidence Matrix。
- [x] 跨模块依赖、风险点和开放问题会进入合成前判断，而不是只读取叙事段落。
- [x] Evidence Matrix 中未解决的问题不会在最终报告中被写成确定性结论。
- [x] 最终报告仍保持 Why > What 的叙事深度，不退化为矩阵字段拼接。

## 补齐 v1.3 人工验收清单

**What to build:** 维护者可以用代表性仓库手工验收 v1.3：检查每个核心模块草稿是否包含 Evidence Matrix、字段是否完整、是否引用 Evidence Plan 问题、源码证据是否有锚点、开放问题是否保留、最终报告是否能基于矩阵合成；验收关注字段语义，不要求 Markdown 排版逐字一致。

**Blocked by:** 用 Evidence Matrix 支撑最终报告合成.

- [x] 验收清单覆盖每个核心模块草稿是否包含 Evidence Matrix。
- [x] 验收清单覆盖 Evidence Matrix 必需字段的语义完整性。
- [x] 验收清单覆盖 Evidence Matrix 是否回应 Evidence Plan 问题。
- [x] 验收清单覆盖源码证据锚点和开放问题保留情况。
- [x] 验收清单覆盖最终报告是否能基于 Evidence Matrix 合成。
- [x] 验收标准不要求 Markdown 排版逐字一致。

## 同步用户文档中的 v1.3 工作流说明

**What to build:** README/中文 README 或同类用户入口说明 v1.3 的新增行为：核心模块草稿会先提交 Markdown Evidence Matrix，主 agent 会用它做合成前检查；同时避免暗示已引入 `module-evidence/*.json`、quality gate、自动解析或新工具链。

**Blocked by:** 补齐 v1.3 人工验收清单.

- [x] 用户文档说明核心模块草稿会包含 Markdown Evidence Matrix。
- [x] 用户文档说明 Evidence Matrix 用于主 agent 合成前对比和发现缺口。
- [x] 用户文档说明 v1.3 仍不引入 JSON、自动 quality gate、自动解析或新 CLI。
- [x] 用户文档与 v1.2 Evidence Plan 说明保持衔接，不把 Evidence Matrix 描述成计划层替代品。

---

# Tickets: v1.4 Unsupported Claims

为 repo-analyzer 的 v1.4 Unsupported Claims 可信度增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.4-unsupported-claims.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 Unsupported Claims 最小行为契约

**What to build:** repo-analyzer 明确在最终报告前必须检查核心确定性结论的证据状态；没有源码锚点、文档证据或外部一手来源的内容不得写成确定性结论，只能进入假设、开放问题、限制说明或 unsupported area；并明确 v1.4 仍是人工/流程级检查，不实现自动检测或机器可读质量报告。

**Blocked by:** None — can start immediately.

- [x] Unsupported Claims 被描述为最终报告前的证据状态检查，而不是自动质量门。
- [x] 没有源码锚点或文档证据的结论不得进入确定性叙事。
- [x] 未验证内容的合法去处被限定为假设、开放问题、限制说明或 unsupported area。
- [x] 明确 v1.4 不实现自动扫描、LLM judge、硬阻塞或 quality-gate-report。

## 在最终合成阶段执行 Unsupported Claims 检查

**What to build:** 主 agent 在合成最终报告前系统检查核心结论与跨模块推断的证据状态；跨模块推断在交叉验证前保持待验证；Evidence Matrix 中的开放问题不会静默消失；缺少证据的判断被降级，而不是被放大成确定性结论。

**Blocked by:** 确立 Unsupported Claims 最小行为契约.

- [x] 最终合成阶段要求检查核心确定性结论是否有源码锚点或文档证据。
- [x] 跨模块推断在主 agent 交叉验证前保持待验证状态。
- [x] Evidence Matrix 中的开放问题会进入最终合成阶段，而不是被静默丢弃。
- [x] 无证据判断会被移动到开放问题、限制说明或 unsupported area。

## 补齐 v1.4 人工验收清单

**What to build:** 维护者可以用代表性仓库手工验收 v1.4：抽查最终报告中的核心结论是否都有证据、无证据判断是否被降级、开放问题是否进入合成、跨模块结论是否经过主 agent 验证；测试重点是最终报告行为，而不是内部草稿措辞。

**Blocked by:** 在最终合成阶段执行 Unsupported Claims 检查.

- [x] 验收清单覆盖最终报告核心结论是否都有证据。
- [x] 验收清单覆盖无证据判断是否被降级为开放问题或限制说明。
- [x] 验收清单覆盖 Evidence Matrix 开放问题是否进入最终合成。
- [x] 验收清单覆盖跨模块结论是否经过主 agent 验证。
- [x] 验收标准关注最终报告行为，不要求内部草稿措辞逐字一致。

## 同步用户文档中的 v1.4 工作流说明

**What to build:** README/中文 README 或同类用户入口说明 v1.4 的新增行为：最终报告会区分已验证结论、合理假设和开放问题；无证据内容不会被写成确定性结论；同时避免暗示已引入自动检测、LLM judge 或硬质量门。

**Blocked by:** 补齐 v1.4 人工验收清单.

- [x] 用户文档说明报告会区分已验证与未验证内容。
- [x] 用户文档说明无证据结论会被标记或降级，而不是静默写成事实。
- [x] 用户文档说明 v1.4 仍是流程级检查，不引入自动 gate 或硬阻塞。
- [x] 用户文档与 v1.3 Evidence Matrix 说明保持衔接，不把 unsupported claims 描述成矩阵替代品。

---

# Tickets: v1.5 Risk Sampling

为 repo-analyzer 的 v1.5 Risk Sampling 风险路径抽样增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.5-risk-sampling.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立风险路径抽样最小行为契约

**What to build:** repo-analyzer 明确每个核心模块必须识别并抽样至少一条与该模块相关的风险路径；抽样结果包含抽样对象、源码锚点、发现结果和对架构评价的影响；不相关类别需说明不适用；并明确不要求风险类别全覆盖、自动识别或安全/并发扫描工具。

**Blocked by:** None — can start immediately.

- [x] 风险路径抽样被描述为每个核心模块的必做流程，而不是可选旁注。
- [x] 风险类别范围覆盖错误处理、配置、插件/扩展点、缓存、并发、权限与安全边界、generated/vendor/test 边界等。
- [x] 每个抽样结果必须包含抽样对象、源码锚点、发现结果和影响说明。
- [x] 不存在相关风险类别时必须说明为什么不适用。
- [x] 明确 v1.5 不要求全覆盖、自动识别、安全扫描器或硬质量门。

## 让核心模块 subagent 执行风险路径抽样

**What to build:** 每个核心模块 subagent 的任务输入和草稿约束都要求执行风险路径抽样，使模块分析不只覆盖主流程；抽样结果进入 Evidence Matrix 或模块草稿的专门小节，用户能在草稿中看到边界条件与风险路径证据。

**Blocked by:** 确立风险路径抽样最小行为契约.

- [x] 核心模块 subagent prompt 要求执行至少一条相关风险路径抽样。
- [x] 风险抽样结果进入 Evidence Matrix 或模块草稿专门小节。
- [x] 风险抽样包含源码锚点，不能只写抽象风险标签。
- [x] 不相关风险类别在草稿中给出不适用理由。

## 让最终报告批判性评价引用风险抽样

**What to build:** 主 agent 汇总各模块风险抽样结果，并在最终报告的批判性评价中引用这些发现；风险路径证据影响对缺陷、边界和工程成熟度的判断，而不是只停留在模块草稿里。

**Blocked by:** 让核心模块 subagent 执行风险路径抽样; 在最终合成阶段执行 Unsupported Claims 检查.

- [x] 最终报告合成步骤要求汇总风险抽样结果。
- [x] 最终报告的批判性评价引用风险抽样证据，而不是只复述 happy path。
- [x] 风险抽样中的未验证推断仍受 unsupported claims 规则约束，不得被放大成确定性结论。
- [x] 风险发现对架构评价的影响在最终报告中可见。

## 补齐 v1.5 验收清单并同步用户文档

**What to build:** 维护者可以手工验收每个核心模块是否有风险抽样记录、是否含源码锚点、是否影响最终评价、不适用类别是否有理由；同时用户文档说明报告会覆盖风险路径，且该能力仍是文档规则而非自动扫描。

**Blocked by:** 让最终报告批判性评价引用风险抽样.

- [x] 验收清单覆盖每个核心模块是否有风险抽样记录。
- [x] 验收清单覆盖风险抽样是否包含源码锚点。
- [x] 验收清单覆盖风险抽样是否影响最终报告评价。
- [x] 验收清单覆盖不适用风险类别是否有理由说明。
- [x] 用户文档说明报告会覆盖风险路径，而不只是主流程。
- [x] 用户文档说明 v1.5 仍是文档规则，不引入自动风险扫描器。

---

# Tickets: v1.6 Budget Profiles

为 repo-analyzer 的 v1.6 Budget Profiles 预算档重定义拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.6-budget-profiles.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立快速/标准/深度预算档契约

**What to build:** 快速、标准、深度模式被重定义为 evidence 数量、风险抽样强度、报告长度、subagent 数量上限和外部调研强度的组合；模式差异不再由“读多少行”决定，而由“回答多少关键问题、提供多少证据、抽样多少风险、输出多深报告”决定；不要求精确 token 统计。

**Blocked by:** 补齐 v1.5 验收清单并同步用户文档.

- [x] 快速模式聚焦核心路径和核心模块，风险抽样最小，报告较短。
- [x] 标准模式覆盖核心模块、关键边界和主要设计决策，风险抽样标准。
- [x] 深度模式扩展到次要模块、边缘路径和替代方案，风险抽样增强。
- [x] 每个模式声明 evidence 深度、风险抽样强度、报告长度、subagent 数量上限和外部调研强度。
- [x] 明确 v1.6 不要求精确 token 统计或自动 token 中断。
- [x] 明确 v1.6 继承 v1.1 到 v1.5 的全部行为。

## 把预算档写入分析模式与执行记录

**What to build:** 分析模式选择真正驱动主 agent 与 subagent 的证据深度、风险抽样强度和输出边界；每次分析记录预算目标和实际执行摘要；超预算时缩小范围、降低深度或显式说明原因，使成本控制成为可观察的工作流契约。

**Blocked by:** 确立快速/标准/深度预算档契约.

- [x] 模式选择影响 evidence 深度、风险抽样强度和报告长度，而不是只改名称。
- [x] subagent prompt 或任务输入体现当前模式的证据读取预算。
- [x] 每次分析记录预算目标和实际执行摘要。
- [x] 超预算时缩小范围、降低深度或显式说明原因。

## 补齐 v1.6 验收清单并同步用户文档

**What to build:** 维护者可用同一仓库分别运行快速、标准、深度模式，比较输出差异；用户文档说明各模式的成本边界与加深方向，让用户理解额外成本花在哪里。

**Blocked by:** 把预算档写入分析模式与执行记录.

- [x] 验收清单覆盖同仓三模式输出的相对差异。
- [x] 验收清单检查快速模式是否减少 evidence 数量和报告长度。
- [x] 验收清单检查标准模式是否保留核心模块和关键权衡。
- [x] 验收清单检查深度模式是否增加风险路径和替代方案分析。
- [x] 验收清单检查每次分析是否记录预算目标和实际执行摘要。
- [x] 用户文档说明三模式差异由 evidence 深度和成本边界定义，而不是行覆盖率。
- [x] 用户文档说明不提供精确 token 计费或自动中断。

---

# Tickets: v1.7 Markdown Repo Map

为 repo-analyzer 的 v1.7 Markdown Repo Map 轻量仓库地图增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.7-markdown-repo-map.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 Markdown Repo Map 最小行为契约

**What to build:** 分析前生成 Markdown Repo Map，包含目录结构、语言分布、入口候选、manifest、核心文档、测试/generated/vendor 候选和高风险区域候选；它只提供候选信号，不直接写最终架构结论；使用现有系统命令和人工整理，不引入 scan CLI、JSON schema、生态命令或 graphify 硬依赖。

**Blocked by:** 补齐 v1.6 验收清单并同步用户文档.

- [x] Repo Map 被描述为深读前的轻量仓库地图，而不是最终架构结论。
- [x] Repo Map 最小字段覆盖目录结构、语言分布、入口候选、manifest、核心文档、测试/generated/vendor 候选和高风险区域候选。
- [x] Repo Map 只能提供候选信号，不能直接写最终架构结论。
- [x] 明确使用现有系统命令和人工整理，不执行生态命令。
- [x] 明确不引入 scan CLI、JSON schema、graphify 硬依赖或符号枚举器。

## 用 Repo Map 驱动 Evidence Plan 与阅读范围

**What to build:** 主 agent 用 Repo Map 生成 Evidence Plan，使架构问题和候选入口更贴近仓库事实；generated/vendor/test 候选影响后续阅读范围，subagent 能理解自己负责的文件在全局中的位置，减少从 README 或目录名直接猜模块边界。

**Blocked by:** 确立 Markdown Repo Map 最小行为契约.

- [x] 分析前生成 Repo Map，并作为 Evidence Plan 的输入。
- [x] Evidence Plan 引用 Repo Map 的候选入口和模块信息。
- [x] generated/vendor/test 候选影响后续阅读范围，避免把低价值区域当核心源码。
- [x] Repo Map 不越权写成最终架构结论。

## 补齐 v1.7 验收清单并同步用户文档

**What to build:** 维护者可以验收 Repo Map 是否存在且字段完整、是否只写候选信号、Evidence Plan 是否引用它、排除区域是否影响阅读范围；用户文档说明深读前会先生成仓库地图，且该步骤保持低依赖、只读、无新 CLI。

**Blocked by:** 用 Repo Map 驱动 Evidence Plan 与阅读范围.

- [x] 验收清单覆盖 Repo Map 是否存在并包含必要字段。
- [x] 验收清单覆盖 Repo Map 是否只写候选信号，不写最终架构结论。
- [x] 验收清单覆盖 Evidence Plan 是否引用 Repo Map 候选入口和模块信息。
- [x] 验收清单覆盖 generated/vendor/test 候选是否影响后续阅读范围。
- [x] 用户文档说明分析前会生成 Markdown Repo Map。
- [x] 用户文档说明 Repo Map 不引入新 CLI、JSON schema 或生态命令。

---

# Tickets: v1.8 Soft Quality Gate

为 repo-analyzer 的 v1.8 Soft Quality Gate 软质量门增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.8-soft-quality-gate.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 Soft Quality Gate 最小行为契约

**What to build:** 最终报告前必须生成 Markdown 质量门摘要，检查 Evidence Matrix 完整性、源码锚点、风险抽样、unsupported claims、预算执行和 Repo Map 使用情况；每个检查项标记通过、未通过或不适用；未通过项不硬阻塞报告生成，但必须进入开放问题、限制说明或 unsupported area。

**Blocked by:** 补齐 v1.7 验收清单并同步用户文档.

- [ ] Soft Quality Gate 被描述为最终报告前的 Markdown 质量门摘要，而不是硬阻塞 CLI。
- [ ] 质量门检查项覆盖 Evidence Matrix、源码锚点、风险抽样、unsupported claims、预算执行和 Repo Map 使用。
- [ ] 每个检查项必须标记通过、未通过或不适用。
- [ ] 未通过项必须有原因和后续处理位置。
- [ ] 明确未通过项不硬阻塞报告生成，也不要求 JSON 或 gate CLI。

## 生成质量门摘要并把未通过项反射进最终报告

**What to build:** 主 agent 在合成前产出可审计的质量门摘要，并基于实际草稿与证据填写检查结果；所有未通过项进入最终报告的开放问题、限制说明或 unsupported area，使用户能看到报告哪些部分可信、哪些存在缺口。

**Blocked by:** 确立 Soft Quality Gate 最小行为契约.

- [ ] 最终报告前生成 Markdown 质量门摘要。
- [ ] 质量门摘要覆盖全部必需检查项，并引用实际草稿和证据，而不是空泛打勾。
- [ ] 未通过项进入最终报告的限制说明、开放问题或 unsupported area。
- [ ] 质量门不阻止最终报告生成。

## 补齐 v1.8 验收清单并同步用户文档

**What to build:** 维护者可以验收每次分析是否生成质量门摘要、是否覆盖必需检查项、未通过项是否进入最终报告、摘要是否引用真实草稿；用户文档说明软质量门让质量缺口可见，但不阻断分析完成，并为后续 v2.0 硬 gate 提供规则样本。

**Blocked by:** 生成质量门摘要并把未通过项反射进最终报告.

- [ ] 验收清单覆盖是否生成质量门摘要。
- [ ] 验收清单覆盖质量门是否覆盖全部必需检查项。
- [ ] 验收清单覆盖未通过项是否进入最终报告限制说明或开放问题。
- [ ] 验收清单覆盖质量门是否引用实际草稿和证据。
- [ ] 用户文档说明最终报告前会有软质量门摘要。
- [ ] 用户文档说明未通过项可见但不硬阻塞，也不引入 JSON gate 或 LLM judge 自动评分。

---

# Tickets: v1.9 Key Unit Coverage Pilot

为 repo-analyzer 的 v1.9 Key Unit Coverage Pilot 关键单元覆盖率试点拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.9-key-unit-coverage-pilot.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立关键单元覆盖率试点契约

**What to build:** 引入关键单元覆盖率试点，定义关键单元可包括入口点、核心数据结构、公共 API、状态定义、配置定义和关键跨模块依赖；每个单元记录是否已锚定分析、源码锚点、设计判断和未覆盖原因；覆盖率用于审计和学习，不作为硬门控；不要求 ctags、ast-grep、graphify、稳定单元 id 或自动枚举分母。

**Blocked by:** 补齐 v1.8 验收清单并同步用户文档.

- [ ] 关键单元覆盖率被描述为 v1.x 试点，而不是 v2.0 硬 schema。
- [ ] 关键单元类型覆盖入口点、核心数据结构、公共 API、状态/配置定义和关键跨模块依赖。
- [ ] 每个关键单元记录是否已锚定、源码锚点、设计判断和未覆盖原因。
- [ ] 覆盖率用于审计和学习，不作为硬阻塞。
- [ ] 明确不要求稳定单元 id、自动枚举分母、ctags/ast-grep/graphify 或 units/gate CLI。

## 在代表性分析中产出关键单元清单与覆盖摘要

**What to build:** 主 agent 与 subagent 在分析中产出关键单元清单和覆盖摘要；已覆盖单元同时具备源码锚点和实质设计判断；未覆盖单元有原因；清单可用来检查模块分析是否忽略入口、数据结构或状态定义，使覆盖率可审计而不是一个不透明数字。

**Blocked by:** 确立关键单元覆盖率试点契约.

- [ ] 代表性分析产出关键单元清单与覆盖摘要。
- [ ] 已覆盖单元同时具备源码锚点和设计判断。
- [ ] 未覆盖单元记录未覆盖原因。
- [ ] 主 agent 可用关键单元清单检查模块分析完整性。
- [ ] 清单可用 Markdown 或轻量 JSON，但不绑定硬 schema。

## 补齐 v1.9 试点验收并沉淀 v2.0 反馈

**What to build:** 维护者在代表性仓库上验收关键单元是否覆盖入口、数据结构、状态/配置和关键依赖，并对比关键单元覆盖率与旧行覆盖率哪个更能解释报告可信度；将试点结论沉淀为对 v2.0 `coverage-units` schema、doctor 检查项和 gate 规则的反馈；用户文档标明这是试点边界，不是硬门控。

**Blocked by:** 在代表性分析中产出关键单元清单与覆盖摘要.

- [ ] 验收清单覆盖关键单元是否包含入口点、核心数据结构、状态/配置和关键依赖。
- [ ] 验收清单覆盖已覆盖单元是否同时具备锚点和设计判断。
- [ ] 验收清单覆盖未覆盖单元是否有原因。
- [ ] 试点结果包含与旧行覆盖率的对比判断，说明哪个更能解释报告可信度。
- [ ] 试点结论沉淀为 v2.0 coverage-units / doctor / gate 的可执行反馈。
- [ ] 用户文档说明关键单元覆盖率仍是试点，不作为硬阻塞，也不要求符号枚举器。
