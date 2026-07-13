# 物理基线与报告质量经验

## 1. reference-runs 与 physical-runs 证明不同事实

**结论：** reference-runs 是高保真内容基线；physical-runs 是固定输入下真实调用、产物谱系和工具证据的快照。两者不能互相复制或替代。

**等级：** 已核验。

**来源范围：** click、HTTPX、Ruff、Codex Plugin CC、Claude Code、Codex 的 physical baseline invocation 记录，以及后续的报告深度对比。

**仓库证据：** [物理基线：报告保真度边界](../../baseline/physical-baseline.md#report-fidelity-boundary)、[参考运行说明](../../baseline/reference-runs/README.md)。

## 2. P2 与 P4 是独立门槛

**结论：** P2 要真实 Agent/runtime 入口和完整调用证据；P4 要相同固定输入的两次独立快照及通过的标准化比较。单次物理目录或成功 doctor 不能替代 P4。

**等级：** 已核验。

**仓库证据：** [真实 UAT 分档与证据](../../../dev-rules/real-uat-regression/README.md)、[物理基线门槛](../../baseline/physical-baseline.md)。

## 3. 报告深度应按模块分解和验证步骤比较

**结论：** 判断新旧报告是否“更好”不能只看行数。至少比较模块拆分、核心模块覆盖、源码证据、交叉验证、限制说明、研究输入和代理协作边界。较短的 physical report 可能是可审计的，但不能被称作与参考报告等价。

**等级：** 已核验。

**来源范围：** 关于 Codex Plugin CC 物理报告 98 行、参考报告 196 行及缺失模块族的记忆与执行记录。

**仓库证据：** [执行记录：报告保真度差异](../goal-execution-record.md#7-physical-baseline-report-depth-differs-from-reference-reports)。

## 4. 物理运行的提示词本身是证据的一部分

**结论：** 固定 source HEAD、输出目录、只读边界、参考 skill 读取要求和限制条件需要随运行保存。它们让后续审阅能够判断一次运行到底分析了什么、未分析什么。

**等级：** 记忆支持，产物结构已核验。

**来源范围：** 2026-07-12 至 2026-07-13 的 click、HTTPX、Ruff、Claude Code、Codex 与 Codex Plugin CC 固定 invocation 记录。

**仓库证据：** `docs/baseline/physical-runs/*/input.md`、`metadata.json`、`execution-log.md`。
