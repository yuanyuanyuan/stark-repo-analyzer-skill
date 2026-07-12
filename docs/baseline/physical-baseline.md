# Physical Baseline Gate

This document separates source fidelity from evidence that the reference workflow actually ran. A report or a complete directory is not evidence of a real invocation.

| Level | Meaning | Required evidence | Current state |
|---|---|---|---|
| P0 | Reference source is fixed and readable | `source-corpus-manifest.json`, clean HEAD checks | PASS |
| P1 | Expected artifacts exist and are structurally parseable | six reference run directories, metadata, reports, checks and coverage | PASS |
| P2 | The reference skill was invoked through its real Agent/runtime entrypoint | fixed input, exit code, stdout/stderr, runtime events, metadata and output directory from that invocation | NOT READY |
| P3 | A machine verifier can classify the artifacts | `acceptance/physical-baseline-check.sh` plus `acceptance/doctor.sh` outputs | PASS for integrity; Graphify gate is implemented |
| P4 | The same fixed input can run twice independently | two complete snapshots, normalized structural diff, source/coverage/failure comparison and threshold | NOT READY |
| P5 | Dynamic behavior was exercised | runtime interaction trace or test execution evidence tied to the analyzed source commit | NOT READY |

## Gate Rules

- P2 and P4 are blocking gates for large-scale reimplementation. Existing baseline documents and partial physical run directories cannot promote either gate.
- P3 checks are deterministic. They may report an incomplete physical baseline without turning an incomplete baseline into a pass.
- A run snapshot must identify the source commit, input, analysis mode, tool versions, model/backend when applicable, start/end time, outputs and failure classification.
- Repeatability compares normalized JSON structure, source references, coverage tables and failure records. Timestamps, run IDs and temporary paths are excluded from the normalized comparison.
- The Graphify sidecar has its own gate: `doctor.sh preflight` must return `0` before extraction and `doctor.sh post-graph` must return `0` before the reference workflow consumes `drafts/01-graphify-map.md`.
- Doctor status codes are stable: `0=ready`, `10=bootstrap_required`, `20=user_configuration_required`, `30=blocked`.

## Current Evidence Boundary

The repository contains P0/P1 evidence and a stopped `click` physical-run directory. That directory explicitly says it was interrupted before decomposition completed, so it is not P2 evidence. Until the real reference runtime entrypoint and two independent runs are captured, the implementation must preserve this limitation in metadata and release notes.
