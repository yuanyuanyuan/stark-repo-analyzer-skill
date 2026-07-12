# Graphify Sidecar Failure Record

- Graphify extraction and normalized post-graph validation completed.
- Isolation failure: the Graphify command created a transient `graphify-out/` in the fixed source tree even though an external `--out` directory was supplied.
- Cleanup: only that tool-created untracked directory was removed; the source tree was rechecked clean.
- Classification: `target-output-isolation-violation`.
- Consequence: normalized graph evidence is retained for diagnosis, but this run is not a Graphify sidecar pass.

## Control-plane retry

On 2026-07-12, the implementation control plane retried the fixed HTTPX source in isolated work directory `/tmp/stark-repo-analyzer-real-httpx-v1`. After approximately nine minutes it remained in partial semantic extraction with no accepted `graph.json`/`GRAPH_REPORT.md` pair and was stopped. The HTTPX source tree remained clean, so no implementation report was accepted from this retry. A separate direct Graphify tuning experiment using the official bounded flags completed and passed normalization/doctor in `/tmp/stark-graphify-httpx-fast-v2`; it is not yet a control-plane run or Agent-gated report.
