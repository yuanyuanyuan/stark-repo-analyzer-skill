# Repo Analyzer v2

An Evidence-First skill for deep architectural analysis of open-source repositories. It preserves the original Why > What narrative style while making evidence collection, key-unit coverage, and final quality decisions auditable.

This is a breaking v2 release. The workflow now requires the bundled CLI and either Universal Ctags or ast-grep. Graphify remains an optional enhancement.

**[中文文档](README.zh.md)**

## Install

```bash
npx skills add yzddmr6/repo-analyzer
```

Or clone the repository into your agent's skills directory. Node.js 20 or newer is required for the deterministic CLI.

Install at least one symbol enumerator before analysis:

```bash
brew install universal-ctags
# or install ast-grep for your platform
```

## What Changed in v2

- Doctor is a hard preflight gate. Missing required tools, language support, or output permissions block analysis with remediation.
- `scan` produces a deterministic `repo-map.json` without running package-manager or ecosystem commands.
- `units` creates stable key-unit IDs, module classifications, parsed/unparsed lists, an auditable `parse_health` summary, reference provenance, and the coverage denominator.
- Each core module requires a machine-readable `module-evidence/*.json` Evidence Matrix plus narrative analysis.
- Coverage counts a unit only when status, source anchor, and substantive design judgment are all present.
- `gate` writes `quality-gate-report.json` and blocks synthesis on missing evidence, insufficient coverage, poor parse/reference quality, shallow reports, or undeclared unsupported areas.
- Quick, Standard, and Deep modes use 30/10, 60/30, and 90/60 percent core/secondary key-unit thresholds.
- Semantic Source Review re-reads sampled source spans before synthesis: Quick reviews 2-3 high-impact analyzed units globally, Standard reviews at least one per core module, and Deep reviews up to three per core module. This adds bounded review cost to reduce diluted or stale anchors; it is not a proof of truth.
- Graphify availability is recorded but never blocks Doctor.

## CLI

The agent runs these commands as part of the skill workflow:

```bash
repo-analyzer doctor --repo "$REPO" --out "$WORK_DIR"
repo-analyzer scan --repo "$REPO" --out "$WORK_DIR"
repo-analyzer summarize --repo "$REPO" --out "$WORK_DIR"
repo-analyzer units --repo "$REPO" --out "$WORK_DIR"
# The agent writes evidence-plan.md, module-evidence/*.json, and report.md.
repo-analyzer gate --repo "$REPO" --out "$WORK_DIR" --mode standard
```

Downstream commands cannot run until `doctor-report.json` has `allowed: true`. Final synthesis cannot proceed until `quality-gate-report.json` has `allowed_to_synthesize: true`.

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `doctor-report.json` | Per-check preflight status, remediation, and release decision |
| `repo-map.json` | Deterministic files, languages, manifests, dependencies, candidates, and exclusions |
| `repo-map.md` | LLM-facing candidate summary with sources and verification questions |
| `coverage-units.json` | Stable key units, module tiers, references, `parse_health`, and coverage state |
| `evidence-plan.md` | Architecture questions, candidate evidence, assignments, and budgets |
| `module-evidence/*.json` | Machine-readable Evidence Matrix for every core module, including sampled `semantic_reviews` |
| `report.md` | Narrative draft with explicit open questions and unsupported areas |
| `quality-gate-report.json` | Mechanical gate results and synthesis decision |

## Analysis Philosophy

Deterministic tools identify candidates; they do not produce architectural conclusions. Every important conclusion must be verified against source anchors, project documentation, or primary external sources. Reports still explain the project overview, core flows, module collaboration, motivation, trade-offs, alternatives, risks, and concrete recommendations instead of degrading into file or symbol inventories. The gate requires at least 80% overall and primary-language source parse rate, at most 20% unparsed core files, and at most 80% core units with partial or missing references.

When subagents are unavailable, the workflow runs serially and records `parallelism: degraded`; evidence completeness, coverage, and other quality requirements stay in force. **Full standard/deep acceptance** still requires real multi-subagent execution records (`parallelism: active`, subagent split, per-subagent artifacts, and main-agent merge). `parallelism: degraded` only proves a serial/CLI mechanical path—not multi-subagent pass. See `docs/specs/v2.0-multi-agent-acceptance.md`.

## Usage

Ask your coding agent naturally:

```text
分析项目 https://github.com/astral-sh/ruff
分析一下 ollama/ollama 这个仓库的架构
对比分析 express 和 fastify
```

The skill supports local paths, full GitHub/GitLab/Gitee URLs, and `owner/repo` shorthand. Reports default to Chinese unless the user requests another language.

## Development

```bash
npm test
npm run typecheck
npm pack --dry-run
```

The published package includes only the CLI runtime, skill files, user documentation, changelog, and license. Maintainer-local hooks, absolute paths, test evidence, and Graphify hook configuration are excluded.

## License

[MIT](LICENSE)
