# 真实UAT回归测试·deep · 验收记录

- generated: 2026-07-11T21:50:30+08:00
- out: `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-214641`
- exitcode: `0`（codex exec 进程正常结束；分析链路在 doctor 正确阻塞）
- ended: 见 `codex-exec.ended`
- mode: **deep**（未静默降级 standard）

## 工件清单

| 产物 | 状态 |
|---|---|
| doctor-report.json | OK（`allowed=false`, `allowed_deep=false`） |
| install-prompt.md | OK |
| evidence-plan.md | OK（mode=deep, parallelism=degraded） |
| module-evidence/src.json | OK（阻塞占位，非有效 Matrix） |
| report.md | OK（阻塞态草稿 55 行） |
| insight-probes.json | OK（三类 `n_a`，合法） |
| quality-gate-report.json | OK（`allowed_to_synthesize=false`） |
| UAT_EXEC_SUMMARY.md | OK |
| diagnostics/* | OK（refusal / reference-edges-block / target-commit） |
| repo-map.json / repo-map.md | **未生成**（doctor 拒绝后 scan 未执行，合规） |
| coverage-units.json | **未生成**（合规） |
| ANALYSIS_REPORT.md | **未生成**（gate 未放行，合规） |

## Gate

- `allowed_to_synthesize: false`
- doctor-deep-capability: **fail**
- workflow-no-silent-downgrade: pass
- evidence-plan: pass
- insight-probe-process: pass
- report-draft: pass
- repo-map / coverage-units / module-evidence-matrix / key-unit-coverage / reference-quality / semantic-source-review / parallelism-execution: **fail**

## 根因（reference-edges）

1. Universal Ctags 对本仓 TS/JS 抽样 **reference_tags=0**（definition≈112）。
2. Graphify 图边存在，但 **未接入** `coverage-units.refs_status`（`graphify_units_refs_wired=false`）。
3. 未设置 `REPO_ANALYZER_GRAPHIFY_UNITS_REFS=1` 假放行（与合同一致）。

## Verdict

| 维度 | 结论 |
|---|---|
| 过程有效（独立 `codex exec` + 严格 deep 合同） | **是** |
| 产品分析完整通过 / deep Full | **否** |
| 相对 standard 报告是否更厚 | **本轮无 Full 报告可对比厚度**（链路在 Phase 0 终止） |

**一句话**：真实UAT·deep **过程有效、产品未完整通过**；缺 `reference-edges` 可验证性时正确拒绝，未伪造 `ANALYSIS_REPORT.md`。
