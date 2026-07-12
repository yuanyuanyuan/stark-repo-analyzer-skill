# risk_count 计数规则（终稿 Density Proxy / Slice A 硬输入）

## 决策

`risk_count` 扫描终稿 `ANALYSIS_REPORT.md`，不扫 matrix alone。

1. **章节定位**：标题匹配风险/改造类正则族（如含 `风险`、`改造优先级`、`风险与改造`）。
2. **条目边界**：该章下优先按 `###` 小节计数；若无 `###` 子节，则按带结构的顶级 `-` 列表项计数。
3. **计入条件**（同时）：
   - 条目内 ≥1 个合法 `file:line`（或 `file:start-end`）锚点；
   - 且（含 `probe-promotion` 标记 **或** 改造方向启发式：如含 `改造` / `建议` / `应` / `fix` 等约定词族）。
4. **Probe Promotion 条目计入** `risk_count`；**不计入** `claim_count`。
5. 无 probe hit 时仍须靠非探针风险条目支撑 `risk_count`；不得以「未命中探针」解释风险为零。
6. baseline 与 candidate **必须用同一规则**重算后再比 `>`。

## 与 ADR-0021

可比场景下 `risk_count_new > risk_count(baseline_v2_standard_pre_qc)` 为 `quality_contract=pass` 硬条件之一。

## 语义

指标名可理解为结构化改造可执行条数；定义标签 `risk_count_definition=structured_v1`。散文风险 ≠ 本计数（见 ADR-0023）。
