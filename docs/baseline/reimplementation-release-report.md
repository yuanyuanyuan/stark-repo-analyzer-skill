# Stark Repo Analyzer V1 Release Report

## Delivered

V1 now provides a faithful repo-analyzer control plane with a required Graphify deep-extraction sidecar. It accepts local paths and public repository inputs, records fixed source identity, runs doctor preflight/post-graph gates, isolates Graphify output under the analysis workspace, normalizes source-locatable graph evidence, hands navigation context to Agent-owned module analysis, validates source citations and coverage, fuses a single Markdown report, and writes a hashed output manifest.

The original analysis responsibilities remain Agent-owned: external research, business-module boundaries, Why > What reasoning, source adjudication, Mermaid narratives, coverage accounting, and final report evaluation. Graphify is navigation evidence only; it does not replace source reading.

## Regression Evidence

| Area | Result | Evidence |
|---|---|---|
| Control-plane tests | PASS | `pytest -q`: 16 passed |
| Skill/plugin contract | PASS | `acceptance/skill-structure-check.sh` |
| Reference artifacts and doctor | PASS | `acceptance/run-contract-check.sh`, `acceptance/doctor-self-test.sh` |
| Physical baseline integrity | PASS | `acceptance/physical-baseline-check.sh` |
| Real accepted runs | PASS | Click, Codex plugin, HTTPX and Claude Code workspaces finalized with complete manifests |
| Real blocked runs | EXPLICIT BLOCKED | Ruff and Codex have no accepted graph/report pair and retain complete failure records |

Accepted real run workspaces:

- `/tmp/stark-repo-analyzer-real-click-v3`
- `/tmp/stark-repo-analyzer-real-codex-plugin-v1`
- `/tmp/stark-repo-analyzer-real-httpx-v2`
- `/tmp/stark-repo-analyzer-real-claude-code-v2`

The cross-project result comparison is maintained in `docs/baseline/implementation-comparison.md`.

## High-Risk Review

- Source trees for all six fixed reference repositories remained clean.
- Graphify output stayed outside target repositories in accepted implementation runs.
- Doctor output records public backend/model identifiers without printing credentials.
- Empty graphs, missing source locations, incomplete module manifests and invalid output boundaries are rejected.
- Claude Code’s bounded module draft reports `6,172/6,752` core lines read (`91.4%`) and explicitly excludes the unread majority of `src/`.
- Ruff and Codex are not represented by fixtures or partial graphs; their Graphify blockers remain visible.

## Residual Scope

P5 dynamic behavior is intentionally not claimed: the analyzed projects were not built, tested, network-exercised or run interactively. Ruff and Codex require a later isolated Graphify run that produces a complete graph/report pair before their implementation workflows can be extended. R03 and R04 remain marked `[!]` in `tasks.txt` to distinguish completed evidence from successful regression output. This does not change the V1 failure boundary.
