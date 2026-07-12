# Stark Repo Analyzer V1 Implementation Goal

## Status

In progress. The user explicitly started implementation; remaining tasks stay active until their evidence is complete.

## Objective

Strictly use the repository-root `goals.txt` and `tasks.txt` as the only control plane to implement `stark-repo-analyzer-skill` V1. Faithfully port the reference `repo-analyzer` phases, design logic, Why > What, source-code adjudication, subagents, coverage, cross-validation, and report fusion. Add only a low-intrusion doctor and Graphify sidecar.

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
- Graphify produces only `$WORK_DIR/drafts/01-graphify-map.md` as navigation context for the reference workflow.
- Graph output is isolated in `$WORK_DIR/graphify-out/`; the target repository is read-only.
- The original skill's flow and decision responsibilities do not change.
- Graphify does not replace source reading: `EXTRACTED` verifies core paths, `INFERRED` remains pending verification, and `AMBIGUOUS` is only a risk or question.

## Permissions And Failures

- Agents may install or upgrade non-sensitive Graphify tooling.
- Agents must not create, read, print, or bypass API keys, enterprise proxies, or private provider configuration.
- A non-zero doctor result stops the run. Only doctor-classified timeouts, HTTP 429, and HTTP 5xx failures may retry, at most twice with backoff.

## Verification

Every task must have a fixed input, single output, verification command, failure classification, and evidence path before `tasks.txt` is updated to complete.
