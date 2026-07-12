# 模块六：Core 会话与回合编排

前一节已经把本地 coding agent 看成由共享运行时承载、而非由某一个界面拥有的产品。本节进入该运行时的第一条主链：用户的一次输入如何被转成一个可中断、可续接、可持久化的 agent 操作。这里的结论是，`codex-rs/core` 将“线程”作为长期状态容器，将“回合”作为配置和权限冻结后的执行单位，再以提交/事件队列形成宿主无关的边界。

## 角色与业务问题

本模块解决的不是“调用一次模型”这么简单，而是本地代理的连续工作问题：一个线程需要保留对话、权限、环境和 token 使用；用户又可能在模型运行时追加指令、回应审批、发来子 agent 消息或中断任务。若将这些状态放在 CLI、IDE 或 app-server 中，新的宿主会重写调度和并发规则，恢复会话也会失去同一语义。

`Codex` 对外只呈现一对异步通道：提交 `Submission`，接收 `Event`（`codex-rs/core/src/session/mod.rs:387-400`）。启动时建立有界的提交通道（容量 512）和无界事件通道，构造 `Session` 后启动后台 `submission_loop`（`codex-rs/core/src/session/mod.rs:538-540,683-742`）。因此宿主面对的是协议操作和生命周期事件，不必拥有模型客户端、工具路由或对话历史。【待主 agent 验证】其他 host crate 是否均以此 `Codex` 队列接口接入。

## 设计方法：长期状态、回合快照、步骤快照

`Session` 是单线程长期运行的协调者：它持有 thread id、受 mutex 保护的 `SessionState`、唯一 `active_turn`、输入队列、服务集合和事件发送端（`codex-rs/core/src/session/session.rs:25-48`）。其“最多一个运行任务、但允许用户输入中断”的约束被写在类型注释里，而不是交给 UI 约定（`session.rs:25-28`）。

配置并不在每次模型采样时随意读取。`SessionConfiguration` 保存线程级 model/协作模式、基础指令、审批与权限档案、环境、持久化历史模式和动态工具等可演化设置（`session.rs:50-111`）；每个用户回合先通过 `apply` 生成已校验的新配置，必要时刷新网络代理，再生成 `TurnContext`（`turn_context.rs:583-649`）。这让设置更新在“下一个回合”成为原子边界，而不是在半途改变正在执行的工具权限。

`TurnContext` 再冻结本回合真正需要的模型、provider、环境快照、权限档案、输出 schema、动态工具、遥测和扩展数据（`turn_context.rs:102-147,477-580`）。每次采样前还会抓取更窄的 `StepContext`：精确环境、能力根、MCP runtime 及一次性缓存的 MCP 工具列表（`step_context.rs:11-48`）。这种三级状态划分将“可长期恢复”“一个用户意图”“一次模型请求”分开，避免工具广告和实际执行使用不同的环境或 MCP 配置。

### 必要类型

| 类型 | 职责 | 证据 |
|---|---|---|
| `Codex` | 宿主可见的 submission/event 队列对，保留 session 与 agent 状态订阅 | `session/mod.rs:387-400,745-795` |
| `Session` | 串行化线程级状态、活动任务、输入、服务与持久化协调 | `session/session.rs:25-48` |
| `SessionConfiguration` | 可更新但受约束的线程设置，能投影出权限/环境/模型配置 | `session/session.rs:50-111,205-413` |
| `TurnContext` | 回合冻结的模型、权限、环境、元数据与扩展 store | `session/turn_context.rs:102-147,477-580` |
| `StepContext` | 单次采样一致性快照，尤其固定 MCP runtime 与工具清单 | `session/step_context.rs:11-48` |
| `TurnInput` / `InputQueue` | 用户输入、已注入 response item、跨 agent 邮件，以及 steer/mailbox 的优先与投递状态 | `session/input_queue.rs:12-38,165-252` |

## 核心流程：一条用户回合

```mermaid
sequenceDiagram
    participant Host as Host client
    participant C as Codex\nsession/mod.rs:745-795
    participant L as submission_loop\nhandlers.rs:714-872
    participant S as Session/TurnContext\nhandlers.rs:194-286\nturn_context.rs:583-790
    participant T as Task scheduler\ntasks/mod.rs:313-451
    participant R as run_turn\nturn.rs:143-460
    participant M as Model + tools\nturn.rs:1113-1208\nturn.rs:1940-2305

    Host->>C: submit(Op::UserInput)
    C->>L: bounded Submission(id, op)
    L->>S: user_input_or_turn
    S->>S: apply settings; build immutable TurnContext
    S->>T: spawn RegularTask(input)
    T->>R: task.run(cancellation token)
    R->>R: capture StepContext; record context/input
    R->>M: prompt(history, base instructions, visible tools)
    M-->>R: streamed items / tool calls / completed
    R->>M: execute tools, append outputs, sample again if needed
    R-->>C: persisted lifecycle and EventMsg stream
    C-->>Host: Event
```

1. `submission_loop` 逐项分派 `Op`，对 `UserInput` 调用 `user_input_or_turn`；未知的非穷尽操作会忽略，进程退出或 channel 关闭时仍执行 session teardown（`codex-rs/core/src/session/handlers.rs:714-872`）。这使协议演进不要求老 core 对新增宿主操作崩溃。
2. 用户输入先尝试 `steer_input`。若已有普通回合，它将附加上下文和用户消息放入该回合的 pending queue；若没有活动回合，才创建 `TurnContext` 并启动 `RegularTask`（`codex-rs/core/src/session/handlers.rs:194-285`; `session/mod.rs:3864-3937`）。Review/Compact 任务被明确拒绝 steering，避免改变其封闭语义（`session/mod.rs:3891-3906`）。
3. 调度器每次启动新任务先取消旧任务、清除 connector 选择，再设置 cancellation token、active turn、起始 token 使用量和统一的 turn lifecycle；任务结束前 flush rollout，成功后从同一出口完成生命周期（`codex-rs/core/src/tasks/mod.rs:313-451`）。这把“替换旧任务”的语义放在 core，而不是让客户端竞态决定。
4. `run_turn` 在首次采样前执行自动压缩检查，抓取首个 `StepContext`，写入 reference context/world state，加载明确提及的技能与插件，执行 hooks 并记录输入（`codex-rs/core/src/session/turn.rs:143-208`）。之后循环以同一个 `ModelClientSession` 请求模型；在每轮前合并允许投递的 pending input，在每轮后计算 token 状态、决定继续、压缩或结束（`turn.rs:218-418`）。
5. 单次采样先据 `StepContext` 构建 `ToolRouter`，并把固定的工具规格、基础指令和 output schema 组成 `Prompt`（`turn.rs:1090-1168,1218-1351`）。流事件一边生成宿主生命周期事件，一边把工具 future 放进有序 in-flight 队列；模型完成时记录 token，工具/`end_turn=false` 则让外层回合继续（`turn.rs:1940-2135,2278-2305`）。【待主 agent 验证】`stream_events_utils` 与 `tools` crate 对工具 future 的具体执行、审批和结果回写契约。

### 有界上下文不是附带优化

`context_window_token_status` 同时计算完整活跃上下文与可配置的压缩计数范围；无论按总量还是“前缀后正文”计数，到达自动压缩阈值或真实模型窗口都会触发限制（`codex-rs/core/src/session/context_window.rs:24-91`）。回合在采样前处理模型兼容 hash 变化或模型降级造成的窗口缩小，在中途则在“仍需 follow-up”时进行压缩（`session/turn.rs:798-947,955-1030,346-370`）。这说明 context 预算是运行时状态机的一部分，不是由前端拼 prompt 时临时截断。

## 协作与依赖

输入队列把“新用户 steer”和“多 agent mailbox”区分开：前者属于活动 turn 的 `TurnState`，后者为 session 范围 FIFO；取数时在锁内原子判断当前 turn 是否接受 mailbox，再在锁外 drain 邮件（`codex-rs/core/src/session/input_queue.rs:34-252`）。带 `trigger_turn` 的邮件只会在 idle session 启动一个空输入的普通回合（`session/handlers.rs:288-304`; `core/src/tasks/mod.rs:453-490`）。这是让协作消息复用同一模型上下文与回合审计的做法，而不是另开一条隐式模型调用路径。

持久化同样是 core 的责任：创建或恢复 `LiveThread` 后，`Session::new` 先发 `SessionConfigured`，再初始化 MCP 并记录初始历史（`codex-rs/core/src/session/session.rs:579-725,1143-1269`）；事件发送时会转换为 rollout item 持久化、写 trace，再投递到事件 channel（`session/mod.rs:1947-1985`）。恢复和 fork 则重建 history、前一回合设置、world state 与 token usage（`session/mod.rs:1321-1450`）。【待主 agent 验证】`codex_thread_store`/rollout crate 的磁盘格式与不同 host 的恢复入口。

插件、技能、扩展和 MCP 没有反向拥有会话。它们在 session 初始化时被预热并安装运行时管理器（`session/session.rs:900-940,1019-1159,1201-1254`），在回合/步骤构造时作为快照或 contributor 输入进入模型上下文和工具路由（`session/turn.rs:512-683,1218-1351`; `session/mod.rs:3126-3175`）。这符合“narrow crate interface”：外围能力贡献数据和执行器，core 仍拥有回合顺序、取消与持久化。

## 关键决策、权衡与替代成本

1. **一个活动任务，而非并发模型回合。** `spawn_task` 总是先 `abort_all_tasks(Replaced)`（`codex-rs/core/src/tasks/mod.rs:313-323`）。代价是不能让同一 thread 并行探索多个模型分支；收益是 history、审批等待、文件差异和 token 账本不需要多版本合并。若改成多回合并发，需要 branch-local history、工具写入隔离和确定性合并策略，复杂度会从任务调度扩散到权限和持久化层。
2. **回合/步骤快照，而非读取全局可变配置。** `new_turn_with_sub_id` 在 mutex 中应用配置更新，`new_turn_context_from_configuration` 随后抓环境、模型和技能快照（`codex-rs/core/src/session/turn_context.rs:583-790`）。代价是设置改变通常要到下一回合生效，且需要维护 snapshot 构造代码；替代方案会造成同一 prompt 广告的工具和真正调用时权限不一致，尤其在 MCP refresh、环境切换和审批更新期间。
3. **事件队列与 rollout 均由 core 输出。** `Codex` 不让 host 直接读取 `SessionState`，而是以 `Event` 输出可观察生命周期（`codex-rs/core/src/session/mod.rs:387-400,1947-2016`）。代价是协议事件较多、宿主需处理异步排序；但 CLI、IDE、服务端可以共享“何时开始、何时询问、何时完成”的语义。把 runtime 塞进 UI store 会更快做出一个界面，却使第二个 host 被迫复制状态机。

## 业界对照与再设计思考

它更像 actor/command-loop 架构，而不是典型聊天 SDK：有界 command mailbox、单一 owner 的可变 session state、取消令牌和异步 event stream。与只维护消息数组的 agent loop 相比，Codex 把权限档案、环境、MCP、持久化和上下文预算也纳入回合边界，适合“会改本地工作区”的长任务。

若重新设计，我会保留这三个边界，但进一步让 `SessionConfiguration` 摆脱 `original_config_do_not_use` 的复制投影。源码已承认该字段应被移除（`codex-rs/core/src/session/session.rs:91-92`），`build_per_turn_config` 也注释了当前需要 clone/mutate 的过渡状态（`session/turn_context.rs:421-460`）。可改为一个显式、不可变的 `ResolvedTurnPolicy`：只含模型、环境、权限和能力开关，由 config 层编译一次。这会减少兼容 projection 和跨字段同步风险，但需要一次较大的协议迁移，不能在当前多种 legacy sandbox 表示并存时仓促进行。

## 亮点与问题

**亮点**

- 以 `StepContext` 固定 MCP 管理器与工具列表，避免一轮请求内部的工具面漂移（`codex-rs/core/src/session/step_context.rs:11-48`）。
- input queue 明确区分 steer 与 mailbox，且针对 mailbox delivery phase 做原子检查，能支持协作而不破坏当前回合（`session/input_queue.rs:119-252`）。
- 从用户消息、工具审批到 `TurnComplete` 的事件和 rollout 都在 session 内统一产生，具备恢复与多宿主一致性的基础（`session/mod.rs:1947-2016`; `session/session.rs:1164-1269`）。

**问题/风险**

- `Session` 聚合了网络代理、MCP、shell、hooks、模型 client、持久化和协作状态，已是高耦合协调器；虽有 `SessionServices` 缓冲，但修改初始化路径的影响面很大（`codex-rs/core/src/session/session.rs:951-1159`）。
- `SessionConfiguration` 同时维护 legacy sandbox projection 与较新的权限档案，更新时有多条条件分支以保留 deny reads/重绑定 cwd（`session/session.rs:205-413`）。这是兼容所需，但也是未来权限回归的高风险区。
- 事件 channel 无界（而 submission 有界），慢宿主或长流式输出时内存背压依赖消费者行为而不是类型边界（`codex-rs/core/src/session/mod.rs:538-540`）。是否存在上层限流或丢弃策略需【待主 agent 验证】。

## 涉及文件

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/session.rs`
- `codex-rs/core/src/session/turn_context.rs`
- `codex-rs/core/src/session/step_context.rs`
- `codex-rs/core/src/session/input_queue.rs`
- `codex-rs/core/src/session/context_window.rs`
- `codex-rs/core/src/session/handlers.rs`
- `codex-rs/core/src/session/turn.rs`
- `codex-rs/core/src/tasks/mod.rs`（仅直接任务调度入口）

本模块将稳定的提交/事件边界、回合快照和持久化语义先固定下来；接下来的 host-facing 层只应把各自的请求翻译成 `Op`、把 `Event` 渲染或转发，而不应重新拥有 agent runtime。【待主 agent 验证】app-server/CLI 等接口层是否严格遵循此边界。

## 阅读覆盖率

模块范围按“用户输入到回合执行、采样、事件与任务调度”的直接生产路径计；排除各文件的 test-only 内容。行数按文件物理总行数统计，已读为本次实际请求的行区间并集。

| 文件名 | 总行数 | 已读行数 | 覆盖率% | 未读原因 |
|---|---:|---:|---:|---|
| `session/mod.rs` | 4071 | 2444 | 60.0 | 未读的是审批、MCP refresh、持久化辅助等非本主链细节 |
| `session/session.rs` | 1284 | 1284 | 100.0 | 无 |
| `session/turn_context.rs` | 842 | 842 | 100.0 | 无 |
| `session/step_context.rs` | 49 | 49 | 100.0 | 无 |
| `session/input_queue.rs` | 420 | 420 | 100.0 | 无；含尾部行为确认测试 |
| `session/context_window.rs` | 92 | 92 | 100.0 | 无 |
| `session/handlers.rs` | 942 | 929 | 98.6 | 仅未读 701-713 的 review 错误收尾 |
| `session/turn.rs` | 2510 | 2096 | 83.5 | 未读主要为 plan-stream 辅助与少量输出 delta 分支 |
| `tasks/mod.rs`（直接入口） | 924 | 301 | 32.6 | 仅读取任务调度区间 280-580；其余 task 实现不属于本模块 |
| **合计（核心会话/回合主链）** | **11134** | **8457** | **76.0** | **达标✅** |
