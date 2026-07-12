# MCP、skills 与 plugins

## 在项目中的角色

扩展模块把外部能力带入 turn，但必须经过发现、配置、加载和上下文注入。run_turn 在采样前构造 skills/plugins injection items（session/turn.rs:176-208），说明扩展不是 UI 装饰，而是模型可见上下文的一部分。

MCP connection manager 负责连接/工具调用生命周期；skills loader 解析 SKILL.md、metadata、root scope 和扫描深度；plugins manager 维护 marketplace、安装状态、缓存和与 skills/MCP 的联动。skills loader 的边界常量限制扫描深度、根目录数量和并发探测，体现了“不让扩展发现无限膨胀”的设计。

Mermaid flow:
flowchart LR
  C[Config / workspace] --> D[Discover roots]
  D --> S[Skills loader]
  D --> P[Plugins manager]
  P --> M[MCP declarations]
  S --> I[Prompt/context injection]
  M --> T[Tool catalog]
  I --> R[Turn request]
  T --> R

## Why > What

直接把插件目录或 MCP 工具列表拼进 prompt 很容易失控：描述过长、工具权限不清、刷新状态与当前 thread 不一致。分层 loader/manager 可以分别处理缓存、错误、scope 和刷新；代价是出现多个 snapshot、cache 和 runtime invalidation 状态，排查难度增加。

AGENTS.md 要求 MCP tool call 优先经过 connection manager（AGENTS.md:34-35），说明项目希望把变更集中在既有抽象，而不是让每个调用方自行管理连接。

## 跨模块协作

Session 消费扩展产物，protocol 暴露 list/read/status，TUI/app-server 提供管理入口，exec/sandboxing 仍是工具执行的最终边界。扩展能力因此不能绕开权限模型。

## 覆盖率

| 文件/范围 | 总行数 | 已读/分析范围 | 覆盖率 | 状态 |
|---|---:|---:|---:|---|
| core-skills/src/loader.rs | 1217 | 约 520 | 42.7% | 通过次要门槛 |
| core-plugins/src/manager.rs | 2821 | 约 360 | 12.8% | 未达 |
| MCP manager 及相关 facade | 未完整统计 | 关键片段 | 未计算 | 未达/待补 |
| 合计 | — | — | — | 部分达到，plugins/MCP 不足 |
