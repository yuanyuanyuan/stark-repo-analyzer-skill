# Graphify Sidecar Failure Record

- Command: `graphify extract <target> --mode deep --out <WORK_DIR>`
- Target: fixed Ruff source HEAD `c588a3f7f57461692652d339936222b4496c5953`
- Preflight: pass; Graphify `0.9.8`, backend/model selected by auto-detection and recorded in `doctor-preflight.json`.
- Outcome: interrupted after the full AST scan and only a small fraction of 145 semantic chunks; no complete `graph.json`/`GRAPH_REPORT.md` pair was accepted.
- Classification: `interrupted-after-long-running-semantic-extraction`.
- Consequence: Graphify post-graph was not run and this project is not a Graphify sidecar pass. The static reference-skill report remains valid as a separate P2 artifact.

## Control-plane retry

On 2026-07-12, the implementation control plane retried the same fixed source in isolated work directory `/tmp/stark-repo-analyzer-real-ruff-v1` using the same `graphify extract <target> --mode deep --out <WORK_DIR>` command. After approximately 13 minutes it remained at a partial semantic extraction with no accepted graph/report pair and was stopped. The Ruff source tree remained clean. This retry does not change the classification or create an accepted implementation run.
