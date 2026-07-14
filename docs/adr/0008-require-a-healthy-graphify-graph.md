---
status: superseded
superseded_by: ADR-0018
---

# 要求健康的 Graphify 图谱

> 此决定已被 [ADR-0018](0018-validate-the-normalized-usable-graph.md) 取代。以下正文保留历史原貌。

有效图谱必须在 `$WORK_DIR/graphify-out/` 中同时包含可解析的 `graph.json` 和 `GRAPH_REPORT.md`，并至少有一个节点；所有节点和边引用必须完整，所有 `source_file` 必须位于目标仓库内。通用仓库不以边数量作为硬门槛，但 V1 的 `click` 试点必须存在至少一条带 `source_file/source_location` 的 `EXTRACTED` 边，否则判为结构证据不足并中止。

## 影响

- 验证器必须检查 JSON 结构、端点引用、来源路径和非空节点，而不是只检查文件是否存在。
- `GRAPH_REPORT.md` 是必要产物和线索来源，不能替代 `graph.json` 中的可定位证据。
- 回归按目标仓库类型区分通用健康门槛与试点加强门槛，避免用小型独立仓库的合理无边图误判。
