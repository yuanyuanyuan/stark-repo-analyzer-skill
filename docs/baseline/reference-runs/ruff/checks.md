# Ruff standard 基线质量检查

| 检查项 | 状态 | 证据 |
|---|---|---|
| 仅分析指定项目 | 通过 | 所有输出位于 `reference-runs/ruff`；未修改其他目录 |
| 开始前确认源码目录 | 通过 | `execution-log.md`；目录存在 |
| 固定 commit 已记录 | 通过 | `metadata.json` 和报告头部记录 `c588a3f7...` |
| 工作树状态已记录 | 通过 | metadata: `clean` |
| 读取 README/配置/入口/开发文档 | 通过 | `execution-log.md` 证据表；README、Cargo、pyproject、CONTRIBUTING 等 |
| 按业务功能划分模块 | 通过 | `drafts/05-modules-plan.md` |
| Why > What | 通过 | 每个核心模块和最终报告含动机、替代方案代价和边界 |
| 核心流程含 Mermaid | 通过 | 每个核心草稿和 `ANALYSIS_REPORT.md` |
| 关键结论有路径/行号 | 通过 | 模块草稿和最终报告引用 `path:line` |
| 未验证内容未写成事实 | 通过 | 研究、报告和限制章节使用“未找到/待验证/未覆盖” |
| 未使用 Git 历史推断 | 通过 | execution log 明确仅使用固定 commit 源码和公开文档 |
| CLI 核心覆盖 >=60% | 通过 | 93.3%，见 `06-module-cli.md` |
| 配置控制面核心覆盖 >=60% | 通过 | 63.5%，见 `06-module-config.md` |
| lint pipeline 核心覆盖 >=60% | 通过 | 76.4%，见 `06-module-lint.md` |
| formatter IR 核心覆盖 >=60% | 通过 | 100%，见 `06-module-formatter.md` |
| 完整 parser 核心覆盖 >=60% | 部分通过 | 22.3%；control plane 达标但 grammar 未读 |
| 次要 semantic 覆盖 >=30% | 未通过 | 约 6.8% |
| 次要 LSP 覆盖 >=30% | 未通过 | 约 7.5% |
| 次要 ty 覆盖 >=30% | 未通过 | 约 0.4% |
| 研究至少包含问题/定位/同类/组织动机 | 通过 | `drafts/03-research.md` 四个章节 |
| 研究工具失败有记录 | 通过 | Exa unavailable 已记录，无伪造搜索结果 |
| 规模与分析模式有记录 | 通过 | `drafts/03-plan.md` |
| 模块清单、报告大纲、叙事线有记录 | 通过 | `drafts/05-modules-plan.md` |
| 交叉验证已完成 | 通过 | `drafts/07-cross-validation.md`，未完成项显式列出 |
| insights 已完成 | 通过 | `drafts/08-insights.md` |
| coverage 已完成 | 通过 | `drafts/08-coverage.md` |
| 最终单一 Markdown 报告 | 通过 | `ANALYSIS_REPORT.md` |
| 写入分块限制 | 通过 | 每次 apply_patch 文件内容控制在 300 行以内 |
| 输出目录完整性 | 通过 | 16 个必需输出文件存在；JSON、行数/大小、Mermaid 和源码 HEAD 检查通过 |
