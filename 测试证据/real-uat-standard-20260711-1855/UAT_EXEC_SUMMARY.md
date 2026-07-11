# UAT 执行摘要 · 真实UAT回归测试·standard

## 基本信息

| 项 | 值 |
|---|---|
| 正式名称 | **真实UAT回归测试·standard**（标签：`real-uat-regression`） |
| 技能 | `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md` |
| 目标仓 | `/tmp/Long_screenshot_splitting_tool` @ `bdee20b` |
| 输出目录 | `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-standard-20260711-1855` |
| 模式 | **standard**（默认可移植路径；禁止 Graphify / Universal Ctags / ast-grep） |
| parallelism | **active**（3 子代理：src-state / src-export / secondary） |
| 开始时间 | 2026-07-11 18:57:40 CST |
| 结束时间 | 2026-07-11 19:00:42 CST |
| Doctor | 放行（`allowed: true`，mode=standard） |
| Gate | **放行**（`allowed_to_synthesize: true`，12/12 checks pass） |

## 完整命令

```bash
# 工作目录
cd /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to

REPO="/tmp/Long_screenshot_splitting_tool"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-standard-20260711-1855"

# Phase 0–2：确定性 CLI（不得跳过）
node bin/repo-analyzer.js doctor --repo "$REPO" --out "$OUT" --mode standard
node bin/repo-analyzer.js scan --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js summarize --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js units --repo "$REPO" --out "$OUT"

# Phase 3–8：Agent 证据与叙事（本会话执行）
# - 并行 3 子代理读源码 → subagent-artifacts/*.json
# - 回填 coverage-units.json；写 evidence-plan.md、module-evidence/src.json、report.md

# Phase 9：质量门
node bin/repo-analyzer.js gate --repo "$REPO" --out "$OUT" --mode standard

# Phase 10：gate 放行后合成
# → ANALYSIS_REPORT.md
```

用户侧触发命令（与本轮一致）：

```bash
严格执行 /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md
分析 /tmp/Long_screenshot_splitting_tool
输出报告到 /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-standard-20260711-1855
# 模式必须为 standard；禁止 Graphify/Ctags/ast-grep
```

## 模式与并行

- **mode = standard**
- **tooling_level = baseline**（enumerator: `heuristic-text` / `standard-baseline`）
- **parallelism = active**
- 子代理分工与产物：
  - `subagent-src-state` → `subagent-artifacts/subagent-src-state.json`（会话+Worker 主链）
  - `subagent-src-export` → `subagent-artifacts/subagent-src-export.json`（上传/导出）
  - `subagent-secondary` → `subagent-artifacts/subagent-secondary.json`（config/shared/tools/scripts）
- 主 Agent 融合：合并 coverage 回填 → `module-evidence/src.json` → Semantic Source Review（5 条）→ `report.md` → gate

## Gate 结果

- **是否放行：是**（`allowed_to_synthesize: true`）
- 检查项：evidence-plan / parallelism-execution / report-draft / module-classification / parse-quality / reference-quality / module-evidence-matrix / key-unit-coverage / core-unparsed-areas / reference-completeness / semantic-source-review / report-depth —— **全部 pass**
- 覆盖率：core `src` 60.23%（159/264）；secondary tools 30.67%、shared-components 33.33%、config 31.91%、scripts 35.29%
- parse_rate：1.0（standard 文件级启发式）
- 失败原因：**无**（gate 放行）

## 产物清单

| 工件 | 状态 |
|---|---|
| `doctor-report.json` | 有 |
| `repo-map.json` | 有 |
| `repo-map.md` | 有 |
| `coverage-units.json` | 有（已回填 analyzed/skip_reason） |
| `evidence-plan.md` | 有（mode: standard，parallelism: active） |
| `module-evidence/src.json` | 有（含 semantic_reviews×5） |
| `subagent-artifacts/*.json` | 有（3 份） |
| `report.md` | 有 |
| `quality-gate-report.json` | 有（allowed=true） |
| `ANALYSIS_REPORT.md` | 有（gate 放行后写入） |
| `UAT_EXEC_SUMMARY.md` | 本文件 |
| `install-prompt.md` | doctor 附带生成 |

## 诚实判定

| 维度 | 结论 |
|---|---|
| **过程有效** | **是**。完整执行 doctor → scan → summarize → units → evidence/plan/matrix/report → gate → 最终合成；未改目标仓源码；未覆盖其他历史测试证据目录。 |
| **产品分析完整通过** | **是**（本轮）。gate `allowed_to_synthesize: true`，已生成 `ANALYSIS_REPORT.md`。 |
| **多子代理验收** | **是（active）**。Evidence Plan 与 subagent-artifacts 记录真实并行分工/产物/融合，非 degraded。 |
| **限制披露** | standard 引用为启发式 partial/missing；不对 deep 级调用图完整性作伪称。 |

## 失败原因

无（本轮 gate 放行，无阻断失败）。

中间曾出现 `report-depth` 失败（章节标题下被 H3 截断导致「设计权衡/风险或限制/具体改进建议」正文不足），已在写 `ANALYSIS_REPORT.md` 前修复 `report.md` 并重跑 gate 通过。

---

本轮明确标识：**真实UAT回归测试·standard**。
