# Module Plan

Narrative: CLI dispatch -> [selects the user-facing operation] -> core orchestration -> [turn state needs a deterministic automation boundary] -> exec/event processing -> [behavior requires policy inputs] -> configuration -> [commands require enforcement] -> sandbox facade.

| Module | Type | Representative evidence |
|---|---|---|
| CLI dispatch | Core | `codex-rs/cli/src/main.rs:1-180` |
| Agent/core orchestration | Core | `codex-rs/core/src/lib.rs:1-150` |
| Non-interactive execution | Core | `codex-rs/exec/src/lib.rs:1-150` |
| Configuration model | Core | `codex-rs/config/src/lib.rs:1-167` |
| Sandbox facade | Core | `codex-rs/sandboxing/src/lib.rs:1-71` |
| Repository documentation/tooling | Secondary | `README.md`, `AGENTS.md`, `package.json` |

## User questions

No user questions were asked in baseline mode. The report consequently uses a concise product introduction and code-first analysis.
