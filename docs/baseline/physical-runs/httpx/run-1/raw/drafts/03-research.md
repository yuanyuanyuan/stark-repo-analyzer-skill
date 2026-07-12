# HTTPX Research Notes

## Evidence boundary

- Source repository: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/httpx`
- Fixed source HEAD: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- This run has not used Git history. Repository documentation and public project URLs named in the source are the initial primary sources.

## Core problem

Python callers need a single client interface that keeps the familiar `requests` ergonomics while handling connection reuse, HTTP/2, streaming, authentication, proxies, strict timeouts, and either synchronous or asynchronous application code. HTTPX presents both execution styles behind comparable APIs, while delegating socket/protocol work to `httpcore` (README.md; pyproject.toml).

## Concrete scenarios

1. A synchronous service needs persistent connections and explicit timeout behavior without moving its request code into an event loop.
2. An ASGI application needs concurrent outbound requests without blocking the loop, but should preserve familiar request, response, cookie, and authentication concepts.
3. A test suite or in-process application needs to direct a client at WSGI/ASGI applications or a mock transport rather than a network socket.

## Comparable projects and positioning

| Project | Positioning / route | Difference relevant to HTTPX |
|---|---|---|
| requests | ergonomic synchronous Python HTTP client | HTTPX retains broadly compatible usage but adds first-class async and HTTP/2 (README.md). |
| urllib3 | lower-level connection and protocol utility | HTTPX exposes higher-level request/response and client state, with `httpcore` below it (README.md). |
| aiohttp | async-first HTTP client/server stack | HTTPX seeks a paired sync/async client interface rather than coupling client use to an async-only API. |
| httpcore | HTTPX's declared underlying transport implementation | It isolates connection and protocol execution so HTTPX can focus on policy, models, and user-facing API (README.md). |

## Why a separate project

Combining `requests` with an unrelated async client would duplicate request construction, authentication, cookie, timeout, and response semantics across call sites. HTTPX's distinct value is a coherent client contract with sync and async realizations, plus replaceable transports and in-process adapters (README.md; docs/async.md; docs/advanced/transports.md).

## Organization motivation

The checked source identifies Encode's HTTPX project and publishes BSD-3-Clause metadata, but this source-only run has not established commercial strategy or organizational intent. **Not found / not performed:** external organizational research.

## Documentation consulted

- README.md: stated product position, feature and dependency list.
- pyproject.toml: Python support, runtime dependencies, optional feature boundaries, CLI entry point.
- Further local documentation is scheduled for the analysis phase; conclusions in this note are intentionally bounded to the current evidence.

## External research status

The reference workflow calls for 3-5 web searches and official-site traversal. No WebSearch/WebFetch capability is exposed in this run, and no substitute web search was used; therefore external-search and external-site-traversal requirements are **not performed**. Local source documentation remains the evidence base.
