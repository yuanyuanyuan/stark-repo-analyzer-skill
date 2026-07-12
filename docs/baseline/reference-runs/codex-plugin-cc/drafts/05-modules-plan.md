# 阶段 5：模块计划与报告叙事线

## 报告大纲

1. 场景化引入：Claude Code 用户为什么需要把 Codex 接入现有工作流。
2. 项目全景：插件包、命令层、共享运行时和持久化层的分工。
3. 一条任务如何完成：从 slash command 到 Codex turn，再到可恢复结果。
4. 核心模块一：命令与任务编排。
5. 核心模块二：App Server 会话与通知状态机。
6. 核心模块三：共享 Broker 的复用和并发边界。
7. 核心模块四：Job 持久化、日志和后台 worker。
8. 核心模块五：生命周期 hooks 与 Stop review gate。
9. 支撑模块：Git 上下文、参数、渲染、进程和插件声明。
10. 交叉验证、洞察、亮点、问题和重新设计建议。

## 业务模块清单

| 顺序 | 模块 | 类型 | 主要证据 |
|---:|---|---|---|
| 1 | 命令与任务编排 | 核心 | `plugins/codex/scripts/codex-companion.mjs:358-1067` |
| 2 | App Server 会话运行时 | 核心 | `plugins/codex/scripts/lib/codex.mjs:302-1219`、`lib/app-server.mjs:57-353` |
| 3 | 共享 Broker | 核心 | `app-server-broker.mjs:48-247`、`lib/broker-lifecycle.mjs:113-209` |
| 4 | Job 状态与后台生命周期 | 核心 | `lib/state.mjs:29-191`、`lib/tracked-jobs.mjs:36-206`、`lib/job-control.mjs:161-308` |
| 5 | Claude 生命周期与 Stop gate | 核心 | `hooks/hooks.json:1-38`、`session-lifecycle-hook.mjs:42-129`、`stop-review-gate-hook.mjs:40-178` |
| 6 | Git review 上下文 | 次要 | `lib/git.mjs:78-347` |
| 7 | 输出、参数与跨平台工具 | 次要 | `lib/args.mjs`、`lib/render.mjs`、`lib/process.mjs` 等 |
| 8 | 插件声明与 command/skill 文档 | 次要 | `plugin.json`、`commands/*.md`、`skills/*`、`schemas/*` |

## 叙事线

```text
Claude slash command
  ->[把用户意图、review target 和运行选项规范化]
命令与任务编排
  ->[创建 Job 并选择 foreground/background]
任务状态与后台生命周期
  ->[需要稳定的 thread/turn 通信和最终输出]
App Server 会话运行时
  ->[多个调用需要复用一个本地进程并共享通知流]
共享 Broker
  ->[运行结果需要持久化、渲染、恢复和取消]
任务状态与输出渲染
  ->[Claude 生命周期决定何时注入 session、清理 job、阻止 stop]
Claude hooks / Stop gate
```

## 过渡逻辑

- 命令层只决定“用户想做什么”，不应承载 JSON-RPC 细节，因此下一章进入 Job 和 App Server 边界。
- App Server 能提供异步事件，但多个 Claude 命令共享一个运行时会出现串流归属和忙状态问题，因此需要 Broker。
- Broker 解决进程复用，却不负责用户可见的恢复和结果查询，因此由 Job 状态层承接。
- Job 层让任务可查询、可取消、可续接，但 Stop gate 还需要把 Claude 生命周期事件转换为一次审查任务，这引出 hooks。
