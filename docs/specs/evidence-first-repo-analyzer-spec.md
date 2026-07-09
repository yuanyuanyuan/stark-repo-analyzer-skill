# Evidence-First Repo Analyzer Spec

## Problem Statement

当前 repo-analyzer skill 在大型仓库分析中依赖大量源码阅读和行覆盖率门控。面对约 50W 行代码的仓库时，分析耗时可能达到 2 小时，token 消耗高，且速度优化容易牺牲原有的深度分析精华。

用户需要对该 skill 做二次开发：提升分析速度、降低 token 使用、明确 tools 使用定义，同时保留原有的 Why > What、代码依据、全局叙事、批判性评价和深度架构洞察。

当前最大问题不是缺少并行，而是质量目标和“读大量源码”绑定在一起。旧流程用 `Read` 行覆盖率作为主要质量门，会让 50W 行仓库天然进入高 token、高耗时路径。

## Solution

将 repo-analyzer 从“覆盖率驱动的大量源码阅读流程”升级为 **Evidence-First Analysis Pipeline**。

这是一个 **breaking v2** 设计：v2 以可靠证据链和可审计质量门为优先目标，不承诺继续保持 v1 的“纯 skill 文档即可开箱运行”体验。缺少 doctor 要求的必备工具时，分析必须阻塞并引导修复；不得为了可用性降级到低可信分析路径。

核心流程：

1. 先用确定性工具生成 repo map，而不是让 LLM 盲读源码。
2. 让 LLM 基于 repo map 提出架构问题和分析假设。
3. 用 Evidence Matrix 约束每个模块必须提交的证据链。
4. 用 Budget Scheduler 控制阶段、模块、subagent 的时间和 token。
5. 用 Quality Gates 验证结论准确性、反证抽样和跨模块一致性。
6. 用 Benchmark Harness 对比旧流程与新流程的速度、token 和质量。
7. 用缓存和增量策略复用 repo map、扫描结果、外部调研和证据索引。

核心原则：

```text
改变证据获取方式，不改变原 skill 的分析哲学。
```

也就是：

```text
旧：为了达到覆盖率，读大量源码。
新：为了回答架构问题，读取最小但关键的源码证据。
```

原 repo-analyzer 的精华必须保留：

- Why > What
- 代码为准
- 全局关联
- 自适应问题
- 深度模块分析
- 批判性评价
- 叙事连贯

## Coverage Redefinition (Lever 1)

这是本文档的核心焦点：把"覆盖率"的度量单位从**读取的源码行占比**改成**已分析并锚定的关键代码单元占比**，让确定性工具枚举的关键单元计入质量门，agent 不必再把几十万行原文灌进 context。

### 旧定义在保护什么（不能丢的精华）

原 SKILL.md 阶段 2：`覆盖率 = 通过 Read 工具实际请求过的行范围之并集 / 文件总行数`，标准档核心模块 ≥ 60%。它同时承担三个职责：

1. 防跳过 — 逼 agent 不对核心模块一句带过（对应"拒绝流水账"）。
2. 防空谈 — 结论必须有代码依据（对应"代码为准，标注 文件:行号"）。
3. 可审计 — 一个百分比 + 明细表 + ✅/❌，人和 agent 都能核。

问题只出在**分母**：它用"读了多少行原文"近似"理解程度"，而质量标准（Why、权衡、业界对比）几乎与行数无关。度量与目标错位，才是 50W 行硬读的根源。改法只换度量单位，上述三个职责必须原样保留。

### 新定义

```text
覆盖率 = 已分析并锚定的关键代码单元数 / 该模块关键代码单元总数
```

三个要点：

1. **分母 = 关键代码单元，不是总行数**。关键单元由确定性工具（graphify + `universal-ctags` / `ast-grep`）枚举，机器可判定，包含：
   - 导出 / 公共符号（函数、类、方法、接口）
   - 入口点（main、路由注册、命令注册、事件处理器）
   - 核心数据结构 / 类型定义
   - 跨模块调用边 / 被跨文件引用的符号
   - 状态与配置定义点

   私有小工具、样板、生成代码、vendor 不进分母。
2. **分子"已锚定" = 双硬条件**（缺一不计入）：
   - 草稿中对该单元有 `文件:行号` 锚点。
   - 且有一句实质设计判断（角色 / 流程 / 权衡三者之一），不是"这里有个函数"。
3. **阅读方式改为锚点驱动**：工具定位单元，只读该单元所在 span（定义 + 紧邻上下文 + 其跨文件引用两端），再分析。不再要求整文件通读。

分档 30 / 60 / 90 全部保留，从"行的百分比"重解释为"关键单元的百分比"：

| 模式 | 核心模块关键单元覆盖 | 次要模块关键单元覆盖 |
|------|--------------------|--------------------|
| 快速 | ≥ 30% | ≥ 10% |
| 标准 | ≥ 60% | ≥ 30% |
| 深度 | ≥ 90% | ≥ 60% |

覆盖率明细表列头改为：

```text
模块 | 关键单元总数 | 已锚定分析数 | 覆盖率% | 未覆盖单元及原因 | 达标 ✅/❌
```

### Coverage Unit Source (No Runtime Degradation)

关键单元的枚举**始终为符号级（AST-level）**，由 graphify + `universal-ctags` / `ast-grep` 产出。可移植性不靠运行时降级保证，而靠 **Phase 0 Doctor Preflight Gate** 在分析开始前确保这些工具已安装配置。因此：

- 不存在"工具缺失就退回正则 / 行覆盖率"的自动降级路径。
- 行覆盖率仅作为辅助诊断指标，不作为分母。
- 若 doctor 不通过，分析根本不会启动，而不是带着降级质量继续。

`git` 提供改动热度信号，用于给关键单元排序（高频改动通常是核心），不作为分母来源。

### Coverage Risks and Mitigations

分母从"客观总行数"变成"关键单元集合"后，风险几乎全部源于此。

1. **分母注水** — agent 缩小分母就能刷覆盖率，架空防跳过精华。
   解法：分母只能由确定性工具枚举并落盘为 `coverage-units.json`，agent 只能在集合上标记 `analyzed / unanalyzed`，不能删条目；把某单元判为不重要必须写一行理由，接受阶段 7 抽查。
2. **工具漏解析（沉默失败）** — 解析不了的语言 / DSL / 宏生成代码不进分母，覆盖率显示 100% 实则有整块盲区。
   解法：doctor 校验目标仓库主要语言均被枚举器支持；枚举结果必须同时报告 `parsed` 与 `unparsed` 清单；解析率本身成为要报告的指标。
3. **锚点掺水** — 贴了 `文件:行号` 但判断为空，用伪分析凑"已锚定"数，违背 Why > What。
   解法：分子计入门槛写死双条件（锚点 + 实质判断）；阶段 7 抽查增加一条"抽查已锚定单元是否含实质判断，纯罗列打回重算"，复用现有 7.2 抽查机制。
4. **锚点驱动丢失全局关联** — 只读单元 span 可能读不到它如何被别处调用、如何参与全局数据流，而全局关联与叙事连贯正是原 skill 精华。
   解法：单元 context span 必须包含其跨文件引用边（graphify / ctags 提供）；module-analysis-guide 四要素中"模块间依赖"与"与其他模块协同"保持强制不变。
5. **可审计性下降** — 工具算出的分母用户不易复核。
   解法：`coverage-units.json` 落盘关键单元清单 + 覆盖状态，明细表每个数字可追到具体单元；审计从"数行"变成"查表"，透明度不降反升。
6. **可移植性（graphify 装不上）** — 分母依赖的工具在别人机器上没有。
   解法：由 Phase 0 Doctor Preflight Gate 硬门控 + 修复引导闭环解决——不通过就阻塞并引导安装，不降级。残留权衡：这提高了首次使用门槛与跨机器摩擦，是"不降级"策略的自觉代价。

残留待拍板：关键单元粒度（私有但高频调用的符号是否计入核心）、降级判定抽查比例——需真实基准仓库标定。

## Deterministic Tool Contract

确定性工具负责做机械扫描、候选定位、统计和索引。它们可以帮助 LLM 找到候选证据，但不能直接产出最终架构结论。

关键约束：

```text
Deterministic tools may identify candidates, but may not produce final architectural conclusions.
Every architectural conclusion must still be verified against source snippets, docs, or external primary sources.
```

### Implementation Carrier

v2 不再只依赖 `SKILL.md` 中的自然语言流程约束。实现载体必须新增一组最小 CLI / scripts，用确定性代码承担无需智力判断的步骤，LLM 只负责架构问题生成、证据解释、权衡判断和最终叙事。

最小脚本边界：

- `doctor`：检查工具版本、graphify 可用性、符号枚举器可用性、目标仓库语言支持、工作目录写入权限，输出 `doctor-report.json`。
- `scan`：生成文件清单、语言分布、LOC、docs/config/dependency 索引、generated/test/vendor 排除清单，输出 `repo-map.json` 的机械部分。
- `units`：基于 graphify + `universal-ctags` / `ast-grep` 枚举关键代码单元，输出 `coverage-units.json` 初始分母、`parsed` / `unparsed` 清单和解析率。
- `summarize`：把确定性扫描结果压缩成 LLM 可消费的 `repo-map.md` 草稿；只能写候选信号，不能写最终架构结论。
- `gate`：读取 Evidence Matrix、`coverage-units.json` 和报告草稿，执行可机械检查的质量门，如缺失锚点、覆盖率不足、必填字段缺失、未支持声明标记。

这些脚本是 workflow contract 的一部分。测试优先验证它们的外部产物，不测试内部 shell 命令细节，除非命令本身被写入工具契约。

### Baseline Tools

这些工具作为默认基础能力，优先使用；缺失时必须降级到同类系统命令。

| 目标 | 首选工具 | 降级方案 | 输出 |
|------|----------|----------|------|
| 文件发现 | `rg --files` | `find` | repo 文件清单 |
| 文本搜索 | `rg` | `grep` | 入口、关键术语、配置、TODO、错误路径 |
| 行数统计 | `wc -l` | shell loop | 文件/目录 LOC |
| Git 元信息 | `git` | 无 | recent files、contributors、history hints |
| 结构化 JSON 处理 | `jq` | shell/awk | package/config JSON 摘要 |
| 文档提取 | `find` + `rg` | `ls` + `grep` | README/docs/ADR/RFC 索引 |

### Optional Lightweight Tools

这些工具可用则使用，不可用不阻塞 skill。注意：`universal-ctags` / `ast-grep` 已上移为 Required Symbol Enumerators（见下），不再属于本表。

| 目标 | 工具 | 用途 |
|------|------|------|
| 更准 LOC | `scc` / `tokei` / `cloc` | 按语言、目录、代码/注释/空行统计 |
| 更快文件查找 | `fd` | 替代 `find`，提高速度 |
| 静态规则扫描 | `semgrep` | 找安全边界、数据流、错误处理模式 |

### Required Symbol Enumerators

这些工具是新覆盖率定义（关键单元枚举）的依赖，由 Phase 0 Doctor Preflight Gate 保证可用，缺失时阻塞分析并引导安装，不降级。

| 目标 | 工具 | 用途 |
|------|------|------|
| 符号索引 | `universal-ctags` | 提取函数、类、接口、类型、导出符号 |
| AST 模式搜索 | `ast-grep` | 找入口模式、调用模式、框架惯例、精确关键单元标定 |

### Graph Intelligence Tool (graphify)

graphify 是受支持的增强工具，用于跨文件关系、god node、社区结构和关键单元枚举。它**由 Phase 0 Doctor Preflight Gate 保证可用**，不是"可选缺失即降级"。

- 安装 / 配置由 skill 协助完成（doctor 检测 + 引导，用户确认后执行）。
- 使用 `graphify query` / `graphify path` / `graphify explain` 做 scoped 查询，禁止把完整 `graph.json` / `GRAPH_REPORT.md` 注入 context。
- 代码修改后用 `graphify update .` 保持图谱最新。

### Ecosystem-Specific Commands

按项目语言和包管理器选择性执行，只读，不修改依赖。

| 生态 | 命令示例 | 用途 |
|------|----------|------|
| JavaScript/TypeScript | `npm ls --depth=0`, `pnpm list --depth=0`, `yarn list` | 依赖和框架识别 |
| Rust | `cargo metadata --no-deps` | workspace、crate、target、依赖结构 |
| Go | `go list ./...` | package graph |
| Python | `python -m pip list`, `find pyproject.toml setup.py requirements.txt` | 项目结构和依赖识别 |
| Java/Kotlin | `find pom.xml build.gradle settings.gradle` | module/build graph |
| Ruby | `bundle list`, `find Gemfile` | 依赖识别 |

### Tool Availability Policy

graphify 及符号枚举器（`universal-ctags` / `ast-grep`）**不再是禁用或纯可选工具**，而是"受支持且由 Phase 0 Doctor Preflight Gate 保证可用"。缺失时不降级，而是阻塞分析并引导安装，直至 doctor 通过。

仍然禁止作为分析依赖的：

- 大型数据库索引器（作为分析主依赖）
- 需要长期 daemon 的服务
- 需要 API key 的工具
- 在**分析扫描阶段**修改源码、安装依赖、运行迁移或启动生产服务的命令

说明：doctor 的安装 / 配置协助属于分析开始前的、经用户确认的 setup 环节，与"分析扫描阶段只读"的约束不冲突。

### Runtime Capability Matrix

v2 必须支持以下运行时。支持的含义不是每个运行时都有完全相同的原生工具，而是每个能力都有明确等价实现；若等价能力不足，必须选择保持质量的保守路径，而不是跳过质量门。

| 能力 | Claude Code | Codex | OpenClaw | 质量保持策略 |
|------|-------------|-------|----------|--------------|
| Subagent 分析 | 使用原生 Agent / Task 类能力并行启动模块分析 | 若环境提供多代理工具则并行；否则主 agent 按 `evidence-plan.md` 串行执行模块任务 | 使用 OpenClaw 的 agent / worker 能力；若不可用则串行执行 | 可以降级并行度，不降级证据要求、Evidence Matrix、覆盖率和质量门 |
| 用户提问 | 使用 AskUserQuestion 或等价交互工具 | 使用普通对话提问；若当前模式不适合阻塞提问，则给出默认假设并标注 | 使用 OpenClaw 的交互/审批机制；无工具时回到普通对话 | 只允许减少交互便利性，不允许跳过会改变分析目标的关键确认 |
| 文件写入 | 使用 Write / Edit 写入 `$WORK_DIR` 草稿和报告 | 使用 shell / patch / 文件工具写入 `$WORK_DIR`，不得修改被分析仓库源码 | 使用可用文件工具写入 `$WORK_DIR` | 写入目标必须限制在分析工作目录和 skill 自身产物，不得污染被分析仓库 |
| 并行执行 | 同一轮启动多个 subagent | 使用运行时提供的并行工具；没有时串行执行并记录 `parallelism: degraded` | 使用 OpenClaw 并行 worker；没有时串行执行 | 并行度是性能优化，不是质量前提；缺并行只影响耗时目标，不影响通过标准 |
| CLI / scripts 调用 | Bash 调用 v2 scripts | shell 调用 v2 scripts | shell 或 OpenClaw command runner 调用 v2 scripts | doctor、scan、units、gate 必须可运行；运行不了就阻塞 |
| 工具缺失处理 | doctor fail 并给修复指引 | doctor fail 并给修复指引 | doctor fail 并给修复指引 | 不允许回退到 regex 分母、行覆盖率主指标或无 graphify 的低可信路径 |

运行时兼容性边界：

- v2 可以降低并行度和交互便利性，但不能降低证据质量。
- 如果运行时没有 subagent，主 agent 必须按模块顺序串行执行同一套 Evidence Matrix 和 coverage gate。
- 如果运行时没有结构化提问工具，必须用普通对话完成关键确认；不能静默采用会显著改变报告目标的假设。
- 如果运行时不能执行最小 CLI / scripts，则 v2 分析不可开始。

### Required Generated Artifacts

确定性扫描阶段至少生成以下本地草稿产物。

#### `repo-map.json`

包含：

- 文件清单
- 语言分布
- 目录 LOC
- 候选入口
- 候选核心模块
- docs/config/dependency files
- generated/test/vendor 排除结果

#### `repo-map.md`

包含：

- 面向 LLM 的压缩摘要
- 项目类型判断信号
- 可能的核心数据流
- 需要进一步验证的问题

#### `evidence-plan.md`

包含：

- 架构问题列表
- 每个问题对应的候选文件/符号
- subagent 分工
- token/时间预算

#### `doctor-report.json`

包含：

- 每个检查项的 `pass / fail` 与版本信息
- 目标仓库语言与枚举器支持情况
- fail 项对应的修复指引
- 是否允许进入分析（全绿才为 true）

#### `coverage-units.json`

包含：

- 确定性工具枚举出的关键代码单元清单（含 `文件:行号`、单元类型、所属模块）
- 每个单元的覆盖状态（`analyzed / unanalyzed`）与降级理由（如有）
- `parsed` 与 `unparsed` 文件清单及解析率

### Packaging and Local Hooks

本机 `.claude/settings.json`、`.codex/hooks.json` 或类似 graphify hook 配置不属于 v2 发布产物。它们只能作为维护者本地开发辅助，不能随 marketplace / npx / git install 包发布。

发布包要求：

- 不包含写死本机绝对路径的 hook 命令。
- 不要求用户预先安装维护者本地 hook。
- graphify 的安装、版本检测和初始化只能通过 doctor / setup 指引完成。
- 如果将来提供 hook 模板，必须以可移植模板形式发布，且默认不启用；用户确认后再写入本机 agent 配置。

## Evidence-First Analysis Pipeline

### Phase 0: Doctor Preflight Gate

分析开始前必须运行 doctor 自检；**只有全部检查通过才能进入 Phase 1**，否则阻塞并引导用户修复，直到通过为止。这是硬门控，不降级。

检查项：

- 必备命令：`git`、`rg`（无则 `grep`）。
- 图谱与符号工具：`graphify`（在 PATH 上、版本可用）、`universal-ctags` 或 `ast-grep`。
- graphify 配置：`graphify-out/` 可初始化、hook / 索引可运行。
- 目标仓库语言：主要语言均被符号枚举器支持，否则明确报告不支持项。
- 工作目录可写。

行为：

- 每项输出 `pass / fail` 及版本信息，落盘为 `doctor-report.json`。
- 任一项 fail：打印可复制的安装 / 配置指引（见 Graph Intelligence Tool），暂停分析，提示用户修复后重跑 doctor。
- 循环直到全绿；不提供"跳过 doctor 强行分析"的默认路径。

定位：doctor 是"能不能可靠地按新覆盖率定义分析"的前置保证，它替代运行时降级——把可移植性问题从"分析中途静默降级"提前到"分析前显式修复"。

### Phase 1: Repository Acquisition and Safe Setup

- 解析用户输入，支持本地路径、GitHub/GitLab/Gitee URL、`owner/repo` 简写。
- 本地路径直接使用；远程仓库使用 shallow clone。
- 创建分析工作目录。
- 记录仓库来源、commit hash、分析时间、运行环境和可用工具。

### Phase 2: Deterministic Scout

不调用大模型，优先用代码和命令完成机械扫描。

输出：

- repo file inventory
- language and LOC distribution
- top-level module size
- docs/config/dependency files
- candidate entry points
- candidate generated/test/vendor files
- candidate high-risk areas

这一阶段的目标是缩小 LLM 后续阅读范围，而不是得出架构结论。

### Phase 3: Repo Map Compression

把 Phase 2 的机械扫描结果压缩成 LLM 可消费的 `repo-map.md`。

要求：

- 保留文件与目录证据。
- 标注信息来源。
- 不添加未经验证的架构判断。
- 明确候选而非结论。

### Phase 4: Architecture Question Planning

LLM 只基于 repo map、README、核心文档和用户目标生成架构问题。

问题示例：

- 这个项目的核心数据流是什么？
- 哪些模块处在请求/任务/编译/执行路径上？
- 哪些抽象边界最能体现项目设计哲学？
- 哪些地方可能隐藏错误处理、兼容性、安全或性能约束？

输出 `evidence-plan.md`。

### Phase 5: Evidence-Scoped Module Analysis

subagent 不再按“读够多少行”工作，而是按 evidence scope 工作。

每个核心模块必须产出 Evidence Matrix：

| 字段 | 含义 |
|------|------|
| Module Role | 模块在系统中的职责 |
| Entry Points | 进入该模块的入口 |
| Core Data Structures | 理解设计必需的数据结构 |
| Main Flow | 主执行流程 |
| Cross-Module Dependencies | 与其他模块的依赖关系 |
| Key Design Decisions | 关键设计决策与权衡 |
| Risk Areas | 错误处理、兼容、安全、并发、缓存等风险点 |
| Source Evidence | 支撑上述结论的文件、行号、文档来源 |
| Open Questions | 需要主 agent 交叉验证的问题 |

每个模块草稿必须先写 Evidence Matrix，再写叙事分析。

### Phase 6: Risk Sampling

为了避免只分析 happy path，必须对高风险区域做抽样。

强制关注：

- 错误处理
- 插件系统
- 扩展点
- 兼容层
- 缓存
- 并发
- 权限和安全边界
- 配置加载
- generated/vendor/test 边界

如果仓库中存在这些区域，最终质量门必须说明是否抽样、抽样了什么、发现了什么。

### Phase 7: Quality Gates

最终报告生成前必须经过质量门。

质量门包括：

- Evidence Matrix 完整性检查
- 核心结论源码证据检查
- 跨模块一致性检查
- unsupported claim 检查
- risk sampling 检查
- Why > What 深度检查
- 报告叙事连贯性检查
- 关键单元覆盖率检查（`coverage-units.json` 达到所选模式的分档目标）

行覆盖率不再作为主指标，只作为辅助诊断指标。

### Phase 8: Report Synthesis

最终报告仍保持原 repo-analyzer 的深度分析风格：

- 场景化问题引入
- 项目全景
- 核心设计哲学
- 深度模块分析
- 设计权衡
- 批判性评价
- 业界对比
- Mermaid 架构图
- 可借鉴经验

报告不应变成目录结构说明或符号列表。

## Budget Profiles

快速、标准、深度三种模式不再只是源码行覆盖率不同，而是 evidence 深度、风险抽样强度和报告长度不同。

| 模式 | 目标 | Evidence 深度 | 风险抽样 | 外部调研 | 报告形态 |
|------|------|---------------|----------|----------|----------|
| 快速 | 快速理解项目全貌 | 只覆盖核心路径和核心模块 | 最小抽样 | 可跳过或只读 README/docs | 短报告 |
| 标准 | 常规架构分析 | 覆盖核心模块、关键边界和主要设计决策 | 标准抽样 | 按需搜索 | 完整报告 |
| 深度 | 深入研究设计决策 | 扩展到次要模块、边缘路径和替代方案 | 强抽样 | 完整调研 | 长报告 |

每个模式必须设置：

- 总耗时目标
- 总 token 预算
- subagent 数量上限
- 每个 subagent 的证据读取预算
- 最终报告长度上限
- 质量门最低要求

## User Stories

1. As a skill user, I want large repositories to be analyzed faster, so that I can use repo-analyzer on 50W-line projects without waiting hours.
2. As a skill user, I want token usage to be bounded, so that large analyses do not become prohibitively expensive.
3. As a skill user, I want the final report to preserve Why > What analysis, so that faster output does not become shallow summary.
4. As a skill user, I want every major architectural claim to include source evidence, so that I can trust the report.
5. As a skill user, I want the skill to identify core modules before deep reading, so that analysis effort focuses on important code.
6. As a skill user, I want fast, standard, and deep modes to have different evidence budgets, so that I can trade speed for depth intentionally.
7. As a skill user, I want external research to be optional or mode-aware, so that known/local/private projects do not waste time on low-value searches.
8. As a skill user, I want reports to remain readable and narrative-driven, so that the output teaches architecture rather than listing files.
9. As a skill user, I want the skill to surface uncertainty, so that I can distinguish verified conclusions from hypotheses.
10. As a skill user, I want high-risk architecture areas to be sampled, so that the analysis does not miss hidden constraints.
11. As a skill maintainer, I want a deterministic tool contract plus a doctor-verified tool environment, so that the skill runs predictably across Claude Code, Codex, and OpenClaw without silently degrading.
12. As a skill maintainer, I want deterministic repo scanning before model reasoning, so that mechanical work does not consume LLM attention.
13. As a skill maintainer, I want tool outputs treated as candidate evidence, so that generated maps do not become unverified conclusions.
14. As a skill maintainer, I want an Evidence Matrix schema, so that subagents produce comparable and mergeable module drafts.
15. As a skill maintainer, I want subagents scoped by evidence questions, so that they do not duplicate reads or drift into unrelated files.
16. As a skill maintainer, I want budget limits per phase and per subagent, so that one module cannot consume the whole analysis budget.
17. As a skill maintainer, I want a Phase 0 doctor preflight gate that blocks analysis and guides installation when required tools (graphify, symbol enumerators) are missing, so that analysis never runs in a silently degraded state.
18. As a skill maintainer, I want risk sampling for edge paths, so that faster analysis does not miss error handling, compatibility, security, or plugin boundaries.
19. As a skill maintainer, I want quality gates after subagent drafts, so that incorrect or unsupported claims are caught before final report generation.
20. As a skill maintainer, I want benchmark repositories, so that performance improvements can be measured instead of assumed.
21. As a skill maintainer, I want report quality scoring, so that speed gains do not silently degrade insight quality.
22. As a skill maintainer, I want cacheable repo maps and evidence indexes, so that repeat analyses are faster.
23. As a skill maintainer, I want the original analysis philosophy preserved, so that the skill remains a deep architecture analyzer, not a code-map generator.
24. As a skill maintainer, I want clear forbidden tools, so that contributors do not accidentally introduce heavy install-time requirements.
25. As a skill maintainer, I want benchmark output to include both performance and quality signals, so that tradeoffs are visible.
26. As a subagent, I want a narrow evidence scope, so that I can analyze deeply without reading unrelated code.
27. As a main agent, I want module drafts to include structured evidence first, so that final synthesis can verify and merge them safely.
28. As a reviewer, I want the final report to expose what was verified and what remains uncertain, so that I can judge reliability.
29. As a skill maintainer, I want v2 to be an explicit breaking release, so that dependency and doctor requirements are honest instead of hidden behind a v1 compatibility promise.
30. As a skill maintainer, I want deterministic CLI / scripts for doctor, scan, unit enumeration, summarization, and gates, so that mechanical work is implemented in code rather than prompt discipline.
31. As a user on Claude Code, Codex, or OpenClaw, I want runtime differences to be explicit, so that I understand when only parallelism or interaction style changes while quality gates remain mandatory.

## Implementation Decisions

- Treat Evidence-First Repo Analyzer as breaking v2. v2 prioritizes evidence reliability over v1's out-of-the-box, prompt-only workflow.
- Add minimal CLI / scripts as the implementation carrier for deterministic work: doctor, scan, units, summarize, and gate.
- Introduce an Evidence-First Analysis Pipeline with phases: deterministic scan, repo map generation, architecture question planning, evidence-scoped module analysis, risk sampling, quality gating, and report synthesis.
- Replace line-read coverage as the primary quality metric with key-unit coverage: `covered = anchored-and-analyzed key units / total key units`, where key units are enumerated by deterministic tools (graphify + universal-ctags / ast-grep).
- Require the numerator to satisfy two hard conditions: a `file:line` anchor AND a substantive design judgment (role / flow / tradeoff), so anchors cannot be padded with empty listings.
- Retain line-read coverage only as an auxiliary diagnostic metric, never as the denominator and never as an automatic fallback.
- Persist enumerated key units and their coverage status to `coverage-units.json`, so coverage is auditable unit-by-unit rather than as an opaque percentage.
- Define an Evidence Matrix for each core module: module role, entry points, core data structures, main execution flow, cross-module dependencies, key design decisions, risk areas, and source evidence.
- Add a deterministic tool contract that separates baseline tools, graph-intelligence tools (graphify), symbol enumerators, ecosystem-specific commands, and tools disallowed as analysis dependencies.
- Baseline tools should rely on commonly available deterministic operations: file listing, text search, line counting, dependency file inspection, documentation scanning, and Git metadata.
- Symbol enumerators (universal-ctags / ast-grep) provide language-aware indexing and are required for the new coverage definition; their availability is guaranteed by the doctor gate, not by runtime degradation.
- graphify is a supported, required-when-selected dependency; the skill assists installation and configuration via the doctor gate and does not silently degrade when it is absent.
- There is no automatic tool-degradation path; if required tools are missing, the doctor gate blocks analysis and guides remediation until all checks pass.
- Support Claude Code, Codex, and OpenClaw through an explicit runtime capability matrix. Missing native subagents may degrade to serial execution, but evidence requirements and quality gates do not degrade.
- Exclude local graphify hook files from published artifacts. Published packages must not contain maintainer-specific absolute paths.
- Add a budget scheduler for modes. Fast mode prioritizes overview and core evidence. Standard mode adds deeper module evidence and risk sampling. Deep mode expands evidence, cross-validation, and design decision analysis.
- Redefine subagent prompts around evidence scope rather than raw file coverage.
- Each subagent must produce an Evidence Matrix before narrative prose.
- Repo map output must be treated as a planning artifact, not a final source of truth.
- Every final report claim about architecture, module behavior, or design tradeoff must trace back to evidence gathered from source, docs, or external research.
- Preserve original deep-analysis principles: Why > What, code as ground truth, global design philosophy, critique, industry comparison, and coherent narrative.
- Add risk sampling categories: error handling, plugin or extension systems, compatibility layers, concurrency, caching, security boundaries, configuration loading, and generated-code boundaries.
- Add quality gates before final synthesis: evidence completeness check, unsupported-claim check, cross-module consistency check, risk-sampling check, and report-depth check.
- Add benchmark harness expectations: run old and new workflows against representative repositories and compare time, token, report depth, and claim accuracy.
- Add cache and incremental strategy for repo maps, scan summaries, evidence indexes, and external research notes.
- Keep final report as a single Markdown artifact, but allow internal drafts and evidence summaries to remain separate.
- Keep external research mode-aware: quick mode can skip it; standard mode runs it only when useful; deep mode performs broader research.
- Keep all deterministic commands read-only unless the user explicitly requests otherwise.

## Testing Decisions

- Tests should validate externally observable behavior of the skill workflow: produced plans, evidence matrices, quality gates, and final report structure.
- Do not test implementation details such as exact shell commands unless they are part of the documented tool contract.
- The primary test seam is the workflow output contract: given a representative repository, the skill should produce repo map, evidence plan, module evidence matrices, quality gate summary, and final report.
- Test fast, standard, and deep modes against the same fixture repository to confirm budget and depth differences.
- Test that the doctor preflight gate blocks analysis and emits remediation guidance when a required tool (graphify, symbol enumerator) is missing, and only allows analysis once all checks pass.
- Test that the final report does not contain unsupported architectural claims.
- Test that every core module has an Evidence Matrix.
- Test that risk sampling is performed for at least the required high-risk categories when those categories exist in the repository.
- Test that external research can be skipped or reduced in fast/local/private modes.
- Test that deterministic tool outputs are not treated as final architectural conclusions.
- Test that the doctor gate detects graphify presence/version and produces a `doctor-report.json` with per-check pass/fail.
- Test that key-unit coverage is computed from `coverage-units.json` and that numerator entries without a substantive judgment are rejected.
- Benchmark testing should include at least one small repository, one medium repository, and one large repository.
- Quality regression testing should compare new reports against legacy reports using human review or an explicit rubric: accuracy, depth, evidence quality, narrative coherence, and missed major modules.
- Performance regression testing should capture elapsed time, tool calls, approximate token usage, and number of source lines read.

## Benchmark Harness

The benchmark harness should measure both speed and quality.

Required metrics:

- elapsed time
- approximate token usage
- number of tool calls
- number of source files inspected
- number of source lines read
- number of evidence items collected
- number of unsupported claims detected
- number of missed major modules
- report quality score

Quality rubric:

- architectural accuracy
- evidence quality
- Why > What depth
- cross-module understanding
- narrative coherence
- critical evaluation
- useful takeaways

Benchmark set should include:

- one small repository for fast iteration
- one medium repository for normal behavior
- one large repository near the 50W-line target

## Cache and Incremental Strategy

The workflow should cache deterministic artifacts when possible:

- repo file inventory
- language and LOC distribution
- dependency metadata
- symbol index from graphify and the required enumerators
- repo map
- evidence plan
- external research notes

Cache invalidation should be based on:

- repository path
- commit hash
- relevant config file hashes
- skill version
- selected analysis mode

If cache is stale or unavailable, the workflow should fall back to full deterministic scan.

## Out of Scope

- Building a full language server or heavyweight semantic indexer beyond graphify + symbol enumerators.
- Guaranteeing perfect architecture understanding for every language ecosystem.
- Rewriting the whole skill into a standalone application.
- Removing the original analysis philosophy documents.
- Producing binary reports, dashboards, or UI.
- Publishing benchmark results to a remote service.
- Adding provider-specific private APIs that make the skill unusable in other agents.
- Publishing maintainer-local `.claude` / `.codex` hook settings or absolute graphify paths.
- Running package installation or modifying analyzed repositories during scan.
- Treating deterministic tool output as final architecture analysis.
- Silently degrading to line coverage or regex enumeration when required tools are missing (the doctor gate blocks instead).

## Further Notes

This spec should be implemented conservatively. The highest-risk failure mode is producing faster but shallower reports. The main protection is to preserve the original quality philosophy while replacing only the evidence acquisition and budget control layers.

The first implementation slice should be:

1. Mark the workflow as breaking v2 and update user-facing docs accordingly.
2. Add the minimal CLI / scripts carrier: doctor, scan, units, summarize, gate.
3. Define Evidence Matrix.
4. Define the deterministic tool contract with graphify + symbol enumerators as doctor-guaranteed dependencies (no fallback tiers).
5. Add the Phase 0 doctor preflight gate: checks, `doctor-report.json`, and the remediation loop.
6. Rewrite the workflow phases around Evidence-First Analysis, including key-unit coverage and `coverage-units.json`.
7. Add runtime capability mapping for Claude Code, Codex, and OpenClaw.
8. Add budget profiles for fast, standard, and deep modes.
9. Add quality gates and benchmark expectations.
10. Keep original analysis philosophy intact.

Implementation should avoid speculative heavy infrastructure. Start with the minimal deterministic scripts needed to make doctor, scanning, unit enumeration, and quality gates repeatable; leave deeper automation until the workflow contract is proven on benchmark repositories.
