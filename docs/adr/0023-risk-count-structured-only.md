# risk_count 只计结构化合规条；pre-QC baseline 可为 0

## 决策

- `risk_count` **只**统计符合 ADR-0022 的结构化 Risk Item，不统计散文中的风险叙述次数。
- 对 `baseline_v1` / `baseline_v2_standard_pre_qc` / 当前 deep 参考稿按同规则重算时，**允许为 0**：表示未达结构合同，不是「项目无风险」。
- 因此在 pre-QC standard baseline 上，ADR-0021 的 `risk_count_new > baseline` 实际等价于 **`risk_count_new ≥ 1`**（在 baseline=0 时）。
- COMPARE 必须标注 `risk_count_definition=structured_v1`；可另附观测用弱指标（如风险词+锚点共现），**不得**与 `risk_count` 混名。
- 禁止把「risk 0→N 升幅 %」解读为历史洞见突然爆炸；正确解读是「从无结构条到有结构条」。

## 与 ADR-0021 / 0022

补充而非废止：硬条件仍是结构化 `risk_count` 相对 baseline 严格上升；本 ADR 澄清语义与 baseline=0 的含义。
