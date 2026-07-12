# Session/turn orchestration

## 在项目中的角色

这是 Codex 的核心 runtime。Codex 对外表现为 submission 队列和 event 队列，而不是让 TUI 直接调用内部函数（codex-rs/core/src/session/mod.rs:387-398）。去掉这个边界，TUI、app-server 和 SDK 会各自复制会话逻辑，无法共享恢复、steer、审批和事件语义。

## 业务问题与设计

coding agent 的一次请求不是一次模型调用：模型可能返回工具调用，用户可能在运行中追加输入，上下文可能触发 compact，工具结果还需要继续采样。run_turn 明确把“采样 -> 工具/事件 -> 后续采样”做成循环，并复用 turn-scoped ModelClientSession（session/turn.rs:143-150、218-225）。

Codex::spawn 负责组装 Config、auth、model、skills、plugins、MCP、thread store 和 agent control，再创建 Session（session/mod.rs:409-446、476-500）。这种依赖注入比在 turn 内临时寻找全局服务更容易测试和替换，代价是 spawn 参数较大、初始化编排复杂。

## 核心数据结构

- Codex：tx_sub、rx_event、agent status、Arc<Session> 和终止 future。
- TurnContext：本轮模型、权限、工作区、网络、协作模式和扩展上下文。
- ModelClientSession：本轮连接/路由复用状态。
- Submission/Event：客户端与 runtime 的异步契约。

## 核心流程

Mermaid sequence:
sequenceDiagram
  participant Client as TUI/app-server
  participant C as Codex
  participant S as Session
  participant M as Model
  participant Tool as Tool/Exec
  Client->>C: submit(Submission)
  C->>S: create TurnContext
  S->>S: pre-sampling compact + capture context
  S->>M: sampling request
  M-->>S: assistant item / tool call
  S->>Tool: policy-gated tool execution
  Tool-->>S: result event
  S->>M: follow-up sampling
  S-->>Client: Event stream

turn 开始前执行 compact、捕获 context、加载 skills/plugins，并把 injection items 写入 conversation（session/turn.rs:153-208）；采样后根据 pending input、token 状态和模型 follow-up 决定继续或 compact（session/turn.rs:298-370）。

## Why > What

1. 上下文先捕获再采样：同一 step context 同时约束 prompt、advertised tools 和 tool calls（turn.rs:248-295）。替代方案是各阶段各自读取实时状态，简单却会让模型看到的上下文与实际执行状态不一致。
2. compact 是 turn 的一等阶段：pre-turn 和 mid-turn 都可触发 compact（turn.rs:798-823、346-370）。代价是状态机复杂，但能避免长会话直接撞上上下文窗口。
3. 事件而非返回值：事件允许 TUI 流式渲染、app-server 转发、客户端处理审批。代价是调用方必须处理异步生命周期和部分事件顺序。

## 跨模块协作

Session 依赖 protocol 的 Op/Event/SandboxPolicy，依赖 exec/tool 执行能力，依赖 skills/plugins/MCP 为 turn 注入工具和上下文；客户端只消费事件。该边界贯彻“核心 runtime + 显式事件”哲学。

## 亮点与问题

亮点是把 steer、compact、工具 follow-up 都纳入同一个 turn loop，避免客户端拼接隐式状态。问题是 session/mod.rs 和 turn.rs 仍然非常大，维护者文档也承认 codex-core 过于膨胀，并建议抵抗继续向其中添加功能（AGENTS.md:72-83）。这说明架构方向正确，但核心 crate 仍是演进瓶颈。

## 覆盖率

| 文件 | 总行数 | 已读/分析范围 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| core/src/session/mod.rs | 4071 | 约 1670 | 41.0% | 多数持久化、恢复、配置更新和测试辅助路径未读 |
| core/src/session/turn.rs | 2510 | 约 1630 | 64.9% | 工具结果分派和少数特殊 turn 分支未读 |
| 合计 | 6581 | 3300 | 50.1% | 未达 standard 核心门槛 60%，不能虚报 |
