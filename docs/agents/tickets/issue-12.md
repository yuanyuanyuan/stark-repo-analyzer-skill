# Ticket

- id: "12"
- title: "v2.0 测试验收不能在 parallelism degraded 时标记完整通过"
- requirement_ref: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/12"
- source_issue: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/12"
- labels: ready-for-agent
- blocked_by: none
- saved_from: "GitHub Issue #12 body + Stage A 结构化补全（test_plan）"
- saved_at: "2026-07-11T16:58:00+08:00"

## what_to_build

修正 v2.0 测试验收口径：当前 `测试证据/v2.0` 的 quick / standard / deep 报告均记录为 `parallelism: degraded`，由主 agent 串行生成证据，没有实际开启多个子代理执行模块深度分析。因此该测试不能算完整通过，只能证明 CLI/gate/coverage 机械链路通过。

本票要把「多子代理执行」纳入 v2.0 验收标准：当运行环境支持 subagent 时，standard/deep 模式必须实际执行多个子代理模块分析，或明确标记为部分通过/未完成，而不能仅凭 gate `allowed_to_synthesize:true` 判定完整通过。

## acceptance_criteria

1. 更新 `测试证据/v2.0/ACCEPTANCE_RESULT.md`，将当前结论从「通过」修正为「部分通过」或「CLI/gate 通过但多子代理验收未通过」。
2. 更新 `测试证据/v2.0/RUN_LOG.md` 和 `COMPARISON_REPORT.md`，明确记录 quick / standard / deep 都是 `parallelism: degraded`，没有多个子代理参与。
3. 补充或创建验收规则：standard/deep 在运行时支持 subagent 时，必须记录实际子代理分工、每个子代理产物、主 agent 融合过程，才能算完整通过。
4. 如要恢复 v2.0 完整通过，需要重新跑一次至少 standard 或 deep 模式的多子代理分析，并让 `module-evidence/*.json` 与最终报告吸收子代理产物。
5. gate 或验收脚本不应只检查 `parallelism` 字段存在；`parallelism: degraded` 不能等价于多子代理执行通过。

## test_plan

### unit

- 若修改 gate / 验收相关脚本或判定逻辑：为「`parallelism: degraded` 不得判完整通过 / 须有 subagent 执行证据字段」增加或更新 `node:test` 用例，并执行 `npm test`。
- 若本票仅更新 Markdown 验收文案与规则文档、无生产代码路径变更：unit 可记 N/A — 理由：无代码路径变更；仍须跑 `npm test` 作为回归基线（绿测证明未误伤）。

### e2e

- 可选：本地对 fixture 或既有 `测试证据/v2.0` 工件核对 doctor→scan→…→gate 链路输出中 `parallelism` 与验收结论一致。
- 默认范围以文档与规则更新为主、不强制重跑 multi-agent 分析时：e2e: N/A — 理由：AC 以验收文档与规则声明为主；重跑 multi-agent 列为可选「恢复完整通过」路径（AC4），非本票默认交付硬条件。

### uat

在 acceptance_env（local-cli + docs-only）下由 agent 代跑核对：

1. `ACCEPTANCE_RESULT.md` / `RUN_LOG.md` / `COMPARISON_REPORT.md` 文案与 AC1–2 一致，不得把 degraded 记为多子代理完整通过。
2. 验收规则文档存在且覆盖 AC3、AC5（子代理分工/产物/融合；degraded ≠ 通过）。
3. 若实现了 gate/脚本加强：用现有 degraded 工件验证「不会被标完整通过」。
4. 若 PR/报告声称完整通过：必须出示 multi-agent 子代理分工与产物证据；否则不得声称完整通过。
5. 基线：`npm test` 与 `npm run typecheck` 退出码 0。
