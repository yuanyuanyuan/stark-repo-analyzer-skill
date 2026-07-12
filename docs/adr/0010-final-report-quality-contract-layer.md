# 终稿质量合同放在 Skill/UAT 层，不默认进 Mechanical Gate hard fail

研究草案 `docs/research/2026-07-11-quality-gap-diagnosis-and-correction-plan.md` 指出：Mechanical Gate 全绿时报告仍可显著薄于 v1.0，根因是把审计地板当成质量终局。

## 决策

- **Final Report Quality Contract**（主链 N 段、独立 claim 下限、风险/改造下限、probe hit 升格、禁止单段权衡散文冒充多 claim）主执行层为 **Skill 交付合同 + 真实UAT / Reader Bar / 对照脚本**，不是 Mechanical Gate 的 hard fail。
- 实施分阶段：Slice A 先文档化合同 + COMPARE/smoke 脚本；指标稳定后，仅允许把**极少数可机判且难刷**的条款升 soft warning 或（极慎重）hard。
- **默认不得**把 unique anchors 下限或独立 claim 数量下限做成 Mechanical Gate hard fail，以免重演「合规浅写 / 刷数字」。
- Mechanical Gate 继续只决定 Full / Degraded（不撒谎）；Beats-v1.0 只认 Accuracy / Usefulness / Quality Reader 三维。

## 与既有 ADR

- 补充 ADR-0003 / 0004（过线器在金样与 Reader，不在 checks 全绿）。
- 不改变 ADR-0001 Synthesis Rule；质量合同失败 ≠ 自动改写 Full/Degraded 语义，除非日后另做显式 soft/hard 升级决策。
