# 模块 06：交互会话调度

> 前一模块已经把启动参数、命令入口和会话上下文交给运行时；这里的职责是把“用户又输入了一句”变成一个**可排队、可取消、可流式观察且能跨工具回合延续**的会话事务。它为下一章的工具能力留出 `canUseTool`、`ToolUseContext` 与任务通知三个边界，而不在界面或 CLI 中复制模型循环。

## 角色与业务问题

Claude Code 不是一次 HTTP 请求就结束的聊天框：同一会话可在模型流式输出期间继续收到输入、等待权限、并行背景任务完成通知和 Ctrl+C。若让 REPL、SDK 和 `-p` 模式各自管理消息数组与取消信号，最容易出现三类故障：同一 prompt 被执行两次、停止后仍写入历史、背景任务结果被最终结果遮住。

本模块以“**输入生产者 / 单一回合消费者 / 事件流观察者**”分开这三件事。它服务于项目的整体哲学：多入口和能力面解耦，但在会话边界用显式状态与契约保持可演进性。去掉该层，前端必须理解模型、工具、压缩和持久化的全部时序，headless 与 REPL 也会漂移。

## 设计与责任边界

| 层 | 责任 | 关键证据 |
|---|---|---|
| 交互 REPL | 收集输入、维护可见消息和加载状态、把后续输入排队或中断当前轮次 | `src/screens/REPL.tsx:3142-3525,3861-4107` |
| headless 编排 | 结构化输入与执行器并发；按优先级取命令、可合批、为每轮新建 abort controller、把事件转发 stdout/bridge | `src/cli/print.ts:1833-2254,2807-2862` |
| 会话引擎 | 在一份持久消息/缓存/用量状态上接收 submit，规范化输入并消费模型查询生成器 | `src/QueryEngine.ts:121-180,410-686` |
| 回合状态机 | 做上下文投影/压缩、调用模型流、收集工具调用、运行工具后决定继续或终止 | `src/query.ts:201-337,500-1120,1120-1729` |
| 任务最小模型 | 为背景任务定义类型、终态、可取消上下文和防碰撞 ID | `src/Task.ts:6-121` |

这不是传统的“UI 调 service 并 await 一个结果”。核心 API 是 `AsyncGenerator`：消费者可以逐条渲染/转发中间事件，而生成器的 `.return()` 与 `AbortController` 也能切断执行。`query()` 仅在正常返回时发送已消费命令的 `completed` 生命周期，异常或 generator return 不伪造完成，保留“已开始但未完成”的真实语义（`src/query.ts:219-237`）。

## 必要数据结构

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking: AutoCompactTrackingState | undefined
  maxOutputTokensRecoveryCount: number
  hasAttemptedReactiveCompact: boolean
  maxOutputTokensOverride: number | undefined
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined
}
```

`State` 将跨 API/工具循环的可变项集中为一个不可变替换单元，避免多个 `let` 在七个 `continue` 分支间遗漏同步；不随循环改变的系统提示、权限函数、来源和依赖则从 `QueryParams` 解构一次（`src/query.ts:182-217,252-280`）。

```ts
type TaskStateBase = {
  id: string; type: TaskType; status: TaskStatus; description: string
  abortController: AbortController; outputFile: string
}
```

任务将取消、状态与磁盘输出作为显式实体；`isTerminalTaskStatus` 定义不可再迁移的终态，ID 使用类型前缀加八随机字节（36^8 空间）来降低可预测路径/符号链接攻击风险（`src/Task.ts:15-27,45-121`）。

## 核心流程

```mermaid
sequenceDiagram
  participant I as REPL / Structured Input
  participant Q as Command Queue
  participant E as QueryEngine / ask
  participant L as query() 状态机
  participant M as Model Stream
  participant T as Tool runtime
  participant O as UI / stdout / bridge

  I->>Q: enqueue(prompt / task notification)
  Q->>Q: 优先级、相邻 prompt 合批
  Q->>E: 新 AbortController + 回合配置
  E->>E: processUserInput; 先持久化 user message
  E->>L: for await query(messages, ToolUseContext)
  L->>L: 投影/压缩上下文，yield request start
  L->>M: 流式 callModel(signal)
  M-->>L: text / tool_use / usage events
  L-->>O: 增量事件和消息
  alt 有工具调用
    L->>T: runTools(权限与 abort context)
    T-->>L: tool_result
    L->>L: state 替换并 continue
  else 无工具调用/终止
    L-->>E: Terminal
    E-->>O: result，记录用量/会话
  end
  I->>E: interrupt
  E->>L: AbortController.abort()
```

具体而言，headless 输入读取和队列消费者是两个并行 async task（`src/cli/print.ts:2807-2816`）；消费者优先读取 `now` 命令来中断当前工作（`src/cli/print.ts:1833-1861`），并将连续 prompt 合并，同时为每个 UUID 发 started/completed，保持 SDK 的逐消息可观察性（`src/cli/print.ts:1934-2008,2248-2250`）。每轮重新读取 MCP 客户端与工具集合，避免晚连的能力永久缺席（`src/cli/print.ts:1984-2004`）。

`QueryEngine.submitMessage` 先把 slash command/附件转为消息，立即写入 transcript，再进入模型循环；这样“刚接受输入即停止”的会话仍可 resume，代价是交互模式在 API 调用前多一次小型 I/O 等待（`src/QueryEngine.ts:410-463`）。本地命令不查询模型，但仍产生统一的 `result` 事件（`src/QueryEngine.ts:556-638`）。真正查询时，它将权限拒绝包装为 SDK 可报告状态，消费 `query()`，持续积累消息、compact 边界和用量（`src/QueryEngine.ts:657-686`）。

在每个模型回合前，`queryLoop` 依次应用工具结果预算、历史 snip、microcompact、context collapse、autocompact，再把新的消息视图放入工具上下文（`src/query.ts:337-620`）。模型流以 `abortController.signal` 调用；工具调用块而非不可靠的 `stop_reason` 是是否继续的主信号（`src/query.ts:621-720`）。这使“工具循环”成为模型回合内部行为，而不是 UI 的隐性递归。【待主 agent 验证】`runTools` 的具体并行度、权限拒绝到消息的映射、`ask` 如何桥接 REPL 与该生成器须由工具模块源码复核。

## 协作与跨模块结论

- REPL 的 `onSubmit` 区分立即执行与 loading 时排队，构造的 `abortController`、流模式与权限上下文交给 query 路径；会话期间的输入不需要直接碰模型状态（`src/screens/REPL.tsx:3142-3525`）。【待主 agent 验证】队列实现和“now/next”优先级定义在未分配文件中。
- CLI 把每个 `ask()` 产生的事件立即 flush 到 SDK 流；若仍有背景 agent，会暂存 `result` 直到任务完成，防止客户端先判定回合已完（`src/cli/print.ts:2211-2245`）。任务完成通知既发 SDK event 又落回模型输入，模型可据此继续决策（`src/cli/print.ts:2010-2094`）。
- 结构化 `interrupt` 与 `end_session` 同时终止当前轮的 controller 和建议生成，随后确认控制消息（`src/cli/print.ts:2830-2862`）；权限等待亦用 `Promise.race` 监听 abort，防止用户停止被对话框无限吞没（`src/cli/print.ts:4147-4230`）。

## 决策、替代方案与权衡

1. **异步生成器而非 callback/event bus。** 生成器把背压、顺序、异常和取消统一在语言级协议里，UI 与 SDK 都能 `for await`；代价是生命周期复杂且调用者必须正确处理未完成。但在一个需要流式文本、工具进度、compact 边界和结果事件同流输出的终端代理中，这个复杂度换来了单一真源。
2. **单消费者队列加受控合批，而不是每条输入立即并发 query。** 合批避免同一上下文上的并发模型调用和重复 token 消耗，且仍为每个 UUID 单独确认（`src/cli/print.ts:1950-1982`）。代价是后来的输入排队；“now”优先级和 abort 给用户保留抢占通道。直接并发虽然延迟更低，却会令消息顺序、工具写操作和会话持久化不可判定。
3. **先落用户消息再调用 API。** 这是面向恢复的写前日志式选择（`src/QueryEngine.ts:436-463`），比“成功后再保存”多一次失败路径 I/O，却保证 Kill/Stop 后不会丢掉已接受的意图。若要进一步优化，应将此抽成显式 append-only session transaction 并记录提交状态，而不是依赖注释约束时序。

## 洞察、亮点与问题

**亮点：状态分层而非全局巨型 store。** 回合循环拥有短生命周期的 `State`，`QueryEngine` 拥有跨 submit 的消息/缓存/用量，`Task` 拥有后台工作状态；这恰好匹配变化频率，且让压缩、预算恢复和 stop hook 不污染 REPL 状态。`QueryEngine` 的注释明确“一会话一实例、每 submit 一回合”（`src/QueryEngine.ts:121-180`）。

**亮点：取消是一条端到端契约。** 不是只在 HTTP fetch 上 abort：控制输入、模型流、权限 prompt、建议生成都接入同一停止语义（`src/cli/print.ts:1024-1030,2830-2862,4178-4228`）。这比多数 CLI 仅杀掉 fetch 更接近可靠的交互事务。

**问题：调度语义分散在巨型边界文件。** `print.ts` 5,594 行、`REPL.tsx` 5,005 行，队列、后台结果 hold-back、控制消息和渲染状态相邻，认知边界比 `QueryEngine` 弱。随着新输入源增加，易出现某源漏发 lifecycle 或漏 abort。建议抽出入口无关的 `TurnScheduler`，将队列策略、UUID lifecycle、结果 hold-back 定义为可测状态机；保留各入口仅负责 I/O 适配。【待主 agent 验证】需要用现有 queue/REPL hook 的测试与调用点确认抽取边界。

**问题：完整性依赖跨层“约定”。** 注释已多次解释为什么某些 replays、flush、hold-back 必须在特定位置（如 `src/cli/print.ts:1964-1982,2216-2245`）。这说明约束真实而脆弱；以事件协议的显式状态（accepted/started/streaming/terminal）替代隐含顺序，会降低新增 transport 时的回归风险。

下一章应沿 `canUseTool`、`ToolUseContext` 与任务通知深入：调度器保证何时调用、何时取消；工具能力模块决定一次调用的授权、执行与结果语义。

## 覆盖率

| 文件名 | 总行数 | 已读行数 | 覆盖率% | 未读原因 |
|---|---:|---:|---:|---|
| `src/cli/print.ts` | 5,594 | 5,594 | 100.0 | 无；全文件分段静态读取，重点复核 1,800-2,390、2,800-2,880、4,140-4,290 |
| `src/screens/REPL.tsx` | 5,005 | 5,005 | 100.0 | 无；全文件分段静态读取，重点复核 2,700-3,550、3,800-4,135、4,850-5,005 |
| `src/QueryEngine.ts` | 1,295 | 1,295 | 100.0 | 无；全文件分段静态读取 |
| `src/query.ts` | 1,729 | 1,729 | 100.0 | 无；全文件分段静态读取 |
| `src/Task.ts` | 125 | 125 | 100.0 | 无；全文件读取 |
| **合计** | **13,748** | **13,748** | **100.0** | **达标✅（标准模式核心模块阈值 ≥60%）** |

## 实际读取与限制

- 源 HEAD：`a371abbe75ffa0d0a3c92290e2bbf56a7ef54367`（`git -C … rev-parse HEAD`，退出 0）；未使用 Git 历史，未修改源树。
- 读取工具/命令（均退出 0）：`wc -l <五个授权文件>`；`sed -n '1,3357p'` / `sed -n '3358,5594p' src/cli/print.ts`；`sed -n '1,3003p'` / `sed -n '3004,5005p' src/screens/REPL.tsx`；`sed -n '1,1295p' src/QueryEngine.ts`；`sed -n '1,1729p' src/query.ts`；`sed -n '1,125p' src/Task.ts`。另以 `nl -ba … | sed -n` 复核上述关键行段，以取得精确行号；`rg -n --glob '!*.map'` 定位入口和取消/流式标记。
- 限制：严格只读分配的五个源码文件和三份用户指定技能指南；未读取相邻工具、队列实现、`ask`、类型与测试源码，故所有跨模块映射均标注【待主 agent 验证】。外部调研、Git 历史、运行测试/构建：按本子任务范围未执行。
