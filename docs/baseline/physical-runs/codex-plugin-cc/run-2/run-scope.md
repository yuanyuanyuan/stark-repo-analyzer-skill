# Physical Baseline Run Scope

- Analysis mode: standard.
- Source tree: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/codex-plugin-cc`.
- Expected source HEAD: `db52e28f4d9ded852ab3942cea316258ae4ef346`.
- Output boundary: this directory and its descendants only.
- Source mutation: prohibited; analysis commands are read-only except project test processes, which are not run unless explicitly logged as safe.
- Git history: prohibited. `git rev-parse HEAD` and `git status --short` are used only to identify and protect the supplied snapshot; no history commands are used.
- Workflow deviation: the reference workflow normally creates a workspace under the user's home directory and asks interactive scoping questions. This invocation fixes the mode, source, and output boundary, so outputs are written here and no interactive question is asked.
- External research: not performed. The instruction to analyze only the fixed local source tree takes precedence; this is recorded in metadata and research notes.
