# Insights

## Design philosophy

Codex consistently makes boundaries explicit: subcommands are typed, execution output has separate human/JSON processors, config has source/provenance types, and sandbox backends are hidden behind a portable facade. The common philosophy is “make operational risk visible at the boundary.”

## Strengths

- One binary provides a coherent lifecycle and shared policy surface.
- Core modules expose a deliberate orchestration API instead of forcing callers to know every leaf crate.
- Non-interactive mode treats stdout as a protocol, which is important for CI and automation.
- Platform sandbox differences are isolated behind common request/error types.

## Risks and improvement directions

- `codex-core` and `cli/src/main.rs` are large composition hubs. More feature crates or command-specific dispatch modules would reduce change contention.
- The public config export surface is broad. A smaller typed runtime configuration plus internal layer types could reduce coupling while retaining diagnostics.
- Full architectural confidence requires reading app-server, provider, TUI, MCP, rollout, and policy implementations and their integration tests.

## Re-design thought experiment

Keep the explicit policy/event boundaries, but make the turn engine a smaller protocol-oriented crate and move product-specific orchestration into narrower adapters. This could preserve the current safety model while reducing the central core's architectural gravity.
