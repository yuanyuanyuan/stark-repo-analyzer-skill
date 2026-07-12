# CLI/TUI user loop

## 在项目中的角色

CLI 是入口和模式选择器，TUI 是事件驱动的交互壳。两者不应该承载 agent 业务本身，而是把参数/按键转成 submission，把 event 转成可读状态。

cli/src/main.rs 声明 app、doctor、MCP、plugin、remote control 等子模块（main.rs:48-61），主入口在 main/cli_main（main.rs:956-1050），交互 TUI 通过 run_interactive_tui 启动（main.rs:2236-2290）。这表明 CLI 是 composition root，而不是单一命令实现。

## TUI 状态模型

ChatWidget 同时持有历史 cell、streaming buffer、bottom pane、审批 overlay、状态文本和输入队列，模块声明集中在 chatwidget.rs:326-446，初始化参数在 chatwidget.rs:480-507。它把 protocol event 映射为可视化状态，再把 key/input 变成 app event。

Mermaid flow:
flowchart TD
  A[CLI args / terminal input] --> B[App event loop]
  B --> C[ChatWidget state]
  C --> D[Submission to Codex]
  D --> E[Event stream]
  E --> C
  E --> F[History/status/approval rendering]

## Why > What

将 TUI 作为事件消费者而非 agent 核心，允许 app-server 或 SDK 复用同一 Session。替代方案是 UI 直接拥有会话状态，初期简单，但会使流式输出、审批、恢复和非交互客户端各自产生不同语义。

TUI 的真实难点不是绘制文本，而是把用户可见状态与异步生命周期保持一致：流式 agent message、tool lifecycle、审批 popup、token/status 和 queued input 都需要协同。模块数量和 ChatWidget 体量也说明这个壳正在承载较多产品逻辑；AGENTS.md 明确把 chatwidget.rs 列为高触摸大文件并要求避免继续增长（AGENTS.md:49-61）。

## 跨模块协作

CLI 依赖 config/auth/app-server/core；TUI 依赖 protocol event、session runner、exec cell、MCP/skills/plugin surfaces。它不应直接绕过 execution safety；审批 UI 只提供决定，最终策略仍由核心执行路径确认。

## 亮点与问题

亮点是“同一 event stream，多种客户端”的结构。问题是 TUI 自身模块化压力很大：app.rs/chatwidget.rs 需要同时关心输入、呈现、工具状态和产品设置；如果继续扩展，可能削弱 UI 与 runtime 的边界。

## 覆盖率

| 文件 | 总行数 | 已读/分析范围 | 覆盖率 | 状态 |
|---|---:|---:|---:|---|
| cli/src/main.rs | 4087 | 约 900 | 22.0% | 部分 |
| tui/src/lib.rs | 3054 | 约 450 | 14.7% | 部分 |
| tui/src/app.rs | 1376 | 约 430 | 31.3% | 部分 |
| tui/src/chatwidget.rs | 2074 | 约 520 | 25.1% | 部分 |
| 合计 | 10591 | 2300 | 21.7% | 未达 standard 核心门槛 60% |
