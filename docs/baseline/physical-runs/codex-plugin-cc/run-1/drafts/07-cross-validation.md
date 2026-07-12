# Cross-Validation and Quality Gate

## Coverage Gate

| Module | Type | Files | Effective lines | Read lines | Coverage | Threshold | Result |
|---|---|---:|---:|---:|---:|---:|---|
| Runtime broker and app-server protocol | Core | 7 | 1,503 | 1,503 | 100% | 60% | ✅ |
| Command orchestration and lifecycle | Core | 11 | 2,627 | 2,627 | 100% | 60% | ✅ |
| Plugin public contract | Secondary | 22 | 1,275 | 1,275 | 100% | 30% | ✅ |
| **Allocated analysis scope** | — | **40** | **5,405** | **5,405** | **100%** | — | **✅** |

Excluded from effective coverage: 11 test files (validated by `npm test` rather than architecture-read coverage), package lockfile, generated/build outputs, license/notice files, and linked prompting reference material not required to understand the plugin's runtime boundary. This is a scope declaration, not a claim that those files were read.

## Claim Sampling

| Claim | Verification evidence | Result |
|---|---|---|
| A shared app-server broker explicitly refuses concurrent work while permitting interruption. | `app-server-broker.mjs:12-22,170-205` defines busy behavior and stream ownership; `turn/completed` releases the stream lock at `84-100`. | Verified. |
| Jobs are durable local control-plane records rather than terminal-only output. | `tracked-jobs.mjs` calls state persistence; `state.mjs:80-115,166-190` maintains index and per-job file; `codex-companion.mjs:838-880` reloads a background worker by job id. | Verified. |
| Review commands are declared read-only and runtime uses review-specific app-server paths. | `commands/review.md:13-16`; `commands/adversarial-review.md:15-18`; `codex-companion.mjs:358-457,712-760`. | Verified, with the limitation that host Markdown tool restrictions rely on Claude Code enforcement. |
| Stop gating is optional, configurable, and separate from the ordinary review command. | `hooks/hooks.json:4-37`; `codex-companion.mjs:540-554`; `stop-review-gate-hook.mjs:142-175`; README `225-237`. | Verified. |
| Plugin version manifests are synchronized. | `npm run check-version` succeeded: `All version metadata matches 1.0.6.` | Verified. |

## Resolved Cross-Module Notes

1. The broker module's concern about `upsertJob` is substantiated: `state.mjs` writes JSON directly and exposes no locking/atomic-replace protocol. This is a **risk under concurrent writers**, not proof that a production corruption event occurred.
2. The broker's busy error has a concrete user-facing path only insofar as command execution propagates app-server failures; no explicit retry queue was found in the sampled command code. This favors transparent failure over hidden serialization.
3. The public contract's read-only language is reinforced by runtime review paths and schemas, but Markdown `allowed-tools` remains a host-level policy rather than an independently enforceable operating-system boundary.
4. `SessionEnd` does tear down active session jobs and broker state, while retained Codex thread ids enable later `codex resume`. The design preserves conversational continuity but not the in-flight job process across Claude sessions.

## Quality Findings

- All module drafts include evidence, architecture/process explanation, global-philosophy linkage, and a coverage table.
- No subagent draft claims to have used Git history or run the broker against a real Codex installation.
- Report conclusions distinguish verified implementation behavior from external-product context and from proposed risks.
