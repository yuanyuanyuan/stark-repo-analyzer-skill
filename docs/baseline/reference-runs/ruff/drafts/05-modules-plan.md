# Ruff 模块规划与报告大纲

## 业务模块清单

| 顺序 | 模块 | 类型 | 业务职责 | 主要证据 |
|---:|---|---|---|---|
| 1 | CLI 与执行控制 | 核心 | 把 check/format/server/graph 等能力统一成命令、退出状态和输出契约 | `crates/ruff/src/main.rs`, `lib.rs`, `commands/check.rs`, `resolve.rs` |
| 2 | 项目配置与文件发现 | 核心 | 从 CLI、pyproject/ruff.toml 和目录层级得到可执行 Settings 与文件集合 | `crates/ruff_workspace/src/resolver.rs`, `pyproject.rs`, `settings.rs` |
| 3 | Python parsing frontend | 核心 | 将文本变为 token、AST 和错误信息，供 linter/formatter/semantic consumers 复用 | `crates/ruff_python_parser`, `ruff_python_ast` |
| 4 | Lint pipeline 与规则/修复 | 核心 | 并行处理文件，执行规则，聚合诊断并生成或应用安全分级的 fixes | `crates/ruff_linter/src/linter.rs`, `fix`, `checkers`, `rules` |
| 5 | Formatter document pipeline | 核心 | 将 AST 格式规则编译成 document IR，再按宽度/缩进打印源码 | `crates/ruff_formatter`, `ruff_python_formatter` |
| 6 | Python semantic model | 次要（本轮降级） | 提供 binding、scope、reference、CFG 等语义查询 | `crates/ruff_python_semantic` |
| 7 | Editor/LSP integration | 次要 | 在会话、请求调度和 workspace 之间复用 lint/format 能力 | `crates/ruff_server` |
| 8 | ty type-checking platform | 次要（本轮降级） | 以 Salsa project database 驱动类型检查、诊断、fix 和 server | `crates/ty`, `ty_project`, `ty_python_semantic` |

## 叙事线

```text
CLI 输入
  -> 配置解析与文件发现
  -> Python lexer/parser/AST
  -> { lint rules -> diagnostics/fixes
     | formatter rules -> document IR -> printer }
  -> Printer/exit status 或 editor session
  -> ty 作为相邻的类型检查平台扩展
```

- CLI 先回答“用户如何请求能力、如何决定退出”；它把配置解析和文件发现作为前置契约。
- 配置模块产出 `PyprojectConfig`、resolver 和每文件 Settings；没有它，linter/formatter 无法解释 include/exclude、规则和目标 Python 版本。
- parser/AST 将文本转换为两个消费者都能复用的结构；它解释为什么 linter 和 formatter 能共享 source ranges，而不把各自输入逻辑重复一遍。
- lint 与 formatter 是两个不同的输出策略：前者允许多个规则诊断和修复，后者追求稳定的源码布局。
- LSP 通过 session/request loop 把一次性 CLI 转为长生命周期交互；ty 则显示 workspace 正在扩张到类型检查，但其边界和缓存模型不同。

## 报告大纲

1. 场景、定位和同类工具的设计差异。
2. 项目全景：flat workspace、Rust binary、Python frontend、linter/formatter 双消费路径。
3. 从 CLI 到配置与文件集合：优先级、watch、stdin 和退出语义。
4. Python frontend：lexer/parser/AST 契约、错误和 source range。
5. Lint pipeline：并行文件检查、诊断聚合、cache/noqa/fix。
6. Formatter pipeline：AST formatting、document IR、printer 宽度决策和 Black 兼容边界。
7. LSP 与 ty：复用点、不同生命周期和未覆盖风险。
8. 评价：整体设计哲学、亮点、实际问题、重设计建议和验证边界。

## 覆盖策略

核心模块优先覆盖控制流、公共类型、边界实现；不把数百个规则文件或所有语法节点当作已读。每个模块草稿末尾提供文件总行数、实际已读行数、覆盖率、门槛和未读原因。
