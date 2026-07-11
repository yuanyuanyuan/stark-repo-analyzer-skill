# 探针流程进入 Mechanical Gate，内容 miss 不挡门

Probe Obligation 分两层：

1. **流程**：必须产出 `insight-probes.json`，Catalog 每一类有结论（hit/miss/n_a+理由）。缺失 → Mechanical Gate 失败 → 不得 Full Delivery（`delivery_status=full`）。
2. **内容**：`miss`（认真查过未发现硬伤）不导致 gate 失败；`hit` 必须进入终稿，否则算有用性/准确度失败（验收层），实现上应尽量机械检查 report_ref。

与 Degraded Delivery 一致：流程 gate 红时仍向 Primary Reader 交付 degraded 终稿，禁止主用户空手；也禁止把流程失败包装成完整通过。
