# Slice A 提供终稿质量骨架模板，降低标记漏写税

## 决策

- 为缓解 R3 注意力税与新增标记义务的张力，Slice A 交付 **最小终稿骨架模板**（references，非 QC-1 全量 JSON 脚手架）。
- 建议路径：`skills/repo-analyzer/references/final-report-quality-skeleton.md`。
- 骨架须含：文首元数据（`delivery_status`、`quality_contract: not_evaluated`、预留 `beats_v1`）、主链五槽 `main-chain` 标记占位、Architecture Claim 示例壳、风险与改造节 + probe-promotion 示例壳、推荐章节标题。
- Skill 要求 agent **套用骨架填肉**，不得再手写一套无标记散文充终稿。
- Slice A **不**新增 agent 手填 QC sidecar；**不**实现 matrix/coverage/probe 候选全自动生成（QC-1 本体留 Slice B）。
- CLI `scaffold-report` 可留到 Slice B；Slice A 用 references 模板即可。

## 与 ADR-0026

属于 QC-0 落地辅助，不视为范围突破到 QC-1 主路径。
