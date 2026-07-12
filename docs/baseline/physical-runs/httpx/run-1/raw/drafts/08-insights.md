# Architecture Insights

## Design philosophy: stable HTTP semantics, replaceable execution

HTTPX's most consequential choice is not simply “support sync and async.” It keeps the meaning of a request, response, URL, headers, cookies, content decoding, redirects, and authentication above the network backend. The `Client` then coordinates policy around a small transport interface, while default and in-process transports exchange the same `Request` and `Response` types. This explains why WSGI, ASGI, mock, proxy, and network paths can present one public API.

## What the sync/async split gets right

The source shares configuration and HTTP-rewrite rules in `BaseClient` but leaves synchronous and asynchronous dispatch explicit. That duplicates some control flow, but avoids obscuring Python's genuinely different iterator, close, context-manager, and hook protocols. For a public networking library, debuggability and predictable resource ownership are worth more than a clever generic executor.

## The important boundaries

1. **Models versus transports.** Canonical URLs and stateful request/response objects stop protocol implementation details from leaking to callers.
2. **Client versus transport.** Redirects, auth flows, hooks, cookies, and mount selection stay in the client; a transport executes a prepared request once.
3. **Eager versus streaming use.** The normal send path reads and closes for convenience; streaming is an explicit opt-in with a visible cleanup boundary.

## Tradeoffs and improvement opportunities

- The mirror-image sync and async loops create semantic-drift risk. Contract tests that exercise both variants from a shared scenario suite are more valuable than forcing a difficult common abstraction.
- `Headers` offers Mapping ergonomics by comma-joining duplicate values. That is convenient but unsafe as a universal reading model for special fields such as `Set-Cookie`; clearer field-aware access guidance or API naming would reduce misuse.
- Buffering a consumed request stream into `ByteStream` makes redirect/replay behavior predictable, but shifts cost into memory. Large-body callers need to retain the explicit streaming path and understand replay constraints.
- The transport API makes resource responsibility explicit, but custom transport authors must implement close behavior precisely. A small compliance test kit for custom transports would make the extension seam safer without expanding the core interface.

## Reusable lessons

An abstraction boundary is successful here because it carries real domain objects, not generic byte tuples: extensions can inspect a `Request`, return a `Response`, and still participate in the same lifecycle as the network implementation. The library is also deliberately opinionated in a few places: strict timeouts, non-default redirects, explicit streaming, and client-scoped cookies reject superficially compatible behavior when it would obscure network cost or state ownership.
