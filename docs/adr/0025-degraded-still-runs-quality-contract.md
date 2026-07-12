# Degraded Delivery 仍跑质量合同盖戳；与 Full 正交

## 决策

- Mechanical Gate 红导致 `delivery_status=degraded` 时，**仍应**运行 QC 对照脚本并盖戳 `quality_contract`。
- 合法组合包括：`full+pass`、`full+fail`、`degraded+pass`、`degraded+fail`、以及 `not_evaluated`。
- `degraded+pass` 表示：能力/门禁未完整通过，但终稿结构与 Probe Promotion 等合同仍达标；**不得**据此宣传 Beats-v1.0，也 **不得** 算 UAT「产品分析完整通过」。
- 「产品分析完整通过」仍要求 Full Delivery（及既有 UAT 合同），与 `quality_contract=pass` 是不同句子。
- 禁止：Degraded 强制 `not_evaluated` 或强制 `fail` 来偷绑两维。
