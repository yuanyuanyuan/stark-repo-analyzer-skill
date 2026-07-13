# Checks

| Check | Result | Evidence |
|---|---|---|
| Fixed source HEAD | PASS | `git rev-parse HEAD` = `9e552e9d15ba52bed7077d5357f3e18e330f8f38` |
| Source tree unchanged | PASS | `git diff --quiet` exit 0 |
| Git history used | NOT PERFORMED | intentionally excluded |
| Required reference files read | PASS | SKILL.md and both guides read |
| Outputs confined to current directory | PASS | all generated paths are relative here |
| Standard repository coverage | FAIL / bounded | see `drafts/08-coverage.md` |
| External web research | NOT PERFORMED | no search/fetch invoked |
| Tests | NOT PERFORMED | source must remain read-only and scope is analysis |
| Subagent parallelism | NOT PERFORMED | Agent tool unavailable in runtime |

| Graphify extraction | PASS | `graphify 0.9.8`, 84,522 raw nodes / 225,979 raw edges |
| Graphify normalization | PASS | 83,327 source-locatable nodes / 224,875 edges; `doctor post-graph` exit 0 |
| Graphify target isolation | BLOCKED | Graphify created transient target `graphify-out/`; cleaned and source rechecked clean |
