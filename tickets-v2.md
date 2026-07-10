# Tickets: Evidence-First Repo Analyzer v2

将 repo-analyzer 从 v1 的文档型流程升级为 Evidence-First v2：以确定性工具获取候选证据，以关键单元覆盖和质量门保证可审计性，同时保留 Why > What 的深度分析。来源规格：`docs/specs/evidence-first-repo-analyzer-spec.slim.md`。

v1.8 和 v1.9 的历史试点 tickets 不构成 v2 的阻塞条件；其经验由本计划的端到端验收吸收。

Work the **frontier**: any ticket whose blockers are all done.

## 交付 v2 Doctor 预检命令

**What to build:** 分析开始前，使用者可以运行预检并得到机器可读的工具、语言、写权限与可选 graphify 状态；缺少符号枚举器时流程明确阻塞并给出修复指引。

**Blocked by:** None — can start immediately.

- [ ] 成功和失败路径都生成带逐项 pass/fail 的预检报告。
- [ ] 预检检查基础命令、至少一种符号枚举器、目标语言支持和工作目录写权限。
- [ ] 必需条件未满足时不允许进入后续分析，并输出可执行修复指引。
- [ ] graphify 状态被记录但不可用时不阻塞预检。

## 交付确定性仓库扫描与 Repo Map 数据

**What to build:** 通过纯确定性扫描产出文件、语言、模块规模、manifest、候选入口、文档、排除范围及风险候选，供后续分析使用。

**Blocked by:** 交付 v2 Doctor 预检命令.

- [ ] 扫描产出完整、可机器读取的仓库地图数据。
- [ ] 扫描从 manifest 派生依赖信息，且不执行生态命令。
- [ ] 输出区分源码、文档、测试、generated 与 vendor 候选范围。
- [ ] 输出只包含候选信号，不包含确定性架构结论。

## 交付关键单元枚举与覆盖率分母

**What to build:** 使用者可得到稳定、可审计的关键单元清单、模块分级、引用边、解析失败清单和解析率，作为后续覆盖率计算的分母。

**Blocked by:** 交付确定性仓库扫描与 Repo Map 数据.

- [ ] 仅接受 universal-ctags 或 ast-grep 作为关键单元的最小枚举能力。
- [ ] 同一提交重复执行时，关键单元标识稳定。
- [ ] 产物记录模块分级、parsed/unparsed 文件、引用边来源和引用完整性。
- [ ] 不使用正则表达式作为关键单元分母的降级路径。

## 交付面向 LLM 的 Repo Map 摘要

**What to build:** 扫描数据可压缩为包含候选信号、来源和待验证问题的 Markdown 输入，减少模型在源码中的盲读。

**Blocked by:** 交付确定性仓库扫描与 Repo Map 数据.

- [ ] 摘要可由扫描数据稳定生成。
- [ ] 摘要包含候选入口、模块、文档、排除范围和待验证问题。
- [ ] 摘要不产生确定性架构结论。
- [ ] 摘要可作为后续 Evidence Plan 的直接输入。

## 接入 v2 Evidence-First 分析工作流

**What to build:** repo-analyzer 按 v2 阶段使用预检、Repo Map、Evidence Plan、模块分级和预算档；无 subagent 的运行时可串行执行，但不降低证据要求。

**Blocked by:** 交付关键单元枚举与覆盖率分母; 交付面向 LLM 的 Repo Map 摘要.

- [ ] 分析流程无法绕过 Doctor 直接进入源码分析。
- [ ] Evidence Plan 明确架构问题、候选证据、分工和时间/token 预算。
- [ ] Evidence Plan 调整模块分级时，覆盖率记录同步更新。
- [ ] 无 subagent 运行时记录串行降级，但维持同一套证据与覆盖率要求。
- [ ] Why > What、源码锚点、风险抽样和叙事分析哲学被保留。

## 交付机器可读的模块 Evidence Matrix

**What to build:** 每个核心模块同时具备机器可检查的证据记录和叙事分析，关键单元可回填锚点、设计判断与未覆盖原因。

**Blocked by:** 接入 v2 Evidence-First 分析工作流.

- [ ] 每个核心模块产出机器可读的 Evidence Matrix。
- [ ] 记录模块角色、入口、核心结构、流程、依赖、决策、风险、证据和开放问题。
- [ ] 已分析关键单元同时具备源码锚点和实质设计判断。
- [ ] 未分析关键单元保留在分母中，并记录未覆盖原因。

## 交付确定性质量门

**What to build:** 最终报告合成前，使用者可得到包含通过/失败、关联证据和放行决定的质量门报告。

**Blocked by:** 交付关键单元枚举与覆盖率分母; 交付机器可读的模块 Evidence Matrix.

- [ ] 质量门机械检查 Evidence Matrix、锚点、覆盖率、必填字段和 unsupported 标记。
- [ ] 覆盖率只在单元状态、锚点和实质判断同时具备时计入分子。
- [ ] core 模块的未解析范围或引用不完整的跨模块结论被显式暴露为 unsupported area 或开放问题。
- [ ] 质量门报告记录每项结果、失败原因、关联证据和是否允许合成最终报告。

## 完成 v2 端到端验收、基准与发布同步

**What to build:** 在代表性仓库上完成可复现的 v2 运行、失败路径验证、graphify 缺失验证、三档预算差异验证，并同步对外文档、版本信息和发布边界。

**Blocked by:** 交付 v2 Doctor 预检命令; 交付确定性仓库扫描与 Repo Map 数据; 交付关键单元枚举与覆盖率分母; 交付面向 LLM 的 Repo Map 摘要; 接入 v2 Evidence-First 分析工作流; 交付机器可读的模块 Evidence Matrix; 交付确定性质量门.

- [ ] 代表性仓库运行产出规格要求的全部 v2 工件。
- [ ] 测试覆盖 Doctor 成功/失败、可选 graphify 缺失、覆盖率双硬条件、未解析 core 区域和质量门失败报告。
- [ ] 在同一 fixture 上验证快速、标准、深度模式的预算和深度差异。
- [ ] 完成新旧流程最小对比：耗时、近似 token、核心模块遗漏和质量指标之一。
- [ ] 用户文档、版本信息与发布内容声明 breaking v2，且不包含维护者本机 hook 或绝对路径。
