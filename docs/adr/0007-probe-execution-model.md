# Insight Probe 执行模型：确定性候选 + LLM 判定

P1 不采用纯 skill 提醒，也不采用跨语言硬编码“自动发现 bug”。采用两段式：

1. **确定性辅助**：枚举候选入口（UI/选项字段、重复规则定义点、配置与平行实现候选列表），降低漏入口风险。
2. **LLM 判定**：沿候选追到运行时路径，产出 `insight-probes.json`（每类至少一条：`category/status/summary/anchors/report_ref`），hit 必须进入终稿风险与改造优先级。

候选枚举不是命中证明；未产出结构化结论或缺类别视为 Probe Obligation 失败。若 G1 等召回仍不稳，优先加强候选枚举信号，而不是退回纯散文或放宽 Gold Sample。
