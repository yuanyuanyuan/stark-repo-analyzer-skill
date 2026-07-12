# Input and Output Contract

## Trigger

Use the skill for repository architecture work when the request mentions project/repository analysis, source-code analysis, architecture analysis, framework research, project evaluation, or comparison of two projects. Do not use it for a single-file code question, debugging, or code review.

## Input

The request accepts one of:

- an existing local repository path;
- a public GitHub/GitLab/Gitee URL;
- an `owner/repository` identifier.

The resolved source is read-only. A local path is used as-is; a remote identifier is cloned into the run workspace and its resolved commit is recorded before analysis. V1 delivers the `standard` analysis mode only. The Graphify command still uses `--mode deep`; that is extraction depth, not a product analysis mode.

## Run Workspace

Each run owns a writable `$WORK_DIR` outside the target repository. It contains:

```text
$WORK_DIR/
  metadata.json
  execution-log.md
  drafts/
    01-graphify-map.md
    03-research.md
    03-plan.md
    05-modules-plan.md
    06-module-*.md
    07-cross-validation.md
    08-insights.md
    08-coverage.md
  graphify-out/
    graph.json
    GRAPH_REPORT.md
  ANALYSIS_REPORT.md
  checks.md
```

The target repository must not receive Graphify output, caches, drafts, metadata or reports.

## Required Flow

1. Normalize the input and capture source commit.
2. Run `acceptance/doctor.sh preflight --target <repo> --work-dir <dir> --json`; non-zero stops the run.
3. Run `graphify extract <target> --mode deep --out <WORK_DIR>` without `--backend`.
4. Run doctor post-graph. Only a healthy, non-empty graph with locatable sources may be consumed.
5. Read the graph map as navigation context, then retain the reference workflow: sizing, research, adaptive questions, module analysis, cross-validation, coverage gate and report fusion.
6. Write one final Markdown report plus metadata, log and checks.

## Failure Contract

- `0`: ready;
- `10`: Agent bootstrap may repair the Graphify executable/import and should re-run doctor;
- `20`: user configuration is required, such as a missing provider configuration selected by Graphify's own resolver;
- `30`: blocked by an invalid target/workspace, empty graph, invalid artifacts, source boundary violation or other non-transient error.

Only network timeouts, HTTP 429 and HTTP 5xx from Graphify's LLM call may be retried, at most twice with backoff. Configuration, permission, executor, empty-graph and artifact errors fail immediately.

## Report Contract

The final report is Chinese by default and must include project positioning, a project-wide view, module analysis, Why > What reasoning, Mermaid architecture visualization, source path/line evidence, limitations, unexamined scope and Graphify conflicts or unverified relations. `EXTRACTED` relations are evidence to verify; `INFERRED` relations remain pending verification; `AMBIGUOUS` relations are risks/questions only. Source code adjudicates conflicts.
