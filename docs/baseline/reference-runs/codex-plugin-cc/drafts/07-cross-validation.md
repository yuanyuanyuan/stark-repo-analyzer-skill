# 阶段 7：交叉验证

## 端到端链路

源码链路一致：command 文档调用 `codex-companion.mjs`，主入口按子命令创建 Job 并调用 `executeReviewRun`/`executeTaskRun`（`commands/review.md:47-54`、`codex-companion.mjs:712-823`）；两者继续调用 `runAppServerReview`/`runAppServerTurn`（`codex-companion.mjs:358-520`、`codex.mjs:1002-1159`）；runner 被 `runTrackedJob` 包装并更新状态和日志（`codex-companion.mjs:658-668`、`tracked-jobs.mjs:142-206`）。

## 关键结论抽查

| 结论 | 源码验证 | 结果 |
|---|---|---|
| 后台任务是 detached worker 而非 Claude 进程内等待 | `codex-companion.mjs:671-709` | 通过 |
| review 与 task 共用 App Server 客户端但 sandbox 不同 | `codex.mjs:1002-1055`、`1095-1159` | 通过：review read-only；task 由 write 选项决定 |
| Broker busy 可回退 direct | `codex.mjs:613-641`、`app-server-broker.mjs:170-195` | 通过 |
| status 默认按 Claude session 过滤 | `job-control.mjs:15-25`、`213-239` | 通过 |
| Stop gate 默认关闭并可配置 | `state.mjs:19-26`、`codex-companion.mjs:215-238`、`stop-review-gate-hook.mjs:142-178` | 通过 |
| transfer 不是复制文件，而是调用 native import 并按 hash 找回 thread | `codex.mjs:653-730`、`1058-1092` | 通过 |

## 测试交叉证据

在固定源码工作区运行 `npm test`，91 个测试全部通过，包含：

- endpoint 跨平台、进程终止、参数和命令文档契约；
- setup、auth、review、adversarial review、task、resume/fresh；
- shared Broker、多 subagent、后台任务、status/result/cancel；
- SessionStart/SessionEnd、Stop gate 的 allow/block/unavailable 分支；
- state pruning 与 `CLAUDE_PLUGIN_DATA` 路径。

测试不代替源码阅读。尤其不能证明未覆盖的真实 Codex provider、外部 ledger 服务、跨平台文件系统竞态和所有 Claude host 版本行为。

## 仍未验证

- 当前 commit 没有独立 architecture/RFC 文档，设计动机主要由 README、命令文档和实现反推；反推结论均标记为源码推断。
- 没有使用 Git 历史，无法验证某些复杂兼容分支是否来自既往故障。
- 当前工具环境没有 Agent/subagent 工具，因此没有执行参考 skill 要求的并行 subagent 阶段；改为单执行者分模块读取，覆盖率和交叉验证仍已完成。
