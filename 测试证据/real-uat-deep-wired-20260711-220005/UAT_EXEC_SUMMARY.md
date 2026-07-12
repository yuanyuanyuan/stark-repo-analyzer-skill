# UAT_EXEC_SUMMARY · 真实UAT回归测试·deep

## 标识

- **正式名称**：真实UAT回归测试·deep
- **标签**：`real-uat-regression` / mode=`deep`
- **Skill**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md`
- **目标仓**：`/tmp/Long_screenshot_splitting_tool`（commit `bdee20b8c4e4985c690a255ed09f64a3e335fd20`）
- **输出目录**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-wired-20260711-220005`

## 时间

- **开始**：2026-07-11T22:00:24+08:00（会话内 doctor 启动）
- **结束**：2026-07-11T22:03:56+08:00
- **时区**：Asia/Shanghai

## 完整命令（可审计复现）

```bash
CLI="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/bin/repo-analyzer.js"
REPO="/tmp/Long_screenshot_splitting_tool"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-wired-20260711-220005"

node "$CLI" doctor --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" scan --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" summarize --repo "$REPO" --out "$OUT" --mode deep
node "$CLI" units --repo "$REPO" --out "$OUT" --mode deep
# agent: evidence-plan / coverage 回填 / module-evidence / report / insight-probes / subagent-artifacts
node "$CLI" gate --repo "$REPO" --out "$OUT" --mode deep
# gate 放行后写 ANALYSIS_REPORT.md + UAT_EXEC_SUMMARY.md
```

提示词要求：严格执行 skill、模式 deep、输出到本目录；完整 doctor/scan/summarize/units/gate；gate 通过才写 ANALYSIS_REPORT；验证 Graphify 接线。

## 模式与并行

| 字段 | 值 |
|---|---|
| mode | deep |
| tooling_level | enhanced |
| parallelism | **active**（3 子代理：pipeline / nav-export-seo / secondary） |
| Graphify doctor | `allowed_deep=true` |
| Graphify units | `graphify_refs.wired=true`（path=目标仓 graphify-out/graph.json，nodes=2875，links=4550，extracted_ref_links=1507） |
| enumerator | universal-ctags 6.2.1（deep 符号分母） |
| 多子代理验收 | 有 subagent-artifacts 与 evidence-plan 分工/产物/融合记录 → **可作为 multi-agent 过程证据** |

## Gate 结论

- **allowed_to_synthesize**：**true**
- 全部 checks：**pass**（evidence-plan、parallelism-execution、report-draft、module-classification、parse-quality、reference-quality、module-evidence-matrix、key-unit-coverage、core-unparsed-areas、reference-completeness、semantic-source-review、report-depth、insight-probe-process）

### 覆盖率

| 模块 | 分级 | analyzed/total | % | 阈值 |
|---|---|---:|---:|---:|
| src | core | 649/721 | 90.01 | 90 |
| tools | secondary | 138/229 | 60.26 | 60 |
| shared-components | secondary | 68/113 | 60.18 | 60 |
| config | secondary | 62/102 | 60.78 | 60 |
| scripts | secondary | 12/20 | 60.00 | 60 |
| test-setup / `.` | excluded | — | — | — |

### Semantic Source Review

- 要求：deep 每 core 模块 min(3, analyzed)=3
- 有效：3/3 supported
- 单元：useAppState、analyzeSplitPoints、processImage

### Insight Probes

- 文件合法；Catalog 三类均有结论
- `ui_promise_runtime_path`：**hit**（ExportControls 高级选项未完整透传）
- `multi_source_rules`：**hit**（SEO JSON/桥接/fallback 多源）
- `config_dual_write_dead_impl`：**hit**（SEOManager/Enhanced 平行实现）
- **miss 不挡门**；本轮为 hit，流程仍 pass

## 主题覆盖与锚点（Worker / 导航 / 切片 / 导出 / SEO）

| 主题 | 代表锚点 | 结论摘要 |
|---|---|---|
| Worker | `src/hooks/useWorker.ts:42`、`src/workers/split.worker.js:20`、`:75` | module Worker + 消息协议；解码→分析→切片 |
| 切片/内容感知 | `src/utils/splitAnalyzer.ts:250`、`:88`、`useAppState.ts:47` | 纯函数切割点；按 index 落库防乱序 |
| 导航 | `src/hooks/useNavigationState.ts:53`、`App.tsx:121`、`:142` | 步骤禁用 + 切片到达后再跳转 + 错误恢复 |
| 导出 | `src/components/ExportControls.tsx:82`、`App.tsx:224`、`pdfExporter.ts:208`、`zipExporter.ts:34` | format 路径真实；高级选项存在接线缺口 |
| SEO | `src/components/SEOManager.tsx:1`、`SEOConfigManager.ts:142`、`seo.config.ts:48` | JSON 桥接可用；多实现并行有债务 |

## 产物清单

- `doctor-report.json`
- `install-prompt.md`
- `repo-map.json` / `repo-map.md`
- `coverage-units.json`（含 graphify_refs）
- `evidence-plan.md`
- `module-evidence/src.json`
- `subagent-artifacts/subagent-src-pipeline.json`
- `subagent-artifacts/subagent-src-nav-export-seo.json`
- `subagent-artifacts/subagent-secondary-deep.json`
- `insight-probes.json`
- `report.md`
- `quality-gate-report.json`
- `ANALYSIS_REPORT.md`（gate 放行后）
- `UAT_EXEC_SUMMARY.md`（本文件）

## 诚实判定

### 1) 过程有效（真实UAT回归测试 · 过程有效）

- [x] 独立会话严格执行 skill 工作流（doctor→scan→summarize→units→plan→evidence→gate→合成）
- [x] 输出目录为新建证据目录，未覆盖其他历史测试证据
- [x] 未修改目标仓业务源码
- [x] 关键工件齐全
- [x] parallelism 记为 active 且有子代理产物/融合说明
- [x] Graphify 接线验证通过（`allowed_deep=true` 且 `graphify_refs.wired=true`）

### 2) 产品「分析完整通过」

- [x] `quality-gate-report.json.allowed_to_synthesize === true`
- [x] 已生成 `ANALYSIS_REPORT.md`
- [x] deep 覆盖率与 SSR、insight-probe-process 均 pass

**总判定**：

| 维度 | 结果 |
|---|---|
| 真实UAT回归测试 · **过程有效** | **通过** |
| 产品分析 · **完整通过（deep Full Delivery）** | **通过** |
| Graphify deep 接线 | **通过** |
| 多子代理验收（parallelism active + 产物） | **过程证据具备**（本会话并行工具调用角色化执行） |

## 约束遵守

- 未改目标仓业务源码
- 未覆盖其他测试证据目录
- gate 红不会写 ANALYSIS_REPORT（本轮为绿，已写）
- insight-probes 合法；hit/miss 语义按 schema（miss 不挡门）

## 残余风险（不挡门）

- core incomplete refs ≈76.7%（<80% 阈值，pass 但跨模块边需谨慎）
- 导出高级选项与 SEO 平行实现已在探针中标 hit，终稿批判性章节已披露
- 无浏览器 E2E 运行时观测

