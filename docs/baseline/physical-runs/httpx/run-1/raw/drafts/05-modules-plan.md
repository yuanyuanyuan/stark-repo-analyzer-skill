# Module and Narrative Plan

## Working design thesis

HTTPX appears to favor **stable user-facing HTTP semantics over a replaceable execution substrate**: the client owns request policy and lifecycle, models own HTTP values and streaming state, and transports translate that contract to network or in-process execution. The analysis will test this thesis against code evidence.

## Modules

| Module | Type | Assigned source scope | Why it is a module |
|---|---|---|---|
| Client lifecycle and dispatch | core | `_client.py`, `_api.py` | owns sync/async request orchestration, redirects, connection lifecycle, and top-level helpers |
| HTTP message and URL semantics | core | `_models.py`, `_urls.py`, `_urlparse.py`, `_content.py` | owns normalized HTTP values and request/response body state shared across clients and transports |
| Transport adapters and runtime policy | core | `_transports/`, `_config.py`, `_auth.py` | maps model contracts to network/ASGI/WSGI/mock execution and applies policy inputs |
| Supporting facilities | secondary | `_decoders.py`, `_multipart.py`, `_exceptions.py`, `_types.py`, `_utils.py`, `_main.py`, `_status_codes.py`, package exports | codecs, CLI, exceptions, types, and utilities that round out the public experience |

## Narrative chain

`client lifecycle` -> [needs stable request and response objects before dispatch] -> `message and URL semantics` -> [needs an execution contract that can target network or in-process applications] -> `transport adapters and runtime policy` -> [relies on codecs, multipart, exceptions, and CLI helpers for complete user experience] -> `supporting facilities`.

## Coverage approach

- Each core module gets an independent analyst and must meet 60% of its assigned production lines.
- The transport/policy analyst also owns the secondary-module draft and must meet 30% of secondary lines.
- The primary analyst will validate representative cross-module claims only after all module drafts complete.
