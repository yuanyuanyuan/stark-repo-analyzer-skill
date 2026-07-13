# Research Draft

## Scope

- Target: OpenAI Codex CLI monorepo at `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/codex`.
- Fixed source HEAD: `9e552e9d15ba52bed7077d5357f3e18e330f8f38`.
- Mode: `standard`, bounded source inspection.

## Core problem

Codex is a local coding agent: a user supplies a natural-language task, the agent reads and changes a repository, executes commands, and reports progress. The product must combine model interaction with local filesystem/process access while preserving an explicit approval and sandbox boundary. README.md describes the local CLI positioning; `codex-rs/cli/src/main.rs:1-180` exposes interactive, exec, review, MCP, plugin, app-server, resume, and sandbox entry points.

## Technical value proposition

The distinctive value is the integration boundary: model turns, tool execution, persistence, approval policy, and platform sandboxing are represented as a single product workflow rather than as independent shell scripts. `codex-rs/core/src/lib.rs:1-150` shows the core assembling threads, context, tools, exec policy, MCP, skills, rollout, and sandboxing.

## Comparable approaches

This baseline did not perform web research. The following are code-level comparison categories only, not externally verified competitor claims: terminal copilots, IDE-integrated agents, hosted cloud agents, and generic workflow/orchestration frameworks. A proper 3-5 competitor comparison is **not performed** because external search/fetch is unavailable under this bounded run.

## Organization/product motivation

The repository separates Rust crates by integration boundary (`codex-rs/*`) and keeps a thin root package for repository tooling. This supports platform-specific implementations and limits API coupling, while the core crate remains a broad orchestration hub.

## Sources consulted

- `README.md`
- `AGENTS.md`
- `package.json`
- `codex-rs/cli/src/main.rs`
- `codex-rs/core/src/lib.rs`
- `codex-rs/exec/src/lib.rs`
- `codex-rs/config/src/lib.rs`
- `codex-rs/sandboxing/src/lib.rs`

## Unperformed

- WebSearch and website traversal: not performed.
- Git history: not used by design.
- User preference questions and outline confirmation: not performed; fixed baseline invocation supplied no interactive answer.
