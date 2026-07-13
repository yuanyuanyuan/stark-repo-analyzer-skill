# Cross Validation

## Verified relationships

1. `cli/src/main.rs` imports both `codex_core` configuration/thread facilities and `codex_exec`, confirming CLI composition at the product boundary.
2. `exec/src/lib.rs` uses an in-process app-server client and event processors, confirming non-interactive execution is an event consumer rather than a separate model implementation.
3. `core/src/lib.rs` exposes both policy/sandbox modules and thread/tool/context modules, confirming governance is part of turn orchestration.
4. `config/src/lib.rs` exports requirements and provenance types, matching the policy inputs consumed by core/CLI.
5. `sandboxing/src/lib.rs` provides platform dispatch and shared error conversion, confirming a portable enforcement facade.

## Architectural insight

The system's dominant pattern is governed orchestration: a single local agent loop is surrounded by explicit configuration provenance, execution modes, event protocols, persistence, and platform enforcement. This is stronger than a simple “chat plus shell” architecture, but concentrates evolution pressure in `codex-core` and the CLI composition root.

## Unverified

- Runtime call ordering inside the large files: not fully verified.
- App-server protocol compatibility and provider-specific behavior: not performed.
- Test evidence: not performed; test files were excluded.
