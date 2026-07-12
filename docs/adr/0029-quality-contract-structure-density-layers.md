# quality_contract 分层：structure 常在、density 仅可比

## 决策

`quality-contract-report.json` 分两层再聚合为总 `quality_contract`：

| 层 | 内容 | 何时判定 |
|---|---|---|
| `structure` | Probe Promotion 100%、Main Chain 五槽标记+锚点、≥1 Architecture Claim 结构、轻量防刷 | **任意**真实分析（有终稿即可） |
| `density` | 合同表面 anchors 与结构化 risk_count 相对 `baseline_v2_standard_pre_qc` 双严格上升 | 仅 **Comparable UAT Profile**（路径+commit+mode） |

## 聚合

- `structure=fail` → 总 `quality_contract=fail`
- `structure=pass` ∧ `density=pass` → 总 `pass`
- `structure=pass` ∧ `density=not_evaluated` → 总 **`pass`**（结构合同仍生效；COMPARE 标明密度未比）
- `structure=pass` ∧ `density=fail` → 总 `fail`
- 未跑脚本 → 总 `not_evaluated`

## 覆盖

修正 ADR-0021「不可比 → 总 not_evaluated」的字面：不可比时 **仅 density** 为 `not_evaluated`，structure 仍可 pass/fail，总结果按上表聚合。
