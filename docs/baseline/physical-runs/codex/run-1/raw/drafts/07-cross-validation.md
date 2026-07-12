# 交叉验证

## 覆盖率门控

| 模块 | 要求 | 草稿报告 | 结论 |
|---|---:|---:|---|
| Core 会话与回合编排 | >=60% | 8,457 / 11,134（76.0%） | 通过 |
| App Server JSON-RPC 边界 | >=60% | 3,151 / 3,151（100%） | 通过 |
| CLI 打包与 JS 工作区 | >=30% | 1,084 / 1,084（100%） | 通过 |

该门控仅适用于各草稿声明的文件/行范围，不是全仓覆盖率。

## 关键结论抽查

| 草稿结论 | 主代理源码抽查 | 结论 |
|---|---|---|
| `Codex` 是提交/事件队列对，提交有界、事件无界。 | `codex-rs/core/src/session/mod.rs:387-400,538-540` 定义队列对并以 `bounded`/`unbounded` 构造。 | 确认。 |
| 同一 session 启动任务前取消既有任务。 | `codex-rs/core/src/tasks/mod.rs:313-323` 的 `spawn_task` 先执行 `abort_all_tasks(Replaced)`。 | 确认。 |
| app-server 将有序列化范围的请求送入队列。 | `codex-rs/app-server/src/message_processor.rs:820-859` 由 `serialization_scope` 决定 enqueue 或 spawn。 | 确认。 |
| 慢的可断开连接会在出站队列满时被断开。 | `codex-rs/app-server/src/transport.rs:154-170` 对 `TrySendError::Full` 调用 `disconnect_connection`。 | 确认。 |
| experimental API 按连接协商可能造成共享线程跨客户端不一致。 | `codex-rs/app-server/src/request_processors/initialize_processor.rs:63-68` 有明确 TODO 和该风险说明。 | 确认。 |

## 跨模块结论

1. **核心运行时与宿主 API 是不同的背压层。** Core 对用户提交施加有界容量、而事件输出无界；app-server 则针对远程可断开客户端在其出站队列满时断开。两者共同表明项目把“不能无限累积用户命令”和“不能让慢网络宿主拖垮服务”放在不同层解决，而不是用一个全局队列策略。证据：`core/src/session/mod.rs:538-540`; `app-server/src/transport.rs:154-170`。
2. **线程内串行化从 core 延续到 API 层。** Core 以一个活动任务并通过替换取消维持线程顺序；app-server 对声明了 scope 的请求再做队列化。后者并不能单独保证模型状态正确，但可减少多个 host 管理操作在到达 runtime 前发生竞态。证据：`core/src/tasks/mod.rs:313-323`; `app-server/src/message_processor.rs:820-859`。
3. **交付层未复制协议或运行时。** npm 启动器只选择平台二进制、传递信号与提示安装修复；app-server 协议才定义 thread/turn/item 通知。故发布层可独立演进，但其对环境变量的下游语义、容器脚本与 runtime sandbox 的交界不在本范围内。证据：`codex-cli/bin/codex.js:16-249`; `app-server-protocol/src/protocol/common.rs:1613-1641`。

## 未能验证的断言

- 其他所有 host crate 是否仅经 `Codex` 队列接入：未检查 TUI、CLI Rust crate 和外部 clients。
- rollout/thread-store 的持久化磁盘格式：未检查外部 crate。
- 工具批准、工具 future 执行和写回的完整跨 crate 契约：未检查 `tools`/MCP 相关实现。
- npm 启动器环境标记的所有下游消费者：未检查完整 workspace。
