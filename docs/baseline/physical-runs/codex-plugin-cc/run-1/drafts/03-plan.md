# Standard Analysis Plan

## Scale and Mode

- Selected mode: **standard** (fixed by baseline request).
- Repository text inventory: 7,120 lines across source-adjacent Markdown, JSON, and JavaScript; the first focused inventory identified 6,494 lines in the primary executable/docs paths. Tests, lockfile, generated artifacts, and package metadata are excluded from effective implementation coverage where appropriate.
- The largest runtime files are `lib/codex.mjs` (1,219 lines) and `codex-companion.mjs` (1,073 lines); coverage must be measured by actual read ranges in module drafts.
- Coverage targets: core modules >=60%; secondary/public surface >=30%.

## Adaptive Questions Identified

1. Why is the app-server broker an isolated process with an endpoint handshake instead of spawning Codex for each command?
2. How does the plugin preserve host-agent ergonomics while making potentially long Codex work cancellable and resumable?
3. What does the optional Stop review gate gain, and what loop/usage risk does it deliberately expose?

## Non-interactive Decision Record

Reference stage 4 normally asks the user up to three questions, including desired report-introduction depth; stage 5 asks the user to confirm the outline. This physical run has a fixed workflow/mode and no requested interactive pause. Both actions are recorded as **not performed**, and the report uses a concise product introduction before code analysis.

## Planned Checks

Run tests, syntax/JSON parsing, version consistency, source snapshot integrity, module coverage gate, and cross-module claim sampling. Do not run build because it writes generated files under the source root.
