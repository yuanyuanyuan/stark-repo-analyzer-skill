# Ticket

- id: "11"
- title: "Spec: v2.2 standard/deep modes and rules-based tool usage"
- requirement_ref: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/11"
- source_issue: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/11"
- labels: ready-for-agent
- state: OPEN
- blocked_by: none
- saved_from: "GitHub Issue #11 body via gh issue view；本地 tickets 结构化落盘（含 test_plan）"
- saved_at: "2026-07-11T18:31:16+08:00"
- issue_created_at: "2026-07-10T07:40:22Z"
- issue_updated_at: "2026-07-11T09:23:58Z"
- note: "Issue 标题/正文写 v2.1 双模式合同；仓库/分支语境为 v2.2 standard/deep。实现时以本票与 issue 正文为准，不因版本号措辞漂移。"

## what_to_build

将 Repo Analyzer 的模式与工具策略收敛为可分发合同：

1. **去掉 quick**：对外只保留 **standard**（默认、可移植）与 **deep**（增强、能力门禁）。
2. **standard**：仅用基线确定性工具（Git、文件发现、行计数、文本搜索；可用 ripgrep/jq 作便利但不改变模式）。**禁止**使用 Graphify / Universal Ctags / ast-grep（即使已安装也必须忽略）。跨文件关系与类符号发现若来自文本/基线扫描，必须标为 heuristic / partial / missing。
3. **deep**：按**能力合同**门禁，而非固定工具包。必需能力：graph queries、symbol enumeration、reference edges。Graphify 为优先图提供方；Ctags / ast-grep 为符号或 AST 结构搜索的**补充**提供方。能力不足时 **拒绝执行、不降级 standard**；可产出诊断工件，**不得**产出分析报告。
4. **local rules**：可分发执行合同（模式允许/禁止工具、能力映射、官方来源元数据、doctor 矩阵、CLI 门禁、报告置信度披露、AI 安装 agent 提示范围）。规则是执行策略 SSOT；SKILL 工作流应指向对应 rule。
5. **doctor / CLI / reports / gate**：doctor 输出能力矩阵与可选 AI 安装 prompt；CLI 在分析前强制模式可用性；报告含 mode、rules version、tooling level、capability state、limitations；gate 与所选模式语义对齐；移除 quick 预算/阈值/测试残留。

不在分析过程中安装增强工具；不把 Graphify 变成 standard 硬依赖；不保留 quick 别名；不静默降级 deep。

## acceptance_criteria

1. 产品/CLI 仅暴露 **standard** 与 **deep**；默认模式为 **standard**；quick 不再作为支持模式（含预算、语义 review 阈值、测试期望清理）。
2. standard 在无增强工具环境可跑；即使机器上装了 Graphify/Ctags/ast-grep，standard **仍不调用**它们；启发式关系/符号在报告中可审计披露。
3. deep 在能力合同未满足时于分析开始前失败（非零退出/明确诊断），**不**降级 standard，**不**生成分析报告（诊断工件除外）。
4. deep 在合格图提供方（优先 Graphify）满足 graph queries + symbol enumeration + reference edges 时可执行；缺符号/结构能力时 doctor 可推荐 Ctags/ast-grep 作补充，而非强制永远三件套。
5. 存在可分发 **local rules**，每条工具分类含：tool name、capability、mode usage、official source URL、verified date、fallback/rejection；SKILL/工作流引用 rules 而非仅靠散文。
6. doctor 输出 **capability matrix**（available/blocked modes、missing capabilities、detected tools、official-source refs、remediation）；支持按目标模式打印 **AI installation prompt**（只补缺失能力、禁止未授权改被分析仓源码/依赖清单）。
7. 分析报告含实际 mode、rules version、tooling level、capability state、confidence/limitations；gate 行为与 standard/deep 合同一致。
8. 自动化测试覆盖：CLI 可见行为与产物、doctor 矩阵三态（standard-only / deep-available / deep-blocked）、standard 忽略增强工具、deep 不降级、rules 官方源元数据、安装 prompt 范围、报告元数据字段。

## test_plan

### unit

- doctor：standard-only / deep-available / deep-blocked 能力矩阵字段与结论。
- CLI/模式门禁：standard 无增强工具可跑；standard 有增强工具仍忽略；deep 缺能力失败且不降级；deep 能力满足可进入分析路径。
- gate：移除 quick 期望；standard/deep 语义 review 与 coverage 期望符合新合同。
- rules：每条工具 rule 含 official-source 元数据与 verified date。
- 安装 prompt：反映缺失能力；不指示修改被分析仓库源码。
- 报告工件：mode / rules version / tooling level / capability state / limitations 存在。
- 执行：`npm test`（及仓库既有 typecheck 若适用）。

### e2e

- 最高缝合面：CLI 可见行为 + 生成工件 + 退出码（非内部 helper 顺序）。
- fixture：standard-only 环境；Graphify-qualified deep 环境；部分增强（应推荐补充工具）环境。
- 路径示例：doctor →（mode gate）→ scan/分析 → 报告/诊断 → gate；断言 deep 失败无分析报告、standard 报告标 heuristic 处可复核。
- 若某环境缺真实 Graphify：可用 mock/fixture 能力矩阵驱动门禁测试，并在用例说明中标注。

### uat

在 acceptance_env（建议 local-cli）下按 AC 逐步核对：

1. 仅 standard/deep 可选；默认 standard；文档/CLI 无 quick 支持承诺。
2. standard 跑通且未调用 Graphify/Ctags/ast-grep（日志/报告/tooling 元数据可证）。
3. 人为制造 deep 缺能力时：失败信息含缺失能力与 remediation；无分析报告。
4. doctor 矩阵与安装 prompt 可打印；prompt 含「不改被分析仓源码」约束。
5. 抽查 rules 文件：模式禁止列表、能力映射、官方 URL、verified date。
6. 报告/gate 与所选模式一致；基线 `npm test`（及 typecheck）退出码 0。

## Implementation Decisions（摘自 issue，实现约束）

- Remove quick；v2.x 仅 standard + deep；standard 默认。
- Baseline：Git、file discovery、line counting、text search；ripgrep 优先于 grep 仍属 standard；jq 可选便利、非必需。
- Standard 禁止 Graphify / Universal Ctags / ast-grep。
- Deep 能力：graph queries、symbol enumeration、reference edges；能力门禁非 bundle 门禁。
- Graphify preferred graph provider；Ctags supplemental symbols；ast-grep supplemental AST structural search。
- Graphify  alone 若已满足三能力则可过 deep；否则 doctor 推荐补充工具。
- Deep 失败：分析前 fail；可诊断工件；不分析报告；不降级。
- Doctor：capability matrix + AI installation prompt（按目标模式补缺失能力）。
- Installation prompt：未授权不得改 analyzed repo source / dependency manifests。
- Local rules：mode policy、capability mapping、official sources、fallback/reject；SKILL 指向 rules。
- Reports：mode、rules version、tooling level、capability state、confidence limitations。
- 保留既有 deterministic scan / doctor / units / summary / gate 管线概念，改模式合同与工具策略。

## Out of Scope（摘自 issue）

- 分析 run 内安装 Graphify/Ctags/ast-grep 等。
- Graphify 作为 standard 硬依赖；quick 别名；deep→standard 自动降级。
- standard 机会主义使用增强工具。
- 替换 evidence-first 哲学；要求外置 API key/托管服务/长驻 daemon。
- 完整 IDE 级 language server / 全语义编译前端。
- 在本 spec issue 内写完最终 rules 全文（本票定义行为；rules 内容为实现交付）。

## User Stories（索引，完整 1–25 见下方 Raw）

用户：双模式、standard 可移植且忽略增强工具、heuristic 披露、deep 能力门禁与拒绝、失败可诊断、安装 prompt、官方源可审计、Graphify 优先、Ctags/ast-grep 补充。  
维护者：rules SSOT、doctor 矩阵、CLI 门禁、报告元数据、gate 对齐、去 quick、官方源登记。  
Agent：机器可读允许/禁止/fallback；安装 agent 范围约束；报告 reader 可见 limitations。

## Further Notes（摘自 issue）

官方来源应写入 rules 并带 verified date：Graphify docs、Universal Ctags docs、ast-grep docs、ripgrep repo、Git docs、jq docs。  
核心纠正：**deep = capability-gated，不是 bundle-gated**。

---

## Raw Issue Body

> 以下为 GitHub Issue #11 原文，供对照；执行以本文件结构化字段 + AC + test_plan 为准。

## Problem Statement

Repo Analyzer currently mixes tool availability, analysis mode semantics, and quality expectations in a way that is hard to distribute as a reusable skill. The earlier quick / standard / deep model creates ambiguity: quick and standard overlap, enhanced tools can blur mode boundaries, and deep-mode requirements can accidentally become tied to a fixed tool combination instead of verified capabilities.

Users need v2.1 to provide a smaller, clearer contract: two modes only, a portable default mode, a capability-gated deep mode, and local rules that future agents can follow without rediscovering the intended tool policy from conversation history.

The current tool recommendations also need to be grounded in official documentation or official repositories. Published rules should say why a tool belongs in a mode, what capability it provides, what official source supports that classification, and what happens when the tool is unavailable.

## Solution

Repo Analyzer v2.1 will replace the quick / standard / deep model with exactly two modes: standard and deep.

Standard mode is the default, portable analysis path. It uses only baseline deterministic tools such as Git, file discovery, text search, line counting, and lightweight structured data processing where available. Standard mode must not use Graphify, Universal Ctags, or ast-grep. Its outputs must clearly mark cross-file relationships and symbol-like findings as heuristic when they come from text search or baseline scans.

Deep mode is the enhanced analysis path. It is gated by a capability contract rather than a hard-coded tool bundle. Deep requires graph queries, symbol enumeration, and reference edges. Graphify is the preferred graph provider when it satisfies those capabilities. Universal Ctags and ast-grep are supplemental providers when the graph provider lacks symbol enumeration or AST-level structural search. If deep capabilities are missing, the request is rejected and is not downgraded to standard.

v2.1 will introduce a local rules directory as a distributable execution contract. The rules define which tools each mode may use, which tools are forbidden, how doctor reports capability state, how the CLI gates modes, how reports disclose tool confidence, and how an AI installation agent should be prompted to configure optional enhancement tools.

## User Stories

1. As a repo-analyzer user, I want only standard and deep modes, so that I do not need to reason about overlapping quick and standard behavior.
2. As a repo-analyzer user, I want standard mode to work with common baseline system tools, so that I can analyze a repository without installing a graph stack first.
3. As a repo-analyzer user, I want standard mode to avoid enhanced tools even when they are installed, so that standard results are more reproducible across machines.
4. As a repo-analyzer user, I want standard mode to disclose heuristic relationships, so that I do not mistake text-search evidence for graph-level certainty.
5. As a repo-analyzer user, I want deep mode to require verified graph and symbol capabilities, so that deep results carry a stronger evidence contract.
6. As a repo-analyzer user, I want deep mode to refuse execution when required capabilities are missing, so that I am not silently given a weaker report.
7. As a repo-analyzer user, I want deep mode failures to explain missing capabilities, so that I know exactly what needs to be installed or configured.
8. As a repo-analyzer user, I want a command to print an AI-agent installation prompt, so that I can delegate optional tool setup safely.
9. As a repo-analyzer user, I want installation prompts to avoid modifying the analyzed repository source, so that setup cannot contaminate analysis evidence.
10. As a repo-analyzer user, I want Graphify to be preferred for deep graph analysis, so that graph queries, paths, and communities are available when supported.
11. As a repo-analyzer user, I want Universal Ctags or ast-grep to be supplemental rather than always mandatory, so that Graphify can stand alone when it already provides the required capabilities.
12. As a repo-analyzer user, I want official source URLs in tool rules, so that tool classification can be audited later.
13. As a repo-analyzer maintainer, I want mode definitions in local rules, so that future agents can execute the same policy consistently.
14. As a repo-analyzer maintainer, I want doctor to emit a capability matrix, so that mode availability is based on capabilities rather than ad hoc command checks.
15. As a repo-analyzer maintainer, I want the CLI to enforce mode availability before analysis, so that invalid deep runs do not create misleading artifacts.
16. As a repo-analyzer maintainer, I want reports to include mode, capability, and tool-confidence metadata, so that generated analysis remains auditable.
17. As a repo-analyzer maintainer, I want gate behavior to align with the selected mode, so that quality thresholds reflect the declared analysis contract.
18. As a repo-analyzer maintainer, I want quick-mode logic removed, so that budgets, semantic review thresholds, and tests no longer carry a deprecated mode.
19. As a repo-analyzer maintainer, I want official documentation checks recorded in rules, so that future tool substitutions are disciplined.
20. As a repo-analyzer maintainer, I want deep-mode setup failures to produce diagnostic output, so that users can recover without reading implementation internals.
21. As an AI coding agent, I want standard and deep rules to be machine-readable enough to follow, so that I do not infer tool policy from prose scattered across docs.
22. As an AI coding agent, I want the rules to state forbidden tools per mode, so that I do not accidentally use Graphify during standard analysis.
23. As an AI coding agent, I want the rules to state fallback behavior, so that I know when to continue, warn, or reject execution.
24. As an AI installation agent, I want a scoped setup prompt, so that I install only optional enhancement tools and report versions back to the user.
25. As a report reader, I want unsupported or low-confidence areas called out, so that limitations are visible in the final analysis.

## Implementation Decisions

- Remove quick as a supported analysis mode. v2.1 exposes only standard and deep.
- Standard is the default mode.
- Standard mode uses baseline deterministic tools only. The baseline set is Git, file discovery, line counting, and text search. ripgrep may be preferred over grep when available, but it does not change the mode from standard.
- jq may be used as a convenience for structured JSON processing when available, but it is not required for standard mode.
- Standard mode must not use Graphify, Universal Ctags, or ast-grep. If these tools are installed, standard still ignores them.
- Standard mode may generate heuristic candidates for symbols and references, but those results must be marked as heuristic, partial, or missing where appropriate.
- Deep mode is gated by capabilities: graph queries, symbol enumeration, and reference edges.
- Graphify is the preferred deep graph provider, based on official documentation describing Tree-sitter static analysis, AST extraction, call graphs, graph artifacts, graph queries, and community structure.
- Universal Ctags is a supplemental symbol provider, based on official documentation describing language-object tag generation and cross-reference output.
- ast-grep is a supplemental AST structural-search provider, based on official documentation describing AST-based search, rewrite, and lint capabilities.
- Deep mode does not require a fixed Graphify plus Ctags plus ast-grep bundle. It requires that the available provider set satisfy the capability contract.
- If Graphify satisfies graph queries, symbol enumeration, and reference edges for the target repository, Graphify alone can satisfy deep mode.
- If Graphify lacks symbol enumeration or structural support for the target repository, doctor can recommend Universal Ctags or ast-grep as supplemental tools.
- If deep capabilities are missing, CLI execution must fail before analysis begins. The request must not be downgraded to standard.
- Deep-mode failure may produce diagnostic artifacts, but it must not produce an analysis report.
- Doctor must report mode availability through a capability matrix. The matrix should include available modes, blocked modes, missing capabilities, detected tools, official-source references, and remediation guidance.
- Doctor should support printing an AI-agent installation prompt for optional enhancement setup.
- The installation prompt should be generated from the selected target mode. For deep, it should ask the installation agent to satisfy missing deep capabilities rather than blindly install every possible tool.
- The installation prompt must instruct the agent not to modify analyzed repository source code or dependency manifests unless explicitly authorized by the user.
- Local rules are a v2.1 feature. The rules define mode tool policy, capability mapping, official source requirements, fallback behavior, and rejection behavior.
- Rules must include official source metadata for each tool classification: tool name, capability, mode usage, official source URL, verified date, and fallback or rejection behavior.
- Rules are the source of execution policy. SKILL-level workflow text should point agents to the relevant rule before running a mode.
- Reports must include the actual mode, rules version, tooling level, detected capability state, and confidence limitations.
- Existing deterministic scan, doctor, units, summary, and gate concepts remain. v2.1 changes their mode contract and tool policy rather than replacing the entire pipeline.

## Testing Decisions

- The highest test seam should be CLI-visible behavior and generated artifacts. Tests should assert public outputs and exit status, not internal helper order.
- Doctor tests should assert the capability matrix for standard-only, deep-available, and deep-blocked environments.
- CLI tests should assert that standard can run without enhanced tools.
- CLI tests should assert that standard ignores enhanced tools even when they are present.
- CLI tests should assert that deep fails before analysis when required capabilities are missing.
- CLI tests should assert that deep does not downgrade to standard.
- CLI tests should assert that deep can run when the capability contract is satisfied by a qualified graph provider.
- Gate tests should be updated to remove quick-mode expectations and thresholds.
- Gate tests should assert standard semantic review and coverage expectations after quick removal.
- Gate tests should assert deep semantic review and coverage expectations under the new capability-gated mode.
- Report-artifact tests should assert that mode, rules version, tooling level, capability state, and limitations are present.
- Rules tests should assert that every tool rule includes official-source metadata and verified date.
- Installation-prompt tests should assert that generated prompts reflect missing capabilities and do not instruct source modification.
- Fixture tests should include standard-only environments, Graphify-qualified deep environments, and partially enhanced environments where supplemental tools are recommended.

## Out of Scope

- Installing Graphify, Universal Ctags, ast-grep, or other tools as part of the analyzer run.
- Making Graphify a hard dependency for standard mode.
- Keeping quick mode as an alias.
- Automatically downgrading deep to standard.
- Using enhanced tools opportunistically in standard mode.
- Replacing the existing evidence-first analysis philosophy.
- Introducing external API keys, hosted services, or long-running daemons as required analyzer dependencies.
- Building a complete IDE-grade language server or full semantic compiler frontend.
- Writing final v2.1 rules content in this spec issue beyond defining the required behavior.

## Further Notes

Official sources used to ground the tool classification include Graphify official documentation, Universal Ctags documentation, ast-grep documentation, ripgrep's official repository, Git documentation, and jq documentation. The v2.1 rules should record these sources directly with verified dates so future agents can revalidate the policy.

The most important design correction is that deep mode is capability-gated, not bundle-gated. Graphify is preferred, but Ctags and ast-grep are supplemental when Graphify does not cover required symbol or reference capabilities for a target repository.
