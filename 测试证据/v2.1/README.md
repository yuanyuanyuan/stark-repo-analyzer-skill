# 测试证据 v2.1

2026-07-11 新建。含两轮 standard 分析证据：

| 目录 | 并行 | 读什么 |
|---|---|---|
| [`standard/`](./standard/) | degraded（串行） | 首轮重跑 |
| [`standard-multiagent/`](./standard-multiagent/) | **active（真多进程子代理）** | 第二轮 multi-agent |
| [ACCEPTANCE_RESULT.md](./ACCEPTANCE_RESULT.md) | — | 串行轮总判定 |
| [ACCEPTANCE_RESULT_MULTIAGENT.md](./ACCEPTANCE_RESULT_MULTIAGENT.md) | — | multi-agent 轮总判定 |
| [RUN_LOG.md](./RUN_LOG.md) | — | 全过程命令 |

## multi-agent 产物入口

- `standard-multiagent/subagent-artifacts/subagent-src-state.json`
- `standard-multiagent/subagent-artifacts/subagent-src-export.json`
- `standard-multiagent/subagent-artifacts/subagent-secondary.json`
- `standard-multiagent/subagent-artifacts/main-agent-fusion.json`
- `standard-multiagent/quality-gate-report.json`（**parallelism-execution: pass**）

两轮均 **无** 本轮 `ANALYSIS_REPORT.md`（parse/refs 未过门，禁止绕过）。
