# 变更日志

## 2.2.0

- 分析模式收敛为 **standard（默认）** 与 **deep**；移除 quick。
- 引入可分发 **local rules**（`skills/repo-analyzer/rules/`）作为工具/模式执行策略 SSOT，含官方源与 verified date。
- doctor 输出 **capability matrix** 与 **AI installation prompt**；deep 按 graph-queries / symbol-enumeration / reference-edges 门禁，缺能力拒绝且不降级。
- standard 仅用基线工具，忽略 Graphify/Ctags/ast-grep；启发式符号/引用须披露。
- 报告与 gate 工件增加 mode / rules_version / tooling_level 元数据。

## 2.0.0

Breaking release：Repo Analyzer 从文档型 v1 工作流升级为 Evidence-First v2。

- 新增 `doctor`、`scan`、`summarize`、`units`、`gate` CLI。
- 使用 Universal Ctags 或 ast-grep 生成稳定关键单元分母，不再使用源码行覆盖率。
- 新增机器可读 Repo Map、Coverage Units、Module Evidence Matrix 和 Quality Gate 工件。
- 覆盖率分子要求 analyzed 状态、源码锚点和实质设计判断三项同时成立。
- Doctor 和质量门均为硬门控；Graphify 调整为可选增强。
- 三档预算按证据深度和关键单元覆盖率区分。
- 发布包排除维护者本机 hook、绝对路径与测试证据。
