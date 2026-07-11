# v2.1 验收结果（repo-analyzer 重跑）

日期：2026-07-11
被测版本：`repo-analyzer@2.0.0`（分析器实现）/ 证据标签 **v2.1**
目标仓库：`/tmp/Long_screenshot_splitting_tool`
目标仓库 commit：`bdee20b8c4e4985c690a255ed09f64a3e335fd20`
证据目录：`测试证据/v2.1`
模式：standard（本轮主跑）
执行环境：本机 · Node v24.18.0 · ast-grep 0.44.1 · graphify 0.9.8 · 无 universal-ctags

## 总判定

**部分通过：CLI 工件链（doctor→scan→summarize→units→人工 Evidence/Matrix/report）已重跑；gate 未放行合成；多子代理验收未通过。**

**不是** v2.0 完整通过，也**不是** multi-agent 完整验收通过。

### 通过项

- Doctor 放行：`standard/doctor-report.json` `allowed: true`
- 确定性链路产出：`repo-map.json/md`、`coverage-units.json`（288 units，parse_rate≈48.2%）
- 人工（主 agent）写入：`evidence-plan.md`、`module-evidence/src.json`、`report.md`
- 覆盖率回填：core `src` 60% analyzed；次要模块 ≥30% 抽样
- Semantic Source Review：core 有效抽查已写入 Matrix（gate: pass）
- 报告深度：项目全景 / 核心流程 / 模块协作（含锚点）/ 改进建议等（gate: pass）
- 未解析 core 文件已在报告声明 Unsupported Area（gate: pass）
- 自动化基线（分析器仓库）：以 PR 分支 `npm test` 为准（见 PR 证据包；本目录不重复强绑）

### 未通过 / 阻塞项

| 门控 | 状态 | 说明 |
|---|---|---|
| parallelism-execution | **fail** | Evidence Plan 记录 `parallelism: degraded`，无真实多子代理分工/产物/融合 |
| parse-quality | **fail** | parse_rate 48.20% < 80%；core 未解析占比过高 |
| reference-quality | **fail** | core 单元 refs_status partial/missing 占比 100% > 80% |
| allowed_to_synthesize | **false** | 因此 **未** 生成新的 `ANALYSIS_REPORT.md`（禁止绕过 gate） |

失败 checks 列表：`['parallelism-execution', 'parse-quality', 'reference-quality']`

### 并行执行诚实声明

- 本轮 **parallelism: degraded**
- 原因：Codex 会话未派发多个 module 级 subagent；主 agent 串行完成 Plan / Matrix / report
- 按 `docs/specs/v2.0-multi-agent-acceptance.md`：**不得**计 multi-agent 完整通过

## 工件清单

```text
测试证据/v2.1/
  ACCEPTANCE_RESULT.md          ← 本文件
  RUN_LOG.md
  COMPARISON_REPORT.md
  README.md
  package/npm-pack-dry-run.txt
  standard/
    doctor-report.json
    repo-map.json
    repo-map.md
    coverage-units.json
    evidence-plan.md
    module-evidence/src.json
    report.md
    quality-gate-report.json
    （无 ANALYSIS_REPORT.md — gate 未放行）
```

## 与 v2.0 证据关系

- `测试证据/v2.0/**`：历史证据，保留不覆盖
- `测试证据/v2.1/**`：2026-07-11 **新重跑** 目录（用户要求新建 v2.1）
- 旧 `v2.0/standard/ANALYSIS_REPORT.md` **不是** 本轮产物

## 恢复「完整通过」仍需

1. 提升 parse/reference 质量或调整目标仓/枚举器，使 parse-quality 与 reference-quality 过门
2. 在支持 subagent 的运行时真正并行，写 `parallelism: active` + 分工 + 产物 + 融合
3. gate 全绿后再合成 `ANALYSIS_REPORT.md`
