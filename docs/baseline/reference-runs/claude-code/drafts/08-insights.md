# 08 Insights

## Systemic Design Philosophy

当前 commit 的主导设计不是“每个功能独立实现”，而是“共享执行内核 + 显式策略上下文 + 可插拔能力来源”。Query、Tool、Task、Skill 和 Memory 都通过 `ToolUseContext`、`AppState`、任务状态或 Command 记录相互连接。

## Strengths

1. **恢复优先。** Query loop 把压缩、流式 fallback、tombstone 和工具结果顺序当作一等问题处理，而不是只处理成功路径。
2. **能力装配清晰。** `getAllBaseTools`、`getCommands` 和 skill loader 都把来源合并与运行时过滤分开，便于加入新来源。
3. **安全边界显式。** deny 规则、`canUseTool`、memory exact-path writer 和 remote/bridge allowlist 构成多层策略。
4. **长任务可管理。** Task 状态、child abort controller、sidechain transcript 和 foreground/background 转换让 agent 不必阻塞主 UI。

## Tensions and Problems

- `main.tsx` 是非常大的 composition root，启动、认证、工具、MCP、插件、远程和 UI policy 都在同一入口汇聚，变化风险高。
- `ToolUseContext` 很强大但边界宽，具体工具、查询、任务、UI 和 MCP 都可以通过它互相影响，降低了模块独立测试性。
- `feature()` 与环境变量分支很多，但当前 commit 缺少构建配置，无法知道哪些功能属于实际发行面。
- 技能、插件和 MCP 都可能产生命令/工具，重复、优先级、权限和缓存清理需要多个模块协同；这比单一插件接口更灵活，也更难验证。
- 任务/代理核心未达到 60% 模块门槛，不能把 swarm 行为写成完整实现事实。

## If Redesigning

1. 把 `main.tsx` 的启动阶段拆成可验证的 bootstrap pipeline：环境、信任、配置、扩展、会话、UI，每一步输入输出明确。
2. 将 `ToolUseContext` 拆为 `QueryContext`、`ExecutionContext`、`PermissionContext` 和 `SurfaceContext`，减少非必要依赖。
3. 为 Command/Tool/Task 建立统一 capability registry，集中处理来源、优先级、权限、生命周期和 cache invalidation。
4. 给每个 feature flag 生成可读的 build manifest，报告和诊断都记录实际启用集合。
5. 把任务状态转换写成可枚举状态机，并为 foreground/background/kill/complete 组合增加动态测试。

## Baseline Use

这份结果适合用来对比重实现的：主查询循环是否仍然可恢复、工具池是否仍然按策略过滤、技能是否仍然可动态发现、任务是否仍然能取消/持久化、上下文是否仍然有缓存和安全边界。外围模块只能作为后续补齐清单。
