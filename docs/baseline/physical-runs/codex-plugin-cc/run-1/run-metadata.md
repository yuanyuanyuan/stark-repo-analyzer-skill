# Physical Baseline Run Metadata

- Run name: `codex-plugin-cc`
- Workflow: reference `repo-analyzer`, `standard` mode
- Source (read-only): `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/codex-plugin-cc`
- Required source HEAD: `db52e28f4d9ded852ab3942cea316258ae4ef346`
- Observed source HEAD: `db52e28f4d9ded852ab3942cea316258ae4ef346`
- Output root: `/tmp/stark-repo-analyzer-codex-plugin-cc-run-b`
- Source mutations: none observed. Initial/final `git status --porcelain=v1` were empty; `package.json` and `README.md` SHA-256 fingerprints were unchanged.
- Git history: not used. `git rev-parse HEAD` and `git status` were used only to establish and verify the supplied fixed snapshot.
- Start time recorded: `2026-07-12T18:35:24+08:00` (first explicit timestamp collected during the run; reference guidance had been read before this timestamp was collected).
- End time: `2026-07-12T18:41:17+08:00`.
- Analysis mode: standard. Effective implementation code is below 50,000 lines, so no large-project simplification was applied.
- Mode confirmation: not performed. The physical baseline prompt fixed `standard`; no interactive AskUserQuestion surface exists in this run.
- Report-outline confirmation: not performed for the same non-interactive baseline constraint.

## Deliverables

- `ANALYSIS_REPORT.md`: integrated report.
- `drafts/03-research.md`, `03-plan.md`, `05-modules-plan.md`: research and analysis planning.
- `drafts/06-module-*.md`: independently authored module analyses.
- `drafts/07-cross-validation.md`, `08-insights.md`, `08-coverage.md`: quality gate and synthesis.
- `EXECUTION_LOG.md`, `CHECKS.md`: reproducibility record and command outcomes.
