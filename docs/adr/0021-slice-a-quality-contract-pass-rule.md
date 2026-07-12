# Slice A quality_contract=pass 判定规则

## 决策

在可比对照场景（**standard 模式** 且目标仓与 `baseline_v2_standard_pre_qc` 声明一致）下，脚本盖戳 `quality_contract=pass` 当且仅当**全部**成立：

1. **Probe Promotion**：`probe_hit_promotion_rate == 100%`（若 hit 数为 0，比率视为 100%；Catalog 流程完整性仍由 Mechanical Gate 约束）。
2. **Main Chain**：5 个角色槽均存在，且每槽 ≥1 个终稿锚点。
3. **Architecture Claim 可枚举**：至少能解析出 ≥1 条合法 claim 容器结构（有 `<!-- arch-claim -->` 等约定标记 + 锚点）；**不**要求数量 ≥12/≥20。
4. **Density 双升**（相对 `baseline_v2_standard_pre_qc`）：
   - `unique_anchors_in_contract_surfaces_new > baseline_contract_surface_anchors`（ADR-0027）
   - `risk_count_new > baseline_risk_count`

任一失败 → `quality_contract=fail`。  
不满足可比对照前提 → `density=not_evaluated`；`structure` 仍判定。总 `quality_contract` 按 ADR-0029 聚合（structure=pass 且 density 未评估 → 总 pass）。UAT 须标明密度是否可比。

## 明确不包含

- 不因相对 v1 仍低而 fail。
- 不自动改写 `delivery_status`。
- 不把本规则做成 Mechanical Gate hard fail。

## 澄清（ADR-0023）

`risk_count` 为结构化条数；pre-QC baseline 按同规则可为 0，此时 `risk_count_new > baseline` ≡ 至少 1 条结构化合规 Risk Item。COMPARE 不得把该上升解读为历史散文风险「数量级爆发」。

## 修正（ADR-0027）

密度双升硬条件中的锚点指标改为 **`unique_anchors_in_contract_surfaces`**（主链标记块 + claim + risk 内），不再用全文 `unique_anchors` 决定 pass。全文 anchors 仍 COMPARE 观测。并启用轻量防刷规则。

## 修正（ADR-0029）

`quality_contract` 分层为 `structure` + `density`。不可比场景下仅 `density=not_evaluated`；`structure=pass` 且 density 未评估时总结果为 **pass**。可比且 density=fail 则总 fail。详见 ADR-0029。
