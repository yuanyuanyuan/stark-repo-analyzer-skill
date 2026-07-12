# Physical Baseline Gate

This document separates source fidelity from evidence that the reference workflow actually ran. A report or a complete directory is not evidence of a real invocation.

| Level | Meaning | Required evidence | Current state |
|---|---|---|---|
| P0 | Reference source is fixed and readable | `source-corpus-manifest.json`, clean HEAD checks | PASS |
| P1 | Expected artifacts exist and are structurally parseable | six reference run directories, metadata, reports, checks and coverage | PASS |
| P2 | The reference skill was invoked through its real Agent/runtime entrypoint | fixed input, exit code, stdout/stderr, runtime events, metadata and output directory from that invocation | PASS: all 6 projects |
| P3 | A machine verifier can classify the artifacts | `acceptance/physical-baseline-check.sh` plus `acceptance/doctor.sh` outputs | PASS for integrity; Graphify sidecar blocked with records (httpx/claude-code isolation incident, ruff/codex interrupted) |
| P4 | The same fixed input can run twice independently | two complete snapshots, normalized structural diff, source/coverage/failure comparison and threshold | PASS: click and codex-plugin-cc |
| P5 | Dynamic behavior was exercised | runtime interaction trace or test execution evidence tied to the analyzed source commit | NOT READY |

## Gate Rules

- P2 and P4 are blocking gates for large-scale reimplementation. Existing baseline documents and partial physical run directories cannot promote either gate.
- P3 checks are deterministic. They may report an incomplete physical baseline without turning an incomplete baseline into a pass.
- A run snapshot must identify the source commit, input, analysis mode, tool versions, model/backend when applicable, start/end time, outputs and failure classification.
- Repeatability compares stable source/mode/coverage/failure fields, normalized JSON structure, source references and machine-level verification status. Timestamps, run IDs, temporary paths, report prose, module names and run-specific limitation wording are excluded from the normalized comparison.
- The repeatability comparator is `acceptance/physical-repeatability-check.sh <run-a> <run-b> [--json]`; it is a read-only classifier and cannot create a P4 pass without two complete run directories.
- The Graphify sidecar has its own gate: `doctor.sh preflight` must return `0` before extraction and `doctor.sh post-graph` must return `0` before the reference workflow consumes `drafts/01-graphify-map.md`.
- Doctor status codes are stable: `0=ready`, `10=bootstrap_required`, `20=user_configuration_required`, `30=blocked`.

## Current Evidence Boundary

The repository contains complete P2 evidence for all six projects. Click and codex-plugin-cc also have two-run P4 evidence with preserved failed attempts and passing normalized repeatability comparisons. The remaining four projects have one physical snapshot each plus a comparison report; P4 is therefore intentionally not claimed for those runs. HTTPX and Claude Code produced source-locatable normalized graphs and passed post-graph doctor, but Graphify also wrote transient target `graphify-out/` directories; those were removed and the incident is recorded, so their isolation gate remains blocked. Ruff and Codex deep extraction was interrupted after long semantic extraction. The overall P0.5 gate remains partial until these Graphify failures and P5 dynamic behavior are resolved.
