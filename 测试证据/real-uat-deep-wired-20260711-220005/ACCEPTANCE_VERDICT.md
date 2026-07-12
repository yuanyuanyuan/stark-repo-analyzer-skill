# 真实UAT回归测试·deep（Graphify 接线后）· 验收记录

- generated: 2026-07-11T22:05:00+08:00
- out: `测试证据/real-uat-deep-wired-20260711-220005`
- exitcode: `0`
- ended: `2026-07-11T22:04:09+08:00`
- mode: **deep**

## 工件

| 产物 | 状态 |
|---|---|
| doctor-report.json | OK `allowed_deep=true`，Graphify units wired |
| repo-map.json / repo-map.md | OK |
| coverage-units.json | OK `graphify_refs.wired=true`（nodes=2875, extracted_ref_links=1507） |
| evidence-plan.md | OK，parallelism=active |
| module-evidence/src.json | OK |
| subagent-artifacts/* | OK（3） |
| report.md | OK |
| insight-probes.json | OK（3 hit） |
| quality-gate-report.json | OK `allowed_to_synthesize=true`（13/13） |
| ANALYSIS_REPORT.md | OK（226 行） |
| UAT_EXEC_SUMMARY.md | OK |

## Gate

全部 pass：evidence-plan、parallelism-execution、report-draft、module-classification、parse-quality、**reference-quality**、module-evidence-matrix、key-unit-coverage、core-unparsed-areas、reference-completeness、semantic-source-review、report-depth、insight-probe-process。

## Insight probes

- ui_promise_runtime_path: **hit**
- multi_source_rules: **hit**
- config_dual_write_dead_impl: **hit**

## Verdict

| 维度 | 结论 |
|---|---|
| 过程有效 | **通过** |
| 产品分析完整通过 / deep Full | **通过** |
| Graphify→refs_status 接线 | **通过** |

**一句话**：接线后真实UAT·deep **Full Delivery** 成功。
