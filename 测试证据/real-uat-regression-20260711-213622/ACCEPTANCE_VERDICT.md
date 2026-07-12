# 真实UAT回归测试 · 验收记录
- generated: 2026-07-11T21:50:22+08:00
- out: /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-213622
- exitcode: 0
- ended: 2026-07-11T21:39:11+08:00

## 工件清单
- OK: doctor-report.json
- OK: repo-map.json
- OK: coverage-units.json
- OK: evidence-plan.md
- OK: report.md
- OK: quality-gate-report.json
- OK: insight-probes.json
- OK: ANALYSIS_REPORT.md
- OK: UAT_EXEC_SUMMARY.md
- module-evidence: 1 ['src.json']
- subagent-artifacts: 3 ['subagent-src-state.json', 'subagent-secondary.json', 'subagent-src-export.json']

## Gate
- allowed_to_synthesize: True
- evidence-plan: pass
- parallelism-execution: pass
- report-draft: pass
- module-classification: pass
- parse-quality: pass
- reference-quality: pass
- module-evidence-matrix: pass
- key-unit-coverage: pass
- core-unparsed-areas: pass
- reference-completeness: pass
- semantic-source-review: pass
- report-depth: pass
- insight-probe-process: pass

## Insight probes
- ui_promise_runtime_path: hit
- multi_source_rules: hit
- config_dual_write_dead_impl: miss

## Verdict
**真实UAT回归测试过程有效；产品分析完整通过**（allowed_to_synthesize=true 且存在 ANALYSIS_REPORT.md）。
