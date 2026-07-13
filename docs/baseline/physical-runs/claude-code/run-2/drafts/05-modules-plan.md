# 模块叙事与模块规划

启动编排 →[建立配置、策略和运行模式]→ 工具执行循环 →[需要外部能力时]→ MCP 管理 →[把结果和上下文持久化]→ 会话记忆/恢复 →[本地会话需要被远程消费时]→ 远程传输 →[把状态呈现给人或 SDK]→ CLI/UI。

## 模块

1. 启动与运行时编排：`src/main.tsx`、`src/entrypoints/*`、`src/bootstrap/*`
2. 工具注册、批准与执行：`src/Tool.ts`、`src/services/tools/*`、`src/tools/*`
3. MCP 外部能力：`src/services/mcp/*`
4. 会话记忆与恢复：`src/services/SessionMemory/*`、`src/assistant/sessionHistory.ts`、`src/utils/sessionStorage.ts`
5. 远程会话与传输：`src/remote/*`、`src/cli/transports/*`、`src/bridge/*`
6. 次要支撑：API/OAuth、插件/技能、遥测、LSP、UI/Ink、commands、utils。

## 报告结构

问题场景 → 项目全景 → 启动边界 → agent loop → MCP → 会话/远程 → 评价与启发 → 限制与覆盖。
