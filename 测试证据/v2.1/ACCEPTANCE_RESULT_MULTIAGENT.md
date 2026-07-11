# v2.1 multi-agent 轮验收结果

日期：2026-07-11  
证据目录：`测试证据/v2.1/standard-multiagent`  
对照串行轮：`测试证据/v2.1/standard`（parallelism: degraded）  
目标仓库：`/tmp/Long_screenshot_splitting_tool` @ `bdee20b8c4e4985c690a255ed09f64a3e335fd20`

## 总判定

**部分通过：真实 multi-agent 并行执行已发生且 gate 的 parallelism-execution 通过；因 parse-quality / reference-quality 未达标，仍不得合成 ANALYSIS_REPORT，也不得声称 v2 完整通过。**

| 维度 | 结果 |
|---|---|
| 多子代理执行（本票 AC 核心） | **通过**（parallelism: active + 分工 + 产物 + 主 agent 融合） |
| CLI 确定性链路 | 通过（doctor 绑定 + 继承同 commit units/map） |
| 质量门合成 | **未通过**（`allowed_to_synthesize: false`） |
| 最终 ANALYSIS_REPORT | **未生成**（正确：不绕过 gate） |

## multi-agent 证据（可逐项打开）

| 子代理 | 日志 | 产物 |
|---|---|---|
| subagent-src-state | `standard-multiagent/logs/subagent-src-state.txt` | `subagent-artifacts/subagent-src-state.json` |
| subagent-src-export | `standard-multiagent/logs/subagent-src-export.txt` | `subagent-artifacts/subagent-src-export.json` |
| subagent-secondary | `standard-multiagent/logs/subagent-secondary.txt` | `subagent-artifacts/subagent-secondary.json` |
| 主 agent 融合 | — | `subagent-artifacts/main-agent-fusion.json` |

并行方式：同一时刻后台启动 3 个 Python worker 进程（PID 记录在 RUN_LOG），`wait` 后全部 exit 0。

## Gate 摘要

- **PASS** parallelism-execution（相对 degraded 轮的关键差异）
- **PASS** evidence-plan / matrix / coverage / report-depth / semantic-source-review / core-unparsed-areas …
- **FAIL** parse-quality（parse_rate ≈ 48.2%）
- **FAIL** reference-quality（core refs partial/missing 100%）

## 与串行 degraded 轮对比

| 项 | standard（degraded） | standard-multiagent（active） |
|---|---|---|
| parallelism-execution | fail | **pass** |
| 子代理产物目录 | 无 | **有** `subagent-artifacts/` |
| parse/reference | fail | fail（环境/目标仓限制，与并行无关） |
| allowed_to_synthesize | false | false |

## 结论一句话

**真 multi-agent 再跑一轮已经做到，并且机器门控承认 parallelism；完整通过仍被解析质量与引用质量挡住。**
