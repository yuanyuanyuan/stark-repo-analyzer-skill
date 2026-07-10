## What to build

修正 v2.0 测试验收口径：当前 `测试证据/v2.0` 的 quick / standard / deep 报告均记录为 `parallelism: degraded`，由主 agent 串行生成证据，没有实际开启多个子代理执行模块深度分析。因此该测试不能算完整通过，只能证明 CLI/gate/coverage 机械链路通过。

这个 issue 要把“多子代理执行”纳入 v2.0 验收标准：当运行环境支持 subagent，standard/deep 模式必须实际执行多个子代理模块分析，或明确标记为部分通过/未完成，而不能仅凭 gate `allowed_to_synthesize:true` 判定完整通过。

## Acceptance criteria

- [ ] 更新 `测试证据/v2.0/ACCEPTANCE_RESULT.md`，将当前结论从“通过”修正为“部分通过”或“CLI/gate 通过但多子代理验收未通过”。
- [ ] 更新 `测试证据/v2.0/RUN_LOG.md` 和 `COMPARISON_REPORT.md`，明确记录 quick / standard / deep 都是 `parallelism: degraded`，没有多个子代理参与。
- [ ] 补充或创建验收规则：standard/deep 在运行时支持 subagent 时，必须记录实际子代理分工、每个子代理产物、主 agent 融合过程，才能算完整通过。
- [ ] 如要恢复 v2.0 完整通过，需要重新跑一次至少 standard 或 deep 模式的多子代理分析，并让 `module-evidence/*.json` 与最终报告吸收子代理产物。
- [ ] gate 或验收脚本不应只检查 `parallelism` 字段存在；`parallelism: degraded` 不能等价于多子代理执行通过。

## Blocked by

None - can start immediately
