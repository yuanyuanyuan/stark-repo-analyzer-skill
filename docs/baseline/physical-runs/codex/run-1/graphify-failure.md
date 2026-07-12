# Graphify Sidecar Failure Record

- Command: `graphify extract <target> --mode deep --out <WORK_DIR>`
- Target: fixed Codex source HEAD `9e552e9d15ba52bed7077d5357f3e18e330f8f38`
- Preflight: pass; Graphify `0.9.8`, backend/model selected by auto-detection and recorded in `doctor-preflight.json`.
- Outcome: interrupted during semantic extraction after the AST scan and partial chunk processing; no complete `graph.json`/`GRAPH_REPORT.md` pair was accepted.
- Classification: `interrupted-after-long-running-semantic-extraction`.
- Consequence: Graphify post-graph was not run and this project is not a Graphify sidecar pass. The static reference-skill report remains valid as a separate P2 artifact.

## Control-plane retry

On 2026-07-12, the implementation control plane retried the fixed Codex source in isolated work directory `/tmp/stark-repo-analyzer-real-codex-v2`. After approximately 12.5 minutes it remained in partial semantic extraction with no accepted graph/report pair and was stopped. The Codex source tree remained clean; this retry does not create an accepted implementation run.
