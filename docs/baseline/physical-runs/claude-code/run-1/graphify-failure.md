# Graphify Sidecar Failure Record

- Graphify extraction and normalized post-graph validation completed.
- Isolation failure: the Graphify command created a transient `graphify-out/` in the fixed source tree even though an external `--out` directory was supplied.
- Cleanup: only that tool-created untracked directory was removed; the source tree was rechecked clean.
- Classification: `target-output-isolation-violation`.
- Consequence: normalized graph evidence is retained for diagnosis, but this run is not a Graphify sidecar pass.
