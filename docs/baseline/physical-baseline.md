# Physical Baseline Gate

This document separates source fidelity from evidence that the reference workflow actually ran. A report or a complete directory is not evidence of a real invocation.

| Level | Meaning | Required evidence | Current state |
|---|---|---|---|
| P0 | Reference source is fixed and readable | `source-corpus-manifest.json`, clean HEAD checks | PASS |
| P1 | Expected artifacts exist and are structurally parseable | six reference run directories, metadata, reports, checks and coverage | PASS |
| P2 | The reference skill was invoked through its real Agent/runtime entrypoint | fixed input, exit code, stdout/stderr, runtime events, metadata and output directory from that invocation | PASS: all 6 projects |
| P3 | A machine verifier can classify the artifacts | `acceptance/physical-baseline-check.sh` plus `acceptance/doctor.sh` outputs | PASS for integrity; Ruff code-only post-graph doctor passes, while semantic-mode and target-isolation incidents remain recorded |
| P4 | The same fixed input can run twice independently | two complete snapshots, normalized structural diff, source/coverage/failure comparison and threshold | PASS: click and codex-plugin-cc; pending comparison for HTTPX, Claude Code and Codex; Ruff semantic/code-only snapshots are intentionally not comparable |
| P5 | Dynamic behavior was exercised | runtime interaction trace or test execution evidence tied to the analyzed source commit | OUT OF V1 SCOPE |

## Gate Rules

- P2 and P4 are blocking gates for large-scale reimplementation. P5 is evaluated and explicitly excluded from V1 acceptance; it remains a future validation tier. Existing baseline documents and partial physical run directories cannot promote either gate.
- P3 checks are deterministic. They may report an incomplete physical baseline without turning an incomplete baseline into a pass.
- A run snapshot must identify the source commit, input, analysis mode, tool versions, model/backend when applicable, start/end time, outputs and failure classification.
- Repeatability compares stable source/mode/coverage/failure fields, normalized JSON structure, source references and machine-level verification status. Timestamps, run IDs, temporary paths, report prose, module names and run-specific limitation wording are excluded from the normalized comparison.
- The repeatability comparator is `acceptance/physical-repeatability-check.sh <run-a> <run-b> [--json]`; it is a read-only classifier and cannot create a P4 pass without two complete run directories.
- The Graphify sidecar has its own gate: `doctor.sh preflight` must return `0` before extraction and `doctor.sh post-graph` must return `0` before the reference workflow consumes `drafts/01-graphify-map.md`.
- Doctor status codes are stable: `0=ready`, `10=bootstrap_required`, `20=user_configuration_required`, `30=blocked`.

## Current Evidence Boundary

The repository contains complete P2 evidence for all six projects. Click and codex-plugin-cc also have two-run P4 evidence with preserved failed attempts and passing normalized repeatability comparisons. HTTPX, Claude Code and Codex now have independent physical run-2 snapshots, but their reports were produced under the runtime's bounded single-agent/no-subagent conditions and their coverage fields are not stable enough to claim P4 without a passing comparison. Their normalized graphs pass post-graph doctor, but Graphify also wrote transient target `graphify-out/` directories; those were removed and the incidents are recorded, so their isolation gates remain blocked. Ruff now has a completed `graphify-code-only` run after semantic extraction was explicitly removed; it is not a semantic P4 repeatability pass, and the mode distinction is recorded in `run-2-code-only/comparison.md`. P5 dynamic behavior is a documented future tier and does not block V1; the overall P0.5 gate remains partial.

## Report Fidelity Boundary

`docs/baseline/reference-runs/` contains earlier high-fidelity reports produced with broader orchestration, separate module drafts, external-source context and project validation. `docs/baseline/physical-runs/` is an invocation/evidence baseline: a complete directory proves fixed-input execution and artifact lineage, not semantic parity or equal report length. The physical reports for HTTPX, Claude Code and Codex explicitly record missing subagent orchestration and bounded coverage. They must not be compared as interchangeable copies of the reference reports.
