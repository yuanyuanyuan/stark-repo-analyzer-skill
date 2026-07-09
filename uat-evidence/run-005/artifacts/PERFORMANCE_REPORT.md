# 性能诊断报告

- total_elapsed_seconds: 415.091
- agent_mode: codex
- agent_attempt_count: 2
- agent_total_elapsed_seconds: 400.419
- agent_timeout: disabled
- agent_timeout_seconds: 0
- slowest_stage: agent-modules-batch
- slowest_agent_run_id: modules-batch

## 慢因结论

本次慢点应优先从 agent 子进程启动、模型推理固定成本和子会话数量定位；默认 timeout 已关闭，不能把限时当成根因修复。

## 阶段耗时 Top20

| 阶段 | 秒 | 状态 |
|---|---:|---|
| agent-modules-batch | 365.253 | PASS |
| agent-cross-ref-review | 35.176 | PASS |
| repomix-slices | 13.181 | PASS |
| checkout-target | 1.332 | PASS |
| render-reports | 0.053 | PASS |
| write-meta | 0.042 | PASS |
| coverage-initial | 0.032 | PASS |
| module-drafts | 0.015 | PASS |
| write-index-and-config | 0.002 | PASS |
| scan-files | 0.001 | PASS |
| classify-repo | 0.001 | PASS |
| cross-ref-deterministic-initial | 0.001 | PASS |
| cross-ref-deterministic-after-agent | 0.001 | PASS |
| prepare-output | 0.000 | PASS |
| agent-init | 0.000 | PASS |
| agent-cross-ref-repair | 0.000 | PASS |
| state-report | 0.000 | PASS |
| sla-report | 0.000 | PASS |

## Agent attempt 耗时 Top20

| run_id | attempt | command | 秒 | timed_out | cwd |
|---|---:|---|---:|---|---|
| modules-batch | 1 | codex exec | 365.246 | False | `/Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts` |
| cross-ref-review | 1 | codex exec | 35.173 | False | `/Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts` |
