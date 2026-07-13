# Graphify Integration Guide

This is the only Graphify-specific addition to the reference `repo-analyzer` workflow. V1 uses static Graphify code-only evidence only.

## Bootstrap and Doctor

The Agent may install or upgrade the non-sensitive Graphify CLI. V1 requires Graphify `0.9.13` or newer with `--code-only`; it must not create, read, print or bypass API keys, enterprise proxies or private provider configuration because no LLM provider is needed.

Run from the skill repository root:

```bash
acceptance/doctor.sh preflight --target <target> --work-dir <WORK_DIR> --json
graphify extract <target> --code-only --no-cluster --out <WORK_DIR>
acceptance/doctor.sh post-graph --target <target> --work-dir <WORK_DIR> --json
```

The extract command must not receive `--backend`, a model, provider configuration, or semantic extraction flags. Record `extraction_mode: code-only`, `semantic_extraction: disabled`, and the Graphify version; backend/model fields are null by design. Do not downgrade to a hand-written or fixture graph when the code-only health gate fails.

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
