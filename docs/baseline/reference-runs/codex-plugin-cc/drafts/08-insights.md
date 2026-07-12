# 阶段 8：架构洞察

## 贯穿全局的设计哲学

这个项目的核心不是“把 Codex 命令翻译成 Claude 命令”，而是建立一个可恢复的跨 agent 运行边界：Claude 负责宿主交互和生命周期，Codex App Server 负责 thread/turn，插件负责参数、权限、Job、日志和结果协议。README 对“复用本地安装、认证、仓库和环境”的描述，与 `CodexAppServerClient`、workspace state 和 hooks 的实现一致（`README.md:302-310`、`app-server.mjs:335-353`、`state.mjs:29-44`）。

## 三个最有价值的设计选择

1. **App Server 而非一次性 CLI**：长连接允许捕获 item、reasoning、subagent 和 final answer；代价是需要显式事件状态机。`captureTurn` 的 buffered notification 和 `scheduleInferredCompletion` 是这个选择的直接后果（`codex.mjs:559-610`、`373-394`）。
2. **共享 Broker 优先、direct fallback**：复用降低进程开销，busy/连接失败时 direct fallback 保证单次命令不被共享状态永久阻塞（`codex.mjs:613-641`）。这是可用性优先于绝对复用率的取舍。
3. **Job 作为持久化产品对象**：后台 task、status、result、cancel、resume 和 stop gate 都围绕同一个 Job 语义工作，而不是各自维护临时状态（`state.mjs:92-170`、`job-control.mjs:213-308`）。

## 真实问题与影响

- **双写一致性风险**：state index 与 job detail 分开写入，崩溃可能造成短暂不一致。影响是 status 可能显示 Job 而 result 找不到详情；当前测试未模拟任意崩溃注入，建议未来增加原子写/恢复扫描。
- **大入口演进风险**：`codex-companion.mjs` 同时承载解析、Job 创建、命令 handler、后台 worker、cancel 和 main switch。现在职责可通过函数分区理解，但新命令会持续扩大文件；可在不改变行为的前提下按 command family 拆分。
- **格式耦合**：Stop gate 依赖 Codex 返回约定的 JSON/rawOutput 形状，解析失败时只能提示人工运行 review。当前这是显式 fail-visible，而不是静默放行，安全上更可取，但协议演进需要版本化或 schema 兼容层。

## 如果重新设计

先不改变插件协议，而是抽出三个稳定接口：`CommandRequest`（用户意图）、`JobStore`（状态/详情原子提交）和 `CodexTransport`（direct/broker）。现有函数可以先适配这些接口，再把主入口拆成 review/task/lifecycle handlers。这样能降低文件级复杂度，同时保留当前测试和用户可见命令。

第二步为 Job store 增加恢复扫描：启动时检查 state index 与 job files，补齐可读详情或将不完整记录标记为 `failed/recoverable`。这针对源码可见的双写边界，不依赖 Git 历史假设。

## 学习点

小型插件若要承载长任务，不能只设计命令名；必须同时设计状态、取消、恢复、日志和宿主生命周期。这个仓库最值得复用的不是某个 JSON-RPC 函数，而是把“运行时、Job、host hook”三条生命周期放在一条可验证链路上。
