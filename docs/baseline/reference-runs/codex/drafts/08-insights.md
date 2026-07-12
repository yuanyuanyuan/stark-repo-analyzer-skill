# 08 Insights：架构洞察

## 1. 统一 runtime 是最重要的架构选择

Codex 的核心抽象不是某个 UI，而是异步的 submission/event 队列。它让 CLI、TUI、app-server 和 SDK 可以共享会话语义。替代方案是每个客户端直接操作模型和工具，短期更简单，长期会复制审批、恢复、streaming 和错误处理。

## 2. 上下文管理与安全管理实际上是同一条控制链

模型看到的工具、skill、插件和 workspace 状态会影响它提出的动作；执行策略又决定动作能否落地。因此 context capture、skills/plugins injection、permission profile 和 sandbox 不能被视为独立功能。代码通过 turn 中统一 capture/injection，再把工具调用送往执行边界来连接它们。

## 3. 事件协议是复用性的收益来源，也是兼容性债务

事件流适合 streaming 和多客户端，代价是协议字段、生命周期、取消和审批必须持续兼容。文档把 app-server 接口标为 experimental，说明项目仍在用协议演进换取生态试验速度。

## 4. 主要亮点

- turn-scoped client session 复用连接和路由状态，避免每个采样重新建连接。
- pre-turn/mid-turn compact 让长会话不会简单撞上 token 上限。
- 权限/审批通过共享数据模型跨 TUI 与 app-server。
- skills/plugins/MCP 的扩展发现有扫描深度、根目录和缓存边界。

## 5. 主要问题与改进方向

- core session 与 TUI 编排文件体量过大；应继续按稳定领域边界抽离，而不是只在大文件中新增方法。
- app-server handler 面较宽；可以用 capability-oriented processor 和统一生命周期适配减少重复分支。
- 扩展 snapshot、cache、runtime refresh 的状态较多；应明确“配置快照、thread 快照、实时连接”三类状态及失效规则。
- 本次安全分析未覆盖完整平台实现；后续基线应按操作系统分别建立安全证据。

## 6. 如果重新设计

保留核心的 Session/Event/Execution 三角，但将 session 的持久化、context manager、extension composition、approval coordinator 拆成更小的 crate 或稳定 trait。让 TUI 和 app-server 都只面对 client-facing event projection，减少它们对 core 内部类型的直接依赖。
