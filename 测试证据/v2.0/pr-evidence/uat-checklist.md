# UAT 核对清单（agent 代跑 · 已授权）

- **uat_runner**: agent
- **uat_authorized_by**: session-user
- **acceptance_env**: local-cli + docs-only
- **日期**: 2026-07-11

## 1. 验收总判定不得把 degraded 写成多子代理完整通过

- [x] **通过**
- 文件: `测试证据/v2.0/ACCEPTANCE_RESULT.md`
- 锚点摘录:

```text
## 总判定
**部分通过：CLI/gate 工件链可运行，但报告质量与多子代理验收均未通过。**
...
- quick / standard / deep 的 Evidence Plan 均记录为 `parallelism: degraded`，由主 agent 串行生成证据，没有实际开启多个子代理执行模块深度分析。
```

## 2. RUN_LOG / COMPARISON 明确三模式 degraded、无多子代理参与

- [x] **通过**
- 文件:
  - `测试证据/v2.0/RUN_LOG.md` §「21. Issue #12 复核」
  - `测试证据/v2.0/COMPARISON_REPORT.md` §3 / §6
- 摘录（RUN_LOG）:

```text
- quick / standard / deep 的 Evidence Plan 均记录 `parallelism: degraded`。
- 三个模式均由主 agent 串行生成 ...
- 本次没有实际开启多个子代理执行模块深度分析。
```

## 3. 验收规则覆盖：分工 / 产物 / 融合；degraded ≠ 通过

- [x] **通过**
- 规则 SSOT: `docs/specs/v2.0-multi-agent-acceptance.md`
- skill 模板: `skills/repo-analyzer/SKILL.md` Phase 5–6
- 工件模板: `skills/repo-analyzer/references/evidence-first-v2.md`
- ACCEPTANCE 内嵌规则节 + 指向 SSOT

## 4. 既有 degraded 工件不会被标「完整通过 / 允许合成」

- [x] **通过（机器证据）**
- 见 `gate-recheck-summary.json` 与下表（来自**已提交** `quality-gate-report.json`，未在本步改写工件）:

| 模式 | parallelism-execution | allowed_to_synthesize | 说明 |
|---|---|---|---|
| quick | pass | false | parallelism 允许 degraded；因 parse/reference/report-depth 仍 blocked |
| standard | fail | false | 明确因 degraded / 缺 active·分工·产物·融合 |
| deep | fail | false | 同上 |

standard 失败原因（工件内原文要点）:

```text
standard 模式记录为 parallelism: degraded，不能作为多子代理执行通过。
standard 模式 Evidence Plan 必须记录 parallelism: active。
... 缺少实际子代理分工 / 每个子代理产物 / 主 agent 融合过程 ...
```

## 5. 若声称完整通过必须出示 multi-agent 证据

- [x] **通过（本 PR 未声称完整通过）**
- PR 与 ACCEPTANCE 结论均为「部分通过」；AC4 可选升级未执行、checkbox 保持 `[ ]`。

## 6. 基线 npm test / typecheck

- [x] **通过**
- 原始日志: `npm-test.log`、`typecheck.log`
- 汇总: tests 35 · pass 35 · fail 0；typecheck EXIT 0
