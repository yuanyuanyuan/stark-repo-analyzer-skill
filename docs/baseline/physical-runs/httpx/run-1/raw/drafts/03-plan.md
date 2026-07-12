# Analysis Plan

## Source and constraints

- Target only: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/httpx`
- Verified HEAD: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Source tree is read-only. Git history is prohibited and will not be queried.
- Outputs belong only in `/tmp/stark-repo-analyzer-httpx-run-1`.

## Scale assessment

| Scope | Python lines | Treatment |
|---|---:|---|
| `httpx/` production package | 8,827 | primary architecture scope |
| tests, docs, build configuration | excluded from effective-code estimate | consulted selectively as supporting evidence |

Mode is user-selected **standard**. Minimum targets: core modules >=60%; secondary modules >=30%. The report will measure actual requested line ranges, not infer reading from filenames.

## Feature-led questions

1. How does HTTPX maintain a familiar API while separating synchronous and asynchronous client execution?
2. Where is the boundary between user-facing HTTP semantics and `httpcore`'s connection/protocol implementation, and what extensibility does that boundary make possible?
3. How do URL/request/response models centralize normalization and state so transports remain interchangeable?

## Report structure

1. The client problem and ecosystem position
2. System map and the sync/async layering decision
3. Client lifecycle: configuration, request assembly, dispatch, redirects, and cleanup
4. Message semantics: URLs, headers, bodies, cookies, requests, responses, and streaming
5. Transport boundary: default network transport plus ASGI, WSGI, and mock adapters
6. Policy components: timeout, proxy/TLS configuration, authentication, decoding and multipart support
7. Critical assessment and reusable lessons

No interactive clarification was requested because the invocation fixes `standard` mode and explicitly requires the baseline artifacts. The report includes the scenario/competitor framing required by the reference skeleton.
