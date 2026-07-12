# Secondary Module: MCP and Plugins

## Role

MCP and plugins provide externally sourced tools, resources, commands, hooks and installation channels. They are an extension boundary, not the primary query algorithm.

## Evidence

MCP config supports signatures, duplicate suppression, allow/deny policy and scoped config loading (`src/services/mcp/config.ts:202-309`, `336-417`, `536-556`, `1258-1384`). MCP client code exposes connection caching, tool/resource/command fetching, result transformation and tool calls (`src/services/mcp/client.ts:552-595`, `1688-1743`, `2226-2408`, `2632-2720`, `3029-3262`).

Plugin loading has versioned cache paths, Git/NPM/local installation paths and manifest loading (`src/utils/plugins/pluginLoader.ts:126-183`, `293-365`, `470-718`, `1147-1265`). The command layer later merges plugin commands and skills with other sources (`src/commands.ts:445-468`).

## Design Assessment

The main design choice is to treat external capabilities as normalized tool/command records, then reuse permission filtering and query execution. MCP deduplication by server signature avoids duplicate prompt cost, while policy filtering makes enterprise restrictions explicit. The cost is a large configuration/transport surface whose exact runtime behavior cannot be built or tested here because dependencies and build configuration are absent.

## Coverage

| File | Lines | Read | Coverage |
|---|---:|---:|---:|
| `src/services/mcp/config.ts` | 1,578 | 732 | 46.4% |
| `src/services/mcp/client.ts` | 3,348 | 1,350 | 40.3% |
| `src/utils/plugins/pluginLoader.ts` | 3,302 | 742 | 22.5% |
| **Total** | **8,228** | **2,824** | **34.3% (secondary target 30%, pass for sampled module)** |

The plugin loader has important un-read marketplace/session paths; the pass is only for this declared sampled module scope, not all plugin code.
