# unique_anchors 计数规则（终稿 Density Proxy）

## 决策

Slice A / COMPARE 的 `unique_anchors` 按下列规则计算，保证与双 baseline 可复现对照。

1. **扫描对象**：仅终稿 `ANALYSIS_REPORT.md` 全文（不是 matrix/coverage  alone）。
2. **匹配族**：`(?:[\w./@-]+)\.[A-Za-z0-9]+:\d+(?:-\d+)?`（`file.ext:line` 或 `file.ext:start-end`）。
3. **规范化**：
   - 去掉围栏/反引号/包裹括号噪声
   - 路径分隔符统一为 `/`
   - **保留完整路径**（不做 basename-only，避免同名文件假合并）
   - 范围锚点 `file:12-40` 以**整串**为 unique key（不按行展开）
4. **`unique_anchors`** = 规范化后 set 大小。
5. 可选附带 `anchor_total_mentions`（含重复出现次数）。
6. 该指标是 Density Proxy：Slice A **不**因低于 v1 而 fail；相对 `baseline_v2_standard_pre_qc` 的升降用于验收趋势。

## 非目标

- 不以 matrix analyzed anchors 替代读者可见终稿密度。
- 不把 unique_anchors 做成 Mechanical Gate hard fail（ADR-0010）。
