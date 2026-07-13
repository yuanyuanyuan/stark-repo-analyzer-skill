# Physical Repeatability: Codex

- Runs: `run-1` vs `run-2`.
- Result: `FAIL`.
- Required artifact failure: run-1 lacks `graphify-out/graph.json`, `GRAPH_REPORT.md`, and `manifest.json`; its interrupted Graphify run cannot serve as a P4 comparison peer.
- Interpretation: run-2 is a valid independent physical snapshot, but P4 is not claimed.
