# Gate 阻塞时仍向主用户做 Degraded Delivery

主用户是 Human Decision Reader 与 Agent Consumer，不是 Acceptance Auditor。

## 决策

- Mechanical Gate 失败（`allowed_to_synthesize=false`）时，验收可判「产品分析未完整通过」，但必须仍交付可用终稿。
- 终稿统一路径 `ANALYSIS_REPORT.md`（Full 与 Degraded 同路径）。
- Full：`delivery_status=full`，文首无降级横幅。
- Degraded：文首降级横幅 + `delivery_status=degraded` + 失败门禁列表 + 结论可信度边界。
- UAT「产品分析完整通过」= gate 全绿 + `delivery_status=full`，不因“存在 ANALYSIS_REPORT 文件”而通过。

## 规则变更

废止旧合同中「`allowed_to_synthesize=false` 时禁止生成任何 `ANALYSIS_REPORT.md`」的绝对禁令；替换为 **Synthesis Rule**（见 CONTEXT.md）。skill、UAT 规格与相关验收清单必须同步改写，禁止实现与文档各说各话。

## 非目标

- 不放宽 Mechanical Gate 阈值来换假 Full。
- 不把长期 Degraded 当 deep 成功终点；Tooling Debt 仍须偿还。
