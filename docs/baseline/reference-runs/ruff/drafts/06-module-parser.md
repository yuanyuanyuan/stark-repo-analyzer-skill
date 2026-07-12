# 模块：Python parsing frontend

## 叙事衔接

配置模块产出文件和目标 Python 版本；linter 与 formatter 都需要把同一份文本解释成稳定的 token/AST。parser 是两条消费路径之间最重要的共享输入边界。

## 在项目中的角色

`ruff_python_parser/src/lib.rs:112-319` 提供 module、expression、range、string annotation、Jupyter cell 等入口；`lexer.rs:36-145` 保存源文本、模式、offset、indentation 和错误状态；`parser/mod.rs` 将 token source 组织为语句/表达式解析。

## 核心流程

```mermaid
flowchart LR
  A[source text + Mode] --> B[Lexer]
  B --> C[tokens + lexical errors]
  C --> D[Parser]
  D --> E[Parsed<Mod>]
  E --> F[AST visitors]
  F --> G[linter / formatter / semantic]
```

parser API 明确把 parse error 和 AST 包在 `Parsed<T>` 中（`lib.rs:281-387`），而不是让调用方自行拼装错误；lexer 用 module/IPython mode 和 source offset 支持普通 Python、Notebook 和片段解析（`lib.rs:559-618`; `lexer.rs:1604-1607`）。

## Why > What

- source range 是重要基础设施：诊断、fix、formatter comment placement 都需要把 AST/token 位置映射回原文。统一 parser 让这些消费者不必各自重新扫描文本。
- `Parsed<T>` 同时保留解析结果和错误，允许工具在容错场景继续工作；代价是下游必须处理不完整/错误 AST，不能把解析失败当成唯一返回路径。
- lexer 显式保存 indentation、括号 nesting、字符串模式和 offset，说明 Python 的换行语义不能用简单 split 实现；这是性能与语法完整性的基础。

## 覆盖边界

本轮读取了 parser 公共 API、parser 控制模块和 lexer 的主要范围，但没有逐行读取 `parser/expression.rs`、`parser/statement.rs` 及所有 AST generated/node 实现。因此以下覆盖只代表 frontend control plane，不代表整个 Python parser。

## 覆盖率

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| `crates/ruff_python_parser/src/lib.rs` | 624 | 624 | 100% | 无 |
| `crates/ruff_python_parser/src/parser/mod.rs` | 1719 | 1719 | 100% | 无 |
| `crates/ruff_python_parser/src/lexer.rs` | 2829 | 2100 | 74.2% | 测试尾部未读 |
| parser expression/statement/pattern 等 | 14714 | 0 | 0% | grammar 体量超出本轮边界 |
| **完整 parser 合计** | **19886** | **4443** | **22.3%** | **核心门槛 60%，未达标 ❌；不能虚报** |
