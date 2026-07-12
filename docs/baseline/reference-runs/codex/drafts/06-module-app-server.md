# App-server integration

## 在项目中的角色

app-server 把 Codex runtime 变成可被 IDE、桌面端或其他客户端调用的服务。它处理 thread/turn 生命周期、JSON-RPC 请求、通知、审批回调和 transport，但不重新实现模型循环。

app-server README 与 MCP interface 文档列出了 thread/start、turn/start、codex/event、审批请求以及 command/exec 等面向客户端的边界。线程处理器的职责是把请求映射到核心线程和 turn。

Mermaid sequence:
sequenceDiagram
  participant App as App client
  participant RPC as App-server
  participant Core as Codex core
  App->>RPC: thread/start
  RPC->>Core: spawn session
  App->>RPC: turn/start
  RPC->>Core: submit turn
  Core-->>RPC: Event stream
  RPC-->>App: notification / approval request
  App-->>RPC: allow/deny
  RPC-->>Core: approval response

## Why > What

将 app-server 作为适配层而非第二个 agent 核心，避免 TUI 与 API 的行为分叉。代价是协议必须表达更多生命周期和分页/兼容字段，且 server 要维护 thread 与 client 之间的关联。

文档列出 legacy compatibility methods 与实验性方法（docs/codex_mcp_interface.md:133-144），说明该边界同时承担演进兼容和新能力试验，未来维护成本高于单一 CLI。

## 覆盖率

| 文件 | 总行数 | 已读/分析范围 | 覆盖率 | 状态 |
|---|---:|---:|---:|---|
| app-server/src/lib.rs | 1367 | 约 300 | 22.0% | 未达 |
| thread_processor.rs | 4609 | 约 320 | 6.9% | 未达 |
| transport facade | 32 | 32 | 100% | 通过 |
| 合计 | 6008 | 652 | 10.9% | 未达次要门槛 30% |

限制：app-server 处理器数量多且当前 commit 的接口面很宽，本次只完成 thread/turn 主线和文档验证。
