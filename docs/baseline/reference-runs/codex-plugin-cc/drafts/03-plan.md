# 阶段 3：分析计划

## 规模估计

源码目录确认存在，固定 HEAD 为 `db52e28f4d9ded852ab3942cea316258ae4ef346`，工作区干净。排除测试、`package-lock.json`、许可证、CI 和生成代码后，生产脚本约 5,424 行，另有 227 行版本脚本。最大文件是 `plugins/codex/scripts/lib/codex.mjs`（1,219 行）和 `plugins/codex/scripts/codex-companion.mjs`（1,073 行）。

规模判断：小型仓库的插件包，但运行时核心已经达到中等复杂度。复杂度来自异步事件流、跨进程通信、后台任务持久化和 Claude hook 生命周期，而不是目录数量。

## 模式与门槛

本次固定使用 `standard`：

| 模块类型 | 目标覆盖率 | 本次策略 |
|---|---:|---|
| 核心模块 | >=60% | 读取核心生产文件的完整行范围，重点复核入口、状态机和通信边界 |
| 次要模块 | >=30% | 读取全部支撑脚本、命令文档和插件元数据，完整记录关键行为 |

覆盖率按参考 skill 的行并集规则计算。测试不计入生产代码覆盖率，但作为运行契约证据单独记录。

## 模块划分

### 核心模块

1. **命令与任务编排**：`codex-companion.mjs`。把 setup/review/adversarial-review/task/transfer/status/result/cancel 统一成命令路由和 Job 生命周期。
2. **Codex App Server 会话运行时**：`lib/codex.mjs`、`lib/app-server.mjs`。管理线程、turn、通知、子 agent、结构化 review 和 Claude session import。
3. **共享 Broker 与运行时复用**：`app-server-broker.mjs`、`lib/broker-lifecycle.mjs`、`lib/broker-endpoint.mjs`。将多个调用复用到一个 Codex app-server，并在繁忙时允许 interrupt。
4. **任务状态、日志与后台生命周期**：`lib/state.mjs`、`lib/tracked-jobs.mjs`、`lib/job-control.mjs`。持久化任务、进度、session 隔离、结果查询和取消所需状态。
5. **Claude 生命周期与停止审查门**：`hooks/hooks.json`、`session-lifecycle-hook.mjs`、`stop-review-gate-hook.mjs`。把 Claude SessionStart/End/Stop 事件接入 runtime。

### 次要模块

- 参数解析：`lib/args.mjs`
- Git review 上下文：`lib/git.mjs`
- 结果渲染：`lib/render.mjs`
- 进程控制：`lib/process.mjs`
- 文件、prompt、workspace 和 Claude session 路径工具：`lib/fs.mjs`、`lib/prompts.mjs`、`lib/workspace.mjs`、`lib/claude-session-transfer.mjs`
- 插件 command/agent/skill 文档、schema 和版本脚本

## 验证计划

- 用 `rg`、`nl`、`sed` 读取入口、配置、核心文件和文档，结论统一附 `path:line`。
- 用 `npm test` 验证现有行为；本次结果为 91/91 通过。
- 对关键链路做交叉验证：命令入口 -> `executeTaskRun/executeReviewRun` -> App Server -> tracked job -> render；Stop hook -> task command -> JSON verdict。
- 对外部资料只记录项目定位和链接，不用它替代源码证据。
- 由于当前 runtime 没有 Agent/subagent 工具，阶段 6 由主执行者完成，并在日志中标记为流程偏差。
