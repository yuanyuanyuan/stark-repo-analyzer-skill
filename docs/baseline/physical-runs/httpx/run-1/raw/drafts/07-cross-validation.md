# Cross-Validation

Validation began only after all four module drafts had completed. The following representative claims were re-read from the fixed source by the primary analyzer.

| Claim | Primary-source check | Result |
|---|---|---|
| The client selects a transport only after request assembly and uses a `Request -> Response` contract. | `_client.py:1001-1023` selects a transport and calls `handle_request`; `_transports/base.py:22-65` defines the one-request contract; `_transports/default.py:230-262` converts the model at the httpcore boundary. | verified |
| Unread response streaming has explicit ownership and release behavior. | `_client.py:827-877` scopes `stream()` in `finally`; `_client.py:920-928` eagerly reads non-streamed results; `_models.py:935-972` closes after raw iteration. | verified |
| Stable user semantics are preserved across transports by models rather than by socket-specific types. | `_models.py:382-423` constructs `Request`; `_transports/default.py:230-262` consumes its raw URL/header/stream fields and creates `Response`; `base.py:22-65` exposes only these models. | verified |
| `httpcore` exceptions are translated on the HTTPX boundary, including while consuming response streams. | `_transports/default.py:57-95`, `121-133`, `230-262`. | verified |
| Default redirect behavior is explicit rather than inherited from Requests. | `docs/compatibility.md` states no default redirect following; client module reports `follow_redirects` handling in `_client.py:930-999`. | verified as documentation-plus-code claim |

## Resolved cross-module inferences

- The drafts' central thesis is supported: `Client` is the policy/lifecycle coordinator, models are the stable HTTP-value contract, and transports are replaceable executors.
- Transport adapters do not need to duplicate redirect, cookie, or authentication policy: the client coordinates those around `handle_request` / `handle_async_request`.
- Model streaming state and transport stream wrappers form a single lifecycle: transport returns a raw-capable `Response`; client binds timing/ownership; model iteration enforces consumed/closed state.

## Quality gate

All module drafts contain a coverage table and satisfy the standard-mode threshold. No module required supplemental source reading for coverage remediation.

## Remaining limits

- The claims concern only this fixed source snapshot. No Git history was inspected, so evolutionary rationale is intentionally absent.
- External ecosystem comparisons are bounded to local project documentation and well-known architectural distinctions; no external web research was performed.
