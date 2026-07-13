# Graphify Sidecar Execution

- Version: `graphify 0.9.8`.
- Preflight: `acceptance/doctor.sh preflight` exit 0; backend `deepseek`, model `deepseek-v4-flash`.
- Extract command: `graphify extract <target> --mode deep --out <run> --max-workers 8 --max-concurrency 8 --token-budget 24000 --api-timeout 120`.
- Cluster command: `graphify cluster-only <run> --max-concurrency 8 --batch-size 100`.
- AST extraction: 3,683/3,683 files completed. Semantic extraction: 20/20 primary chunks completed; adaptive retries preserved partial results for oversized documents.
- Raw graph: 84,522 nodes and 225,979 edges. Normalized graph: 83,327 nodes and 224,875 edges.
- Post-graph doctor: exit 0.
- Visualization: skipped because the graph exceeded Graphify's 5,000-node HTML limit.
- Isolation: blocked. Graphify transiently created `graphify-out/` in the target tree; it was removed and the target was rechecked clean.
