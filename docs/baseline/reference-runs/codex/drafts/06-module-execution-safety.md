# Execution safety boundary

## 在项目中的角色

模型只能提出命令、补丁或工具调用，不能直接获得宿主机副作用。执行安全模块把意图转换为审批、权限策略、沙箱和结果事件；它是 agent 能力与本地工作区之间的闸门。

协议层把 SandboxPolicy、审批决定和权限 profile 作为显式数据，而不是隐藏在 TUI 中（codex-rs/protocol/src/protocol.rs、permissions.rs）。AGENTS.md 还要求不要修改 sandbox 环境变量相关代码，说明沙箱边界是受保护的系统契约（AGENTS.md:8-10）。

执行路径可以拆成三层：

1. exec 负责启动/等待/流式读取命令。
2. execpolicy 负责命令是否需要允许、拒绝或升级。
3. sandboxing/平台 crate 负责具体 Seatbelt、Landlock、Windows 或 Linux 实现。

Mermaid flow:
flowchart LR
  A[Model tool call] --> B[Approval request]
  B --> C{Exec policy}
  C -->|deny| D[Error/event]
  C -->|ask| E[Client decision]
  C -->|allow| F[Sandbox launcher]
  E -->|allow| F
  E -->|deny| D
  F --> G[stdout/stderr/exit result]
  G --> H[Session event + next sampling]

## Why > What

把审批只放在 UI 中会让 app-server、MCP 或 SDK 绕过安全边界；把沙箱只放在 OS launcher 中又无法表达“这个命令是否符合用户当前权限意图”。分层的代价是策略、审批和平台沙箱之间需要保持一致，但换来多个客户端共享同一安全语义。

一个重要张力是自动化速度 vs 可控副作用：workspace-write 类模式允许 agent 工作，权限 profile 和网络策略限制外溢；更开放的模式减少摩擦，却扩大主机风险。固定 commit 的 SECURITY.md 只指向官方安全说明，具体产品策略仍以源代码和配置为准，未把外部页面当实现证据。

## 跨模块协作

Session 负责决定何时调用工具和如何把结果送回模型；protocol 负责传递审批请求和事件；TUI/app-server 负责收集决定；sandboxing 负责最终执行。安全边界因此位于核心 loop 的下游，而不是客户端的装饰层。

## 亮点与问题

亮点是把权限语义放进共享协议，避免“终端安全、API 不安全”的双轨实现。问题是本次只深读了执行 crate 的 facade 与关键入口，未完整展开平台实现、网络策略、shell parser 和所有 tool handler，因此不能判断不同平台的安全等价性。

## 覆盖率

| 文件/范围 | 总行数 | 已读/分析范围 | 覆盖率 | 状态 |
|---|---:|---:|---:|---|
| exec/src/lib.rs | 2015 | 约 320 | 15.9% | 部分，通过入口 |
| execpolicy facade | 30 | 30 | 100% | 通过 |
| sandboxing facade | 71 | 71 | 100% | 通过 |
| linux-sandbox facade | 31 | 31 | 100% | 通过 |
| 合计 | 2147 | 452 | 21.1% | 未达 standard 核心门槛 60% |

未读原因是平台实现分布在多个子模块，且本轮 bounded standard 没有逐平台展开。
