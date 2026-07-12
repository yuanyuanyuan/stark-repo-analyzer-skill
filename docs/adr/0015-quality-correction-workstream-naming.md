# 纠偏工作包命名：QC-* 与既有 First Delivery P1–P4 分轨

## 决策

- **保留** CONTEXT / ADR-0009 既有 **First Delivery Slice** 编号语义：
  - P1 Insight Probe
  - P2 Full/Degraded Delivery
  - P3 Gold Sample / Reader Rubric / Agent Smoke
  - P4 deep reference Tooling Debt
- 质量落差纠偏方案（原研究稿 P0–P5）**禁止**再使用裸 `P0`–`P5` 指代纠偏包，以免与上表串台。
- 纠偏包正式前缀为 **`QC-*`（Quality Correction Workstream）**：
  - `QC-0` 终稿质量合同（原 P0）
  - `QC-1` 降低 JSON 税（原 P1）
  - `QC-2` 业务模块叙事（原 P2）
  - `QC-3` 深读预算（原 P3）
  - `QC-4` 对照指标产品化（原 P4）
  - `QC-5` Reader 闭环执行落地（原 P5；对齐旧 P3 的执行缺口，不是替换旧 P3 定义）
- 实施切片继续用 **`Slice A/B/C`**：
  - Slice A ⊂ QC-0 最小闭环 + QC-4 对照脚本
  - 与 First Delivery Slice「流程是否齐备」正交：旧切片可已齐，QC 仍可未过线
- 历史研究稿若仍出现裸 P0–P5 纠偏义，以本 ADR 与 CONTEXT 为准；后续编辑应改为 QC-*。
