# 压过 v1.0 的实施切片顺序与第一交付范围

工作包划分：

1. **P1 Insight Probe** — Catalog、确定性候选 + LLM 判定、`insight-probes.json`、Probe Process Gate、命中进终稿
2. **P2 Delivery Contract** — Full/Degraded 同路径 `ANALYSIS_REPORT.md` + `delivery_status`
3. **P3 验收锁** — Gold Sample Set v1、Reader Rubric、Agent Smoke
4. **P4 deep Tooling Debt** — reference 接线（不阻塞第一交付切片）

**第一交付切片 = P1+P2+P3**。工程节奏为 **多 PR 串联**（建议 PR1=P1 → PR2=P2 → PR3=P3），全部落地前不得宣称 Beats-v1.0。P4 另开并行。
