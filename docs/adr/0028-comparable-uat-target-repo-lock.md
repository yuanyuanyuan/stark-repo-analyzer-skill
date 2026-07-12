# 可比 UAT 目标仓锁定（Slice A 密度双升前提）

## 决策

Slice A 启用 `quality_contract` 密度双升硬条件时，目标仓必须与 baseline 声明一致：

| 字段 | 值 |
|---|---|
| `repo_path` | `/tmp/Long_screenshot_splitting_tool` |
| `repo_commit` | `bdee20b`（与 `测试证据/real-uat-regression-20260711-213622` 摘要一致） |
| `mode` | `standard` |

- UAT 必须记录实际 `git rev-parse HEAD`。
- 与声明 commit **不一致** → 默认 `quality_contract=not_evaluated`（结构/探针项仍可出诊断明细），除非显式 `ignore_commit_drift: true` 并写理由。
- 更换路径/commit 须更新 baseline 清单与变更记录，禁止 silently 对比。
- 产品 Insight Probe 类别仍保持跨仓通用；**可比密度验收**可绑定该实例仓。

## 与 ADR-0029

commit/路径漂移时默认仅 **density** 层 `not_evaluated`，不是整票取消 structure 判定。
