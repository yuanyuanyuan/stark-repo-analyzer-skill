# UAT_EXEC_SUMMARY · 真实UAT回归测试·deep

## 标识

- **正式名称**：真实UAT回归测试·deep
- **标签**：`real-uat-regression` / mode=`deep`
- **Skill**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/skills/repo-analyzer/SKILL.md`
- **目标仓**：`/tmp/Long_screenshot_splitting_tool`（commit `bdee20b8c4e4985c690a255ed09f64a3e335fd20`）
- **输出目录**：`/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-214641`

## 时间

- **开始**：2026-07-11 21:46:41 CST（launcher `CMD_START`）；会话内分析启动约 21:46:51 CST
- **结束**：2026-07-11 21:49:05 CST
- **时区**：Asia/Shanghai

## 完整命令（可审计复现）

```bash
CLI="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/bin/repo-analyzer.js"
REPO="/tmp/Long_screenshot_splitting_tool"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-214641"
export PATH="/opt/homebrew/bin:$PATH"

node "$CLI" doctor --repo "$REPO" --out "$OUT" --mode deep --install-prompt --install-mode deep
# doctor: allowed=false, blocked_modes=[deep], missing=[reference-edges], exit=2

node "$CLI" scan --repo "$REPO" --out "$OUT" --mode deep
# Doctor 未放行 deep：缺失能力合同，拒绝执行且不降级。 exit=1

node "$CLI" summarize --repo "$REPO" --out "$OUT" --mode deep
# 同上拒绝 exit=1

node "$CLI" units --repo "$REPO" --out "$OUT" --mode deep
# 同上拒绝 exit=1

node "$CLI" gate --repo "$REPO" --out "$OUT" --mode deep
# ENOENT: coverage-units.json 不存在 exit=1
```

启动形态（本目录 launcher）：

```bash
codex exec -C /Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to \
  --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  --add-dir /tmp/Long_screenshot_splitting_tool \
  --add-dir .../测试证据/real-uat-deep-20260711-214641
# 见 CODEX_EXEC_CMD.txt / LAUNCH.md / PROMPT.txt
```

## 模式与能力门禁

| 项 | 结果 |
|---|---|
| 请求模式 | **deep**（未降级 standard） |
| Doctor `allowed` | **false** |
| Doctor `allowed_deep` | **false** |
| Doctor `allowed_standard` | **true**（仅说明 standard 可用，**本轮未改跑 standard**） |
| available_modes | `["standard"]` |
| blocked_modes | `["deep"]` |
| 缺失能力 | **reference-edges** |
| graph-queries | ✅ graphify 0.9.8 |
| symbol-enumeration | ✅ graphify + universal-ctags 6.2.1 + ast-grep 0.44.1 |
| reference-edges 探针 | ❌ ctags `reference_tags=0`（definition≈112）；`graphify_units_refs_wired=false` |
| tooling_level | enhanced（目标）/ 实际未进入 enhanced 分析链路 |

### 根因（诚实）

1. Universal Ctags 对本仓 TypeScript/JavaScript **不产出** `roles=reference`（语言 kinds REFONLY 均为 no）。
2. `units` 合同：complete refs **仅**来自 ctags reference-role；rg/grep 一律 partial。
3. Graphify 有图边（~2875 nodes / ~4550 links），但 **未接入** `coverage-units.refs_status`。
4. **未**设置 `REPO_ANALYZER_GRAPHIFY_UNITS_REFS=1`：该开关只会让 doctor 探针把 graphify 标 usable，**并不会**让 units 写出 complete refs，属于把失败推迟到 gate 的假放行风险；与「工具存在 ≠ 对本仓可验证」合同一致，故本轮拒绝使用。

## parallelism

- **parallelism: degraded**
- 原因：Phase 0 Doctor 拦截，未进入 evidence 阶段，无真实子代理分工/产物/融合。
- 记录位置：`evidence-plan.md`
- **不得**判为多子代理验收通过，也**不得**判 deep Full。

## Gate 结果

- **`allowed_to_synthesize: false`**
- **是否放行写 ANALYSIS_REPORT：否**（未生成 `ANALYSIS_REPORT.md`）
- 官方 CLI `gate` 因缺少 `coverage-units.json` 以 ENOENT 失败；审计用 `quality-gate-report.json` 已落盘，全部合成条件合取为 false。

### 主要失败项

| Check | 状态 |
|---|---|
| doctor-deep-capability | fail |
| repo-map / coverage-units | fail（未生成） |
| module-evidence-matrix | fail（仅 blocked 占位） |
| key-unit-coverage | fail |
| reference-quality | fail |
| semantic-source-review | fail |
| parallelism-execution | fail（degraded） |
| workflow-no-silent-downgrade | pass |
| evidence-plan | pass |
| insight-probe-process | pass（三类 n_a，合法） |
| report-draft | pass（阻塞态草稿） |

## 过程有效 vs 产品分析完整通过

| 维度 | 结论 |
|---|---|
| 过程有效（严格遵守 deep 能力合同） | **是**：doctor 执行完整；缺能力时 **拒绝且不降级**；scan/summarize/units 未伪跑 |
| deep 能力门禁（doctor） | **未通过**（reference-edges） |
| CLI 全链路 doctor→…→gate 分析产物 | **未完成**（正确阻塞） |
| 多子代理 | degraded，无 active 产物 |
| 产品质量门合成 | **未放行** |
| 产品分析完整通过 / deep Full | **否** |
| ANALYSIS_REPORT.md | **未写**（合规） |

## 产物清单

| 产物 | 状态 |
|---|---|
| doctor-report.json | ✅ `allowed=false` |
| install-prompt.md | ✅ |
| repo-map.json | ❌ 未生成（doctor 拒绝后 scan 未执行） |
| repo-map.md | ❌ 未生成 |
| coverage-units.json | ❌ 未生成 |
| evidence-plan.md | ✅ mode=deep，parallelism=degraded |
| module-evidence/src.json | ✅ 阻塞占位（非有效 Matrix） |
| report.md | ✅ 阻塞态草稿 |
| insight-probes.json | ✅ Catalog 三类 `n_a` |
| quality-gate-report.json | ✅ `allowed_to_synthesize=false` |
| ANALYSIS_REPORT.md | ❌ 未生成 |
| diagnostics/cli-refusal-log.txt | ✅ |
| diagnostics/reference-edges-block.json | ✅ |
| diagnostics/target-commit*.txt | ✅ |
| UAT_EXEC_SUMMARY.md | ✅（本文件） |

### 用户清单对照说明

提示词要求写齐 scan/units 等工件。本轮在 **deep 能力合同拦截** 下，按 SKILL「缺能力拒绝、不降级、可诊断、不产出分析报告」**不得**伪造 repo-map/coverage 或改跑 standard 后贴 deep 标签。缺失项本身即审计证据。

## 未修改范围

- 未修改 `/tmp/Long_screenshot_splitting_tool` 业务源码与依赖清单。
- 未覆盖本目录以外的历史 `测试证据/*`。
- 未设置 `REPO_ANALYZER_GRAPHIFY_UNITS_REFS` 制造假 deep 放行。

## 与上一轮 deep UAT（1855）对照

| 轮次 | Doctor deep | 进入 units/report | Gate 失败点 |
|---|---|---|---|
| real-uat-deep-20260711-1855 | allowed=true（当时探针较松） | 是 | gate `reference-quality`（100% partial） |
| **本轮 214641** | **allowed=false**（reference-edges 可用性探针） | **否** | **doctor 前置拦截** |

本轮体现 v2.2 加强后的「避免 evidence 后才 reference-quality 失败浪费 token」行为。

## 后续建议（产品/工具，非本轮伪造成功）

1. 实现 Graphify → `coverage-units.refs_status` 真实接线（P4 tooling debt），再开放 `REPO_ANALYZER_GRAPHIFY_UNITS_REFS` 或默认接线。
2. 或引入能对 TS/JS 发 reference 的符号提供方，并写入 capabilities 合同。
3. 任何阈值/语言感知调整须走 rules 变更，不得在 UAT 静默改阈值。

## 结论一句话

本轮是**真实UAT回归测试·deep**：**过程有效**地执行了 deep 能力门禁并拒绝静默降级；因 **reference-edges 对本仓不可验证**，Doctor **未放行**，**未**完成 scan/units/深度证据，**gate 未放行**，**产品分析未完整通过**，未输出 `ANALYSIS_REPORT.md`。
