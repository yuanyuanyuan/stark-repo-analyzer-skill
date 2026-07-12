# Protocol/event contract

## 在项目中的角色

协议 crate 是跨边界语言：Session 产生 event，TUI 和 app-server 消费 event，客户端通过 submission/JSON-RPC 发送操作。它让不同入口共享同一业务状态，而不是共享实现细节。

session/mod.rs 直接使用 Op、Event、Submission、SandboxPolicy 等 protocol 类型（session/mod.rs:360-381）。MCP 接口文档也说明 app-server 的 codex/event payload 与 core 的 Event/EventMsg 对齐（codex-rs/docs/codex_mcp_interface.md:95-103）。

## 关键模型

- 操作：用户输入、turn 控制、审批决定、配置/线程操作。
- 事件：生命周期、assistant/tool item、错误、token、审批和状态通知。
- 权限：approval policy、sandbox policy、permission profile。

Mermaid flow:
flowchart LR
  Client[CLI/TUI/SDK] -->|Submission/JSON-RPC| P[Protocol types]
  P --> S[Session]
  S -->|Event/EventMsg| P
  P --> Client
  P --> A[App-server transport]

## Why > What

共享事件协议比每个客户端直接读取 Session 内部状态更稳定：客户端依赖数据契约，核心可以替换内部实现。代价是协议一旦暴露，字段演进会变成兼容性成本；app-server 文档将接口标为 experimental，并要求以 protocol source 为权威（docs/codex_mcp_interface.md:142-144），这是对演进成本的显式承认。

权限模型放在 protocol 而非 TUI 中，使非交互客户端必须明确处理审批。代价是客户端实现复杂，收益是安全语义不随入口漂移。

## 覆盖率

| 文件 | 总行数 | 已读/分析范围 | 覆盖率 | 状态 |
|---|---:|---:|---:|---|
| protocol/src/protocol.rs | 6216 | 约 2100 | 33.8% | 达到次要门槛 |
| protocol/src/models.rs | 3685 | 约 900 | 24.4% | 未达 30% |
| protocol/src/permissions.rs | 3269 | 约 1100 | 33.6% | 达到次要门槛 |
| 合计 | 13170 | 4100 | 31.1% | 部分达到，models.rs 未达标 |
