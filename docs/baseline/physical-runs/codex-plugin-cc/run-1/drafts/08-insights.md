# Architecture Insights

## Systemic Design Philosophy

The extension treats cross-agent integration as a **local control-plane problem**, not a prompt-routing problem. Commands are contracts; the app-server is a separately owned protocol process; jobs and session data are durable filesystem state; renderers expose the resulting state back to Claude users. This is why the code spends effort on endpoint discovery, PID/log cleanup, job IDs, explicit review schemas, and `status/result/cancel` rather than simply spawning `codex` and piping stdout.

## Strong Decisions

1. **Single broker with explicit busy semantics.** It protects a stateful app-server from ambiguous concurrent turns. Rejecting instead of silently queueing makes latency and ownership visible, which is appropriate for an interactive plugin.
2. **Filesystem-backed job model.** Detached work survives the originating CLI process and gains inspectable logs without requiring a daemon database. It is unusually practical for a zero-service plugin.
3. **Separate review and rescue permission tracks.** Read-only review and potentially writing delegation are represented as distinct commands/subagent contracts instead of a single permissive escape hatch.
4. **Optional, fail-closed parsing in the review gate.** When the gate is enabled and produces malformed review output, it blocks; when unavailable or disabled, it yields. This makes the tradeoff explicit, though users must understand it is not a universal security control.

## Tensions and Improvements

| Tension | Current choice | Improvement direction |
|---|---|---|
| Simple local state vs concurrent correctness | Direct JSON index and job-file writes | Use atomic temp-write/rename plus a lock, or a small SQLite store, before expanding concurrent usage. |
| Fast background start vs durable handoff | Worker spawn and job record creation have a narrow ordering window | Persist `queued` job before spawning; have worker update a claimed/started timestamp. |
| Clean SessionEnd vs long-running work | Session-owned jobs are terminated at session end | Offer an explicit detach/adopt mode with visible ownership and a TTL, rather than silently preserving jobs. |
| Manifest synchronization vs release narrative | Script verifies machine-readable versions; CHANGELOG trails at 1.0.0 | Add changelog/version validation to the release check or document intentional changelog policy. |
| Zero-dependency broker vs operational resilience | Temporary endpoint/PID/log lifecycle is best effort | Add single-flight startup locking and diagnostic status for stale endpoint cleanup. |

## Industry Perspective

The runtime resembles an LSP-style local JSON-RPC process plus an IDE task runner: protocol messages operate through a dedicated local transport, while human-facing work is represented by task IDs, logs, and cancellation controls. It consciously does not become a remotely scalable queue or a full orchestrator. That restraint is fitting for its product goal, but it makes file-level state integrity and lifecycle cleanup the architectural pressure points.

## Re-design Priority

1. Make state/job persistence atomic and lock-protected.
2. Remove startup/spawn ordering races with a durable queued-to-running state transition.
3. Make broker contention actionable: return retry metadata or provide a small observable queue, while retaining cancellation priority.
4. Keep review gate opt-in, but expose clear status explaining whether it is disabled, unavailable, timed out, or blocked.
