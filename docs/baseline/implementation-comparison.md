# Physical Reference Comparison

This document records the six-project physical regression boundary. It compares each new physical snapshot with the committed reference-output baseline; it does not claim that the reimplementation has passed the later R03-R05 implementation regression tasks.

| Project | Fixed HEAD | Physical snapshot | Physical coverage | Comparison | P4 |
|---|---|---|---:|---|---|
| `click` | `b67832c...` | `run-2`, `run-3` | stable | `physical-runs/click` | pass |
| `httpx` | `b5addb64...` | `run-1` | 97.43% bounded | `physical-runs/httpx/run-1/comparison.md`; Graphify blocked on isolation incident | not evaluated |
| `ruff` | `c588a3f...` | `run-1` | 70.3% bounded | `physical-runs/ruff/run-1/comparison.md`; Graphify blocked with record | not evaluated |
| `codex-plugin-cc` | `db52e28...` | `run-1`, `run-2` | stable | `physical-runs/codex-plugin-cc` | pass |
| `claude-code` | `a371abbe...` | `run-1` | 91.0% bounded | `physical-runs/claude-code/run-1/comparison.md`; Graphify blocked on isolation incident | not evaluated |
| `codex` | `9e552e9...` | `run-1` | 82.6% bounded | `physical-runs/codex/run-1/comparison.md`; Graphify blocked with record | not evaluated |

All six physical invocations used fixed local source snapshots and left those source trees clean after cleanup; the HTTPX and Claude Code Graphify runs recorded a transient output-isolation violation. Graphify status is explicitly blocked rather than inferred from report presence. P5 dynamic behavior remains pending, and R03-R05 remain separate implementation-regression work.
