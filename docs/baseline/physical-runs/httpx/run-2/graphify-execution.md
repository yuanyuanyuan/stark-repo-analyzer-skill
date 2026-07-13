# Graphify Sidecar Execution

- Version: `graphify 0.9.8`.
- Preflight: `acceptance/doctor.sh preflight` exit 0; backend `deepseek`, model `deepseek-v4-flash`.
- Extract command: `graphify extract <target> --mode deep --out <run> --max-workers 8 --max-concurrency 8 --token-budget 24000 --api-timeout 120`.
- Cluster command: `graphify cluster-only <run> --max-concurrency 8 --batch-size 100`.
- Extraction: exit 0; raw graph 1,888 nodes and 3,765 edges; cluster-only completed with 147 communities.
- Normalization: raw artifacts retained; normalized graph 1,584 nodes and 3,502 edges.
- Post-graph doctor: exit 0.
- Isolation: blocked. Graphify transiently created `graphify-out/` in the target tree; it was removed and the target was rechecked clean.
