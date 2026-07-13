# Graphify Code-Only Execution

- Version: `graphify 0.9.13` (`graphifyy==0.9.13`).
- Command: `graphify extract <target> --code-only --no-cluster`.
- Semantic extraction: disabled; no LLM/provider backend configured or invoked.
- Target: fixed Ruff HEAD `c588a3f7f57461692652d339936222b4496c5953`.
- AST corpus: 5,098 code files; raw graph 58,118 nodes and 152,791 edges.
- Cluster-only follow-up: 4,611 communities and 123,337 clustered edges.
- Normalized graph: 58,040 source-locatable nodes and 152,791 edges.
- Post-graph doctor: exit 0, failures empty.
- Runtime guard: Graphify's Python relative-module resolver raised `ValueError: PosixPath('/') has an empty name`; the isolated guard skipped only that failing edge resolution and preserved the rest of the code-only graph. It did not alter the Ruff source tree or the installed Graphify package.
- Raw artifacts are preserved under `graphify-out/raw-code-only-*`; normalized artifacts are the doctor-consumed `graph.json`, `GRAPH_REPORT.md` and `manifest.json`.

This is static code-structure evidence only. It must not be labeled `raw-deep`, semantic Graphify, or evidence of inferred business intent.
