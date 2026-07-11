# 准确度过线：Gold Sample 必中且必须进终稿

相对 v1.0 的 Accuracy Bar 采用「金样必中 + 命中进终稿」，而不是「跑过探针」或纯主观打分。

## Gold Sample Set v1

- **G1** · UI Promise → Runtime Path：界面/API 承诺的选项或行为未进入真实执行路径；终稿必须列为一致性风险与改造项。
- **G2** · Multi-Source Rules：同一访问或业务规则多处定义且不一致；终稿必须指出多源冲突与收敛建议。
- **G3** · Config Dual-Write / Dead Implementation：多配置源或未挂主路径的平行实现；终稿必须指出事实源分叉或死实现。
- **G4** · 非 UI 形态仓护栏：在库/服务端等形态上要么真实命中，要么「不适用 + 形态理由」；禁止静默跳过或乱报。

新版本漏检 G1–G3，或命中只留在 JSON/草稿未进入 `ANALYSIS_REPORT.md` 的风险与改造优先级，均判准确度未达标。实例仓可含长截图对照，但产品范围不绑定该业务域。
