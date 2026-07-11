# PR 测试证据包 · Issue / Ticket 12

- **PR**: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/pull/15
- **Issue**: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/12
- **分支**: `yuanyuanyuan/v2.0-parallelism-degraded`
- **环境**: 本机仓库根 · Node v24.18.0 · npm 11.16.0

## 先看：哪个文件是 UAT 报告？

| 文件 | 角色 |
|---|---|
| **[UAT_REPORT.md](./UAT_REPORT.md)** | **本轮 UAT 正式报告（从这里读）** |
| [uat-checklist.md](./uat-checklist.md) | UAT 勾选底稿 |
| [VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md) | 总验证包（unit 细节 + 摘要；**不是**单独的「重跑 UAT」） |
| [npm-test.full.txt](./npm-test.full.txt) / [typecheck.full.txt](./typecheck.full.txt) | unit/typecheck 全量日志 |
| [gate-recheck-summary.json](./gate-recheck-summary.json) | 三模式 gate 摘要 |

## 明确不是 UAT 报告

- `测试证据/v2.0/standard/ANALYSIS_REPORT.md`
- `测试证据/v2.0/deep/ANALYSIS_REPORT.md`

它们是**更早的架构分析草稿/历史样例**，本轮**没有**为 UAT 重跑生成，也**不能**当「UAT 重跑报告」。

## 本轮 UAT 一句话

**docs-only 验收口径核对**（agent 代跑）：查文档和既有工件有没有把 `parallelism: degraded` 装成完整通过。  
**不是** multi-agent 分析重跑，**不是**远程环境 UAT。

## 30 秒结论

1. UAT（docs-only 五条）: **PASS** — 见 `UAT_REPORT.md`
2. 产品「完整通过」: **否**（仍部分通过；AC4 未做）
3. unit: 35/35；typecheck: 绿
4. standard/deep 既有工件: `parallelism-execution` **fail**
