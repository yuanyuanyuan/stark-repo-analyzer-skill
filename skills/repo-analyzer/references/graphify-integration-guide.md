# Graphify Integration Guide

This is the only Graphify-specific addition to the reference `repo-analyzer` workflow.

## Bootstrap and Doctor

The Agent may install or upgrade non-sensitive Graphify tooling and re-run the doctor. It must not create, read, print or bypass API keys, enterprise proxies or private provider configuration. A missing provider configuration is a user action and is reported as doctor code `20`.

Run from the skill repository root:

```bash
acceptance/doctor.sh preflight --target <target> --work-dir <WORK_DIR> --json
graphify extract <target> --mode deep --out <WORK_DIR>
acceptance/doctor.sh post-graph --target <target> --work-dir <WORK_DIR> --json
```

The extract command deliberately omits `--backend`. Graphify's `detect_backend()` owns provider priority. Record only the selected backend and model name. Do not downgrade to AST-only output when the required Graphify health gate fails.

## Retry Boundary

Only a classified network timeout, HTTP 429 or HTTP 5xx may be retried, with backoff and no more than two retries. Invalid configuration, permission errors, executor errors, empty graphs and incomplete artifacts fail immediately. The failed run keeps its diagnostic metadata and log.

## Consuming the Map

After post-graph succeeds, save a concise navigation map as `drafts/01-graphify-map.md`. Include graph counts, communities, candidate module paths and source citations. The map is not a report source by itself:

| Graphify confidence | Allowed use |
|---|---|
| `EXTRACTED` | Navigation candidate; verify against source before stating it as a fact |
| `INFERRED` | Pending verification only |
| `AMBIGUOUS` | Risk/question only |

The reference phases remain responsible for project research, questions, module analysis, coverage, cross-validation and final report fusion. The target repository remains read-only and all generated files remain under `$WORK_DIR`.
