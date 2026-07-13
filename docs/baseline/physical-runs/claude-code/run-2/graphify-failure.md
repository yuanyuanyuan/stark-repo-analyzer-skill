# Graphify Sidecar Failure Record

- Classification: `target-output-isolation-violation`.
- The extraction was directed to the isolated run directory, but Graphify 0.9.8 also created a transient `graphify-out/` under the fixed Claude Code source tree.
- Cleanup removed only that tool-created directory. `git status --porcelain` was empty after cleanup.
- The raw and normalized sidecar artifacts remain available for diagnosis; this run is not counted as an isolation-clean P3 pass.
