# quality_contract 由确定性脚本盖戳，不以 agent 自报为准

## 决策

- `quality_contract` /（及后续协议写入的）`beats_v1` **不得**由分析 agent 自行填 `pass` 作为有效过线。
- 合成终稿时 agent 若需占位，只允许 `quality_contract: not_evaluated`（或省略待补）。
- Slice A 对照脚本（QC-4 最小版）为盖戳权威：
  1. 读取终稿 + `insight-probes.json` 等产物
  2. 写出 **`quality-contract-report.json` 作为机读 SSOT**
  3. patch 或要求终稿文首与脚本结果一致
- UAT 以 `quality-contract-report.json` 为准；终稿文首与 json 不一致 → UAT 红（防手改 pass）。
- `beats_v1` 默认 `not_evaluated`，仅在金样 + Reader Rubric 约定流程完成后由脚本/人工协议写入。

## 与既有 ADR

- 落实 ADR-0016 的字段语义，堵住自欺通道。
- 不改变 Mechanical Gate / `delivery_status` 语义（ADR-0001 / 0010）。
