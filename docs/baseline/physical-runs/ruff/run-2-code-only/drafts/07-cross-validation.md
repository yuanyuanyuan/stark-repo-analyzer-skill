# 07 交叉验证

## 已验证链路

1. `args.rs` 的 `CheckCommand` 把 fix policy 显式化；`commands/check.rs` 确实消费 `fix_mode`、`unsafe_fixes` 并传给 `diagnostics::lint_path`（`check.rs:34-40, 194-204`）。
2. check 与 format 都消费 cache：check 在 `check.rs:74-184` 初始化/持久化，format 在 `commands/format.rs` 的 `format_path` 读取 formatted 标记。这支持“缓存是命令编排层能力”的结论。
3. printer 接收 `Diagnostics` 和 `FixTable`，所以“诊断作为跨输出中间表示”有源码证据（`printer.rs:9-31, 41-220`）。
4. parser/AST visitor 的结构化遍历为 linter/formatter 提供共同下游；这是跨 crate 接口推断，源码入口支持，但本次未逐规则验证。

## Graphify 边界

Graphify code-only 结果有 58,118 nodes、152,791 edges、5,098 code files，且 semantic extraction disabled。它能帮助定位 `Printer`、`LinterSettings`、`Parser`、`TypeInferenceBuilder` 等高连接节点，但不提供自然语言设计意图、业务语义、调用条件的可靠证明。semantic Graphify 若启用模型抽取，会增加语义关系/解释性边，但可能引入模型推断；本次禁止该路径。因此所有 Why 与行号均来自源码审读，不从图的“EXTRACTED/INFERRED”标签推导设计结论。

`doctor-post-graph.json` 显示 failures 为空、status ready，证明图可被现有 doctor 消费；不代表源码分析已经全覆盖。

## 未决风险

未运行 build/test，未验证跨平台文件写入、缓存并发和 formatter round-trip；未做 P5 动态行为验证。
