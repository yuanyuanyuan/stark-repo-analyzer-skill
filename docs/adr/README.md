# ADR 目录

ADR 是 Architecture Decision Record，即“架构决策记录”。它解释一个长期有效的选择为什么成立、放弃了什么以及边界在哪里；它不记录每日执行过程。

## 快速入口

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 保存重要技术选择的决策、原因、影响和取代关系 |
| 当前状态 | 当前没有 `active` roadmap；ADR-0016 至 ADR-0024 描述已实现基线，ADR-0025 描述已接受但尚未实施的交付目标 |
| 人类怎么读 | 先在下表按主题选一份，再看“决策、原因、影响、取代关系” |
| Agent 怎么读 | 只加载与当前变更相关的当前 ADR；沿 `supersedes` 回看历史，不全量扫描 |
| 何时更新 | 出现新的长期决策、关键权衡或需要取代旧决定时 |
| 关联真源 | 已实现行为以 spec 和当前代码为准；目标架构由 accepted ADR 解释，只有 active roadmap 才授权实施 |

## 当前主线决策索引

以下集合来自最近完成 roadmap 所固化的已实现基线。它是“快速必读集”，不是新的执行授权：

| 主题 | 当前决策 |
|---|---|
| Graphify 提取与证据边界 | [ADR-0016：固定 code-only](0016-graphify-code-only-v1.md)、[ADR-0018：验证规范化可用图](0018-validate-the-normalized-usable-graph.md) |
| 控制面与工件边界 | [ADR-0017：程序控制面只保留 Graphify gate](0017-limit-the-control-plane-to-the-graphify-gate.md)、[ADR-0019：大型运行工件不进 Git](0019-keep-large-run-artifacts-out-of-git.md) |
| 安装与兼容路径 | [ADR-0021：引导安装并允许显式兼容流程](0021-guide-graphify-installation-and-allow-compatibility-fallback.md) |
| 验收分层 | [ADR-0022：区分普通 UAT 与真实回归 UAT](0022-separate-focused-uat-from-real-regression-uat.md) |
| 大仓库范围 | [ADR-0023：允许显式有界分析](0023-allow-explicit-bounded-analysis-for-large-repositories.md) |
| subagent 降级 | [ADR-0024：降级前取得用户同意](0024-require-consent-for-subagent-degradation.md) |

## 已接受但尚未实施

| 主题 | 目标决策 | 实施状态 |
|---|---|---|
| Skill 交付与安装 | [ADR-0025：以 Skill 核心交付包作为唯一分发真源](0025-use-the-skill-bundle-as-the-single-distribution-source.md) | 关联 roadmap/plan 均为 `proposed`，当前代码与 spec 尚未迁移 |

当前主线只采用上表中的 ADR-0016 至 ADR-0019、ADR-0021 至 ADR-0024。ADR-0001 至 ADR-0015 和 ADR-0020 默认都是历史输入；只有当前 ADR 或活动 roadmap 明确重新引入的部分，才能继续约束实现。

## 已取代决策索引

下表只列当前 ADR 明确声明的直接取代关系。`superseded` 表示旧决定不再指导当前实现，不表示删除正文或否定它在当时的背景。

| 历史决策 | 当前替代 | 取代范围 |
|---|---|---|
| [ADR-0003](0003-graphify-is-a-required-structure-evidence-gate.md) | [ADR-0021](0021-guide-graphify-installation-and-allow-compatibility-fallback.md) | Graphify 缺失时全局禁止兼容流程 |
| [ADR-0004](0004-graphify-autodetects-the-required-llm-engine.md)、[ADR-0005](0005-use-graphify-headless-cli-for-automated-analysis.md)、[ADR-0007](0007-bound-graphify-retries-by-failure-class.md)、[ADR-0010](0010-separate-graphify-deep-extraction-from-analysis-depth.md)、[ADR-0015](0015-use-doctor-as-a-non-invasive-graphify-sidecar.md) | [ADR-0016](0016-graphify-code-only-v1.md) | semantic/LLM 执行方式、重试与当前 Graphify 命令假设 |
| [ADR-0008](0008-require-a-healthy-graphify-graph.md) | [ADR-0018](0018-validate-the-normalized-usable-graph.md) | 原始图必须零噪声的严格健康门 |
| [ADR-0013](0013-agent-led-graphify-bootstrap-with-secret-boundaries.md) | [ADR-0016](0016-graphify-code-only-v1.md)、[ADR-0021](0021-guide-graphify-installation-and-allow-compatibility-fallback.md) | semantic 假设与 Agent 自动安装语义 |
| [ADR-0020](0020-use-two-mode-focused-real-uats.md) | [ADR-0022](0022-separate-focused-uat-from-real-regression-uat.md) | 日常完整 UAT 数量与聚焦/发布验收分层 |

未出现在本表中的早期 ADR 仍是历史记录，不会因为没有 `superseded` 标记自动成为当前主线决定。需要回读时，先从上方当前决策索引进入，再沿链接追溯。

## 什么时候创建

只有满足以下任一条件才新增 ADR：

- 存在多个合理方案，并做出了会长期影响系统的选择；
- 决定改变模块边界、数据/控制流、依赖策略、安全或验收架构；
- 将来维护者很可能追问“为什么不采用另一个方案”；
- 新决定需要取代当前 ADR。

局部实现细节、任务顺序和临时排障不需要 ADR。

## 怎么创建

文件名使用下一连续编号：`{四位编号}-{英文-kebab-case-决策名}.md`。正文以中文为主，至少包含：

```markdown
# 决策标题

状态：proposed | accepted | superseded

## 决策
最终选择是什么。

## 原因
为什么选择它，关键约束是什么。

## 备选方案
考虑过什么，为什么没有选择。

## 影响
得到什么、付出什么、边界是什么。

## 取代关系
取代或被哪份 ADR 取代。
```

## 怎么维护

- `accepted` ADR 原则上不重写决策历史，只修正链接、错字和不改变原意的澄清。
- 决策实质变化时新建 ADR，并把旧 ADR 标记为 `superseded by ADR-xxxx`。
- 新旧 ADR 必须双向链接；活动 roadmap 同步更新当前决策索引。
- ADR 只解释“为什么”，行为合同同步写入 spec，执行动作同步写入 plan/progress。

## 主线总结

先从本索引按主题选择当前 ADR，不要从 0001 开始顺序通读。需要理解历史时，再沿取代关系向后追溯；需要改变行为时，ADR 解释原因，spec 才负责固定产品合同。
