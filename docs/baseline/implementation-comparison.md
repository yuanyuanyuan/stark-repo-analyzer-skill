# Reference And Implementation Comparison

This document separates physical reference evidence from the reimplementation control-plane regression. Fixture runs reuse a previously captured, source-locatable Graphify sidecar so the deterministic implementation can be tested without claiming a second semantic Graphify extraction.

| Project | Fixed HEAD | Physical snapshot | Physical coverage | Comparison | P4 |
|---|---|---|---:|---|---|
| `click` | `b67832c...` | `run-2`, `run-3` | stable | `physical-runs/click` | pass |
| `httpx` | `b5addb64...` | `run-1`, `run-2` | run-1 97.43%; run-2 41.2% bounded | `physical-runs/httpx`; Graphify normalized and doctor-passed, isolation blocked | pending |
| `ruff` | `c588a3f...` | `run-1`, `run-2-code-only` | run-1 70.3%; run-2 bounded | `physical-runs/ruff/run-2-code-only/comparison.md`; code-only graph doctor PASS, semantic run blocked | not comparable across Graphify modes |
| `codex-plugin-cc` | `db52e28...` | `run-1`, `run-2` | stable | `physical-runs/codex-plugin-cc` | pass |
| `claude-code` | `a371abbe...` | `run-1`, `run-2` | run-1 91.0%; run-2 0.41% bounded | `physical-runs/claude-code`; Graphify normalized and doctor-passed, isolation blocked | pending |
| `codex` | `9e552e9...` | `run-1`, `run-2` | run-1 82.6%; run-2 15.24% bounded | `physical-runs/codex`; Graphify normalized and doctor-passed, isolation blocked | pending |

All six physical invocations used fixed local source snapshots and left those source trees clean after cleanup; HTTPX, Claude Code and Codex run-2 Graphify executions recorded a transient output-isolation violation. Physical Graphify status is explicitly blocked rather than inferred from report presence. P5 dynamic behavior is outside V1 scope; implementation regressions are recorded separately below.

Physical snapshots are invocation/evidence records, not semantic-parity replacements for `docs/baseline/reference-runs/`. The physical `codex-plugin-cc/run-2` report is 98 lines with three module families, while the earlier reference report is 196 lines with separate App Server, Broker, Hooks and secondary module drafts. The difference is recorded as `report-fidelity-mismatch` in `docs/agents/goal-execution-record.md`.

## Reimplementation Control-Plane Runs

| Project | Fixed HEAD | Sidecar input | Result | Evidence |
|---|---|---|---|---|
| `click` | `b67832c...` | physical `run-2` graph | complete; 1,809 nodes / 3,615 edges; 2 module tasks | `/tmp/stark-repo-analyzer-impl-click-fixture` |
| `codex-plugin-cc` | `db52e28...` | physical `run-1` graph | complete; 442 nodes / 1,074 edges; 1 module task | `/tmp/stark-repo-analyzer-impl-codex-plugin-fixture` |
| `httpx` | `b5addb64...` | physical `run-1` graph | complete; 1,587 nodes / 3,476 edges; 1 module task | `/tmp/stark-repo-analyzer-impl-httpx-fixture` |
| `ruff` | `c588a3f...` | code-only accepted graph; semantic run blocked | code-only physical report complete; semantic P3 remains blocked | `physical-runs/ruff/run-2-code-only/`; `run-1/graphify-failure.md` |
| `claude-code` | `a371abbe...` | physical `run-1` graph | complete; 16,205 nodes / 61,615 edges; bounded | `/tmp/stark-repo-analyzer-impl-claude-code-fixture` |
| `codex` | `9e552e9...` | no accepted graph artifact in physical snapshot | blocked at physical Graphify contract; implementation v3 later completed | physical `run-1/graphify-failure.md`; `/tmp/stark-repo-analyzer-real-codex-v3` |

## Real Agent-Gated Runs

The following are independent real runs with accepted Graphify output and Agent-owned module drafts. They are evidence for the implementation control plane and source adjudication, not claims of semantic equivalence with the reference reports.

| Project | Fixed HEAD | Graphify result | Agent/coverage result | Final gate |
|---|---|---|---|---|
| `click` | `b67832c...` | raw `2,053/4,127`; normalized `1,900/4,010`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; target clean | 2 module drafts; `6,325/6,325` and `11,613/12,288`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-click-v3`: `validate --complete`, `finalize`, manifest `complete` |
| `codex-plugin-cc` | `db52e28...` | normalized `442/1,074`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; target clean | 1 module draft; `4,394/4,394`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-codex-plugin-v1`: `validate --complete`, `finalize`, manifest `complete` |
| `httpx` | `b5addb...` | raw `1,879/3,716`; normalized `1,584/3,472`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; bounded official tuning recorded in metadata; target clean | 1 module draft; `5,062/5,062`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-httpx-v2`: `validate --complete`, `finalize`, manifest `complete` |
| `claude-code` | `a371ab...` | raw `16,225/61,639`; normalized `16,205/61,615`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; bounded official tuning recorded in metadata; target clean | 1 bounded module draft; `6,172/6,752` (`91.4%`); source adjudication PASS | `/tmp/stark-repo-analyzer-real-claude-code-v2`: `validate --complete`, `finalize`, manifest `complete` |
| `codex` | `9e552e...` | raw `84,554/220,435`; normalized `83,357/219,333`; `graphify 0.9.8`, auto-selected backend/model recorded in preflight; official bounded tuning recorded; target clean | 6 Agent business-module drafts; Session/turn bounded core slice `9,010/12,028` (`74.9%`); source adjudication PASS | `/tmp/stark-repo-analyzer-real-codex-v3`: `validate --complete`, `finalize`, manifest `complete` |

An earlier HTTPX retry in `/tmp/stark-repo-analyzer-real-httpx-v1` stalled after approximately nine minutes; the accepted `/tmp/stark-repo-analyzer-real-httpx-v2` run used the official bounded tuning flags and completed the full Agent-gated workflow. Claude Code completed the same bounded workflow in `/tmp/stark-repo-analyzer-real-claude-code-v2`; its module draft explicitly excludes the unread majority of `src/`. Ruff's semantic retries in `/tmp/stark-repo-analyzer-real-ruff-v1`, `/tmp/stark-repo-analyzer-real-ruff-v2` and `/tmp/stark-repo-analyzer-real-ruff-v3` stopped after long-running partial extraction without an accepted graph/report pair. The later `run-2-code-only` continuation completed the static evidence path without LLM chunking; it remains a distinct evidence kind and is not a semantic replacement. Codex v2 was similarly interrupted, but the subsequent v3 run completed the accepted graph, six Agent module drafts and final manifest.

## Accepted Differences

- The implementation report is a deterministic fusion skeleton plus Agent-owned drafts; the fixture module drafts prove mechanical contracts only and are not semantic replacements for the reference reports. Semantic parity remains an Agent reading task.
- The initial control plane derives candidate tasks from source directory groups; real Agent runs replace those candidates with business modules. Codex v3 records six responsibility/data-flow modules rather than treating its nine top-level directories as conclusions.
- The implementation refuses to continue when Graphify writes into the target or when the graph/report pair is absent. This is intentional and safer than accepting a partial report; the actual click attempt recorded this boundary after Graphify exit 0.
- `ruff` semantic extraction remains blocked, but the user-approved code-only continuation is archived as `graphify-code-only`; it is not a semantic P4 pass. HTTPX, Claude Code and Codex run-2 snapshots are complete invocation artifacts, but their P4 comparisons remain pending and their Graphify isolation gates remain blocked. Codex's separate v3 implementation run is complete; no partial physical graph was promoted. These residual risks remain explicit.

## Follow-Up Tasks

- Resolve Graphify target-output isolation, then rerun the P4 comparison for HTTPX, Claude Code and Codex.
- Re-open the physical report parity gap with full module decomposition and verification when an Agent-capable runtime is available; do not copy reference prose into physical snapshots.
- Run real Agent module-analysis passes on the remaining accepted workspaces and compare semantic module structure against `docs/baseline/reference-runs/`.
- Keep P5 dynamic behavior as a future tier; these checks validate orchestration and contracts, not the analyzed projects' runtime behavior.
