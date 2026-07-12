# 分析报告草稿（deep · Doctor 阻塞）

<a id="blocked-delivery"></a>

## 执行状态

| 项 | 值 |
|---|---|
| 模式请求 | deep |
| Doctor allowed | **false** |
| allowed_deep | **false** |
| 缺失能力 | **reference-edges** |
| 是否降级 standard | **否**（合同：reject_no_downgrade） |
| scan/summarize/units | **拒绝执行** |
| Full Delivery | **否** |
| ANALYSIS_REPORT.md | **不生成** |

## 阻塞根因（可审计）

1. Universal Ctags 在本仓 TS/JS 抽样中 `roles=reference` 标签为 0（definition≈112）。TS 语言 kinds 的 REFONLY 均为 no。
2. `units` 仅把 ctags reference-role 记为 `refs_status=complete`；rg/grep 文本命中一律 `partial`。
3. Graphify 图存在（nodes≈2875, links≈4550）且声明 reference-edges，但**未接线**到 `coverage-units.refs_status`；`graphify_units_refs_wired=false`。
4. 本轮**未**设置 `REPO_ANALYZER_GRAPHIFY_UNITS_REFS=1`：该开关只会让 doctor 探针放行，并不会让 units 真正产出 complete refs，与「工具存在 ≠ 对本仓可验证」合同冲突。

诊断：`diagnostics/reference-edges-block.json`、`diagnostics/cli-refusal-log.txt`、`doctor-report.json`、`install-prompt.md`。

## 本不应宣称的结论

以下主题在用户期望中需要覆盖，但 **本轮无源码锚点证据**，一律降级为「未验证 / Unsupported」：

- Worker 协议/时序
- 导航规则一致性
- 切片索引语义
- 导出选项贯通
- SEO 多源

## Unsupported Area

- **deep 模式整体**：reference-edges 能力对本仓不可验证 → 不声明 deep 覆盖充分，不输出 Full 终稿。
- **core 源码架构结论**：未运行 units/coverage 回填，无 analyzed 单元。

## 预算执行摘要

- parallelism: **degraded**（doctor 拦截后无子代理）
- 外部调研：未展开（分析链路终止）
- 报告长度：阻塞态摘要，非 deep 深度叙事

## 开放问题

1. Graphify→units `refs_status` 接线（P4 tooling debt）何时落地？
2. TS/JS 是否应引入非 ctags 的 reference provider 并写入 capabilities 合同？
3. doctor 探针与 gate reference-quality 阈值是否应对语言族做差异化（须走规则变更，不得在 UAT 静默改阈值）？

---
*本文件是质量门前的阻塞态草稿，不是 Full Delivery 终稿。*
