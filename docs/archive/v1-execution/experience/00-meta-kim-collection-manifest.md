# Meta_Kim 采集清单

## 采集范围

| 维度 | 数值/规则 |
| --- | --- |
| 主数据源 | `~/Library/Application Support/mcp-memory/sqlite_vec.db` 的 `memories` 表 |
| 直接项目记录 | `tags` 包含 `stark-repo-analyzer-skill` 的 861 条 observation |
| 相关上下文 | 记录内容明确出现项目根目录、但标签属于子工作区或物理运行目录的 559 条 observation |
| 合计 | 1,420 条 observation |
| 时间范围 | 2026-07-06 至 2026-07-13 |
| 直接记录事件 | 452 个 `user-prompt`、316 个 `stop`、93 个 `session-start` |

全量检索条件是项目标签或项目根目录字符串；它覆盖主工作树、`spec-*` 与 `v2.0-*` 子工作区，以及以 `/tmp/stark-*` 运行的物理基线任务。它不覆盖仅凭语义相似度命中的其他项目记录，避免把相似话题误归属到本项目。

## 为什么不逐字导出 1,414 条记录

原始记录主要包含重复的启动/停止事件、用户提示词、工作树状态和转录片段。逐字复制会：

1. 将 406 条启动/停止类记录当作“经验”；
2. 将当时的 WIP、已被后续决定替代的方案和不完整命令误写成结论；
3. 在项目中持久化大量无关的工作树状态。

因此，本目录按主题对全部记录去重、归类和降噪。原始数据库仍是可回溯来源；每张经验卡均说明它覆盖的记录族，而不是声称某一条 observation 已经被独立验证。

完整的逐条来源目录见 [06-meta-kim-observation-catalog.tsv](06-meta-kim-observation-catalog.tsv)。它保留 1,420 条记录的时间、范围、事件、内容哈希、标签和短摘要；不复制完整转录或工作树状态。

## 归类方法

| 记录族 | 归档去向 | 处理方式 |
| --- | --- | --- |
| V1/V2、目标、规格与能力边界 | `01-product-contract-and-evolution.md` | 与 goals、spec 和实现载体交叉核验 |
| Graphify、doctor、代码/语义模式、来源定位 | `02-graphify-and-acceptance.md` | 以验收规则与脚本为准 |
| reference-runs、physical-runs、P2/P4、报告对比 | `03-physical-baseline-and-report-quality.md` | 区分实际运行、参考输出和待完成比较 |
| Ruff、中断、恢复、隔离与未完成项 | `04-failures-recovery-and-open-risks.md` | 保留失败分类，不补写根因 |
| subagent、任务分解、文件写入、证据和交付节奏 | `05-workflow-and-collaboration.md` | 区分用户偏好与已验证流程规则 |

## 证据等级

- **已核验**：当前仓库文档、脚本、测试或保存的真实运行产物直接支持。
- **记忆支持**：Meta_Kim 记录反复出现的任务决策或约束，但本次未逐条重新验证其所有实现细节。
- **待验证**：记录了目标、方案或问题，不可据此声称实现完成或验收通过。

## 维护边界

本清单是 2026-07-13 的冻结快照。后续记忆应增量归档，不应修改本次计数；若数据库清理、去重或新会话改变了数量，应新建一份带日期的采集清单。
