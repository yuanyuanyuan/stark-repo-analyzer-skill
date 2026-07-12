# Secondary Module: Entry and Terminal UI

## Role

The entry/UI module turns process startup into an interactive session: early prefetch, trust gating, migrations, command selection, state initialization and Ink/REPL rendering. It is the human-facing shell around the query/tool core.

## Evidence

`main.tsx` performs startup profiling, MDM/keychain prefetch and conditional imports before the rest of the entry code (`src/main.tsx:1-81`). It runs migrations and only prefetches Git context after trust or in non-interactive mode (`src/main.tsx:323-375`). The import graph shows that entrypoint code wires commands, tools, MCP, plugins, permissions, analytics and remote state into one startup surface (`src/main.tsx:82-168`).

## Design Assessment

The startup design prioritizes latency and safety: independent prefetches begin early, while Git operations are delayed behind trust. Conditional `feature()` imports reduce external builds but make the final deployed feature set unverifiable without build metadata. `main.tsx` is a very large integration point, so it is a strong composition root but a high-change coupling hotspot.

## Coverage

| File | Lines | Read | Coverage |
|---|---:|---:|---:|
| `src/main.tsx` | 4,683 | 822 | 17.6% |
| `src/replLauncher.tsx` | 22 | 22 | 100% |
| `src/setup.ts` | 477 | 180 | 37.7% |
| `src/entrypoints/init.ts` | 260 | 260 | 100% |
| **Total** | **5,442** | **1,284** | **23.6% (secondary target 30%, fail)** |

The failure is expected: the main entry and REPL screen are large integration files and only boundary-critical sections were read.
