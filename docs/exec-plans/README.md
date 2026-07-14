# 执行计划目录

本目录存放 roadmap 的执行计划和进度记录，包括活动计划与已完成记录。可以把 roadmap 理解为“要到哪里”，把 exec plan 理解为“下一段具体怎么走”；这个类比的边界是，执行计划还必须记录依赖、验证和失败边界，而不只是任务清单。

## 快速入口

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | plan 定义未来动作；progress 记录已经发生且可验证的事实 |
| 当前状态 | 当前无 `active` plan；最近完成 [代码地图导航](code-map-navigation-plan.md)；[默认 Judge 审查机制](default-judge-review-plan.md) 已 `completed` |
| 人类怎么读 | 先看 plan 的“当前主线”，再看 progress 的“当前快照”和最新一条记录 |
| Agent 怎么读 | 先解析生命周期；`completed` plan 只用于恢复背景，不能授权继续执行其中 P1/P2 条目 |
| 何时更新 | 任务顺序/范围变化时改 plan；每一刀结束时追加 progress |
| 关联真源 | 方向回到 roadmap，产品行为回到 spec，架构理由回到 ADR |

## 应包含什么

一份执行计划必须包含：

- 对应 roadmap 的链接和当前状态；
- 当前主线目标、所处阶段和下一刀；
- 按顺序排列的 P0/P1/P2 任务、依赖与所有权边界；
- 每项任务的预期输出和验证方式；
- 阻塞、失败分类和需要人工决策的位置；
- 证据链接，但不能把“文件存在”当成“验收通过”。
- 完整门时：目标关、启动关与工作区基线（见下方模板）。

工作跨越多轮时，使用配套的 `{任务名}-progress.md`。progress 采用追加式记录，写清实际改动、准确验证结果、阻塞和下一刀，不能把历史失败改写成成功。

## 状态合同

plan 可以使用 `proposed`、`active`、`awaiting-judge`、`blocked`、`completed` 或 `superseded`。`awaiting-judge` 表示 Worker 自验结束、等待独立 Judge 或用户豁免；完整门下不得从实现中直接跳到 `completed`。只有被活动 roadmap 引用的 plan 才能标记为 `active`；完成时必须说明哪些验收已执行、哪些未执行。

只有 `{任务名}-plan.md` 声明生命周期状态。配套的 `{任务名}-progress.md` 声明 `文档类型：progress-log`，继承关联 plan 的状态，不能再声明第二个 `active`。

完成度百分比是可选信息。使用时必须说明分母，例如“roadmap 阶段 3/5”或“必需任务 8/10”；可选清理和未来改进要与主线完成度分开。

## 命名

- `{任务名}-plan.md`：范围、顺序、所有权和验证合同。
- `{任务名}-progress.md`：按时间记录的执行证据与交接状态。

## 创建与维护

从活动 roadmap 拆解工作时成对创建 plan 和 progress：

1. plan 先写当前主线、阶段和下一刀，再列 P0/P1/P2、依赖、输出与验证。
2. progress 只建立“当前快照”，不预写尚未发生的完成记录。
3. 每刀结束后，先写实际验证与失败，再更新 plan 状态；不能只勾选任务。
4. 改变目标或产品合同不是 plan 内部调整，应回到 roadmap/spec/ADR 处理。

progress 采用追加式维护。可以更新顶部快照，但历史记录只补充澄清，不能把失败改写为成功，也不能把未执行验证写成通过。

## 最近完成计划

- [`graphify-simplification-plan.md`](graphify-simplification-plan.md)：已完成 G0-G4 必需任务。
- [`github-v1-release-plan.md`](github-v1-release-plan.md) /
  [`github-v1-release-progress.md`](github-v1-release-progress.md)：`completed`；首次 `v1.0.0` GitHub 源码 Release 已公开。
- [`skill-distribution-architecture-plan.md`](skill-distribution-architecture-plan.md) /
  [`skill-distribution-architecture-progress.md`](skill-distribution-architecture-progress.md)：
  Skill 原子交付已 `completed`（含独立 Judge pass）。未执行的真实外部安装与 G5 不能推断为已通过。

当前无活动计划。最近完成：[`default-judge-review-plan.md`](default-judge-review-plan.md) / [`default-judge-review-progress.md`](default-judge-review-progress.md)（独立 Judge pass）。被取代的任务清单和实现计划保留在 `docs/archive/v1-control-plane/`，不能覆盖当前合同。

## 最近完成（本轮）

- [`code-map-navigation-plan.md`](code-map-navigation-plan.md) /
  [`code-map-navigation-progress.md`](code-map-navigation-progress.md)：
  `completed`（独立 Judge pass）；与 [code-map-navigation-roadmap](../roadmap/code-map-navigation-roadmap.md) 配对。


## 完整门模板段落

触发 [Task Quality Gates 完整门](../dev-rules/task-quality-gates/README.md) 时，在 plan/progress 中增加下列段落（轻量门不强制）。

### plan（`{任务名}-plan.md`）建议结构

```markdown
# {任务名称}

- 状态：proposed | active | awaiting-judge | blocked | completed | superseded
- 质量门：完整门 | 轻量门
- 独立Judge：必须 | 可省略
- 日期：YYYY-MM-DD
- 对应 roadmap：链接或「无（高风险单轮）」
- 协调入口：无 | GitHub Issue URL

## 当前主线
## 目标关
### 目标
### 非目标
### 完成条件
## 启动关
### Blindspot Pass
### 关键假设
### 工作区基线
## 执行计划
### P0 / P1 / P2
## 验证合同
```

关键假设应包含置信度与验证方式。

### progress（`{任务名}-progress.md`）追加区块

每一刀或收尾时按需追加，不预写未发生的成功：

```markdown
## 当前快照
- 继承 plan 状态：…
- 下一刀：…

## 记录 · YYYY-MM-DD
### 实际改动
### Worker 验证
### Deviations
无 | …
### Boundary Check
### Judge Review
Verdict: pass | revise | blocked
…
### 阻塞与下一刀
```

Judge 协议见 [dual-agent-review](../dev-rules/dual-agent-review/README.md)。
`completed` 与 Judge 的条件硬门槛见 [document-control](../dev-rules/document-control/README.md) 第八节。

## 主线总结

plan 决定“接下来怎么做”，progress 记录“实际上做了什么”。完整门的 Blindspot、Deviations、Judge Review 也按上表拆入二者，不合并成单文件治理合同。只有一个 plan 可以代表当前主线，验证事实必须写进 progress，不能靠任务状态推断。
