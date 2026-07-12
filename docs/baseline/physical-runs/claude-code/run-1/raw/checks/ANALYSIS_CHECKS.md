# Analysis Checks

## Preconditions

| Check | Result | Evidence |
|---|---|---|
| Required reference skill read before analysis | PASS | `SKILL.md`, `references/analysis-guide.md`, `references/module-analysis-guide.md` were segmented and read. |
| Source fixed HEAD | PASS | `git rev-parse HEAD` returned `a371abbe75ffa0d0a3c92290e2bbf56a7ef54367`. |
| Source tree not modified at initialization | PASS | `git diff --quiet` exit 0. |
| Git history not used | PASS | No log/show/rev-list command executed. |
| Source analysis read-only | PASS (ongoing) | All recorded source operations are read-only. |
| External research | NOT PERFORMED | Explicit local-only analysis scope. |
| Build/test/runtime execution | NOT PERFORMED | No package manifest found at checked root; execution not required for static architecture report and may create state. |

## Completion Gates

- [x] Each core draft contains a coverage table and >=60% aggregate coverage.
- [x] Each core draft has a Mermaid flow and evidence with source line numbers.
- [x] Two substantive claims per core draft have source-level spot checks.
- [x] Cross-module claims marked by agents are verified or downgraded.
- [x] Final report discloses scope, sources, limitations and non-performed work.
