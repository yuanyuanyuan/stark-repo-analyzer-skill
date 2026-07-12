# 模块：Formatter document pipeline

## 叙事衔接

Lint pipeline 输出离散诊断和 edits；formatter 处理的是整个文件的布局。它需要一个比字符串拼接更高层的 document IR，最后再依据行宽决定换行和缩进。

## 在项目中的角色

`ruff_python_formatter` 将 Python AST 节点格式化为通用 formatter 元素；`ruff_formatter` 提供 `FormatElement`、`Format` trait、上下文和 printer。仓库开发文档明确描述 Python formatter 先生成中间表示，再由 `ruff_formatter` 按配置行宽打印（`CONTRIBUTING.md:150-161`）。

## 核心流程

```mermaid
flowchart LR
  A[Python source] --> B[parser / AST]
  B --> C[ruff_python_formatter node rules]
  C --> D[FormatElement document IR]
  D --> E[Group / line-width decisions]
  E --> F[Printer queue/stack]
  F --> G[formatted source]
```

`ruff_python_formatter/src/lib.rs:136-180` 暴露 source/AST formatting API；`ruff_formatter/src/lib.rs:596-705` 用 traits 把节点规则与 context 解耦；`ruff_formatter/src/lib.rs:859-940` 提供最终 `write/format`；`format_element.rs:21-155,308-459` 定义 document、line mode、best-fitting variants 等 IR 概念。

## Why > What

- 先构造 IR 再打印，允许“同一格式规则在不同宽度下重新选择布局”，而不是在 AST visitor 中立即输出字符串。代价是额外的元素模型和 printer 状态，但避免把换行决策散落在每个语法节点。
- `FormatContext`/`FormatOptions` 与具体 Python formatter 分离，使通用 printer 不需要知道 Python 语法；这是为未来语言/输入扩展保留的边界。
- 公开 formatter 文档把 Black 兼容放在性能和统一工具链之后，说明产品选择是“迁移阻力最小 + 执行更快”，不是重新设计 Python 风格。当前源码可验证接口和 IR，不能仅凭本轮读取证明所有 Black 差异都已实现。

## 跨模块协作

formatter 复用 parser/AST 和 source range；配置由 workspace 提供 line width、quote/indent 等选项；最终 CLI 负责文件发现、stdin、preview 和输出。formatter 本身不负责项目发现和进程退出，这使它能被 CLI、server 或 WASM 等入口复用。

## 问题与边界

Python formatter 目录约 32k 行，绝大多数 expression/statement 节点未逐一阅读；本草稿只把语言无关 IR 与 public API 作为 formatter 核心切片。具体 Python 节点的格式选择、comment placement 和 preview deviations 需要后续 deep 基线。

## 覆盖率

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| `crates/ruff_formatter/src/lib.rs` | 974 | 974 | 100% | 无 |
| `crates/ruff_formatter/src/format_element.rs` | 620 | 620 | 100% | 无 |
| `crates/ruff_formatter/src/formatter.rs` | 250 | 250 | 100% | 无 |
| **合计** | **1844** | **1844** | **100%** | **核心门槛 60%，达标 ✅；Python 节点后端单列为未覆盖范围** |
