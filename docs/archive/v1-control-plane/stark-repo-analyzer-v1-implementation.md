# Stark Repo Analyzer V1 Implementation Goal

> **Status: superseded.** Replaced by the active
> [Graphify simplification roadmap](../../roadmap/graphify-simplification-roadmap.md).
> This document remains a historical record of the earlier V1 control-plane and
> six-project baseline goal.

## Historical Status

At the time this document was superseded, the V1 Graphify migration was in
progress. The target was Graphify `0.9.13+` `code-only` only; semantic/LLM
extraction had been removed from that path. Existing semantic physical/reference
runs remained historical comparison evidence. The Click pilot gate had passed
and was archived at `docs/baseline/physical-runs/click/run-4-code-only/`; the
six-project standard baseline remained pending under this historical goal.

## Objective

Strictly use the repository-root `goals.txt` and `tasks.txt` as the only control plane to implement `stark-repo-analyzer-skill` V1. Faithfully port the reference `repo-analyzer` phases, design logic, Why > What, source-code adjudication, real subagents, coverage, cross-validation, and report fusion. Add only a low-intrusion Graphify `0.9.13+ --code-only` sidecar and keep semantic reasoning in the source-reading agents.

P5 dynamic behavior validation of the analyzed repositories is explicitly out of V1 scope. V1 validates the analyzer's control plane and required Graphify/source-evidence workflow; it does not claim that the analyzed repositories were built, tested, network-exercised, or run interactively.

## Required Order

1. Complete D05 and D06.
2. Complete the P0.5 physical-baseline gate, especially P2 real invocation and P4 repeatability.
3. Complete S01-S04.
4. Complete I01-I08.
5. Complete R01-R05.
6. Complete G01-G03.

Do not advance past a dependency without the task's required evidence.

## Graphify And Doctor Boundaries

- All programmatic checks belong in `acceptance/doctor.sh preflight|post-graph`.
- Graphify raw and normalized output is isolated in `$WORK_DIR/graphify-out/`; the target repository is read-only. The normalized graph/report is a validated sidecar input, and only `$WORK_DIR/drafts/01-graphify-map.md` is passed into the reference workflow as navigation context.
- The control plane runs `graphify extract <target> --code-only --no-cluster --out <WORK_DIR>`, then may materialize `GRAPH_REPORT.md` with `cluster-only <WORK_DIR> --no-label --no-viz`; it retains `raw-code-only-*` and normalized artifacts, and `acceptance/doctor.sh post-graph` remains the acceptance gate.
- The original skill's flow and decision responsibilities do not change.
- Graphify does not replace source reading: `EXTRACTED` verifies core paths, `INFERRED` remains pending verification, and `AMBIGUOUS` is only a risk or question.

## Permissions And Failures

- Agents may install or upgrade non-sensitive Graphify tooling.
- Agents must not create, read, print, or bypass API keys, enterprise proxies, or private provider configuration.
- A non-zero doctor result stops the run. Current code-only extraction makes no provider calls and does not retry semantic/LLM failures; deterministic executor, empty graph, artifact and source-boundary failures stop immediately.

## Verification

Every task must have a fixed input, single output, verification command, failure classification, and evidence path before `tasks.txt` is updated to complete. The migration additionally requires one small-project pilot with real repo-analyzer subagents and an old-vs-new comparison before the six-project baseline rerun.
