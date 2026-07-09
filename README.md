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
- **Adaptive report structure** — No fixed template; chapters are designed based on each project's unique characteristics
- **Parallel subagent analysis** — Spawns multiple agents to analyze core modules concurrently for large codebases
- **Evidence Matrix module drafts** — Requires each core module draft to start with a Markdown evidence structure before narrative analysis
- **Unsupported claims check** — Before the final report, downgrades evidence-free judgments to assumptions, open questions, limitations, or unsupported areas
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

After scanning the codebase, the skill asks you to choose a depth level:

| Mode | Source-Anchor Depth (guidance, not a gate) | Best For |
|------|---------------------------------------------|----------|
| **Quick** | Key judgments of core modules anchored; secondary modules sampled | Getting a high-level overview |
| **Standard** (default) | All key judgments of core modules anchored; representative anchors for secondary | Regular architecture analysis |
| **Deep** | Every design decision anchored, including secondary modules | Studying every design decision |

## How It Works

1. **Clone & Scan** — Clones the repo (or uses a local path), counts effective lines of code by module
2. **External Research** — Web searches for reviews, comparisons, and architecture discussions; crawls the official website
3. **Adaptive Q&A** — Generates targeted questions based on project characteristics, not a fixed checklist
4. **Dynamic Report Structure** — Designs chapter layout and writes a lightweight Evidence Plan for each core module before deep reading, including architecture questions, candidate entry points, required evidence types, risk paths, and expected judgment scope
5. **Parallel Deep Analysis** — Spawns subagents for each core module with its Evidence Plan, and requires each core module draft to start with a Markdown Evidence Matrix covering role, entry points, data structures, main flow, dependencies, design decisions, risks, source evidence, and open questions
6. **Cross-Validation** — Verifies conclusions across modules, checks source anchors, checks whether module drafts answer their Evidence Plan, and uses Evidence Matrix fields to spot gaps or conflicts before synthesis
7. **Multi-Source Fusion** — Merges research, module analyses, insights, and Evidence Matrix comparisons into a cohesive narrative; runs a final unsupported-claims check so evidence-free judgments stay out of certain claims
8. **Final Report** — Outputs a single Markdown file with Mermaid diagrams that distinguishes verified conclusions from assumptions, open questions, limitations, and unsupported areas

Evidence Plan is a planning-layer Markdown artifact embedded in the existing module plan. Evidence Matrix is a Markdown structure inside module drafts, used for comparison and synthesis before the final report. Unsupported Claims is a process-level final-report check: missing evidence is downgraded rather than auto-scored. This v1 workflow does not add a CLI, JSON schema, `module-evidence/*.json`, automatic parsing, automatic generation, LLM judge, or a hard quality gate.

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
