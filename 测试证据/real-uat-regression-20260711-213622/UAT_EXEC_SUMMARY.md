# UAT 执行摘要 · 真实UAT回归测试·standard

## 基本信息

| 项 | 值 |
|---|---|
| 正式名称 | **真实UAT回归测试·standard**（标签：`real-uat-regression`） |
| 技能 | `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md` |
| 目标仓 | `/tmp/Long_screenshot_splitting_tool` @ `bdee20b` |
| 输出目录 | `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-213622` |
| 模式 | **standard**（默认可移植路径；禁止 Graphify / Universal Ctags / ast-grep） |
| parallelism | **active**（3 子代理：src-state / src-export / secondary） |
| 开始时间 | 2026-07-11 21:36:40 CST |
| 结束时间 | 2026-07-11 21:39:06 CST |
| Doctor | 放行（`allowed: true`，mode=standard，available_modes=[standard]，blocked_modes=[deep]） |
| Gate | **放行**（`allowed_to_synthesize: true`，13/13 checks pass，含 insight-probe-process） |

## 完整命令

```bash
# 工作目录
cd /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to

REPO="/tmp/Long_screenshot_splitting_tool"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-213622"
BIN="node bin/repo-analyzer.js"

# Phase 0–2：确定性 CLI（不得跳过）
$BIN doctor --repo "$REPO" --out "$OUT" --mode standard
$BIN scan --repo "$REPO" --out "$OUT"
$BIN summarize --repo "$REPO" --out "$OUT"
$BIN units --repo "$REPO" --out "$OUT"

# Phase 3–8：Agent 证据与叙事（本会话执行）
# - 并行 3 子代理读源码 → subagent-artifacts/*.json
# - 回填 coverage-units.json；写 evidence-plan.md、module-evidence/src.json、report.md、insight-probes.json

# Phase 9：质量门
$BIN gate --repo "$REPO" --out "$OUT" --mode standard

# Phase 10：gate 放行后合成
# → ANALYSIS_REPORT.md + UAT_EXEC_SUMMARY.md
```

用户侧触发命令（与本轮一致）：

```bash
严格执行 /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md
分析 /tmp/Long_screenshot_splitting_tool
输出报告到 /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-213622
# 模式必须为 standard；禁止 Graphify/Ctags/ast-grep；真实UAT回归测试
```

## 模式与并行

- **mode = standard**
- **tooling_level = baseline**（heuristic-text；增强工具即使已安装也必须忽略）
- **parallelism = active**
- 子代理分工与产物：
  - `subagent-src-state` → `subagent-artifacts/subagent-src-state.json`（会话+Worker 主链）
  - `subagent-src-export` → `subagent-artifacts/subagent-src-export.json`（上传/导出）
  - `subagent-secondary` → `subagent-artifacts/subagent-secondary.json`（config/shared/tools/scripts）
- 主 Agent 融合：校验 unit_id/anchor/judgment → 回填 coverage → 合成 module-evidence/src.json → Semantic Source Review（5 条）→ report.md → insight-probes.json → gate

## Gate 结果

| check | status |
|---|---|
| evidence-plan | pass |
| parallelism-execution | pass |
| report-draft | pass |
| module-classification | pass |
| parse-quality | pass |
| reference-quality | pass |
| module-evidence-matrix | pass |
| key-unit-coverage | pass |
| core-unparsed-areas | pass |
| reference-completeness | pass |
| semantic-source-review | pass |
| report-depth | pass |
| insight-probe-process | pass |

- **allowed_to_synthesize: true**
- 失败原因：无（gate 放行）

## 覆盖摘要

| 模块 | classification | analyzed / total | 约覆盖率 |
|---|---|---:|---:|
| src | core | 159 / 264 | 60.23% |
| config | secondary | 15 / 47 | 31.91% |
| shared-components | secondary | 6 / 18 | 33.33% |
| tools | secondary | 23 / 75 | 30.67% |
| scripts | secondary | 6 / 17 | 35.29% |
| . / test-setup | excluded | — | 不进分母 |

## 产物清单

| 工件 | 状态 |
|---|---|
| doctor-report.json | 已写 |
| install-prompt.md | doctor 副产物 |
| repo-map.json | 已写 |
| repo-map.md | 已写 |
| coverage-units.json | 已写（回填 analyzed + skip_reason） |
| evidence-plan.md | 已写（mode: standard；parallelism: active） |
| module-evidence/src.json | 已写（含 semantic_reviews×5） |
| subagent-artifacts/*.json | 已写（3） |
| report.md | 已写 |
| insight-probes.json | 已写（Catalog 三类：hit/hit/miss） |
| quality-gate-report.json | 已写（放行） |
| ANALYSIS_REPORT.md | **已写**（gate 放行后） |
| UAT_EXEC_SUMMARY.md | 本文件 |

## 诚实结论

| 维度 | 结论 |
|---|---|
| **过程有效** | 是。完整执行 doctor → scan → summarize → units → evidence → report → insight-probes → gate，未跳过硬门控；未修改目标仓源码；未覆盖其他历史测试证据目录。 |
| **产品分析完整通过** | 是。`allowed_to_synthesize: true`，并已合成 `ANALYSIS_REPORT.md`。 |
| **多子代理验收** | parallelism: active，三份子代理产物 + 主 Agent 融合过程已记录于 evidence-plan。 |
| **Insight Probe** | 流程产物合法；ui_promise_runtime_path=hit、multi_source_rules=hit、config_dual_write_dead_impl=miss；miss 不挡门。 |
| **失败原因** | 无。 |

## 标签

`real-uat-regression` · `standard` · `parallelism:active` · `gate:pass` · `20260711-213622`
