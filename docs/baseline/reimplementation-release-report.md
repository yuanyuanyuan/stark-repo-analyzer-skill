# Stark Repo Analyzer V1 Release Report

## Delivered (Conditional Release)

V1 now provides a faithful repo-analyzer control plane with a required Graphify deep-extraction sidecar. It accepts local paths and public repository inputs, records fixed source identity, runs doctor preflight/post-graph gates, isolates Graphify output under the analysis workspace, normalizes source-locatable graph evidence, hands navigation context to Agent-owned module analysis, validates source citations and coverage, fuses a single Markdown report, and writes a hashed output manifest.

The original analysis responsibilities remain Agent-owned: external research, business-module boundaries, Why > What reasoning, source adjudication, Mermaid narratives, coverage accounting, and final report evaluation. Graphify is navigation evidence only; it does not replace source reading.

## Regression Evidence

| Area | Result | Evidence |
|---|---|---|
| Control-plane tests | PASS | `pytest -q`: 17 passed |
| Skill/plugin contract | PASS | `acceptance/skill-structure-check.sh` |
| Reference artifacts and doctor | PASS | `acceptance/run-contract-check.sh`, `acceptance/doctor-self-test.sh` |
| Physical baseline integrity | PASS | `acceptance/physical-baseline-check.sh` |
| Real accepted runs | PASS | Click, Codex plugin, HTTPX, Claude Code and Codex v3 workspaces finalized with complete manifests |
| Real blocked runs | EXPLICIT BLOCKED | Ruff semantic extraction remains blocked, while its separate code-only run is complete; HTTPX/Claude Code/Codex physical Graphify isolation remains blocked and their P4 comparisons remain pending |

Accepted real run workspaces:

- `/tmp/stark-repo-analyzer-real-click-v3`
- `/tmp/stark-repo-analyzer-real-codex-plugin-v1`
- `/tmp/stark-repo-analyzer-real-httpx-v2`
- `/tmp/stark-repo-analyzer-real-claude-code-v2`
- `/tmp/stark-repo-analyzer-real-codex-v3`

The cross-project result comparison is maintained in `docs/baseline/implementation-comparison.md`.

## High-Risk Review

- Source trees for all six fixed reference repositories remained clean.
- Graphify output stayed outside target repositories in accepted implementation runs.
- Doctor output records public backend/model identifiers without printing credentials.
- Empty graphs, missing source locations, incomplete module manifests and invalid output boundaries are rejected.
- Claude Code’s bounded module draft reports `6,172/6,752` core lines read (`91.4%`) and explicitly excludes the unread majority of `src/`.
- Ruff is not represented by fixtures or partial graphs; its Graphify blocker remains visible. Codex v3 is represented by a complete accepted graph/report pair and six Agent-owned business-module drafts; the older physical baseline failure remains separately documented.
- Physical baseline report depth is not treated as semantic parity: bounded snapshots may be shorter than earlier `reference-runs` reports when external research, subagent orchestration or project validation was unavailable.

## Residual Scope

P5 dynamic behavior is explicitly outside V1 scope: the analyzed projects were not built, tested, network-exercised or run interactively, and this release makes no claim about their runtime behavior. Ruff semantic extraction remains a documented residual risk; its code-only continuation is explicitly separate and does not establish semantic parity. R03 remains marked `[!]`. HTTPX, Claude Code and Codex now have physical run-2 evidence, but P4 comparison and target-output isolation are still pending. R04-R05/G01-G03 retain these residual risks.
