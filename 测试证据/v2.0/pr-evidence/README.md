# PR 测试证据包 · Issue / Ticket 12

- **PR**: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/pull/15
- **Issue**: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/12
- **生成时间**: 2026-07-11 17:12 CST
- **分支**: `yuanyuanyuan/v2.0-parallelism-degraded`
- **提交（证据采集时）**: 见 git log；本包随 `chore`/`docs` commit 进入 PR
- **环境**: Node `v24.18.0` · npm `11.16.0` · 工作目录仓库根

## 这个目录是什么

给 reviewer **直接打开就能核对** 的证据，不只写「测试通过」。

| 文件 | 内容 |
|---|---|
| [VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md) | **主阅读入口**：命令、结果、UAT 逐条、与 AC 对照、摘录 |
| [npm-test.log](./npm-test.log) | 完整 `npm test` 原始输出（35 pass / 0 fail） |
| [typecheck.log](./typecheck.log) | 完整 `npm run typecheck` 原始输出 |
| [gate-recheck-summary.json](./gate-recheck-summary.json) | 三模式已提交 gate 工件中 parallelism 与失败项摘要 |
| [uat-checklist.md](./uat-checklist.md) | UAT 逐条勾选与文件锚点 |

相关仓库路径（本 PR 外已有证据，不重复拷贝大文件）：

- `测试证据/v2.0/ACCEPTANCE_RESULT.md`
- `测试证据/v2.0/RUN_LOG.md`（§21 Issue #12 复核）
- `测试证据/v2.0/COMPARISON_REPORT.md`
- `测试证据/v2.0/{quick,standard,deep}/evidence-plan.md`
- `测试证据/v2.0/{quick,standard,deep}/quality-gate-report.json`
- `docs/specs/v2.0-multi-agent-acceptance.md`
- `test/gate.test.js`（parallelism 相关用例）

## 30 秒结论

1. **自动化**: `npm test` 35/35 绿；`typecheck` 绿。
2. **本票口径**: standard/deep 在 `parallelism: degraded` 时 **不能** 完整通过；gate 会 fail `parallelism-execution`。
3. **quick**: 允许 degraded；parallelism 检查 pass（仍可因 parse/report 等其它门 blocked）。
4. **UAT**: 文档与规则与 AC1–3/5 一致；AC4 multi-agent 重跑 **未做**（可选，PR 诚实声明）。
5. **e2e**: N/A（默认范围是文档/规则收口，不是重跑完整分析链路）。
