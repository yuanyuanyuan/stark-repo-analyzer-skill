# Coverage Summary

Coverage means the union of source line ranges actually read by a module analyst, per the reference skill. Tests, docs, and build configuration are excluded from the 8,827-line effective production-code denominator.

| Module | Type | Files | Effective lines | Read lines | Coverage | Target | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Client lifecycle and dispatch | core | 2 | 2,457 | 2,230 | 90.76% | >=60% | pass |
| HTTP message and URL semantics | core | 4 | 2,685 | 2,685 | 100.00% | >=60% | pass |
| Transport adapters and runtime policy | core | 8 | 1,482 | 1,482 | 100.00% | >=60% | pass |
| Supporting facilities | secondary | 9 | 2,203 | 2,203 | 100.00% | >=30% | pass |
| **Total** | — | **23** | **8,827** | **8,600** | **97.43%** | — | **pass** |

Core-only aggregate: 6,397 / 6,624 = **96.57%**, above the standard-mode core target.

The only production source not read is `_client.py:1036-1262` (227 lines), documented in the client module draft as repetitive synchronous convenience methods. No conclusion relies exclusively on that unread range.
