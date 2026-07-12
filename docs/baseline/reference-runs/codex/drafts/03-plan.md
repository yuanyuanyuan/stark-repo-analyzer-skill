# 03 Plan：standard 分析计划

## 规模估计

- 工作区顶层 Rust crate：约 101 个。
- 生产 Rust 行数粗扫：约 690524 行；该数字排除了测试目录和 \`*test*.rs\`，但仍包含许多外围 crate。
- 最大风险：\`codex-rs/tui\`、\`codex-rs/core\` 和 app-server 的大型编排文件会让全仓库逐行 standard 不可控。

## 分析模式

选择 \`standard\`，但采用显式 bounded scope：

- 核心模块目标：至少 60%；纳入会话/turn、执行安全、CLI/TUI 用户闭环的代表性生产文件。
- 次要模块目标：至少 30%；纳入协议、app-server、MCP、skills、plugins 的入口和关键实现文件。
- 测试、生成代码、lock、构建系统和未进入用户闭环的外围 crate 不进入本轮深读分母。

## 核心问题

1. CLI/TUI 和 app-server 是否都通过同一 session/turn 核心，而不是各自复制 agent 逻辑？
2. 模型上下文、工具调用、用户 steer、自动 compact 和持久化如何在一个 turn 中协同？
3. 审批、exec policy、sandbox、网络权限之间的边界是否显式？
4. protocol event 是否足以让 TUI、app-server、MCP client 复用同一运行时？
5. skills/plugins/MCP 如何注入能力，同时不破坏上下文和权限边界？

## 覆盖计划

| 逻辑模块 | 类型 | 计划文件范围 | 门槛 |
|---|---|---|---:|
| Session/turn orchestration | 核心 | \`core/src/session/mod.rs\`, \`session/turn.rs\` | 60% |
| Execution safety boundary | 核心 | \`exec/src/lib.rs\`, \`execpolicy\`, \`sandboxing\`, \`linux-sandbox\` | 60% |
| CLI/TUI user loop | 核心 | \`cli/src/main.rs\`, \`tui/src/lib.rs\`, \`tui/src/app.rs\`, \`tui/src/chatwidget.rs\` | 60% |
| Protocol/event contract | 次要 | \`protocol/src/protocol.rs\`, \`models.rs\`, \`permissions.rs\` | 30% |
| App-server integration | 次要 | \`app-server/src/lib.rs\`, \`request_processors/thread_processor.rs\`, transport | 30% |
| Extensibility | 次要 | MCP connection manager, skills loader, plugins manager | 30% |

实际覆盖率、分母和未读原因见 \`08-coverage.md\`。未达标模块不补写成达标。
