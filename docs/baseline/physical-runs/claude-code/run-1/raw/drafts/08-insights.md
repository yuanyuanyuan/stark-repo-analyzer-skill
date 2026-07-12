# 架构洞察

## 设计哲学

从已覆盖路径看，系统不是把 CLI、会话和工具拼在一起，而是先建立**运行边界**，再执行**可取消的回合**，最后调用**受治理的能力**。这解释了动态导入、独立 bridge 初始化、异步生成器、工具并发分区和 MCP 多 transport 适配为何同时出现：它们分别控制启动成本、生命周期、执行副作用和外部协议的不确定性。

## 主要亮点

- `preAction` 让 help/轻量命令避免完整初始化，同时使真实 action 共享可观测性和迁移前置条件（`src/main.tsx:884-967`）。
- 会话层通过单消费者与 abort 协议避免多输入源直接争抢同一段模型历史（`src/cli/print.ts:1833-2008`；`src/query.ts:659-665`）。
- 工具并发不由名称白名单决定，而由已解析输入的 `isConcurrencySafe` 决定，并对异常保守串行（`src/services/tools/toolOrchestration.ts:91-115`）。
- Hook 可以丰富授权体验，但规则仍保留否决权，适合本地插件和组织策略共存（`src/services/tools/toolHooks.ts:372-405`）。

## 演进风险与建议

1. `main.tsx` 与 `bridgeMain.ts` 分别拥有入口初始化。建议提取无 UI 的 capability initializer，并用命令形态矩阵测试两条路径的策略、sink 与 trust 不变量。
2. `cli/print.ts` 和 `screens/REPL.tsx` 承担大量调度语义。建议把队列优先级、生命周期事件和 result hold-back 提炼成入口无关的 `TurnScheduler` 状态机。
3. `services/mcp/client.ts` 聚集连接、认证、发现、调用和结果治理。建议在不改变外部 API 前提下分为 Connection、Discovery、Invocation、Result-normalization 四个内部协作者。

这些是静态架构建议，不是经运行复现的缺陷诊断。
