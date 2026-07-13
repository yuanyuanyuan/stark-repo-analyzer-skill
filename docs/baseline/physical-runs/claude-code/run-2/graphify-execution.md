# Graphify Sidecar Execution

- Version: `graphify 0.9.8`.
- Preflight: `acceptance/doctor.sh preflight` exit 0; backend `deepseek`, model `deepseek-v4-flash`.
- Extract command: `graphify extract <target> --mode deep --out <run> --max-workers 8 --max-concurrency 8 --token-budget 24000 --api-timeout 120`.
- Cluster command: `graphify cluster-only <run> --max-concurrency 8 --batch-size 100`.
- AST extraction: 1,901/1,901 files completed. Semantic extraction: 1/1 chunk completed.
- Raw graph: 16,226 nodes and 61,639 edges. Normalized graph: 16,205 nodes and 61,615 edges.
- Post-graph doctor: exit 0.
- Visualization: skipped because the graph exceeded Graphify's 5,000-node HTML limit.
- Isolation: blocked. Graphify transiently created `graphify-out/` in the target tree; it was removed and the target was rechecked clean.
