# 08 洞察

## 1. Ruff 的真正抽象是“可复用结果”，不是命令

CLI、server 和 formatter 都围绕结构化 settings、diagnostics、edits、formatted source 工作。这样做的 Why 是让同一份事实可以进入人类输出、机器协议、缓存和编辑器；命令只是不同适配器。

## 2. 性能目标通过边界组合实现

缓存 key、package root、批量路径、Rust parser 和延迟打印共同减少重复工作。单点优化无法解释全部架构；真正的选择是让每个阶段都输出可缓存或可组合的中间状态。

## 3. 显式状态换取可审计性

`fix`、`unsafe_fixes`、`diff`、`isolated` 等状态增加了 API 表面积，但把“会不会修改文件”和“读取哪个配置”公开化。对于 CI 工具，这比隐式 heuristics 更容易复现。

## 4. 改进建议

可以把部分 CLI 互斥 bool 收敛为更强的策略枚举，并为跨命令 settings/diagnostics 契约补充架构级文档和静态契约测试。由于本次未运行测试，这只是设计建议，不是缺陷结论。
