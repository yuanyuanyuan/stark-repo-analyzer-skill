# Slice A 范围冻结与完成定义

## 决策

Slice A（⊂ QC-0 最小闭环 + QC-4 最小对照脚本）**只做**：

1. 文档：skill/references 质量合同短节；标记族（main-chain / probe-promotion / arch-claim）；双 baseline 清单；QC-* 命名对齐。
2. 确定性脚本：读终稿 + `insight-probes.json`（+ baseline），写 `quality-contract-report.json` 与 COMPARE，按 ADR-0021 等盖戳。
3. Skill 义务：终稿结构与标记；禁止 agent 自报 `quality_contract: pass`；占位仅 `not_evaluated`。
4. 真实UAT：约定样例仓 + **standard**；新目录出 COMPARE/盖戳。

Slice A **明确不做**：QC-1 JSON 骨架生成、QC-2 ≥3 业务模块叙事强制、QC-3 深读预算硬门槛、QC-5 金样/Rubric 全自动流水线、Mechanical Gate hard 扩建、宣称 Beats-v1.0。

## 完成定义（DoD）

- 脚本 + skill 短节已落地。
- 至少 1 次真实UAT **跑通盖戳链路**。
- 第一次 UAT 允许 `quality_contract=fail`，只要脚本判定可解释且与合同一致；**禁止**为冲 pass 而伪造标记/刷锚点。
- 冲击目标仍是 pass，但 DoD 是「链路真、判定对」，不是「第一次必须绿」。

## 补充（ADR-0032）

Slice A 文档交付含 `final-report-quality-skeleton.md` 最小终稿骨架模板；不因此打开 QC-1 全量 JSON 自动生成范围。
