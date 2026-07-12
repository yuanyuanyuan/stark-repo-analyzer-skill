# 统一质量检查表

状态含义：通过 = 有源码/文档证据；部分通过 = 证据存在但存在边界；未通过 = 本次没有足够证据。

| 检查项 | 状态 | 证据 |
|---|---|---|
| 固定源码目录和 HEAD 已确认 | 通过 | `metadata.json`；HEAD=`b67832c2167e5b0ff6764a8c04a0a9087e697b5a`。 |
| 未使用 Git 历史推断实现 | 通过 | `execution-log.md` 记录只读取当前工作树。 |
| 只写入独立输出目录 | 通过 | 本次产物均位于 `docs/baseline/reference-runs/click`。 |
| 读取 README、配置和开发者文档 | 通过 | `README.md`、`pyproject.toml`、`docs/why.md`、commands、advanced、testing、extending 等。 |
| 按业务功能识别模块 | 通过 | `drafts/05-modules-plan.md` 按命令、参数、终端、completion、测试划分。 |
| Why > What | 通过 | 最终报告第 6、7、8、10 节包含动机、替代方案、代价和重设计。 |
| 核心流程含 Mermaid | 通过 | 最终报告第 4 节和各核心模块草稿。 |
| 关键结论含路径和行号 | 通过 | 报告与草稿中的源码引用均带路径/行号。 |
| 核心模块覆盖率 >=60% | 通过 | `08-coverage.md`：核心 100%。 |
| 次要模块覆盖率 >=30% | 通过 | `08-coverage.md`：次要 77.7%。 |
| 覆盖率不能虚报 | 通过 | 平台模块明确列出未读分支，且使用静态读取口径。 |
| 交叉验证已完成 | 通过 | `drafts/07-cross-validation.md` 列出 6 项源码/文档对照。 |
| 外部研究已记录边界 | 部分通过 | 使用官方页面、GitHub 元数据和搜索；竞品实现级比较未完成。 |
| Windows、真实 shell、pager 行为已运行验证 | 未通过 | 本次仅静态读取和 Python smoke，已在日志和报告标记。 |
| Agent 并行模块分析已执行 | 未通过 | 当前环境没有 Agent 工具，未伪造 subagent 证据。 |
| 单一最终报告已生成 | 通过 | `ANALYSIS_REPORT.md`。 |
