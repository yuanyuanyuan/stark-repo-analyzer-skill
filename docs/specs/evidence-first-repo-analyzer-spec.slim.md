# Evidence-First Repo Analyzer Spec (Slim)

> 精简稿。基于第一性原理剔除了不在核心因果链上的机制（缓存、重型 benchmark、行覆盖率辅助指标、生态命令、LOC 精度工具），并把 graphify 从硬阻塞降为可选增强。原始详稿见 [evidence-first-repo-analyzer-spec.md](/Users/chuzu/projests/stark-repo-analyzer-skill/docs/specs/evidence-first-repo-analyzer-spec.md)。

## First Principle

这个 skill 不可再分的目标只有一个：

```text
用最小的 LLM 注意力，产出证据锚定、深度不降的架构报告。
```

一切机制只有落在这条因果链上才保留。当前病根是质量目标和“读大量源码”绑定：旧流程用 `Read` 行覆盖率当主质量门，50W 行仓库天然进入高 token、高耗时路径。

## Solution

把 repo-analyzer 从“覆盖率驱动的大量源码阅读”升级为 **Evidence-First Analysis Pipeline**：

1. 确定性工具先生成 repo map，而不是让 LLM 盲读源码。
2. LLM 基于 repo map 提架构问题和假设。
3. Evidence Matrix 约束每个模块必须提交的证据链。
4. Budget Profiles 控制阶段、模块、并行的时间和 token。
5. Quality Gates 验证结论准确性、反证抽样和跨模块一致性。

核心原则：**改变证据获取方式，不改变原 skill 的分析哲学**。

```text
旧：为了达到覆盖率，读大量源码。
新：为了回答架构问题，读取最小但关键的源码证据。
```

这是一个 **breaking v2**：优先保证可靠证据链和可审计质量门，不再承诺 v1 的“纯 skill 文档开箱即用”。必备工具缺失时分析阻塞并引导修复，不降级到低可信路径（此原则全文只声明一次，后续不再重复）。

原 repo-analyzer 的精华必须原样保留：Why > What、代码为准、全局关联、自适应问题、深度模块分析、批判性评价、叙事连贯。

## Coverage Redefinition (核心杠杆)

把“覆盖率”的度量单位从**读取的源码行占比**改成**已分析并锚定的关键代码单元占比**。

```text
覆盖率 = 已分析并锚定的关键代码单元数 / 该模块关键代码单元总数
```

旧行覆盖率承担三个职责，全部保留：防跳过（不对核心模块一句带过）、防空谈（结论必须有代码依据）、可审计（百分比 + 明细表可核）。问题只在**分母**——用“读了多少行”近似“理解程度”，与质量目标错位。新定义只换分母单位，三个职责不变。

三个要点：

1. **分母 = 关键代码单元**，由符号枚举器（`universal-ctags` 或 `ast-grep`，二选一即可）机器枚举，包含：导出/公共符号、入口点（main、路由/命令/事件注册）、核心数据结构与类型、跨模块调用边、状态与配置定义点。私有小工具、样板、生成代码、vendor 不进分母。
2. **分子“已锚定” = 双硬条件**（缺一不计入）：草稿中对该单元有 `文件:行号` 锚点；且有一句实质设计判断（角色/流程/权衡三者之一），不是“这里有个函数”。
3. **阅读方式为锚点驱动**：工具定位单元，只读该单元 span（定义 + 紧邻上下文 + 其跨文件引用两端），不要求整文件通读。

分档从“行百分比”重解释为“关键单元百分比”：

| 模式 | 核心模块关键单元覆盖 | 次要模块关键单元覆盖 |
|------|--------------------|--------------------|
| 快速 | ≥ 30% | ≥ 10% |
| 标准 | ≥ 60% | ≥ 30% |
| 深度 | ≥ 90% | ≥ 60% |

覆盖率明细表列头：

```text
模块 | 关键单元总数 | 已锚定分析数 | 覆盖率% | 未覆盖单元及原因 | 达标 ✅/❌
```

关键单元清单落盘为 `coverage-units.json`，agent 只能在集合上标记 `analyzed / unanalyzed`，不能删条目；判某单元不重要必须写一行理由，接受质量门抽查。

### Key-Unit Schema

`coverage-units.json` 的字段级契约，供 `units` 产出、`gate` 机械校验。`units` 写机器可判定字段，agent 只回填分子字段（`status` / `anchor` / `judgment` / `skip_reason`），不得改动 `units` 写的字段。

顶层：

```text
repo         : { path, commit, skill_version, mode }   # 缓存与审计元信息
modules[]    : 模块分级数组 [{name, path_globs, classification, reason, source}]
units[]      : 关键单元数组（见下）
parsed[]     : 成功解析的文件相对路径
unparsed[]   : 未解析的文件相对路径（沉默失败盲区）
parse_rate   : parsed / (parsed + unparsed)
```

`modules[].classification` 只能是 `core | secondary | excluded`，用于决定覆盖率分档。分类可以由 `scan` 候选信号、Phase 4 计划或用户目标共同确定，但必须落盘为结构化记录；`gate` 只读取该记录，不在检查时临时推断。`excluded` 必须写明理由，且不得用来绕过核心模块覆盖率。

每个 unit：

```text
id           : 稳定单元 id，如 "src/x.ts:handleRequest:function:<hash>" # units 写
file         : 相对路径                                            # units 写
line         : 定义起始行（可选 end_line）                          # units 写
symbol       : 符号名                                              # units 写
type         : export | entrypoint | datastruct | type
               | cross_ref_target | state | config                 # units 写（枚举）
module       : 所属模块                                            # units 写
refs         : 跨文件引用边 [{file, line, dir, source, confidence}] # units 写（锚点驱动读 span 的依据）
refs_status  : complete | partial | missing                        # units 写
churn        : git 改动热度分（用于排序，可选）                     # units 写
status       : analyzed | unanalyzed                              # agent 回填
anchor       : "文件:行号"（分子硬条件 1）                          # agent 回填
judgment     : 实质设计判断文本（分子硬条件 2，角色/流程/权衡）      # agent 回填
skip_reason  : 判为不重要时必填的一行理由                           # agent 回填
```

`refs[].source` 可为 `ctags | ast-grep | rg | graphify`，`confidence` 可为 `exact | heuristic`。graphify 缺失时允许 `refs_status == partial` 或 `missing`，但最终报告必须把跨模块关系的不确定性显式标出，不能假装拥有完整图谱。

`gate` 的判定规则（确定性、无需 LLM）：

- 计入分子当且仅当 `status == analyzed` **且** `anchor` 非空 **且** `judgment` 非空。三者缺一即视为 `unanalyzed`。
- `status == unanalyzed` 且无 `skip_reason` 的核心单元触发覆盖率不足告警；有 `skip_reason` 也仍留在分母中，只改变审计说明，不提高覆盖率。
- `judgment` 长度或结构不足（纯罗列、复述符号名）由 Phase 7 抽查用 LLM 复核并可打回，`gate` 只做存在性和覆盖率的机械检查。
- 单元只能被标记，不能被删除；`units` 每次重跑对同一 `commit` 必须产出稳定 `id`，以支持增量与审计。
- core 模块存在未解析源码文件时，`gate` 必须 fail，除非最终报告把对应路径标为 `unsupported area` 且不对该区域做覆盖充分声明。

这个 schema 是 `units` 与 `gate` 之间的唯一契约面：`judgment` 字段把"实质设计判断"从模块草稿显式拉进单元记录，`gate` 才能在不读叙事的前提下确定性地判"已锚定"。

### 覆盖率风险与缓解

1. **分母注水**（缩小分母刷覆盖率）：分母只能由确定性工具枚举并落盘，agent 不能删条目，判不重要须写理由并抽查。
2. **工具漏解析（沉默失败）**：枚举结果必须同时报告 `parsed` 与 `unparsed` 清单，解析率本身作为要报告的指标；doctor 校验目标仓库主要语言被枚举器支持。
3. **锚点掺水**（贴行号但判断为空）：分子双硬条件写死；质量门抽查已锚定单元是否含实质判断，纯罗列打回重算。
4. **锚点驱动丢失全局关联**：单元 context span 必须尽量包含其跨文件引用边；Evidence Matrix 的“跨模块依赖”与“协同”字段强制不变。引用边缺失或只有启发式结果时，必须以 `refs_status` 和报告中的 unsupported area 暴露不确定性。
5. **可审计性**：`coverage-units.json` 使每个数字可追到具体单元，审计从“数行”变成“查表”，透明度不降。

行覆盖率**退役**：不计算、不落盘、不作为任何指标，避免 agent 重新往行数上锚。

## Deterministic Tool Contract

确定性工具负责机械扫描、候选定位、统计和索引。它们帮 LLM 找候选证据，但不产出最终架构结论。

```text
Deterministic tools may identify candidates, but may not produce final architectural conclusions.
Every architectural conclusion must still be verified against source snippets, docs, or external primary sources.
```

### Implementation Carrier

v2 新增一组最小 CLI / scripts，用确定性代码承担无需智力判断的步骤，LLM 只负责架构问题生成、证据解释、权衡判断和最终叙事：

- `doctor`：检查必备命令、符号枚举器可用性、目标仓库语言支持、工作目录写入权限，输出 `doctor-report.json`。
- `scan`：生成文件清单、语言分布、LOC（粗略即可）、docs/config/dependency 索引（直接读 manifest，不执行生态命令）、generated/test/vendor 排除清单，输出 `repo-map.json` 的机械部分。
- `units`：用符号枚举器枚举关键代码单元，输出 `coverage-units.json` 初始分母、`parsed` / `unparsed` 清单和解析率。
- `summarize`：把扫描结果压缩成 LLM 可消费的 `repo-map.md` 草稿；只写候选信号，不写最终结论。
- `gate`：读取 Evidence Matrix、`coverage-units.json` 和报告草稿，执行可机械检查的质量门（缺失锚点、覆盖率不足、必填字段缺失、未支持声明标记）。

这些脚本是 workflow contract 的一部分。测试优先验证外部产物，不测内部 shell 命令细节，除非命令本身被写入契约。

### Baseline Tools

默认基础能力，优先使用，缺失时降级到同类系统命令：

| 目标 | 首选 | 降级 |
|------|------|------|
| 文件发现 | `rg --files` | `find` |
| 文本搜索 | `rg` | `grep` |
| 行数统计 | `wc -l` | shell loop |
| Git 元信息 | `git` | 无 |
| 结构化 JSON | `jq` | shell/awk |

依赖信息从已索引的 manifest（`package.json`、`Cargo.toml`、`go.mod`、`pyproject.toml` 等）派生，不执行生态命令（`npm ls` / `cargo metadata` 等）——那会引入本机 toolchain 依赖且是冗余。

### Required Symbol Enumerator (二选一)

关键单元枚举的最小必需依赖，`universal-ctags` 或 `ast-grep` **任一可用即可**，由 doctor 保证。缺失时阻塞并引导安装，不降级到正则分母。

| 工具 | 用途 |
|------|------|
| `universal-ctags` | 提取函数/类/接口/类型/导出符号，并提供引用边 |
| `ast-grep` | AST 模式搜索：入口模式、调用模式、框架惯例、精确关键单元标定 |

`git` 提供改动热度信号，用于给关键单元排序（高频改动通常是核心），不作为分母来源。

### Graph Intelligence Tool (graphify，可选增强)

graphify 提供 god node、社区结构、跨文件关系，是**可选增强，不是硬依赖**。分母所需的跨文件引用边由符号枚举器提供，因此 graphify 缺失不阻塞分析。

- 可用则用 `graphify query` / `graphify path` / `graphify explain` 做 scoped 查询，禁止把完整 `graph.json` / `GRAPH_REPORT.md` 注入 context。
- 不可用则跳过图谱增强，覆盖率与质量门不受影响。
- 理由：graphify 体量大、跨机器安装摩擦高；把它列为硬阻塞会抬高首次使用门槛，而它提供的能力对“证据锚定的架构报告”是加分项，不是必需项。

### Tool Availability Policy

仍然禁止作为分析依赖的：

- 大型数据库索引器（作为分析主依赖）
- 需要长期 daemon 的服务
- 需要 API key 的工具
- 在**分析扫描阶段**修改源码、安装依赖、运行迁移或启动生产服务的命令

doctor 的安装/配置协助属于分析前、经用户确认的 setup 环节，与“分析扫描阶段只读”不冲突。

### Runtime Compatibility

一条原则即可，不展开逐运行时矩阵：

```text
确定性工作放进运行时无关的 CLI（doctor/scan/units/summarize/gate 必须可运行）。
交互方式与并行度可以降级；Evidence Matrix、覆盖率与其它质量门永不降级。
standard/deep 完整验收额外要求真实多子代理记录；parallelism: degraded 不能冒充完整通过。
```

- 无 subagent 的运行时：主 agent 按 `evidence-plan.md` 串行执行同一套 Evidence Matrix 和 coverage gate，记录 `parallelism: degraded`；standard/deep 此时只能判部分通过/机械链路通过，见 `docs/specs/v2.0-multi-agent-acceptance.md`。
- 无结构化提问工具的运行时：用普通对话完成关键确认，不静默采用会改变分析目标的假设。
- 不能运行最小 CLI / scripts 的运行时：v2 分析不可开始。

### Generated Artifacts

workflow 至少生成以下本地产物；确定性 CLI 产出扫描与覆盖率基础数据，LLM / subagent 只回填 evidence 与判断字段，`gate` 负责最终机械检查：

- `repo-map.json`：文件清单、语言分布、目录 LOC、候选入口、模块分级候选、docs/config/dependency、generated/test/vendor 排除。
- `repo-map.md`：面向 LLM 的压缩摘要、项目类型信号、可能的核心数据流、待验证问题。
- `evidence-plan.md`：架构问题列表、每问题对应候选文件/符号、subagent 分工、token/时间预算。
- `doctor-report.json`：每检查项 `pass/fail` 与版本、语言与枚举器支持情况、fail 修复指引、是否放行（全绿才 true）。
- `coverage-units.json`：关键单元清单（`文件:行号`、类型、模块）、覆盖状态与降级理由、`parsed`/`unparsed` 清单及解析率。
- `module-evidence/*.json`：每个核心模块的 Evidence Matrix 机器可读记录，供 `gate` 检查；Markdown 叙事可以从它派生，但不能替代它。
- `quality-gate-report.json`：每个 gate 的 `pass/fail`、失败原因、关联文件/单元/报告段落，以及是否允许进入最终报告合成。

### Packaging

本机 `.claude/settings.json`、`.codex/hooks.json`、graphify hook 配置不属于发布产物，只作维护者本地开发辅助。发布包不含写死绝对路径的 hook，不要求用户预装维护者本地 hook。graphify 的检测/初始化通过 doctor / setup 指引完成；hook 模板若提供必须可移植且默认不启用。

## Evidence-First Analysis Pipeline

### Phase 0: Doctor Preflight Gate

分析前必须运行 doctor 自检，全绿才进入 Phase 1，否则阻塞并引导修复。硬门控，不降级。

检查项：必备命令（`git`、`rg` 无则 `grep`）；符号枚举器（`universal-ctags` 或 `ast-grep` 至少一个可用）；目标仓库主要语言被枚举器支持；工作目录可写。graphify 只做“可用性探测”，不可用不阻塞。

行为：每项输出 `pass/fail` 与版本，落盘 `doctor-report.json`；任一必需项 fail 则打印可复制的安装/配置指引、暂停、提示修复后重跑；循环直到全绿；不提供“跳过 doctor 强行分析”的默认路径。

### Phase 1: Repository Acquisition

解析用户输入（本地路径、GitHub/GitLab/Gitee URL、`owner/repo` 简写）；本地路径直接用，远程 shallow clone；创建分析工作目录；记录仓库来源、commit hash、分析时间、运行环境和可用工具。

### Phase 2: Deterministic Scout

不调用大模型，用代码和命令完成机械扫描。输出：文件清单、语言与 LOC 分布、顶层模块体量、docs/config/dependency、候选入口、候选 generated/test/vendor、候选高风险区。目标是缩小 LLM 后续阅读范围，不得出架构结论。

### Phase 3: Repo Map Compression

把 Phase 2 结果压缩成 `repo-map.md`：保留文件与目录证据、标注来源、不加未验证判断、明确候选而非结论。

### Phase 4: Architecture Question Planning

LLM 只基于 repo map、README、核心文档和用户目标生成架构问题（核心数据流、关键路径模块、抽象边界、可能隐藏的错误处理/兼容/安全/性能约束），输出 `evidence-plan.md`。若 Phase 4 调整模块分级，必须同步写入 `coverage-units.json` 的 `modules[]` 或等价结构化产物，供后续覆盖率 gate 使用。

### Phase 5: Evidence-Scoped Module Analysis

subagent 按 evidence scope 工作，不按“读够多少行”。每个核心模块先产出 `module-evidence/*.json` 形式的 Evidence Matrix，再写叙事分析。

| 字段 | 含义 |
|------|------|
| Module Role | 模块在系统中的职责 |
| Entry Points | 进入该模块的入口 |
| Core Data Structures | 理解设计必需的数据结构 |
| Main Flow | 主执行流程 |
| Cross-Module Dependencies | 与其他模块的依赖关系 |
| Key Design Decisions | 关键设计决策与权衡 |
| Risk Areas | 错误处理、兼容、安全、并发、缓存等风险点 |
| Source Evidence | 支撑结论的文件、行号、文档来源 |
| Open Questions | 需主 agent 交叉验证的问题 |

### Phase 6: Risk Sampling

对高风险区域抽样，避免只分析 happy path。强制关注（存在则抽样）：错误处理、插件/扩展点、兼容层、缓存、并发、权限与安全边界、配置加载、generated/vendor/test 边界。质量门必须说明是否抽样、抽了什么、发现什么。

### Phase 7: Quality Gates

最终报告前必须过质量门，并落盘 `quality-gate-report.json`：Evidence Matrix 完整性、核心结论源码证据、跨模块一致性、unsupported claim 检查、risk sampling 检查、Why > What 深度检查、叙事连贯性检查、关键单元覆盖率检查（`coverage-units.json` 达到所选模式分档）。任何 core 模块的 `unparsed` 文件、`refs_status == missing` 的跨模块结论、或未通过的 gate，都必须进入报告的 unsupported area / open questions，不得被写成已验证结论。

### Phase 8: Report Synthesis

最终报告保持原深度分析风格：场景化问题引入、项目全景、核心设计哲学、深度模块分析、设计权衡、批判性评价、业界对比、Mermaid 架构图、可借鉴经验。报告不应退化为目录说明或符号列表。

## Budget Profiles

三种模式的差别在 evidence 深度、风险抽样强度和报告长度，不在源码行覆盖率。

| 模式 | 目标 | Evidence 深度 | 风险抽样 | 外部调研 | 报告形态 |
|------|------|---------------|----------|----------|----------|
| 快速 | 快速理解全貌 | 核心路径与核心模块 | 最小 | 可跳过或只读 README/docs | 短报告 |
| 标准 | 常规架构分析 | 核心模块、关键边界、主要设计决策 | 标准 | 按需搜索 | 完整报告 |
| 深度 | 深入研究设计决策 | 扩展到次要模块、边缘路径、替代方案 | 强 | 完整调研 | 长报告 |

每个模式必须设置：总耗时目标、总 token 预算、subagent 数量上限、每 subagent 证据读取预算、报告长度上限、质量门最低要求。

## User Stories

1. 作为用户，我希望大仓库分析更快、token 有界，这样能在 50W 行项目上使用而不必等待数小时或承担高昂成本。
2. 作为用户，我希望报告保留 Why > What 的深度分析，这样提速不会变成浅层摘要。
3. 作为用户，我希望每个主要架构结论都带源码证据，这样报告可信。
4. 作为用户，我希望 skill 在深读前先识别核心模块，这样精力集中在重要代码上。
5. 作为用户，我希望快速/标准/深度模式有不同 evidence 预算，这样能有意识地用速度换深度。
6. 作为用户，我希望报告暴露不确定性，这样能区分已验证结论与假设。
7. 作为维护者，我希望有确定性工具契约 + doctor 校验的工具环境，这样 skill 在各运行时行为可预测、不静默降级。
8. 作为维护者，我希望机械扫描先于模型推理，且工具输出被当作候选证据而非结论。
9. 作为维护者，我希望有 Evidence Matrix 模式和按证据问题划分的 subagent 边界，这样模块草稿可比较、可合并、不重复读。
10. 作为维护者，我希望有阶段/模块级预算、风险抽样和质量门，这样提速不会漏掉隐藏约束或放过无证据结论，并保留原分析哲学。

## Implementation Decisions

- Evidence-First Repo Analyzer 作为 breaking v2，优先证据可靠性。
- 新增最小 CLI / scripts 作为确定性工作的实现载体：doctor、scan、units、summarize、gate。
- 用关键单元覆盖率替代行读取覆盖率作为主质量指标；分子须满足双硬条件（`file:line` 锚点 + 实质设计判断）。
- 行覆盖率退役，不计算、不落盘。
- 关键单元及覆盖状态落盘 `coverage-units.json`，逐单元可审计。
- 模块分级必须结构化落盘，`core | secondary | excluded` 决定覆盖率分档；`excluded` 不得用来绕过核心覆盖。
- 引用边必须记录来源、置信度和完整性状态；graphify 缺失时可继续分析，但跨模块结论必须暴露不确定性。
- `gate` 必须产出 `quality-gate-report.json`；核心模块 Evidence Matrix 必须有 `module-evidence/*.json` 机器可读记录。
- 符号枚举器（`universal-ctags` 或 `ast-grep`）二选一为最小必需依赖，由 doctor 保证；无自动降级到正则分母。
- graphify 为可选增强，缺失不阻塞；分母所需跨文件引用边由符号枚举器提供。
- 依赖信息从 manifest 派生，不执行生态命令。
- 运行时兼容用单一原则表达：确定性工作进 CLI，仅并行度/交互可降级，质量门不降级。
- 发布产物排除维护者本地 hook 与绝对路径。
- 所有确定性命令默认只读，除非用户显式要求。
- 保留原深度分析哲学：Why > What、代码为准、全局设计哲学、批判、业界对比、叙事连贯。

## Testing Decisions

- 测 skill workflow 的外部可观测行为：repo map、evidence plan、Evidence Matrix、质量门摘要、最终报告结构。
- 不测实现细节（具体 shell 命令），除非它被写入工具契约。
- 测三种模式在同一 fixture 仓库上的预算与深度差异。
- 测 doctor gate：必需工具（符号枚举器）缺失时阻塞并给修复指引，全绿才放行，并产出带逐项 pass/fail 的 `doctor-report.json`。
- 测 graphify 缺失时分析仍能进行（可选增强路径）。
- 测最终报告不含无证据架构结论；每个核心模块都有 Evidence Matrix。
- 测存在高风险类别时执行了风险抽样。
- 测关键单元覆盖率由 `coverage-units.json` 计算，且无实质判断的分子条目被拒。
- 测模块分级决定覆盖率阈值，`excluded` 必须有理由且不能让核心模块消失。
- 测 core 模块存在 `unparsed` 文件时 gate fail，除非报告显式标为 unsupported area。
- 测 `quality-gate-report.json` 记录每个 gate 的 pass/fail 和失败证据。
- 测确定性工具输出不被当作最终架构结论。

## Minimal Benchmark

只保留证明改进所需的最小度量，不建重型 harness：

- 新旧流程各跑一次代表性仓库。
- 对比四项：elapsed time、approximate token usage、是否漏掉核心模块、quality gate pass rate / unsupported claims count（二选一即可）。

更细的多指标 rubric、小/中/大三仓矩阵作为愿景延后，等 workflow 在基准仓库跑通再引入。

## Out of Scope

- 构建超出符号枚举器的完整 language server 或重型语义索引器。
- 保证对每种语言生态的完美架构理解。
- 把整个 skill 重写成独立应用。
- 移除原分析哲学文档。
- 产出二进制报告、dashboard 或 UI。
- 把 benchmark 结果发布到远程服务。
- 引入使 skill 在其它 agent 不可用的私有 API。
- 发布维护者本地 `.claude` / `.codex` hook 或 graphify 绝对路径。
- 分析扫描期间安装依赖或修改被分析仓库。
- 把确定性工具输出当作最终架构分析。
- 缓存与增量策略（本次剔除；重复分析优化等 workflow 跑通后再评估）。

## Further Notes

保守实现。最高风险失败模式是“更快但更浅”。主要防护是保留原质量哲学，只替换证据获取和预算控制层。

首个实现切片：

1. 标记 breaking v2，更新面向用户文档。
2. 新增最小 CLI / scripts：doctor、scan、units、summarize、gate。
3. 定义 Evidence Matrix。
4. 定义确定性工具契约：符号枚举器二选一为必需，graphify 为可选增强。
5. 加 Phase 0 doctor preflight gate：检查项、`doctor-report.json`、修复循环。
6. 重写 workflow 各 Phase，含关键单元覆盖率与 `coverage-units.json`。
7. 加快速/标准/深度预算档。
8. 加质量门与最小 benchmark（时间、token、核心模块遗漏、质量门/unsupported claim 指标）。
9. 保留原分析哲学。

避免投机性重型基础设施。先做让 doctor、扫描、单元枚举、质量门可复现的最小确定性脚本，其余自动化等 workflow 契约在基准仓库验证后再加。
