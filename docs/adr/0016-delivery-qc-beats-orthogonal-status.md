# Full Delivery、质量合同、Beats-v1.0 三维状态正交

## 决策

一次分析对外状态拆成三层，**互不偷绑**：

1. **`delivery_status: full|degraded`** — 仅反映 Mechanical Gate / Synthesis Rule（不撒谎的 Full/Degraded Delivery）。
2. **`quality_contract: pass|fail|not_evaluated`** — Final Report Quality Contract / Slice A（及后续 QC）是否过线；由对照脚本与 UAT 判定。
3. **`beats_v1: pass|fail|not_evaluated`** — Accuracy + Usefulness + Quality 相对 v1 是否过线；依赖金样、Reader Rubric 与约定对照，不由 gate 13/13 推出。

## 规则

- QC 失败 **不**自动把 `delivery_status` 改成 `degraded`，也 **不**自动 `allowed_to_synthesize=false`（ADR-0010）。
- UAT「产品分析完整通过」= Full Delivery 前提语义保持；**不**隐含 `quality_contract=pass` 或 `beats_v1=pass`。
- Slice A 起：终稿 `ANALYSIS_REPORT.md` **文首/元数据区必须写出** `delivery_status` 与 `quality_contract`；`beats_v1` 可先 `not_evaluated`，但字段建议预留。
- 禁止话术与验收暗示：「gate 全绿 ⇒ 压过 v1」或「Full ⇒ 质量合同已过」。

## 与既有 ADR

- 补充 ADR-0001（Delivery）与 ADR-0003/0004（Beats 过线器），不废止它们。

## Degraded 场景（ADR-0025）

Degraded 仍跑 QC 盖戳；允许 `degraded+pass`，但不得宣传 Beats 或「产品分析完整通过」。
