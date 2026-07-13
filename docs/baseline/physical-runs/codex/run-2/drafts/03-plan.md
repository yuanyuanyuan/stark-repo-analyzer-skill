# Analysis Plan

## Mode and bounded scope

The requested mode is `standard`. The repository contains 5,395 tracked files and a very large Rust workspace; a full standard threshold of 60% of all effective code was not feasible in this single bounded run. The analysis therefore prioritizes the executable path and its policy boundaries.

Included: root product documentation, CLI dispatch, core orchestration surface, non-interactive exec surface, typed configuration exports, and sandboxing facade.

Excluded: tests, generated artifacts, lockfiles, Bazel/Nix implementation, TUI internals, app-server internals, provider implementations, MCP internals, and most leaf crates.

## Planned narrative

1. Product problem and repository shape.
2. CLI dispatch turns user intent into an execution mode.
3. Core turns and tool/context orchestration.
4. Exec event processing for automation and JSONL.
5. Config layering and policy inputs.
6. Sandbox facade and platform backends.
7. Cross-module tradeoffs and gaps.

## Required workflow deviations

- Interactive scope selection was not performed; scope was bounded by the baseline instruction.
- Agent subagents were not spawned because this runtime exposed no Agent tool; the single-agent path is recorded here and in `execution-log.md`.
- External research was not performed.
