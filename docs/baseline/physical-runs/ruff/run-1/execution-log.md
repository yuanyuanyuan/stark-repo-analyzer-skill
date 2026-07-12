# Execution ledger

All commands below were issued from `/tmp/stark-repo-analyzer-ruff-run-1` unless a
source path was passed explicitly. Commands are read-only with respect to the Ruff
source tree. `mkdir -p drafts checks logs && touch logs/execution.log` modified only
this output directory.

| # | Command (abridged only for repeated file lists) | Exit | Result |
|---:|---|---:|---|
| 1 | `git -C <ruff> rev-parse HEAD` | 0 | requested HEAD matched |
| 2 | `git -C <ruff> status --short` | 0 | no output; clean at inspection |
| 3 | `rg --files <reference-skill-dir>` | 0 | located required three instruction files |
| 4 | `sed -n '1,260p' SKILL.md` and `sed -n '261,330p' SKILL.md` | 0 | full 274-line skill read |
| 5 | `sed -n '1,360p' references/analysis-guide.md` | 0 | full 166-line guide read |
| 6 | `sed -n '1,360p' references/module-analysis-guide.md` | 0 | full 150-line guide read |
| 7 | `rg --files <ruff>` | 0 | repository structure scan |
| 8 | `find <ruff>/crates ... -exec wc -l {} +` | 0 | 665,641 physical Rust lines (coarse count) |
| 9 | `sed` reads of `AGENTS.md`, `CLAUDE.md`, `README.md`, `Cargo.toml`, crate manifests and user docs | 0 | project/document evidence gathered |
| 10 | `cargo --version; rustc --version; cargo nextest --version` | 127 | all unavailable in environment |
| 11 | `test -f ...; test -s ...; find . -maxdepth 2 -type f` | 0 | all requested output artifacts present and non-empty |
| 12 | `tail -25 drafts/06-module-*.md | rg ...` | 0 | three core coverage tables detected |
| 13 | `sed` samples of CLI, lint/fix and formatter/printer source | 0 | cross-module contract claims verified |
| 14 | final `git -C <source> rev-parse HEAD; status --porcelain` | 0 | requested HEAD; no source modifications observed |
| 15 | `rg TODO...; test $? -eq 1` | 0 | no unfinished placeholder markers in deliverables |

## Source commands intentionally not run

- `cargo nextest run` / `cargo test`: `AGENTS.md` prescribes `INSTA_UPDATE=always` and
  `MDTEST_UPDATE_SNAPSHOTS=1`; these can mutate snapshots, while this baseline must not
  modify the source tree. They are also unavailable because `cargo` is absent.
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: unavailable
  because `cargo` is absent.
- Any `git log`, `git show <commit>`, blame, diff or history command: forbidden by user.
- Network search/crawl: not performed.
