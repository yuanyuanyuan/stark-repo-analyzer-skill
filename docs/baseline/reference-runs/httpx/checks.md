# HTTPX Standard Baseline Checks

状态定义：`通过` = 有固定 commit 证据且满足要求；`部分通过` = 有证据但存在边界；`未通过` = 缺少关键产物或证据。

| 检查项 | 状态 | 证据 |
|---|---|---|
| 输出目录独立 | 通过 | 所有产物位于本目录；未修改共享文档。 |
| 源码目录与 HEAD 已确认 | 通过 | `metadata.json`、`execution-log.md`；HEAD=`b5addb6`。 |
| 未使用 Git 历史推断 | 通过 | shallow checkout；日志明确只使用固定工作树。 |
| README、配置、入口、核心模块已读取 | 通过 | `execution-log.md` 读取序列；覆盖表为全量生产 Python。 |
| 开发者文档已读取 | 通过 | `docs/contributing.md`、`.github/CONTRIBUTING.md`、`mkdocs.yml`。 |
| 按业务功能识别模块 | 通过 | `drafts/05-modules-plan.md` 六条请求生命周期叙事线。 |
| Why > What | 通过 | 每个模块草稿都有动机、替代方案代价、边界和评价。 |
| 关键结论有路径和行号 | 通过 | 草稿和最终报告使用 `path:line` 证据。 |
| 核心流程 Mermaid | 通过 | Client 生命周期图、transport 关系图、消息数据流图。 |
| 核心模块覆盖至少 60% | 通过 | 7,559/7,559 = 100%，门槛 4,536 行。 |
| 次要模块覆盖至少 30% | 通过 | 1,268/1,268 = 100%，门槛 381 行。 |
| 覆盖率未与测试覆盖率混淆 | 通过 | `drafts/08-coverage.md` 明确统计口径和限制。 |
| 外部调研记录来源与限制 | 部分通过 | GitHub/Jina 已记录；Exa 未配置，网页未锁定 commit。 |
| 交叉验证完成 | 通过 | `drafts/07-cross-validation.md` 有上游/下游证据矩阵。 |
| 组织动机有充分一手证据 | 部分通过 | 本地资料不足，已标记“未找到/不能推断”。 |
| 可选依赖和外部 httpcore 已运行验证 | 未通过 | 本轮只读代码和配置，没有运行 optional integrations。 |
| 最终报告为单一 Markdown | 通过 | `ANALYSIS_REPORT.md`；覆盖率留在独立 draft。 |
| 输出文件分块限制 | 通过 | 每个写入块低于 300 行且低于 15KB。 |
