# UAT 执行摘要 · v2.1-unparsed-read

## 基本信息

| 项 | 值 |
|---|---|
| 目标仓库 | `/tmp/Long_screenshot_splitting_tool` |
| 目标 commit | `bdee20b8c4e4985c690a255ed09f64a3e335fd20` |
| Skill | `skills/repo-analyzer/SKILL.md`（Evidence-First v2） |
| 输出目录 | `测试证据/v2.1-unparsed-read` |
| 模式 | **standard** |
| 并行 | **parallelism: degraded**（主 Agent 串行，subagent=0） |
| Unparsed 补读并行 | **unparsed_read_pass.parallelism: degraded** |
| 开始时间 | 2026-07-11 18:05:33 CST |
| 结束时间 | 2026-07-11 18:08:20 CST |
| Gate 是否放行 | **否**（`allowed_to_synthesize: false`） |
| 是否写入 ANALYSIS_REPORT | **否**（按契约：gate 未通过不写） |

## 执行命令

```bash
# 工作目录
cd /Users/chuzu/projests/stark-repo-analyzer-skill/spec-unparsed-core-unsupported-rg-find-wc

REPO=/tmp/Long_screenshot_splitting_tool
WORK=$(pwd)/测试证据/v2.1-unparsed-read
CLI=node $(pwd)/bin/repo-analyzer.js

# Phase 0-2 确定性 CLI
$CLI doctor --repo "$REPO" --out "$WORK"
$CLI scan --repo "$REPO" --out "$WORK"
$CLI summarize --repo "$REPO" --out "$WORK"
$CLI units --repo "$REPO" --out "$WORK"

# Phase 3-8 人工/Agent：文档研读、evidence-plan、Unparsed File Read Pass、
# coverage 回填、module-evidence、report.md（未改目标仓源码）

# Phase 9 质量门
$CLI gate --repo "$REPO" --out "$WORK" --mode standard
```

用户触发提示词要求：严格执行 skill 分析目标仓，工件输出到本目录（真实 UAT 回归约束）。

## Doctor / Units 快照

- Doctor：`allowed: true`（git / rg / ast-grep / TS+JS 语言支持 / 输出可写 / graphify 可选通过）
- Units：`units=288`，`parse_rate≈48.20%`（主语言 TypeScript ≈42.73%）
- Core 模块：`src`（classification=core）
- Core unparsed 文件数：**45**（components/App/main/SEO 等 TSX 为主）
- 关键单元覆盖回填后：src **118/190 ≈ 62.1%** analyzed；次要模块均 ≥30% 抽样

## Unparsed File Read Pass（core unparsed 非空 → 已执行）

| 项 | 说明 |
|---|---|
| 是否执行 | **是**（强制补读，非仅列 Unsupported） |
| 并行 | degraded（主 Agent 串行） |
| 工具 | rg / read / wc（只读） |
| 高影响补读 | 7 个主路径文件 |
| 产物 | `unparsed-file-reviews/*.md`、`unparsed-file-reviews.json`、`module-evidence/src.json#unparsed_manual_reads` |
| 语义 | confidence=`manual-read`；**未**清除 unparsed；**未**提升 parse_rate；**未**标 analyzed unit |
| 报告锚点 | report 对 App/FileUploader/ExportControls 等写 manual-read 锚点，并仍声明 Unsupported Area |

补读文件列表：

1. `src/main.tsx`
2. `src/App.tsx`
3. `src/components/FileUploader.tsx`
4. `src/components/ExportControls.tsx`
5. `src/components/ScreenshotSplitter.tsx`
6. `src/components/ImagePreview.tsx`
7. `src/components/Navigation.tsx`

其余 SEO/debug/example 等 core unparsed 在预算内 skip，仍出现在 Unsupported Area 完整列表。

## 质量门结果

`allowed_to_synthesize: false`

| 检查项 | 状态 | 说明 |
|---|---|---|
| evidence-plan | pass | |
| parallelism-execution | **fail** | standard 要求 `parallelism: active` 与真实子代理分工；本轮如实 degraded |
| report-draft | pass | |
| module-classification | pass | |
| parse-quality | **fail** | parse_rate 48.20% < 80%；主语言 42.73% < 80%；core unparsed 占比 53.57% > 20% |
| reference-quality | **fail** | core 单元 refs partial/missing = 100% > 80% 阈值（enumerator/rg 启发式限制） |
| module-evidence-matrix | pass | |
| key-unit-coverage | pass | core/secondary 覆盖达标 |
| core-unparsed-areas | pass | 报告声明全部 core unparsed |
| **unparsed-manual-review** | **pass** | 补读记录齐全（本轮验证重点） |
| reference-completeness | pass | |
| semantic-source-review | pass | 3 条 supported |
| report-depth | pass | |

### 失败原因（汇总）

1. **parallelism-execution**：standard 模式下 Evidence Plan 记录 `parallelism: degraded`，无真实多子代理执行；按门禁不能作为多子代理完整通过。
2. **parse-quality**：目标仓大量 TSX 未被 ast-grep 解析，全局/主语言 parse_rate 与 core unparsed 占比均不达标。**补读不能也不应伪装抬高 parse_rate**。
3. **reference-quality**：core 单元引用完整性启发式结果全为 partial/missing，超过 80% 阈值。

因此 **不得** 合成 `ANALYSIS_REPORT.md`。CLI/工件链与 unparsed 补读门（`unparsed-manual-review`）本身已跑通。

## 产物清单

| 产物 | 路径 | 说明 |
|---|---|---|
| doctor-report.json | 本目录 | Doctor 放行 |
| repo-map.json / repo-map.md | 本目录 | 确定性仓库地图 |
| coverage-units.json | 本目录 | 分母 + 回填 analyzed |
| evidence-plan.md | 本目录 | 含 parallelism: degraded + Unparsed File Read Pass |
| module-evidence/src.json | module-evidence/ | Evidence Matrix + semantic_reviews + unparsed_manual_reads |
| unparsed-file-reviews/* | unparsed-file-reviews/ | 7 份补读笔记 |
| unparsed-file-reviews.json | 本目录 | 补读汇总 |
| report.md | 本目录 | 叙事草稿（含 manual-read 锚点） |
| quality-gate-report.json | 本目录 | Gate 未放行 |
| UAT_EXEC_SUMMARY.md | 本目录 | 本文件 |
| ANALYSIS_REPORT.md | — | **未生成**（gate 未放行） |
| subagent-artifacts/README.md | subagent-artifacts/ | 说明无真实 subagent |

## 合规对照（用户约束）

1. 未跳过 doctor/units/gate：已执行。
2. 可审计工件已写入指定目录：齐全；ANALYSIS_REPORT 因 gate 失败按契约省略。
3. Evidence Plan 如实记录 `parallelism: degraded` 及无子代理融合。
4. core unparsed 非空 → 已执行 Unparsed File Read Pass 并落盘 reviews / matrix；报告含 manual-read 锚点；未伪装 parse_rate 提升。
5. 本摘要中文记录命令、时间、模式、parallelism、gate、产物、补读与失败原因。
6. 未修改被分析仓库源码；未覆盖其他历史测试证据目录。

## 结论

本轮作为 **真实 UAT 回归**：v2 强制工作流与 **unparsed-manual-review** 质量项已验证通过；整体 `allowed_to_synthesize` 因 parse-quality / reference-quality / parallelism-execution 失败为 **false**。这与目标仓低 parse_rate 及本运行时无多子代理的客观条件一致，符合“诚实降级 + 强制补读”的产品契约。
