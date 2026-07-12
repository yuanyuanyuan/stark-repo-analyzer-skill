# 质量对照双 baseline 固定路径

## 决策

真实UAT / COMPARE 使用 **双 baseline**，路径固定；更换须文档变更记录，禁止每次口头替换。

| 角色 | 固定路径（本 worktree） |
|---|---|
| `baseline_v1` | `测试证据/v1.0没改造前/ANALYSIS_REPORT.md` |
| `baseline_v2_standard_pre_qc` | `测试证据/real-uat-regression-20260711-213622/ANALYSIS_REPORT.md` |

参考（非 Slice A 主对照）：

| 角色 | 路径 |
|---|---|
| `reference_deep_wired` | `测试证据/real-uat-deep-wired-20260711-220005/ANALYSIS_REPORT.md` |

## Slice A 验收

- **主对照** `baseline_v2_standard_pre_qc`：`unique_anchors` 与 `risk_count` 相对上升；`probe_hit_promotion_rate=100%`；主链 5 槽过线；`quality_contract` 由脚本盖戳。
- **副对照** `baseline_v1`：输出差距表；**不要求**本刀 `beats_v1=pass`。
- 目标仓与 mode 须与 baseline 声明一致（standard 对 standard；同一约定样例仓）。

## 非目标

- 不以 deep 220005 作为 Slice A 主 baseline。
- 不以「与上一次 run 比」替代固定 pre-QC baseline。
