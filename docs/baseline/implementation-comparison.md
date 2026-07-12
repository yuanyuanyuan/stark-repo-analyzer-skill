# Reference And Implementation Comparison

This document separates physical reference evidence from the reimplementation control-plane regression. Fixture runs reuse a previously captured, source-locatable Graphify sidecar so the deterministic implementation can be tested without claiming a second semantic Graphify extraction.

| Project | Fixed HEAD | Physical snapshot | Physical coverage | Comparison | P4 |
|---|---|---|---:|---|---|
| `click` | `b67832c...` | `run-2`, `run-3` | stable | `physical-runs/click` | pass |
| `httpx` | `b5addb64...` | `run-1` | 97.43% bounded | `physical-runs/httpx/run-1/comparison.md`; Graphify blocked on isolation incident | not evaluated |
| `ruff` | `c588a3f...` | `run-1` | 70.3% bounded | `physical-runs/ruff/run-1/comparison.md`; Graphify blocked with record | not evaluated |
| `codex-plugin-cc` | `db52e28...` | `run-1`, `run-2` | stable | `physical-runs/codex-plugin-cc` | pass |
| `claude-code` | `a371abbe...` | `run-1` | 91.0% bounded | `physical-runs/claude-code/run-1/comparison.md`; Graphify blocked on isolation incident | not evaluated |
| `codex` | `9e552e9...` | `run-1` | 82.6% bounded | `physical-runs/codex/run-1/comparison.md`; Graphify blocked with record | not evaluated |

All six physical invocations used fixed local source snapshots and left those source trees clean after cleanup; the HTTPX and Claude Code Graphify runs recorded a transient output-isolation violation. Graphify status is explicitly blocked rather than inferred from report presence. P5 dynamic behavior remains pending, and R03-R05 remain separate implementation-regression work.

## Reimplementation Control-Plane Runs

| Project | Fixed HEAD | Sidecar input | Result | Evidence |
|---|---|---|---|---|
| `click` | `b67832c...` | physical `run-2` graph | complete; 1,809 nodes / 3,615 edges; 2 module tasks | `/tmp/stark-repo-analyzer-impl-click-fixture` |
| `codex-plugin-cc` | `db52e28...` | physical `run-1` graph | complete; 442 nodes / 1,074 edges; 1 module task | `/tmp/stark-repo-analyzer-impl-codex-plugin-fixture` |
| `httpx` | `b5addb64...` | physical `run-1` graph | complete; 1,587 nodes / 3,476 edges; 1 module task | `/tmp/stark-repo-analyzer-impl-httpx-fixture` |
| `ruff` | `c588a3f...` | no accepted graph artifact | blocked at Graphify contract | physical `run-1/graphify-failure.md` |
| `claude-code` | `a371abbe...` | physical `run-1` graph | complete; 16,205 nodes / 61,615 edges; bounded | `/tmp/stark-repo-analyzer-impl-claude-code-fixture` |
| `codex` | `9e552e9...` | no accepted graph artifact | blocked at Graphify contract | physical `run-1/graphify-failure.md` |

## Real Agent-Gated Runs

The following are independent real runs with accepted Graphify output and Agent-owned module drafts. They are evidence for the implementation control plane and source adjudication, not claims of semantic equivalence with the reference reports.

| Project | Fixed HEAD | Graphify result | Agent/coverage result | Final gate |
|---|---|---|---|---|
| `click` | `b67832c...` | raw `2,053/4,127`; normalized `1,900/4,010`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; target clean | 2 module drafts; `6,325/6,325` and `11,613/12,288`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-click-v3`: `validate --complete`, `finalize`, manifest `complete` |
| `codex-plugin-cc` | `db52e28...` | normalized `442/1,074`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; target clean | 1 module draft; `4,394/4,394`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-codex-plugin-v1`: `validate --complete`, `finalize`, manifest `complete` |
| `httpx` | `b5addb...` | raw `1,879/3,716`; normalized `1,584/3,472`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; bounded official tuning recorded in metadata; target clean | 1 module draft; `5,062/5,062`; source adjudication PASS | `/tmp/stark-repo-analyzer-real-httpx-v2`: `validate --complete`, `finalize`, manifest `complete` |
| `claude-code` | `a371ab...` | raw `16,225/61,639`; normalized `16,205/61,615`; `graphify 0.9.8`, auto-selected `deepseek/deepseek-v4-flash`; bounded official tuning recorded in metadata; target clean | 1 bounded module draft; `6,172/6,752` (`91.4%`); source adjudication PASS | `/tmp/stark-repo-analyzer-real-claude-code-v2`: `validate --complete`, `finalize`, manifest `complete` |

An earlier HTTPX retry in `/tmp/stark-repo-analyzer-real-httpx-v1` stalled after approximately nine minutes; the accepted `/tmp/stark-repo-analyzer-real-httpx-v2` run used the official bounded tuning flags and completed the full Agent-gated workflow. Claude Code completed the same bounded workflow in `/tmp/stark-repo-analyzer-real-claude-code-v2`; its module draft explicitly excludes the unread majority of `src/`. Ruff was retried in `/tmp/stark-repo-analyzer-real-ruff-v1` and made a final tuned retry in `/tmp/stark-repo-analyzer-real-ruff-v2`; both stopped after long-running partial semantic extraction without an accepted graph/report pair, with the final evidence in `/tmp/stark-repo-analyzer-real-ruff-v2/graphify-failure.md`. Codex was independently retried in `/tmp/stark-repo-analyzer-real-codex-v2`; after approximately 12.5 minutes it also remained in partial semantic extraction with no accepted graph/report pair. Ruff and Codex remain blocked rather than being represented by fixtures or partial graphs.

## Accepted Differences

- The implementation report is a deterministic fusion skeleton plus Agent-owned drafts; the fixture module drafts prove mechanical contracts only and are not semantic replacements for the reference reports. Semantic parity remains an Agent reading task.
- The implementation derives candidate module tasks from source directory groups. The reference workflow derives business modules through Agent reasoning, so task counts are expected to differ until real module drafts are supplied.
- The implementation refuses to continue when Graphify writes into the target or when the graph/report pair is absent. This is intentional and safer than accepting a partial report; the actual click attempt recorded this boundary after Graphify exit 0.
- `ruff` and `codex` remain blocked physical regressions because their Graphify artifacts are incomplete. No output is accepted for either project, preserving the failure boundary.

## Follow-Up Tasks

- Re-run Graphify for `ruff` and `codex` with an isolated, valid output pair, then rerun the fixture-independent implementation workflow.
- Run real Agent module-analysis passes on the remaining accepted workspaces and compare semantic module structure against `docs/baseline/reference-runs/`.
- Keep P5 dynamic behavior separate; these checks validate orchestration and contracts, not the analyzed projects' runtime behavior.
