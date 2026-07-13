# Ruff Physical Run Comparison

The two snapshots are intentionally not a P4 repeatability pair:

| Snapshot | Graphify mode | Result |
|---|---|---|
| `run-1` | `0.9.8 --mode deep` with semantic extraction | interrupted after long-running semantic extraction; no accepted graph/report |
| `run-2-code-only` | `0.9.13 --code-only --no-cluster` | accepted static graph; post-graph doctor exit 0 |

The second run answers the user's request to remove Graphify LLM chunking and complete the previously unfinished Ruff run. It does not prove semantic extraction repeatability, and its report is not a semantic replacement for `docs/baseline/reference-runs/ruff/ANALYSIS_REPORT.md`.

Stable evidence from the new run:

- fixed source HEAD: `c588a3f7f57461692652d339936222b4496c5953`;
- source tree clean before and after analysis;
- code-only Graphify: 5,098 code files, 58,118 raw nodes, 152,791 raw edges;
- normalized post-graph doctor: ready, no failures;
- analysis model: `gpt-5.6-luna`, reasoning effort `low`;
- semantic extraction, external research, Git history, build/test and P5 dynamic validation: not performed or excluded as recorded in `metadata.json` and `checks.md`.
