# Graphify Sidecar Execution

- `doctor.sh preflight`: exit 0.
- `graphify extract <target> --mode deep --out <WORK_DIR>`: exit 0; raw graph preserved in `graphify-out/raw-deep-graph.json`.
- `graphify cluster-only <WORK_DIR>`: exit 0.
- Source-locatable normalization: complete; `doctor.sh post-graph`: exit 0.
- Isolation check: failed because Graphify transiently created `graphify-out/` in the target tree; the generated directory was removed, the source tree is clean, and the sidecar remains blocked until the tool is isolated.
