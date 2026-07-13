# 产品契约与演进经验

## 1. V1 的质量边界优先于“尽量给出结果”

**结论：** 缺少 doctor 所需的结构证据时，分析应阻断，而不是以正则、行数或手写说明降级。V1 的目标是可安装、可触发、可验证的标准分析流程，不是所有场景都要生成报告。

**等级：** 已核验。

**来源范围：** Meta_Kim 中关于 breaking v2、证据优先、doctor、coverage 与 quality gate 的规格讨论和执行记录。

**仓库证据：** [goals.txt](../../../goals.txt)、[V1 实施目标](../../goals/stark-repo-analyzer-v1-implementation.md)、[真实 UAT 规则](../../../dev-rules/real-uat-regression/README.md)。

**边界：** 这不授权忽略用户选择的范围外事项；P5 动态行为验证是 V1 明确排除的验证层，不是被声称已完成的能力。

## 2. 规格需要有确定性实现载体

**结论：** 仅靠 prompt 约束不足以保持长期一致性。可机器检查的 doctor、运行元数据、coverage、manifest 和 gate 产物，才是把架构分析流程变成可回归产品的载体。

**等级：** 已核验。

**来源范围：** Meta_Kim 中关于最小 CLI/scripts、coverage-units、quality-gate-report 与 runtime capability matrix 的两轮规格整理。

**仓库证据：** [验收脚本目录](../../../acceptance/)、[输入输出契约](../../spec/input-output-contract.md)、[任务执行记录](../goal-execution-record.md)。

**边界：** 机器检查只验证其声明的事实；不能以验证器通过替代源码裁决、真实调用或动态验证。

## 3. 版本演进必须保持模式和证据的可比较性

**结论：** 当比较旧 V1 与新的 code-only 方案时，必须固定输入、源码版本、分析模式和评分维度。先声明差异，再比较架构覆盖、证据质量、报告深度和失败分类；不能只比较图谱节点数或报告是否生成。

**等级：** 记忆支持，比较原则已核验。

**来源范围：** 2026-07-13 关于去掉 Graphify LLM 分块、升级到 `0.9.13`、先以小项目试点验证效果的项目记忆。

**仓库证据：** [物理基线](../../baseline/physical-baseline.md)、[实现比较](../../baseline/implementation-comparison.md)、[真实 UAT 规则](../../../dev-rules/real-uat-regression/README.md)。

**边界：** 当前工作树仍包含相关 WIP；该记忆记录的是演进意图，不是“迁移已完成”证明。

## 4. 发布状态必须从目标与证据状态推导

**结论：** 项目是否 ready 不能由代码改动量、目录数量或单个成功运行判断；需回到目标状态、P2/P4 证据、隔离结论及残余风险。

**等级：** 已核验。

**来源范围：** 多次关于“是否 ready”“缺什么”“哪些结果可算真实 UAT”的项目记忆。

**仓库证据：** [V1 状态](../../goals/stark-repo-analyzer-v1-implementation.md#status)、[物理基线当前边界](../../baseline/physical-baseline.md#current-evidence-boundary)。
