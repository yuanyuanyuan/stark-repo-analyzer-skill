# 架构洞察与评价

## 核心判断

Codex 在所覆盖路径上不是把“模型调用”当作产品核心，而是把**可恢复的线程状态机**当作核心，并把 CLI、IDE、桌面等视为该状态机的宿主。这个判断由三层证据支撑：core 的 submission/event 边界与单活动任务，app-server 的 thread/turn 协议和通知，npm 包仅负责平台原生二进制的启动与交付。

## 值得学习的设计

1. **冻结点比全局配置更适合长任务。** `SessionConfiguration`、`TurnContext` 与 `StepContext` 将长期配置、单回合权限/环境、单次采样工具面分离。其代价是构造和兼容映射复杂；收益是避免正在执行的回合因环境或 MCP 刷新出现“prompt 看到的能力”和“实际执行的能力”不一致。
2. **把 API 兼容性作为单独设计问题。** v2 DTO、JSON Schema/TS 生成与 experimental capability gate 看似冗长，却使客户端不会依赖 Rust 内部对象。相较直接暴露 runtime 状态，维护成本前置但扩展宿主的成本显著更可控。
3. **背压必须分层。** 提交队列的有界性和网络宿主的慢连接断开策略分别处理不同资源风险。它们不应被混为“队列优化”，而是各自对应用户意图积压与传输消费者失速。

## 风险与建议

| 风险 | 影响 | 建议 |
|---|---|---|
| Core `Session` 同时协调许多基础设施 | 初始化或权限改动的影响面大 | 继续把可解析的回合策略提炼为不可变值对象，逐步收缩 legacy projection。 |
| Core 事件通道无界 | 慢的本地宿主可能累积内存 | 先测量真实 event 速率和消费者行为；如需限制，按事件类别定义可合并/不可丢失语义，而非盲目改成有界队列。 |
| experimental capability 按连接、线程可共享 | 两个客户端可能观察不同能力面 | 按源码 TODO，评估 instance-global 一致性或在 attach 时拒绝能力不匹配。 |
| lagged thread-created 广播不重同步 | 某连接可能错过 thread attachment | 增加可恢复的 resync/列表拉取语义，并定义客户端应对 lag 的协议行为。 |

## 结论的边界

这些建议只适用于已读的 core session、app-server protocol 与 npm delivery 路径。没有测试运行、外部调研、Git 历史或全仓审计，因而不对性能、线上故障率、成熟度排名或其他子系统作判断。
