# Coverage Summary

Analysis mode: `standard` (required by baseline prompt).

| Module | Type | Files | Effective lines | Read lines | Coverage | Requirement | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Runtime broker / app-server protocol | Core | 7 | 1,503 | 1,503 | 100% | >=60% | ✅ |
| Command orchestration / lifecycle | Core | 11 | 2,627 | 2,627 | 100% | >=60% | ✅ |
| Plugin public contract | Secondary | 22 | 1,275 | 1,275 | 100% | >=30% | ✅ |
| **Allocated scope** | — | **40** | **5,405** | **5,405** | **100%** | — | **✅** |

Coverage is the union of actual line reads reported in the three module drafts. It does not count test execution as source-line coverage. Tests, lockfile, generated/build output, legal notices, and non-runtime reference content were intentionally excluded as described in `07-cross-validation.md`.
