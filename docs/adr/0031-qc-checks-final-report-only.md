# 质量合同只检查终稿 ANALYSIS_REPORT.md

## 决策

- Final Report Quality Contract / 对照脚本的检查对象是 **`ANALYSIS_REPORT.md` 终稿**，不是 pre-gate 草稿 `report.md` alone。
- 不要求 agent 在 Mechanical Gate 之前的 `report.md` 已写满 main-chain / probe-promotion / arch-claim 标记。
- 标记与结构义务在**合成终稿时**落地。
- 缺终稿时：
  - 目录被标为「已完成 UAT 交付」却无 `ANALYSIS_REPORT.md` → `structure=fail`（从而总 `quality_contract=fail`）
  - 研究性半成品 / 未宣称交付完成 → `quality_contract=not_evaluated`
- Slice A 不对 `report.md` 做 soft gate 指标绑定（与 ADR-0011/0026 一致）。
