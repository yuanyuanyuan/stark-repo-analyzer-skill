# 合同表面锚点双升 + Slice A 轻量防刷

## 决策

### 双指标

- **`unique_anchors`**：终稿全文规范化 unique（ADR-0020），COMPARE 打印，**观测**。
- **`unique_anchors_in_contract_surfaces`**：仅统计落在合同表面内的锚点——Main Chain 标记块、Architecture Claim 条目、Risk Item 条目。

### Slice A 硬条件修正（相对 ADR-0021）

可比场景下密度双升改为：

- `unique_anchors_in_contract_surfaces_new > baseline_contract_surface_anchors`
- `risk_count_new > baseline_risk_count`（结构化，ADR-0022/0023）

全文 `unique_anchors` 不单独决定 pass/fail。pre-QC baseline 的合同表面锚点可为 0。

### 轻量防刷（Slice A）

1. 同一规范化锚点只计一次。
2. 每个 main-chain 槽：标记块内 ≥1 锚点，且正文达到最小实质长度（实现默认 ≥80 字，可配置）。
3. 五槽的锚点集合不得五槽完全同一单锚点复制（至少需要一定分散；实现可要求「并非全部槽位 anchors 集合完全相等」）。
4. claim/risk 条目不得仅有标记而无判断/改造语句。
5. **不做**目标仓文件存在性/行号校验（留给后续阶段）。

## 非目标

- 不声称能防止所有灌水；Reader Rubric 仍负责洞见真伪。
