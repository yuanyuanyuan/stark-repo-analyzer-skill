# Checks

## Completed

| Check | Command | Status | Evidence / limitation |
|---|---|---|---|
| Required fixed revision | `git -C SOURCE rev-parse HEAD` | PASS | `db52e28f4d9ded852ab3942cea316258ae4ef346` |
| Source integrity before/after | `git -C SOURCE status --porcelain=v1`; SHA-256 sentinels | PASS | Empty status; package and README fingerprints unchanged. |
| Unit/integration tests | `npm test` | PASS | 27 TAP subtests passed. |
| JavaScript syntax | `find . -name '*.mjs' ... | xargs node --check` | PASS | All non-test `.mjs` files parsed successfully. The first broad command mistakenly included JSON; see execution log. |
| JSON syntax | `find . -name '*.json' ... | xargs node -e JSON.parse` | PASS | All JSON files parsed successfully. |
| Version manifests | `npm run check-version` | PASS | `All version metadata matches 1.0.6.` |
| Coverage gates | Module draft tables | PASS | Both core and secondary targets are 100%; see `drafts/08-coverage.md`. |

## Intentionally Not Performed

- Build: `npm run build` is not executed because its prebuild writes generated app-server type files into the fixed source tree, prohibited by the run contract.
- Git-history analysis: prohibited by the run contract.
