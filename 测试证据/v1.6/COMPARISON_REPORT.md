# v1.6 与历史测试证据对比

对比目录：

- `测试证据/v1.0没改造前`
- `测试证据/测试证据v1.1/Long_screenshot_splitting_tool-20260709`
- `测试证据/v1.2`
- `测试证据/v1.3`
- `测试证据/v1.6`

当前 `测试证据` 下未发现既有 `v1.4`、`v1.5` 目录，因此 v1.6 主要与相邻已有版本 `v1.3` 对比，并补充 v1.0-v1.2 趋势。

## 1. 产物完整性对比

| 版本 | 主要新增能力 | 过程证据 | 最终报告 | 对比报告 | 验收报告 |
|---|---|---:|---:|---:|---:|
| v1.0没改造前 | 旧流程重跑，补齐基本草稿 | 有 | 有 | 有 | 有 |
| v1.1 | 源码锚点优先，降低无效阅读 | 有 | 有 | 有 | 有 |
| v1.2 | Evidence Plan | 有 | 有 | 有 | 有 |
| v1.3 | Evidence Matrix | 有 | 有 | 无/未列入 | 有 |
| v1.6 | Budget Profiles + Risk Sampling + Unsupported Claims + Repo Map | 有 | 有 | 有 | 有 |

## 2. 相比 v1.3 的增量

v1.3 已验证 Markdown Evidence Matrix，使模块草稿可比较、可审计。v1.6 在此基础上新增：

- `drafts/02-repo-map.md`：深读前生成 Markdown Repo Map，覆盖目录结构、语言分布、入口候选、manifest、核心文档、测试/generated/vendor 候选和风险候选。
- `drafts/03-plan.md`：记录标准模式预算目标，包括 evidence 深度、风险抽样强度、报告长度目标、subagent 数量上限和外部调研强度。
- `drafts/07-cross-validation.md`：显式汇总风险抽样、Unsupported Claims 检查和实际执行摘要。
- `drafts/08-insights.md`：记录 Budget Profile 实际执行摘要。
- 每个核心模块草稿包含风险路径抽样，风险发现进入最终评价。

## 3. 质量趋势

| 维度 | v1.0 | v1.1 | v1.2 | v1.3 | v1.6 |
|---|---|---|---|---|---|
| 源码锚点 | 有，但旧流程目标不明确 | 明确成为目标函数 | 继承 | 继承 | 继承并抽查 |
| Evidence Plan | 无 | 无 | 有 | 有 | 有，且引用 Repo Map |
| Evidence Matrix | 无 | 无 | 无 | 有 | 有 |
| Risk Sampling | 无 | 无 | 无 | 未作为验收核心 | 有 |
| Unsupported Claims | 人工弱约束 | 有降级意识 | 有 | 有 | 明确流程记录 |
| Budget Profiles | 无 | 无 | 无 | 无 | 有，但仅标准模式 |
| Markdown Repo Map | 无 | 无 | 无 | 无 | 有 |

## 4. v1.6 的不足

严格按 `docs/specs/v1.6-acceptance-checklist.md`，v1.6 完整验收需要快速、标准、深度三种模式都跑，并比较 evidence 数量、风险强度和报告长度。本次用户要求创建 `v1.6` 目录保存测试结果，但未要求实际三轮运行；出于成本边界，本次只执行标准分析。

因此：

- v1.6 的 Budget Profile 记录、计划影响、实际摘要：通过。
- v1.6 的快速/标准/深度三模式对比：未满足。
- v1.6 总验收：部分通过，不应标为完全通过。

## 5. 总结

v1.6 相比 v1.3 的主要进步是把“有矩阵”推进到“有预算、有风险、有 Repo Map、有 unsupported claims 降级”。它更像一次完整 evidence-first 标准分析。但由于没有跑快速/深度两种额外模式，不能宣称 v1.6 acceptance checklist 全部通过。
