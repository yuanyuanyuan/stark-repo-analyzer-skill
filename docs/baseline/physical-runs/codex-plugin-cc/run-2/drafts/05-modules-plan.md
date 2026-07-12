# 阶段 5：模块与叙事计划

## 整体架构假设

这是一个“薄适配器 + 显式持久化生命周期”插件：Claude Code 命令提供交互入口；Node 脚本将请求协议化并调用本机 Codex CLI/App Server；状态文件和 broker 将长任务从当前 Claude turn 中解耦；Hook 将可选审查约束接回 Claude 的停止点。该假设将在阶段 7 以模块草稿交叉验证。

## 逻辑模块

| 模块 | 类型 | 业务职责 | 主要文件 |
|---|---|---|---|
| 命令编排与 Codex 调用 | 核心 | 解析 Claude 命令、选择执行方式、渲染人类可读结果并驱动 CLI/App Server | `codex-companion.mjs`、`lib/args.mjs`、`lib/codex.mjs`、`lib/app-server.mjs`、`lib/process.mjs`、`lib/render.mjs` |
| 后台作业生命周期 | 核心 | 提供 broker、端点发现、任务登记、状态持久化、查询/取消与会话转移 | `app-server-broker.mjs`、`lib/tracked-jobs.mjs`、`lib/broker-lifecycle.mjs`、`lib/job-control.mjs`、`lib/state.mjs` |
| 审查门控与插件契约 | 核心/次要 | 把 review/adversarial-review 转为受控命令，并用 Stop Hook 执行可选发布前闸门；维护命令、skill、schema、打包元数据 | `stop-review-gate-hook.mjs`、`session-lifecycle-hook.mjs`、`commands/`、`prompts/`、`hooks/`、`schemas/` |

## 叙事线

`命令编排与 Codex 调用` →[一次调用可完成审查，但长任务需要脱离前台 Claude turn]→ `后台作业生命周期` →[任务已可追踪，仍需定义何时允许 Claude 正常结束]→ `审查门控与插件契约`。

首章从用户输入如何跨运行时落地讲起；第二章解释为什么将状态显式化并交给 broker；第三章说明契约层怎样把强制审查限制为可选、可操作的生命周期规则。每个模块草稿需以这一因果链衔接，而非按目录陈列。

## 最终报告结构

1. 场景、边界与项目定位
2. 全景架构与一次交互/后台交互的数据流
3. 命令编排与 Codex 调用
4. 后台作业生命周期
5. 审查门控与插件契约
6. 交叉验证、设计哲学、亮点与风险
7. 重设计建议与工程启发
