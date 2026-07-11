## 结果

已按 `skills/repo-analyzer/SKILL.md` v2 强制工作流分析 `/tmp/Long_screenshot_splitting_tool`，工件在：

[`测试证据/v2.1-unparsed-read`](/Users/chuzu/projests/stark-repo-analyzer-skill/spec-unparsed-core-unsupported-rg-find-wc/测试证据/v2.1-unparsed-read)

| 项 | 值 |
|---|---|
| 模式 | standard |
| parallelism | **degraded**（主 Agent 串行，subagent=0） |
| parse_rate | ≈48.2%（未因补读抬高） |
| core unparsed | 45；已做 Unparsed File Read Pass（7 个主路径） |
| Gate | **`allowed_to_synthesize: false`** |
| ANALYSIS_REPORT | **未写**（契约要求） |

## 通过 / 失败

**通过的关键门**：doctor、units 覆盖（src≈62%）、matrix、semantic-source-review、**unparsed-manual-review**、core-unparsed-areas、report-depth。

**失败原因**：
1. `parallelism-execution`：standard 需要 `active` 多子代理，本轮如实 degraded  
2. `parse-quality`：parse_rate / core unparsed 占比不达标  
3. `reference-quality`：core refs partial/missing 过高  

## 产物

`doctor-report.json`、`repo-map.*`、`coverage-units.json`、`evidence-plan.md`、`module-evidence/src.json`、`unparsed-file-reviews/*` + `unparsed-file-reviews.json`、`report.md`、`quality-gate-report.json`、中文 [`UAT_EXEC_SUMMARY.md`](/Users/chuzu/projests/stark-repo-analyzer-skill/spec-unparsed-core-unsupported-rg-find-wc/测试证据/v2.1-unparsed-read/UAT_EXEC_SUMMARY.md)

未改目标仓源码；未覆盖其他历史证据目录。