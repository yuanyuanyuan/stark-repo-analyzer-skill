# Repo Analyzer

An AI coding agent skill for deep architectural analysis of open-source projects. Generates professional-grade architecture reports with design insights, trade-off analysis, and Mermaid diagrams.

Compatible with [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), [OpenClaw](https://github.com/anthropics/openclaw), and any AI coding agent that supports the skills format.

**[中文文档](README.zh.md)**

## Related Articles

- [一键生成专业级分析报告：迭代20多轮的深度架构分析Skill，我决定开源了](https://mp.weixin.qq.com/s/sOPHFaNS8pIkhB4F-FysTQ)
- [Claude Code 源码深度架构分析](https://mp.weixin.qq.com/s/GjZ-tFBVwfJwK11F1lP5TQ)

## Quick Install

**npx (Recommended)**

```bash
npx skills add yzddmr6/repo-analyzer
```

**Plugin Marketplace**

```
/plugin marketplace add yzddmr6/repo-analyzer
/plugin install repo-analyzer@repo-analyzer
```

**Manual (Git Clone)**

```bash
# macOS / Linux
git clone https://github.com/yzddmr6/repo-analyzer.git ~/.claude/skills/repo-analyzer

# Windows
git clone https://github.com/yzddmr6/repo-analyzer.git %USERPROFILE%\.claude\skills\repo-analyzer
```

## Features

- **Architecture-level analysis** — Focuses on *why* things are designed the way they are, not just *what* the code does
- **Markdown repo map** — Before deep reading, builds a lightweight repo map (directory structure, language mix, entry-point and manifest candidates, core docs, test/generated/vendor candidates, and high-risk area candidates) using existing system commands to guide the Evidence Plan
- **Adaptive report structure** — No fixed template; chapters are designed based on each project's unique characteristics
- **Parallel subagent analysis** — Spawns multiple agents to analyze core modules concurrently for large codebases
- **Evidence Matrix module drafts** — Requires each core module draft to start with a Markdown evidence structure before narrative analysis
- **Unsupported claims check** — Before the final report, downgrades evidence-free judgments to assumptions, open questions, limitations, or unsupported areas
- **Risk-path sampling** — Requires each core module to sample relevant risk paths such as error handling, configuration, extension points, cache, concurrency, security boundaries, and generated/vendor/test boundaries
- **Budget profiles** — Defines Quick, Standard, and Deep modes by evidence depth, risk sampling strength, report length, subagent limits, and research intensity instead of source-line coverage
- **Competitive positioning** — Compares design philosophy and technical trade-offs against similar projects
- **Mermaid diagrams** — Architecture overviews, data flows, and per-module sequence diagrams throughout the report
- **Interactive workflow** — Asks targeted questions based on project traits before diving into analysis

## Usage

Simply ask Claude Code to analyze a project:

```
分析项目 https://github.com/astral-sh/ruff
```

```
分析一下 ollama/ollama 这个仓库的架构
```

```
对比分析 express 和 fastify
```

The skill also accepts `owner/repo` shorthand, full GitHub/GitLab/Gitee URLs, or local paths.

### Trigger Keywords

The skill activates automatically when you mention:

`分析项目` `分析仓库` `分析 GitHub` `项目分析` `源码分析` `架构分析` `代码分析` `学习这个项目` `研究这个框架` `看看这个库怎么实现的` `对比两个项目` `项目评测` `框架评测`

> **Note:** The skill outputs reports in Chinese by default. If you ask in another language, it follows your language.

## Analysis Modes

After scanning the codebase, the skill asks you to choose a depth level. The modes are cost boundaries, not source-line coverage targets: deeper modes spend more work on evidence, risk paths, secondary modules, alternatives, and research.

| Mode | Evidence Depth | Risk Sampling | Report Length | Subagent Limit | Research Intensity | Best For |
|------|----------------|---------------|---------------|----------------|--------------------|----------|
| **Quick** | Core paths and a small set of core modules; representative secondary evidence only | Minimal: at least one most relevant risk path per core module | Short report focused on overview and key conclusions | 2-3 core module subagents; secondary modules may be merged or skipped | Minimal: README/docs first, light search only when needed | Getting a high-level overview |
| **Standard** (default) | Core modules, key boundaries, and main design decisions | Standard: at least one risk path per core module, with extra samples for important boundaries | Full report with main trade-offs and critical evaluation | 4-6 core module subagents; secondary modules handled in batch | Standard: 3-5 searches plus official site/core docs | Regular architecture analysis |
| **Deep** | Secondary modules, edge paths, and alternatives in addition to core modules | Enhanced: multiple risk samples where useful, including edge paths and alternative-design risks | Longer report with richer alternatives and engineering maturity analysis | Around 8 subagents; split or merge modules when needed | Full: competitors, official docs, design docs, and first-hand sources | Studying every design decision |

Each run records the selected budget target and an execution summary: actual subagent count, module scope, risk samples, research scope, report length, and any scope reductions. v1.6 does not provide exact token billing or automatic token interruption.

## How It Works

1. **Clone & Scan** — Clones the repo (or uses a local path), counts effective lines of code by module
2. **Repo Map** — Before deep reading, builds a Markdown repo map from existing system commands with candidate signals (directory structure, language mix, entry points, manifests, core docs, test/generated/vendor candidates, high-risk areas); it feeds the Evidence Plan and never writes final architecture conclusions
3. **External Research** — Web searches for reviews, comparisons, and architecture discussions; crawls the official website
4. **Adaptive Q&A** — Generates targeted questions based on project characteristics, not a fixed checklist
5. **Dynamic Report Structure** — Designs chapter layout and writes a lightweight Evidence Plan for each core module before deep reading, drawing candidate entry points and modules from the repo map, plus architecture questions, required evidence types, risk paths, expected judgment scope, and the selected budget profile
6. **Parallel Deep Analysis** — Spawns subagents for each core module with its Evidence Plan and budget profile, and requires each core module draft to start with a Markdown Evidence Matrix covering role, entry points, data structures, main flow, dependencies, design decisions, risk-path samples, source evidence, and open questions
7. **Cross-Validation** — Verifies conclusions across modules, checks source anchors, checks whether module drafts answer their Evidence Plan, checks budget execution, and uses Evidence Matrix plus risk-path samples to spot gaps or conflicts before synthesis
8. **Multi-Source Fusion** — Merges research, module analyses, insights, Evidence Matrix comparisons, risk-path findings, and the budget execution summary into a cohesive narrative; runs a final unsupported-claims check so evidence-free judgments stay out of certain claims
9. **Final Report** — Outputs a single Markdown file with Mermaid diagrams that distinguishes verified conclusions from assumptions, open questions, limitations, and unsupported areas

The Markdown repo map is a pre-reading, low-dependency overview built from existing system commands; it only provides candidate signals and feeds the Evidence Plan. Evidence Plan is a planning-layer Markdown artifact embedded in the existing module plan. Evidence Matrix is a Markdown structure inside module drafts, used for comparison and synthesis before the final report. Risk-path sampling is a manual module-analysis rule: each core module samples at least one relevant boundary or failure path with source anchors, and final critical evaluation cites those findings. Budget Profiles make Quick, Standard, and Deep differ by evidence depth and cost boundary rather than line coverage. Unsupported Claims is a process-level final-report check: missing evidence is downgraded rather than auto-scored. This v1 workflow does not add a CLI, JSON schema, `module-evidence/*.json`, automatic parsing, automatic generation, automatic risk scanners, ecosystem commands, a graphify hard dependency, symbol enumerators, exact token metering, automatic token interruption, LLM judge, or a hard quality gate.

## Report Output

The final report is saved as a single Markdown file at:

```
~/repo-analyses/{project-name}-{date}/ANALYSIS_REPORT.md
```

Every report includes (adapted per project):

- **Problem Context** — What problem does this solve? Why do existing solutions fall short?
- **Competitive Positioning** — Design philosophy differences vs. alternatives (not feature checklists)
- **Project Overview** — Architecture at a glance
- **Deep Module Analysis** — Why > What analysis with trade-offs and industry comparisons
- **Evaluation & Takeaways** — Honest assessment of strengths, weaknesses, and lessons learned
- **Architecture Diagrams** — Mermaid charts for system overview and per-module flows

## Optional Dependencies

The skill works with Claude Code's built-in tools out of the box. For enhanced research capabilities, these MCP servers are optional:

- [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) — Website crawling via `tavily_crawl`
- [Brave Search MCP](https://github.com/anthropics/anthropic-quickstarts/tree/main/brave-search-mcp) — Alternative web search provider

## File Structure

```
repo-analyzer/
├── .claude-plugin/
│   └── plugin.json                         # Plugin metadata
├── package.json                            # Package manifest
├── skills/
│   └── repo-analyzer/
│       ├── SKILL.md                        # Main skill definition
│       └── references/
│           ├── analysis-guide.md           # Analysis philosophy & evaluation framework
│           └── module-analysis-guide.md    # Module analysis guide & subagent templates
├── README.md                               # English documentation
├── README.zh.md                            # Chinese documentation
└── LICENSE                                 # MIT License
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

If you'd like to improve the analysis workflow, the core logic lives in `skills/repo-analyzer/SKILL.md`. The evaluation framework and subagent templates are in the `references/` directory.

## License

[MIT](LICENSE)
