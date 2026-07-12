# 次要模块：语义、LSP 与 ty

## 共同角色

这些模块把一次性 lint/format 工具扩展为可交互、可理解项目语义的平台，但本轮只做入口和边界分析，不把大规模类型/规则实现写成已覆盖事实。

## Python semantic model

`ruff_python_semantic/src/model.rs:58-240` 的 `SemanticModel` 持有 AST、source、scope 和 bindings 等查询上下文；`scope.rs:14-320` 用 `Scope`、`ScopeKind`、`ScopeId` 组织函数、类、模块和生成器作用域。它的业务价值是让规则回答“名称引用了什么”，而不仅是匹配局部语法。完整 semantic crate 约 9,687 行，本轮只读约 660 行代表范围，未达 30% 次要门槛。

## Editor/LSP integration

`ruff_server/src/server/main_loop.rs` 负责长生命周期请求循环，`session.rs` 管理 workspace/session 状态，`lint.rs` 和 `format.rs` 将编辑器请求桥接到已有 lint/format 逻辑。它的边界价值是将一次性命令转为增量交互；请求取消、调度公平性和多 workspace 细节未完整验证。server 约 10,071 行，本轮读取约 760 行，约 7.5%，未达标。

## ty type-checking platform

`ty/src/main.rs` 提供独立 `ty check/server/version/explain` CLI；`ty_project/src/db.rs:40-170` 通过 Salsa storage、project metadata、system filesystem 和 `freeze` 形成增量数据库；`ty_python_semantic/src/lib.rs:50-125,175-215` 把 parser errors、type checks 和 diagnostics 汇合到 `check_file`。公开 CLI 文档也确认 `ty check`、`ty server` 是独立命令（`crates/ty/docs/cli.md:5-20`）。

ty 的设计张力是增量查询速度与数据库状态/取消/一致性复杂度之间的权衡。ty 相关有效源码约 162,379 行，本轮只读入口约 600 行，约 0.4%，远低于 30%；这是本次 standard 基线的最大未覆盖面。

## 结论

这些次要模块的存在和边界已被验证，但实现深度未达门槛。后续 deep 基线应优先补 ty 的 project metadata、module resolver、semantic index、type inference 和 diagnostic/fix 流程，再补 server 的 request scheduling。
