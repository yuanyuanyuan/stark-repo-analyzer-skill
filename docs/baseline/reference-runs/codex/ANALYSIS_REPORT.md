# OpenAI Codex 架构分析基线

> 分析模式：standard（bounded baseline）  
> 源码 HEAD：9e552e9d15ba52bed7077d5357f3e18e330f8f38  
> 证据范围：固定本地源码与其中的公开文档；外部公开信息仅作定位背景。

## 1. 先给结论

Codex 的核心不是一个终端聊天界面，而是一个由 Session/turn、Protocol/Event、Execution safety 三个边界组成的本地 agent runtime。CLI/TUI、app-server、MCP、skills 和 plugins 都围绕这个 runtime 提供入口或能力。

这个选择解决了 coding agent 最难的三个问题：长会话状态如何保持，模型提出的副作用如何受控，同一套 agent 能力如何服务不同客户端。代价也很清楚：core session、TUI 和 app-server 的编排复杂度较高，协议兼容和扩展刷新成为长期维护成本。

## 2. 场景化问题与定位

README 把 Codex CLI 定义为在本地计算机运行的 coding agent（README.md:1-8）。用户期待的不是一次文本回答，而是“理解工作区 -> 修改代码 -> 执行命令 -> 观察结果 -> 继续修正”的闭环，同时保留审批、恢复和可解释状态。

把模型 API、shell、git 和 UI 简单串联只能得到原型。它无法自然处理用户在模型运行中追加输入、上下文窗口耗尽、工具调用需要审批、不同客户端消费流式事件等问题。Codex 用 Rust 多 crate workspace 将这些问题分到 runtime、协议、安全和适配层。

## 3. 一次 coding turn 的全景

\`\`\`mermaid
sequenceDiagram
  participant U as User
  participant UI as CLI/TUI or app-server
  participant S as Session
  participant M as Model
  participant X as Policy/Sandbox
  U->>UI: prompt / command
  UI->>S: Submission
  S->>S: capture context + load extensions
  S->>M: sampling request
  M-->>S: message or tool call
  S->>X: approval and execution
  X-->>S: result / error
  S->>M: follow-up or compact
  S-->>UI: Event stream
  UI-->>U: transcript / approval / status
\`\`\`

run_turn 的源码说明模型通常在每次采样返回 assistant message 或 function call；function call 会执行后再进入下一次采样，assistant message 则可能结束 turn（session/turn.rs:130-150）。采样前会做 compact、捕获 step context、构造 skills/plugins injection；采样后会检查 pending input、token 状态和 follow-up 条件（turn.rs:153-208、298-370）。

## 4. Session/turn：把 agent 变成可恢复状态机

Codex 对外是 submission/event 队列（session/mod.rs:387-398）。Codex::spawn 组装 config、认证、model、skills、plugins、MCP、thread store 和 agent control，再构造 Session（session/mod.rs:409-446、476-500）。这样客户端不需要知道内部线程、上下文和服务依赖。

turn loop 的关键设计是一次 turn 复用 ModelClientSession，并用同一个 step context 约束 prompt、工具广告和工具调用（turn.rs:218-225、248-295）。这比每一步读取不同的实时状态更一致；代价是 turn context 必须携带较多策略、模型和环境信息。

自动 compact 不是外围 housekeeping，而是 turn 状态机的一部分。pre-sampling compact 处理上一模型/当前窗口的约束，mid-turn compact 处理 follow-up 后的 token 上限（turn.rs:798-823、346-370）。这让长会话可继续，但增加了恢复、错误和上下文可见性问题。

## 5. Execution safety：从模型意图到主机副作用

模型只能提出工具调用；审批、exec policy 和平台 sandbox 才决定命令是否落地。协议显式承载 SandboxPolicy、审批决定和 permission profile，客户端只收集决定，最终执行器仍需要应用策略。

这个边界比“在 TUI 弹一个确认框”更可靠：app-server、MCP 和 SDK 不能因为没有终端 UI 就跳过权限检查。替代方案是把权限逻辑放到每个客户端，开发快但会造成入口间安全不一致。

代码层面的实现分成 exec、execpolicy、sandboxing 和平台 crate。当前基线只读取了 facade 和部分入口，没有把所有 macOS/Linux/Windows 实现逐一交叉验证，因此不对平台等价性作结论。

## 6. CLI/TUI：事件驱动的交互壳

CLI main 声明 app、doctor、MCP、plugin 和 remote control 等子模块，并在 cli_main 处分发模式（cli/main.rs:48-61、956-1050）。交互路径通过 run_interactive_tui 启动（main.rs:2236-2290），说明 CLI 更像 composition root。

ChatWidget 持有历史、streaming buffer、bottom pane、审批 overlay、状态文本和输入队列（tui/chatwidget.rs:326-446、480-507）。它把 protocol event 映射为屏幕状态，把按键映射为 app event，再由 runner 发送 submission。

好处是 TUI 不拥有第二套 agent loop；问题是 TUI 编排文件也积累了大量产品状态。AGENTS.md 直接把 app.rs 和 chatwidget.rs 列为高触摸大文件，并要求避免继续增长（AGENTS.md:49-61）。

## 7. Protocol 与 app-server：把 runtime 变成复用接口

Session 使用 Op、Event、Submission、SandboxPolicy 等 protocol 类型（session/mod.rs:360-381）。MCP interface 文档明确说明 codex/event 的 payload 与 core Event/EventMsg 对齐（docs/codex_mcp_interface.md:95-103）。因此 TUI 和 app-server 消费的是同一个事件语言。

app-server 负责 thread/start、turn/start、审批请求、通知和 command/exec 等客户端边界，不应重新实现模型循环。它带来复用和 IDE/桌面接入能力，代价是实验性协议、legacy compatibility methods、分页和生命周期兼容成为长期债务（docs/codex_mcp_interface.md:133-144）。

## 8. MCP、skills、plugins：扩展能力的受控注入

扩展在 turn 采样前被发现并注入：skills loader 负责 SKILL.md 和 root scope，plugins manager 负责 marketplace/cache/install state，MCP manager 负责连接和工具调用。扩展不只是“显示更多工具”，而是改变模型可见上下文，因此必须受扫描深度、缓存和权限边界约束。

优势是能力可发现、可配置、可通过 app-server 管理；代价是 snapshot、cache、runtime refresh 和 thread 选择状态增加了并发复杂度。AGENTS.md 要求 MCP 调用优先经过 connection manager（AGENTS.md:34-35），体现了集中管理连接状态的意图。

## 9. 亮点、问题与重设计建议

### 亮点

- Submission/Event 让多个客户端共享同一 runtime。
- turn-scoped model session、context capture 和 compact 共同支撑长会话。
- 权限与审批通过共享数据模型跨 TUI 与 app-server。
- 扩展能力进入 turn 前有 loader/manager 边界。

### 问题

- core session 与 TUI 编排文件过大，未来改动容易增加耦合。
- app-server handler 面广，本次未达到覆盖门槛，错误/恢复/取消路径不能视为已验证。
- 平台 sandbox 与完整 tool handler 未覆盖，安全结论只能停留在边界设计层。
- 扩展缓存/刷新状态需要更明确的配置快照、thread 快照和实时连接三分法。

### 如果重新设计

保留 Session/Event/Execution 三角，把 persistence、context manager、extension composition、approval coordinator 拆到更小的稳定 crate。TUI 和 app-server 只依赖 client-facing event projection，减少对 core 内部类型的直接耦合。

## 10. 基线限制

本报告是 bounded standard baseline，不是全仓库逐行分析。生产 Rust 粗扫约 690524 行；核心模块实际合计覆盖 31.3%，次要模块 24.3%。参考 skill 要求并行 subagent，但当前 runtime 未提供 Agent/subagent 工具，因此由主 agent 完成模块扫描和交叉验证。详细分母、范围和未读原因见 drafts/08-coverage.md 与 execution-log.md。
