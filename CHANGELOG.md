# Changelog

All notable release changes for repo-analyzer are recorded here. The product version true source is the root `VERSION` file.

## 1.1.2

- Corrective source release after v1.1.1: root `.gitleaks.toml` allowlists confirmed large baseline/UAT graph dumps so the exact full-history gitleaks command can finish; pre-release security scan evidence is completed **before** this tag.
- Clarifies that `--max-target-megabytes` must not substitute for full-history secret coverage.
- Analyzer user-facing Graphify gate and report contract are unchanged.

## 1.1.1

- Maintainer release gate: `docs/dev-rules/pre-release-security-scan/` requires worktree + full git history secret scans before tags / GitHub Releases.
- AGENTS, real-uat-regression, and dev-rules index route the security scan as a release blocker parallel to product UAT (they do not substitute for each other).
- `.gstack/` local security report artifacts are gitignored.
- Analyzer user-facing Graphify gate and report contract are unchanged in this release.

## 1.1.0

- Maintainer code map: `docs/code-map/` feature → layer → entrypoints index, with `docs/dev-rules/code-map/` maintenance rules and AGENTS task routing.
- Codex reminder hooks for stale code-map sync (`PostToolUse` edit + `Stop`); warn-only, never blocks edits.
- ADR-0027 records YAML semantic truth + Graphify assist + reminder-hook trade-offs.
- Default independent Judge with scoped review package (ADR-0026) remains the delivery close path.
- Analyzer user-facing Graphify gate and report contract are unchanged in this release.

## 1.0.0

- Skill core package delivers `SKILL.md`, references, bundled Graphify gate, and gate status schema.
- Claude Code and Codex install through adapter manifests that share one Skill implementation.
- Gate stable command: `python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>`.
