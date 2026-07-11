# UAT_EXEC_SUMMARY · 真实UAT回归测试·deep

## 标识

- **正式名称**：真实UAT回归测试·deep  
- **标签**：`real-uat-regression` / mode=`deep`  
- **Skill**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md`  
- **目标仓**：`/tmp/Long_screenshot_splitting_tool`（commit `bdee20b8c4e4985c690a255ed09f64a3e335fd20`）  
- **输出目录**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-1855`  

## 时间

- **开始**：2026-07-11 19:01:13 CST（会话内执行；LAUNCH 记录 launcher started 2026-07-11T18:55:09+08:00）  
- **结束**：2026-07-11 19:07:12 CST  
- **时区**：Asia/Shanghai  

## 完整命令（可审计复现）

```bash
# CLI 入口
CLI="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/bin/repo-analyzer.js"
REPO="/tmp/Long_screenshot_splitting_tool"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-1855"
export PATH="/opt/homebrew/bin:$PATH"   # 使 Universal Ctags 优先于系统 ctags

node "$CLI" doctor --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" scan --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" summarize --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" units --repo "$REPO" --out "$OUT" --mode deep
# Agent：evidence-plan / module-evidence / coverage 回填 / report / subagent-artifacts
node "$CLI" gate --repo "$REPO" --out "$OUT" --mode deep
```

辅助（未改源码业务逻辑；生成分析用图）：

```bash
# 环境能力补齐（分析主机工具，非目标仓依赖）
brew install universal-ctags

# deep graph provider：在目标仓生成 graphify-out（AST-only）
cd /tmp/Long_screenshot_splitting_tool && graphify update . --no-cluster
```

本轮由独立 `codex exec` 提示词驱动，要求严格执行 skill，mode 固定 deep。

## 模式与能力门禁

| 项 | 结果 |
|---|---|
| 请求模式 | **deep**（未降级 standard） |
| Doctor `allowed` | **true** |
| Doctor `allowed_deep` | **true** |
| 能力 | graph-queries ✅ graphify；symbol-enumeration ✅ graphify+ctags+ast-grep；reference-edges ✅（doctor 层 graphify 宣称） |
| units enumerator | **universal-ctags 6.2.1**（优先 concrete symbol provider） |
| parse_rate | **1.0**（139/139 source files） |
| tooling_level | enhanced |

说明：首次仅有 ast-grep 时 deep units parse_rate≈48%（tsx 模式覆盖不足）。按 install-prompt 精神在**分析主机**安装 Universal Ctags 后重跑 doctor/units，parse-quality 恢复。**未**修改被分析仓库源码与依赖清单。

## parallelism

- **parallelism: active**  
- 子代理 3 个（真实并行角色产物落盘）：  
  1. `subagent-src-pipeline` → `subagent-artifacts/subagent-src-pipeline.json`  
  2. `subagent-src-export-ui` → `subagent-artifacts/subagent-src-export-ui.json`  
  3. `subagent-secondary-deep` → `subagent-artifacts/subagent-secondary-deep.json`  
- 主 Agent 融合：回填 `coverage-units.json`、合成 `module-evidence/src.json`、Semantic Source Review×3、撰写 `report.md`、执行 gate。  

## 覆盖回填（gate 机械）

- core `src`：约 **90.01%** analyzed（649/721）  
- secondary：tools/shared-components/config/scripts 均 **≥60%**  
- excluded：`test-setup`、`.` 不计入硬门槛  
- Semantic Source Review：3 条，verdict=supported  

## Gate 结果

- **`allowed_to_synthesize: false`**  
- **是否放行写 ANALYSIS_REPORT：否**（未生成 `ANALYSIS_REPORT.md`，不伪造通过）  

### 检查项摘要

| Check | 状态 |
|---|---|
| evidence-plan | pass |
| parallelism-execution | pass |
| report-draft | pass |
| module-classification | pass |
| parse-quality | pass |
| **reference-quality** | **fail** |
| module-evidence-matrix | pass |
| key-unit-coverage | pass |
| core-unparsed-areas | pass |
| reference-completeness | pass |
| semantic-source-review | pass |
| report-depth | pass |

### 失败原因（根因）

**reference-quality**：deep 要求 core 单元 `refs_status` 为 partial/missing 的占比 ≤ 80%，实测 **100%**。

根因（诚实、可复核）：

1. `units` 在 universal-ctags 路径下仅当 ctags 产出 `roles` 含 `reference` 时标记 `refs_status=complete`；  
2. Universal Ctags 对 **TypeScript/JavaScript** 未对本仓产出可用的 reference-role 标签（抽样 `refs=0`）；  
3. 回退的 `rg` 文本引用一律记为 **partial**；  
4. Graphify 虽有 EXTRACTED 边（~4550），但 **未接线**到 `coverage-units.json` 的 `refs_status` 字段。  

**禁止项遵守**：未伪造 `refs_status=complete` 以骗过 gate。

诊断工件：`diagnostics/reference-quality-block.json`。

## 过程有效 vs 产品分析完整通过

| 维度 | 结论 |
|---|---|
| 过程有效（CLI 工作流） | **是**：doctor→scan→summarize→units→plan→evidence→report→gate 完整执行；mode=deep 未降级 |
| deep 能力门禁（doctor） | **通过** |
| 多子代理记录 | **active** 且有产物/融合记录（机械 parallelism-execution pass） |
| 产品质量门（gate 合成） | **未通过**（reference-quality） |
| 产品分析完整通过 | **否** |
| ANALYSIS_REPORT.md | **未写**（合规） |

## 产物清单

| 产物 | 状态 |
|---|---|
| doctor-report.json | ✅ |
| install-prompt.md | ✅（doctor 附带） |
| repo-map.json | ✅ |
| repo-map.md | ✅ |
| coverage-units.json | ✅（deep / ctags / 回填完成） |
| evidence-plan.md | ✅（mode: deep，parallelism: active） |
| module-evidence/src.json | ✅ |
| subagent-artifacts/* | ✅ ×3 |
| report.md | ✅（质量门前草稿） |
| quality-gate-report.json | ✅ `allowed_to_synthesize=false` |
| ANALYSIS_REPORT.md | ❌ 未生成（gate 未放行） |
| diagnostics/* | ✅ |
| UAT_EXEC_SUMMARY.md | ✅（本文件） |

## 未修改范围

- 未修改 `/tmp/Long_screenshot_splitting_tool` 业务源码与 package 依赖清单。  
- 未覆盖本目录以外的历史 `测试证据/*`。  
- 目标仓 `graphify-out/` 为 AST 图分析工件（非业务源码）。  

## 后续建议（产品/工具，非本轮伪造成功）

1. 在 `repo-analyzer units` deep 路径把 Graphify reference/call edges 映射为 `refs_status=complete|partial` 的可审计规则；或  
2. 引入能对 TS/JS 发 reference 的符号提供方，并纳入 capabilities 合同；或  
3. 调整 deep `maxCoreIncompleteReferenceRate` 的语言感知阈值并在 rules 中明示——须走规则变更，不得在 UAT 中静默改阈值。  

## 结论一句话

本轮是**真实UAT回归测试·deep**：工作流与 doctor 能力门禁通过，证据与报告草稿齐备，但因 TS/JS 引用边无法达到 deep reference-quality 机械阈值，**gate 未放行**，**产品分析未完整通过**，未输出 `ANALYSIS_REPORT.md`。
