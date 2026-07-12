# Probe hit 升格判定：终稿可机关联 + 最小改造结构

## 决策

对每个 `insight-probes.json` 中 `status=hit` 的探针，**Probe Promotion** 过线条件为（Slice A 质量合同 / UAT，非 Mechanical Gate hard）：

1. 检查对象是终稿 **`ANALYSIS_REPORT.md`**（不得仅以草稿 `report.md` 或 JSON 侧车为准）。
2. 终稿「风险与改造优先级」中存在可关联该 probe 的条目（关联方式见实现约定，须稳定可脚本化）。
3. 该条目至少可机判包含：
   - **源码锚点**（`file:line` 形态）
   - **改造方向**（独立小节/列表项中的改造表述，非仅复述现象）
4. 「现象 / 影响」完整四要素由 Reader Rubric 抽检，不作 Slice A 脚本硬失败条件。
5. `miss` / `n_a` 不要求升格条目；映射失败 → 质量合同失败与 UAT 红，**不**自动 `allowed_to_synthesize=false`。
6. UAT 输出 `probe_hit_promotion_rate` 作为 Density Proxy / 准确度落地指标。

## 非目标

- 不以非空 `report_ref` 单独作为升格成功。
- 不以人工抽检作为每次 UAT 唯一路径（金样仓可叠加人工）。

## 与 ADR-0031

Probe Promotion 检查对象明确为终稿 `ANALYSIS_REPORT.md`，与质量合同其它条款一致。
