# lessons（只追加）

> 写 lessons ≠ writeback agent/SOUL。产品票 Evolution 默认 none-with-reason。

## 初始化

- 2026-07-11：目录 scaffold。尚无历史 lessons。

## 2026-07-11 · ticket 12 · degraded 验收收口

- 现象：Issue #12 AC 与仓库主体（ACCEPTANCE/gate）已大体一致，但 README/spec 仍写「缺并行不影响通过标准」，与 `parallelismExecutionCheck` 冲突；ISSUE 本地 checkbox 未勾。
- 正确做法：规则 SSOT 落 `docs/specs/v2.0-multi-agent-acceptance.md`；修 README/spec 表述；AC1–3/5 勾选；AC4 保持可选未勾；补 quick 允许 degraded 的单测。
- 误伤点：勿把历史 `allowed_to_synthesize:true` 或「质量门其它项不降级」写成 standard/deep 多子代理完整通过。
- 分支约定：本仓库工作分支 `yuanyuanyuan/v2.0-parallelism-degraded` 即 ticket 12 交付分支；用户可覆写「不新建 feat/12」。

## 2026-07-11 · Loop · PR #15

- PR: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/pull/15（正式，非 draft）
- 差距：无阻塞 residual；AC4 multi-agent 完整重跑仍为可选升级，未纳入本 PR（诚实声明）。
- Next LOOP：Done（除非用户要做 AC4 或修 PR review 意见）。
- time_param：手动：贴入 review/CI 结果后继续。

## 2026-07-11 · 用户反馈 · PR 需要可读测试证据

- 现象：仅写「35 pass」不够；review 需要命令、全量日志、UAT 锚点、真实工件 gate 表。
- 做法：在 `测试证据/v2.0/pr-evidence/` 落 VERIFICATION_REPORT + full txt 日志 + uat-checklist + gate-recheck-summary，并更新 PR body 深链。
- 注意：`*.log` 被 gitignore；证据日志用 `.full.txt`。

## 2026-07-11 · UAT 报告纠错

- 用户反馈：UAT 重跑报告不对；且易把 `standard/deep/ANALYSIS_REPORT.md` 当成 UAT。
- 纠正：本轮 UAT 是 docs-only 核对，不是 ANALYSIS 重跑；正式报告定为 `测试证据/v2.0/pr-evidence/UAT_REPORT.md`，并在 PR body 置顶纠错表。

## 2026-07-11 · UAT 必须独立 codex exec

- 用户纠正：同会话 docs-only / 手写 report / 同会话 multiagent 实验 ≠ 完整 UAT。
- 正确 UAT：单独 `codex exec "严格执行 …/skills/repo-analyzer/SKILL.md 分析 $REPO ，输出报告到 …/测试证据/v2.1-human"`。
- 规则已落盘 `docs/specs/v2.1-codex-exec-uat.md`，并在 `AGENTS.md` 引用。
