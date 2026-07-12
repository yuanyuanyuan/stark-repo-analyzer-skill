# 交叉验证

## 抽查结果

| 模块 | 结论 | 验证证据 | 结果 |
|---|---|---|---|
| 启动边界 | `remote-control` 在进入 bridge 前先验证认证、最低版本和策略 | `src/entrypoints/cli.tsx:108-160` | 已确认 |
| 启动边界 | bridge 因绕过主 TUI 初始化而自行初始化 config/sinks/trust | `src/bridge/bridgeMain.ts:2036-2093` | 已确认 |
| 会话调度 | 模型流获得会话级 abort signal | `src/query.ts:659-665` | 已确认 |
| 会话调度 -> 工具 | `query` 模块导入 `runTools` 和 `StreamingToolExecutor`，故工具循环属于模型回合而不是 UI 递归 | `src/query.ts:99-100`，以及模块草稿中的 `query.ts:621-720` | 已确认 |
| 工具/MCP | 并发仅针对输入解析成功且 `isConcurrencySafe` 的连续批次；异常降级为串行 | `src/services/tools/toolOrchestration.ts:26-67,91-115` | 已确认 |
| 工具/MCP | Hook allow 不绕过策略 deny/ask | `src/services/tools/toolHooks.ts:347-405` | 已确认 |

## 已撤销的候选问题

模块草稿曾标出 URL elicitation 完成通知可能向 `findElicitationInQueue` 传错参数。复核显示函数签名为 `(queue, serverName, elicitationId)`，调用在 `src/services/mcp/elicitationHandler.ts:189-193` 也严格按此顺序传入。该项是阅读过程中的误读，**不构成问题**。

## 跨模块模式

1. **能力按路径延迟装载。** 启动层先把常规 CLI、远控和后台路径分开，工具/MCP 层再把 transport 和审批收敛在服务边界内。
2. **取消贯穿而不由 UI 私有。** 会话层给模型和工具提供同一 abort 语义；工具层还以 child controller 控制并发子过程。
3. **扩展低于策略。** 多入口可通过动态 import 扩展，工具可通过 Hook/MCP 扩展，但远控策略、工作区 trust 和 permission rule 保留最终裁决。

## 限制

验证仅覆盖分配文件和精确主干结论；未验证未分配的队列实现、`Tool` registry、MCP UI hook、全部命令与服务。没有运行构建、测试或网络调用。
