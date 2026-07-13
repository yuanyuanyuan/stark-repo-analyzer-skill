# 次要模块边界

- parser：`ruff_python_parser/src/token_source.rs:9-268` 用 token source 管理 trivia、checkpoint/rewind 和 re-lex；parser 通过 recovery 保持错误定位与继续分析的可能性。
- AST：`ruff_python_ast/src/visitor.rs:119-638` 提供显式 `walk_stmt`/`walk_expr` 分派；这种统一遍历契约让 lint 规则和 formatter 消费同一结构。
- cache：`crates/ruff/src/cache.rs:65-306` 以 package root、settings、文件时间戳和权限构造 key，写入采用临时文件加 rename（`:164-190`），优先保证崩溃/并发下文件完整性。
- server：`crates/ruff/src/commands/server.rs` 是薄入口；实际 LSP 由 `ruff_server/src/server/*`、session、schedule、edit 组成。其边界把持续会话状态与一次性 CLI 编排分开。
- ty：本次仅作入口导航，Graphify hubs 包含 `TypeInferenceBuilder`、`SemanticIndexBuilder`、`ConstraintSetBuilder`；未把这些导航名当作完整语义证明。详细类型推断不在 bounded 核心范围。

## 覆盖率

| 边界 | 读取范围 | 状态 |
|---|---|---|
| parser/AST | 入口、token source、visitor 关键段 | bounded / estimated |
| cache | `cache.rs` 核心实现 65-306、数据结构及持久化段 | bounded / estimated |
| server | command 入口与目录结构、关键 server 文件定位 | bounded / not measured |
| ty | Graphify 导航 + 入口定位 | not measured；不声称覆盖 |
