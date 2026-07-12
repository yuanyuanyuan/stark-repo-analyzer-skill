# Density Baselines（Slice A / QC-4）

> 更换须同步 ADR-0019 / ADR-0028 与变更记录。

## 可比场景声明

| 字段 | 值 |
|---|---|
| `repo_path` | `/tmp/Long_screenshot_splitting_tool` |
| `repo_commit` | `bdee20b` |
| `mode` | `standard` |
| commit 漂移默认 | `quality_contract=not_evaluated` |

## 固定 baseline 终稿

| id | 路径 | 角色 |
|---|---|---|
| `baseline_v1` | `测试证据/v1.0没改造前/ANALYSIS_REPORT.md` | v1 密度/叙事天花板对照 |
| `baseline_v2_standard_pre_qc` | `测试证据/real-uat-regression-20260711-213622/ANALYSIS_REPORT.md` | 纠偏前 standard 主对照 |

## 参考（非 Slice A 主对照）

| id | 路径 |
|---|---|
| `reference_deep_wired` | `测试证据/real-uat-deep-wired-20260711-220005/ANALYSIS_REPORT.md` |

## 指标定义指针

- 全文 `unique_anchors`：ADR-0020  
- 合同表面 anchors / 防刷：ADR-0027  
- `risk_count`：ADR-0022 / 0023  
- `quality_contract=pass`：ADR-0021（经 0027 修正）  
- 盖戳 SSOT：ADR-0018 → `quality-contract-report.json`
