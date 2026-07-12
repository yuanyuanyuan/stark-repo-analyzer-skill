# Slice A 终稿质量合同最小范围

在 ADR-0010（质量合同不默认 hard gate）前提下，Slice A 的最小必达与观测边界如下。

## 决策

Slice A **硬必达**（真实UAT / Skill 合同失败，不进 Mechanical Gate hard fail）：

1. **Probe 升格**：每个 `status=hit` 的 Insight Probe 必须出现在终稿「风险与改造优先级」；仅 `insight-probes.json` hit 不算过线。
2. **主链结构**：终稿须含可配置 N 段主链（默认 5）；每段至少 1 个 `file:line` 锚点。
3. **Claim 可枚举**：关键设计决策 / 架构 claim 须为列表或独立小节，禁止单段权衡散文冒充多 claim；提供粗计数脚本。

Slice A **仅观测、不设失败阈值**（Density Proxy）：

- 独立 claim 数量建议值（standard≥12 / deep≥20）
- 风险/改造条数建议值（standard≥5 / deep≥8）
- unique anchors 相对 v1 与相对当前 baseline 的升降

Slice A **明确不做**：

- 不把 anchors/claim 数量下限做成 Mechanical Gate hard fail
- 不改写 report-depth 的 Full/Degraded hard 语义（最多 soft 指标）
- 不做更多 doctor 能力扩张

验收口径：相对当前 standard baseline（如 213622），unique anchors 与风险条数应上升；probe hit → 终稿映射率 100%；Full/Degraded 仍诚实。

## 修正

ADR-0021 将「相对 baseline_v2_standard_pre_qc 的 unique_anchors 与 risk_count 双严格上升」升级为可比场景下 `quality_contract=pass` 的硬条件；**绝对数量建议下限**（≥12 claim 等）仍仅观测。本 ADR 中「密度仅观测、不设失败阈值」对**趋势双升**不再适用。
