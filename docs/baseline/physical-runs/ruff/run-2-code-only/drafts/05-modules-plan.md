# 05 模块规划与叙事线

叙事线：CLI/config →[将用户意图解析为 Settings 与命令状态]→ lint/fix →[产生 diagnostics 与 edits]→ printer/formatter →[把结构化结果变成稳定文本或源码]→ cache →[把重复工作变成可复用状态]→ parser/AST →[为规则与格式化提供结构基础]→ server/ty 边界。

核心模块：

1. CLI/config：`crates/ruff/src/args.rs`、`commands/mod.rs`、`resolve.rs`。
2. lint/fix：`crates/ruff/src/commands/check.rs`、`diagnostics.rs`，以及 linter crate 的 settings/engine 入口。
3. formatter/printer：`commands/format.rs`、`printer.rs`、`ruff_formatter/src/printer/*`。

次要模块：parser/AST（`ruff_python_parser`、`ruff_python_ast`）、cache（`cache.rs`）、server（`ruff_server` 与 `commands/server.rs`）、ty（`ruff_db`/`ruff_python_semantic`/`ruff_python_type` 的入口关系）。

每个模块都回答：为什么存在、边界如何减少耦合、替代方案代价、对整体“显式配置 + 结构化中间表示 + 批处理性能”哲学的贡献。
