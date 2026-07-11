---
name: repo-analyzer
description: Use when the user mentions "分析项目"、"分析仓库"、"分析 GitHub"、"项目分析"、"源码分析"、"架构分析"、"代码分析"、"学习这个项目"、"研究这个框架"、"看看这个库怎么实现的"、"对比两个项目"、"项目评测"、"框架评测"
---

# Evidence-First Repo Analyzer v2

对开源项目进行证据优先的深度架构分析。目标不是罗列文件与符号，而是用最小的模型注意力产出可审计、Why > What、叙事完整的架构报告。

v2.2 是 breaking workflow：必须运行本仓库提供的确定性 CLI。仅暴露 **standard**（默认、可移植）与 **deep**（能力门禁）。执行策略以 [rules/](rules/) 为 SSOT；SKILL 工作流须先读对应 rule。

## 不可降低的分析原则

1. 从业务问题和使用场景进入，不从目录树进入。
2. 每个确定性架构判断必须有源码 `文件:行号`、项目文档或外部一手来源。
3. 每个核心模块都解释动机、权衡、替代方案代价和全局协同，保留 Why > What。
4. 确定性工具只生成候选信号，不能把扫描结果写成最终架构结论。
5. 每个核心模块同时提交 JSON Evidence Matrix 和叙事分析。
6. 未解析范围、引用不完整和证据不足必须进入开放问题或 Unsupported Area；**Unsupported ≠ 禁止分析**：core unparsed 必须先走 Unparsed File Read Pass 再声明 residual。
7. 最终报告合成前必须通过机器质量门；失败时修复证据或明确 unsupported 后重跑，不得绕过。

分析哲学与写作标准继续遵守 [analysis-guide.md](references/analysis-guide.md) 和 [module-analysis-guide.md](references/module-analysis-guide.md)。v2 工件模板见 [evidence-first-v2.md](references/evidence-first-v2.md)。

## 工具前提（见 rules）

- **standard（默认）**：仅基线工具——`git`、文件发现/行计数、`rg` 或 `grep`。**禁止**使用 Graphify / Universal Ctags / ast-grep（即使已安装也必须忽略）。符号/引用若来自文本启发式，须标 heuristic / partial / missing。详见 `rules/modes.json` 与 `rules/tools/*`。
- **deep**：能力合同门禁——`graph-queries`、`symbol-enumeration`、`reference-edges`。Graphify 为优先图提供方；Ctags / ast-grep 为补充。能力不足时 **拒绝执行、不降级 standard**；可诊断、不产出分析报告。
- 官方源与 verified date 写在各 tool rule 中，勿凭会话记忆改分类。

## 适用边界与输出语言

适用于完整项目的架构分析、源码研究、框架学习、同类项目对比与项目评测。不用于单文件解释、普通 bug 调试或代码审查。

默认输出中文；用户明确使用其他语言时跟随用户。报告像资深工程师给新同事做 onboarding：有观点、有推理、有对比，避免学术堆砌和目录流水账。

## v1 精华的保真要求

Evidence-First 只改变证据获取和审计方式，不改变以下分析能力：

- **业务视角优先**：从谁在什么场景遇到什么问题开始，而不是从函数签名开始。
- **抽象层次克制**：默认讲流程、边界、模式和权衡；只有实现本身是核心卖点时才展示少量代码，并先用自然语言解释。
- **全局关联**：每个模块都要连接项目整体设计哲学，解释局部约束来自哪里、变化会影响谁。
- **启发性写作**：读者应能理解设计并参与架构讨论，而不是只知道“有哪些文件”。
- **Why > What**：每个核心设计回答为什么这样做、不这样会怎样、替代方案代价、业界差距和重新设计建议。
- **批判性评价**：指出真实缺陷和工程成熟度，不回避风险，不把功能清单伪装成竞品分析。
- **叙事连贯**：模块按数据流、分层或问题演进组织，章节之间解释前一结论如何引出下一问题。

## 分析模式

| 模式 | 核心/次要关键单元覆盖率 | 证据范围 | 风险抽样 | 并行上限 | 工具策略 |
|---|---:|---|---|---:|---|
| standard（默认） | 60% / 30% | 核心模块与关键边界 | 核心模块 + 重要边界 | 6 | 仅基线；忽略增强工具 |
| deep | 90% / 60% | 次要模块、边缘路径、替代方案 | 多路径增强抽样 | 8 | 能力门禁；缺能力拒绝 |

两档改变深度、预算与工具合同。Semantic Source Review：standard 每个 core 模块至少 1 个；deep 每个 core 模块最多 3 个代表性 analyzed unit（不足则全抽）。**quick 已移除**。

## 强制工作流

设目标仓库为 `$REPO`，分析工件目录为 `$WORK_DIR`。

Doctor、关键单元分母和 gate 是硬契约，不可跳过。调研范围、提问轮次、报告章节和并行方式可按项目特征与预算调整，但不得降低证据质量。

### Phase -1：项目获取与初始化

解析本地路径、完整 GitHub/GitLab/Gitee URL 或 `owner/repo` 简写。远程仓库 shallow clone 到 `~/repo-analyses/{repo}-{YYYYMMDD}`，本地路径直接使用。记录来源、commit、分析时间和运行环境；此阶段只准备仓库，不开始架构判断。

### Phase 0：Doctor 硬门控

```bash
repo-analyzer doctor --repo "$REPO" --out "$WORK_DIR" --mode standard
# deep 目标：
# repo-analyzer doctor --repo "$REPO" --out "$WORK_DIR" --mode deep
# 可选安装 prompt：
# repo-analyzer doctor --repo "$REPO" --out "$WORK_DIR" --install-prompt --install-mode deep
```

读取 `doctor-report.json` 的 **capability matrix**（available/blocked modes、missing capabilities、detected tools、official-source refs）以及 **reference-edge-usability 探针**。standard 只需基线放行；deep 需三能力满足，且 `reference-edges` 必须在目标仓抽样可验证（ctags `roles=reference` 或已接线的 Graphify units refs），否则拒绝且不降级——避免证据阶段后才因 reference-quality 失败浪费 token。安装 prompt 不得指示修改被分析仓源码/依赖清单（除非用户显式授权）。

### Phase 1：确定性 Repo Map

```bash
repo-analyzer scan --repo "$REPO" --out "$WORK_DIR"
repo-analyzer summarize --repo "$REPO" --out "$WORK_DIR"
```

读取 `repo-map.json` 与 `repo-map.md`，确认入口、模块、文档、manifest、test/generated/vendor 和风险区域都只是候选。依赖直接读取 manifest，禁止执行生态命令。

### Phase 2：关键单元分母

```bash
repo-analyzer units --repo "$REPO" --out "$WORK_DIR"
```

检查 `coverage-units.json` 的模块分级、parsed/unparsed、parse_rate、refs 和 refs_status。关键单元集合只能标记，不得删除。若 Evidence Plan 调整模块分级，必须同步修改 `modules[]` 的 classification、reason、source。

### Phase 3：外部调研与项目文档研读

遵循“先搜再读”，调研强度由模式控制：

1. 阅读 README、架构文档、RFC/ADR、CONTRIBUTING 和官方设计说明，优先获取作者的一手动机与历史约束。
2. README 提供官网时，阅读首页、Features、Use Cases、Comparison、Blog 等与架构定位有关的页面。
3. 标准/深度模式调研 3-5 个最相关竞品或替代方案，比较设计哲学和技术路线，不做功能清单。
4. 形成研究笔记：核心使用场景、现有方案为何不足、项目独特价值、官方设计动机、竞品差异、未找到的信息。
5. 外部资料只能支撑定位、历史和业界对比；源码行为仍以当前 commit 为准。

standard 可聚焦 README/核心文档与必要搜索；deep 增加官网、设计文档、替代方案和一手资料。

### Phase 4：项目特征识别与自适应提问

结合 Repo Map 和调研结果识别项目类型、规模、成熟度、技术栈、设计风格、核心数据流和主要设计张力。问题必须来自观察到的项目特征，例如：

- 不常见技术选择背后的动机
- 简单性与灵活性、性能与可维护性等真实取舍
- 插件系统、兼容层、类型复杂度或配置驱动是否是用户关注重点
- 报告是否需要完整场景化引入与竞品定位，还是直接进入代码全景

每轮最多提出 3 个会实质改变分析方向的问题；能从代码或文档确定的事实不要问用户。根据 Repo Map 向用户展示规模与候选模块，确认 **standard** 或 **deep** 模式（默认 standard）。

### Phase 5：动态报告结构与 Architecture Question Planning

基于 Repo Map、README、核心文档和用户目标写 `$WORK_DIR/evidence-plan.md`。必须包含：

- 架构问题
- 每个问题的候选文件、关键单元或文档证据
- 核心/次要/排除模块分级及理由
- subagent 分工；运行时无 subagent 时写 `parallelism: degraded` 并串行执行。standard/deep 若要作为多子代理完整通过，必须写明实际子代理分工、每个子代理产物和主 Agent 融合过程；`parallelism: degraded` 只能判为 CLI/gate 机械链路通过，不能判为多子代理验收通过。
- 当前模式的总时间、总 token、subagent 上限、单 agent 证据预算和报告长度预算
- 风险抽样计划与预期 Unsupported Area
- 若 `coverage-units.json` 中存在 **core 模块 unparsed 文件**，必须规划 **Unparsed File Read Pass** 节（文件列表/选样优先级、工具白名单、预算、产物路径、`unparsed_read_pass.parallelism: active|degraded`）；禁止仅写「预期 Unsupported 路径列表」后结束
- 报告章节结构与模块叙事线：选择数据流、分层或问题驱动顺序，并说明模块 A 的什么结论引出模块 B

模块按业务能力和数据流识别，不按顶层目录直接定案。报告结构必须适配项目：可以省略无信息价值的章节，但通常应覆盖问题场景、竞品定位、项目全景、核心设计哲学、核心模块、批判性评价和可借鉴经验。

### Phase 6：证据限定的模块分析

按问题而不是按文件数量读取源码。每个核心模块先写 `$WORK_DIR/module-evidence/{module}.json`，字段必须符合 v2 模板；随后写叙事草稿。已分析关键单元必须回填：

- `status: analyzed`
- `anchor: 文件:行号`
- `judgment`: 角色、流程或权衡之一的实质判断

三项缺一不计入覆盖率。未分析单元保留在分母中，并填写 `skip_reason`。

并行时按 Evidence Plan 的问题边界分工，不按文件数平均切分。每个模块任务携带当前预算和叙事上下文：前一章节留下什么问题、本模块回答什么、结尾为下一模块铺垫什么。运行时无 subagent 时按同一顺序串行执行，并在 Evidence Plan 明确记录降级；standard/deep 的完整验收需要真实多子代理执行记录，不能只凭 `allowed_to_synthesize:true` 判定通过。

### Phase 6.5：Unparsed File Read Pass（core unparsed 强制补读）

当 Phase 2 之后（或模块分析过程中）发现 **classification=core 的模块存在 unparsed 文件** 时，**必须**调度一次 **Unparsed File Read Pass**，不得仅把路径写入报告 Unsupported Area 后结束。

1. **执行者**：优先子代理；无 subagent 时主 Agent **串行**同一 pass，并在 Evidence Plan 记录 `unparsed_read_pass.parallelism: active|degraded`（与模块分析 parallelism 分字段，勿混用语义）。
2. **基线只读工具白名单**：`rg`/`grep`、`find`、`wc`、文件读取类工具；可用 `git` 只读。**禁止**：安装依赖、启动服务、用正则发明 units 分母、修改目标仓源码、把 unparsed 静默移出 `unparsed` 列表。
3. **选样优先级**：入口/编排 → 主用户路径 UI → Matrix 跨模块依赖点名的 unparsed → 风险路径 → 其余 SEO/debug/example 按预算浅读或写 `skip_reason`。
4. **模式预算**（写死在本 skill）：
   - quick：全局最多 **5** 个高影响 unparsed 文件
   - standard：覆盖各 core 主路径相关 unparsed 子集；其余预算外写 skip 原因
   - deep：提高比例，但仍允许预算内 skip 并记录原因
5. **可审计产物**（`$WORK_DIR`）至少其一：
   - `unparsed-file-reviews/*.md` 或 `unparsed-file-reviews.json`
   - 和/或 `module-evidence/{module}.json` 的 `unparsed_manual_reads[]`（字段：`path`、`tools_used`、`anchors`、`observation`、`confidence`=`manual-read`、`residual_gap`）
   - Evidence Plan 增加「Unparsed File Read Pass」节（分工/文件列表/产物路径/预算/parallelism）
6. **语义边界（硬）**：
   - 仍须声明 core unparsed 为 Unsupported Area
   - 补读 **不** 清除 unparsed、**不** 提升 `parse_rate`、**不** 豁免 `parse-quality` / `reference-quality`
   - **不** 把补读文件计为 `status: analyzed` unit；报告可引用 `文件:行号` 但必须标明 **manual-read / 非枚举单元**
   - 未补读文件保留在 Unsupported，并写预算/优先级 skip 原因

### Phase 7：风险抽样与交叉验证

每个核心模块至少抽样一条相关风险路径，记录类别、源码锚点、发现和对架构评价的影响。检查跨模块依赖两端；`refs_status` 为 partial/missing 时，不得写成已完全验证的跨模块结论。

主 Agent 必须交叉验证模块角色、主流程、共享状态和依赖方向；检查每个模块是否回应 Evidence Plan、连接整体设计哲学，并把冲突、未验证推断和开放问题保留下来。风险抽样结果必须进入最终批判性评价，而不是只留在 Matrix。

必须执行 Semantic Source Review：模块分析完成后，主 Agent 按当前模式预算重新读取被抽样 analyzed unit 的当前源码 span，并在对应 `module-evidence/{module}.json` 写入 `semantic_reviews` 数组。选样优先级固定为跨模块关系、`refs_status` 不完整、风险路径、影响最终批判性评价的判断；不得按文件顺序或随机挑选。每条记录包含：

- `unit_id`：`coverage-units.json` 中稳定的单元 ID
- `anchor`：coverage 当前 `anchor`
- `judgment`：coverage 当前 `judgment`
- `source_observation`：复核者从源码 span 看到的事实
- `verdict`：只能用 `supported` 表示已解决复核

`anchor` 和 `judgment` 必须逐值匹配 coverage 当前状态。若复核得到 partial 或 unsupported，不得把该记录作为已解决结果写入最终 Matrix；先修正判断，或把该单元降级为 `unanalyzed` / 开放问题，并保持 coverage、Matrix 和报告一致后重新抽查。运行时无 subagent 时，按独立串行复核 pass 执行，同样不能降低证据要求。该机制增加少量源码重读成本，目标是降低锚点掺水风险，但不提供数学意义上的真实性证明。

### Phase 8：多源融合与报告草稿

写 `$WORK_DIR/report.md`。报告保持场景化问题、项目全景、核心设计哲学、深度模块分析、设计权衡、批判性评价、业界对比、Mermaid 图和可借鉴经验。开放问题与 Unsupported Area 不得静默消失。

融合时以 Phase 5 的叙事线组织章节，不按草稿文件顺序拼接。模块开头自然承接上一个问题，结尾引出下一约束。核心结论逐条核对源码锚点、项目文档或外部一手来源；证据不足时降级为假设、限制、开放问题或 Unsupported Area。

记录预算执行摘要：实际并行/串行方式、核心与次要模块范围、风险抽样数量、外部调研范围、报告长度，以及任何超预算后的范围收缩。

### Phase 9：确定性质量门

```bash
repo-analyzer gate --repo "$REPO" --out "$WORK_DIR" --mode standard
```

读取 `quality-gate-report.json`。只有 `allowed_to_synthesize: true` 才能进入最终合成。质量门检查 Evidence Plan、模块分级、核心 Evidence Matrix、源码锚点、风险抽样、双硬条件覆盖率、实际解析质量、未解析 core 范围、**core unparsed 时的补读记录（`unparsed-manual-review`）**、引用质量和报告叙事深度。

`unparsed-manual-review`：core unparsed 非空时，必须存在 Evidence Plan「Unparsed File Read Pass」、`unparsed-file-reviews*` 或 Matrix `unparsed_manual_reads` 之一；**有补读记录仍不豁免** `parse-quality` 失败。补读成功不等于解析成功。

质量门还会检查 `semantic-source-review`：standard 要求每个 core 模块至少 1 条，deep 要求每个 core 模块最多 3 条且单元不足时全抽。未知或非 analyzed 单元、重复抽查、过期 anchor/judgment、空 `source_observation` 或非 `supported` verdict 都会阻止最终合成，并在质量报告中列出当前模式阈值、有效数量、关联 unit 与失败原因。

### Phase 10：最终合成

只在质量门通过后生成 `$WORK_DIR/ANALYSIS_REPORT.md`。扫描候选不能直接升格为结论；Evidence Matrix 的开放问题必须被验证或继续保留。最终报告仍以连贯叙事解释 Why，不退化为符号清单。

最终交付至少满足：

- 单一 Markdown 报告，标题和章节根据项目动态设计
- 核心流程、架构或模块协同使用 Mermaid 可视化
- 核心模块解释动机、流程、全局协同、权衡和风险
- 竞品比较聚焦设计哲学与技术路线
- 明确区分已验证结论、假设、限制、开放问题和 Unsupported Area
- 读者能理解系统为什么这样设计，并据此参与架构讨论

## 特殊场景

- **超大仓库**：优先 god node、核心数据流和高风险边界，按预算分批处理；不为凑行数读取低价值文件。
- **Monorepo**：先确认分析整个仓库还是指定 package；模块分级和覆盖率按确认范围落盘。
- **文档稀缺**：把动机类结论降级，增加源码与提交历史证据，不凭常识补作者意图。
- **多语言仓库**：Doctor 以主要语言能力放行，次要语言解析盲区必须进入 unparsed/Unsupported Area。
- **对比两个项目**：两个项目分别跑完整 v2 工件链，再对比问题建模、边界、扩展机制、权衡和工程成熟度。

## 输出工件

| 工件 | 生产者 | 用途 |
|---|---|---|
| `doctor-report.json` | doctor | 预检逐项结果与放行决定 |
| `repo-map.json` | scan | 确定性仓库候选数据 |
| `repo-map.md` | summarize | 面向模型的候选摘要 |
| `coverage-units.json` | units + agent 回填 | 稳定分母、覆盖状态和引用完整性 |
| `evidence-plan.md` | agent | 架构问题、证据范围、分工与预算 |
| `module-evidence/*.json` | agent | 核心模块机器可读 Evidence Matrix；包含按模式预算抽样的 `semantic_reviews` |
| `report.md` | agent | 质量门前叙事草稿与 unsupported 声明 |
| `unparsed-file-reviews/*` 或 `unparsed-file-reviews.json` | agent | core unparsed 的 Unparsed File Read Pass 可审计补读观察（confidence=`manual-read`） |
| `quality-gate-report.json` | gate | 逐项质量结果与合成放行决定 |

## 禁止事项

- 不得绕过 Doctor 或 gate。
- 不得用正则表达式生成关键单元分母。
- 不得执行 `npm ls`、`cargo metadata`、`go list`、安装依赖、迁移或生产服务。
- 不得把 generated/vendor/test 候选静默当作核心源码，也不得借 excluded 绕过核心覆盖。
- 不得把没有锚点和设计判断的单元计入已分析。
- 不得把 unparsed 补读伪装成 enumerator 解析成功、抬高 parse_rate，或把补读文件标为 analyzed unit。
- 不得在 core unparsed 非空时仅追加 Unsupported 路径列表而不执行 Unparsed File Read Pass。
- 不得发布维护者本机 hook、绝对路径或默认启用的 graphify hook。
