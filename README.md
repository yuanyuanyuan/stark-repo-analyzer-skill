# Repo Analyzer

An AI coding-agent skill for deep architectural analysis of open-source repositories. It produces a source-backed report with design insights, trade-off analysis, Mermaid diagrams, and optional, auditable Graphify structure navigation.

Before deep source reading, the Agent checks for a compatible Graphify installation. When available, a code-only gate builds and validates the navigation graph. When unavailable, the Agent provides installation guidance and waits for the user to choose between rechecking after installation and using the source-only compatibility workflow for this run. Graphify supplies navigation context; source code resolves conflicts, and all generated artifacts stay outside the target repository.

Officially supported runtimes: [Claude Code](https://claude.ai/claude-code) and [Codex](https://github.com/openai/codex). Four install adapters share one Skill core package; other Skills-compatible hosts are outside the formal support matrix.

For Chinese documentation, see [README.zh.md](README.zh.md).

## Origin and attribution

This independently maintained Skill reimplements and extends ideas from the MIT-licensed [yzddmr6/repo-analyzer](https://github.com/yzddmr6/repo-analyzer) reference project, including an auditable Graphify navigation enhancement. It is not an upstream mirror or officially affiliated project, and its support scope is defined by this repository.

## Related Articles

- [Generate a Professional Analysis Report with One Command: The Architecture Analysis Skill Refined Through 20+ Iterations](https://mp.weixin.qq.com/s/sOPHFaNS8pIkhB4F-FysTQ) (Chinese)
- [Deep Architecture Analysis of the Claude Code Source](https://mp.weixin.qq.com/s/GjZ-tFBVwfJwK11F1lP5TQ) (Chinese)

## Quick Install

Install adapters share one Skill core package under `skills/repo-analyzer/`.

**npx**

```bash
npx skills add yuanyuanyuan/stark-repo-analyzer-skill
```

**Claude Code plugin**

```text
claude plugin marketplace add yuanyuanyuan/stark-repo-analyzer-skill
claude plugin install repo-analyzer@repo-analyzer
```

**Codex plugin**

Use the repository as a Codex plugin source:

```bash
codex plugin marketplace add yuanyuanyuan/stark-repo-analyzer-skill
codex plugin add repo-analyzer@repo-analyzer
```

After installation, Codex discovers the Skill from `skills/`.

**Manual installation**

```bash
# macOS / Linux
git clone https://github.com/yuanyuanyuan/stark-repo-analyzer-skill.git ~/.claude/skills/repo-analyzer

# Windows
git clone https://github.com/yuanyuanyuan/stark-repo-analyzer-skill.git %USERPROFILE%\.claude\skills\repo-analyzer
```

Gate command after Skill discovery:

```bash
python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>
```

`SKILL_ROOT` is the directory that contains the loaded `SKILL.md`. Hosts that cannot resolve that path must stop before starting the gate.

## Features

- **Architecture-level analysis** - Focuses on why the system is designed this way, not on listing functions.
- **Adaptive report structure** - Builds the report around each project's actual characteristics instead of a fixed template.
- **Parallel subagent analysis** - Assigns independent Agents to core modules for efficient large-codebase analysis.
- **Competitive positioning** - Compares design philosophy and technical approaches rather than feature checklists.
- **Mermaid diagrams** - Uses architecture, data-flow, and sequence diagrams throughout the report.
- **Interaction only when needed** - Standard analysis runs directly; explicit deep analysis performs one consolidated alignment round after a quick scan.

## Usage

Ask your coding Agent directly:

```text
Analyze project https://github.com/astral-sh/ruff
```

```text
Analyze the architecture of ollama/ollama
```

```text
Compare express and fastify
```

The skill accepts `owner/repo`, full GitHub/GitLab/Gitee URLs, and local repository paths.

Common trigger phrases include repository analysis, source analysis, architecture analysis, framework research, project evaluation, and project comparison. The skill also recognizes its documented Chinese trigger phrases.

The report defaults to Chinese and follows the user's language when another language is used.

## Analysis Modes

The skill uses standard analysis when no mode is specified. It enters deep analysis only when the user explicitly asks for it. There is no quick mode.

| Mode | Core module coverage | Secondary module coverage | Intended use |
|---|---:|---:|---|
| **Standard** (default) | >= 60% | >= 30% | Routine architecture analysis |
| **Deep** (explicit) | >= 90% | >= 60% | Confirm scope and priorities once after a quick scan, then investigate design decisions in depth |

## Workflow

1. **Clone and scan** - Clone the repository or use a local path, pin the commit, and select the analysis mode.
2. **Graphify navigation** - Run the code-only gate when Graphify is available; otherwise wait for the user's installation or compatibility choice.
3. **Scope and research** - Measure code size and gather external evidence; deep mode confirms scope and priorities in one consolidated interaction.
4. **Dynamic report design** - Define report sections and module boundaries from the repository's actual data flow.
5. **Parallel deep analysis** - Assign core modules to subagents; if subagents are unavailable, obtain user consent before sequential execution.
6. **Cross-validation** - Verify graph candidates and cross-module claims against source code and check reading coverage.
7. **Multi-source synthesis** - Combine research, module findings, and architectural insights into one coherent narrative.
8. **Final report** - Deliver one Markdown report with Mermaid diagrams.

## Report Output

The user receives one Markdown file:

```text
~/repo-analyses/{project}-{date}/ANALYSIS_REPORT.md
```

Each report includes, as relevant to the project:

- **Problem framing** - Concrete scenarios, user pain, and limitations of existing approaches.
- **Competitive positioning** - Differences in design philosophy and technical direction.
- **Project overview** - A fast mental model of the architecture.
- **Deep module analysis** - Why-over-what reasoning, trade-offs, and industry comparisons.
- **Evaluation and lessons** - Honest strengths, weaknesses, and reusable engineering insights.
- **Architecture diagrams** - System-level and module-level Mermaid diagrams.

## Optional Dependencies

The Agent can complete the source-only compatibility workflow with its basic source tools. Graphify `0.9.13+` is an optional structure-navigation enhancement. The Agent never installs or upgrades it automatically; when it is missing, the Agent provides guidance and waits for the user's choice.

The following MCP servers are optional research enhancements:

- [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) - Crawl websites with `tavily_crawl`.
- [Brave Search MCP](https://github.com/anthropics/anthropic-quickstarts/tree/main/brave-search-mcp) - Alternative web search.

## Repository Structure

```text
repo-analyzer/
|-- .claude-plugin/                         # Claude plugin + marketplace adapter
|-- .codex-plugin/plugin.json               # Codex plugin adapter
|-- .agents/plugins/marketplace.json        # Codex marketplace adapter
|-- skills/repo-analyzer/                   # Skill core package (single delivery source)
|   |-- SKILL.md
|   |-- scripts/graphify_gate.py
|   `-- references/
|       |-- analysis-guide.md
|       |-- graphify-integration-guide.md
|       |-- module-analysis-guide.md
|       `-- contracts/graphify-gate-status.schema.json
|-- package.json                            # Minimal identity for npx skills add
|-- VERSION
|-- CHANGELOG.md
|-- README.md
|-- README.zh.md
`-- LICENSE
```

## Contributing

Issues and pull requests are welcome.

The main workflow lives in `skills/repo-analyzer/SKILL.md`. The evaluation framework and subagent templates live under `skills/repo-analyzer/references/`.

## License

[MIT](LICENSE)
