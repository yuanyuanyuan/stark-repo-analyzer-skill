# Checks

| Check | Result | Evidence |
|---|---|---|
| Fixed HEAD | PASS | `git rev-parse HEAD` matched required value |
| Source tree read-only | PASS | pre/post `git diff --exit-code` clean |
| Outputs confined to current directory | PASS | all generated files are under `/tmp/stark-repo-analyzer-httpx-run-2` |
| Required drafts present | PASS | drafts listed below |
| External research | NOT PERFORMED | no web-search tool in execution environment |
| User preference confirmation | NOT PERFORMED | no interactive question tool in execution environment |
| Parallel subagents | NOT PERFORMED | no Agent tool exposed |
| Graphify extraction | PASS | `graphify 0.9.8`, fixed source, 1888 raw nodes / 3765 raw edges |
| Graphify normalization | PASS | 1584 source-locatable nodes / 3502 edges; `doctor post-graph` exit 0 |
| Graphify target isolation | BLOCKED | Graphify created transient target `graphify-out/`; cleaned and source rechecked clean |
