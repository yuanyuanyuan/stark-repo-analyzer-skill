# 03 Research

## Evidence Classification

本节将公开资料用于产品背景；所有“如何实现”的判断必须回到当前 commit 源码。

## Project Problem

官方文档把 Claude Code 描述为能够理解整个代码库、跨多个文件和工具完成开发任务的 AI coding assistant，并覆盖终端、IDE、桌面、Web 和 JetBrains 等使用表面。这个定位对应的工程问题不是“调用一次模型”，而是把会话、上下文、工具执行、权限和扩展机制组织成可持续的 agent loop。

当前源码能直接证实的实现问题边界是：

- `src/query.ts:219-307` 建立异步查询生成器和跨迭代状态。
- `src/query.ts:365-467` 在模型请求前组合压缩、裁剪和上下文投影。
- `src/query.ts:551-580` 准备工具执行器和运行时模型。
- `src/tools.ts:193-250` 建立可用工具池，并由 feature/env 选择条件能力。
- `src/context.ts:116-189` 将 Git 状态、CLAUDE.md 和日期注入系统/用户上下文。

## Positioning

公开资料支持的产品定位：以 Claude 模型为核心、面向开发者工作流的多表面 coding assistant。当前镜像 README 的定位更窄且更不可靠：它自称源码归档/研究镜像，并明确不是 Anthropic 官方产品。因此不能把镜像 README 中的宣传性功能列表当作当前 commit 的实现契约。

## Same-Category Comparison

| 类别 | 代表方案 | 与当前项目的可核验差异 |
|---|---|---|
| 终端 agent CLI | OpenAI Codex CLI、Aider | 本次未读取其固定 commit 源码，具体对比待验证；只能作为同类名称，不能写实现事实 |
| IDE/桌面 coding assistant | Cursor、GitHub Copilot | 官方资料显示 Claude Code 支持多表面，但本 commit 是否包含对应客户端实现，待验证 |
| 通用 agent SDK | Anthropic Agent SDK | 官方文档将 SDK 作为扩展方向；当前源码中的 `runAgent`、SkillTool 和 task 类型能证明内部 fork/agent 形态，但不能等同于 SDK |
| MCP-enabled assistant | MCP 客户端生态 | 当前 `src/services/mcp/config.ts` 和 `client.ts` 证明存在 MCP 配置、连接、工具/资源/命令获取路径；具体协议版本未由缺失依赖文件确认 |

## Why a Separate Project

从源码形态看，单纯把模型 API、shell wrapper 和终端 UI 拼接在一起不足以覆盖：

1. 查询循环需要在压缩、流式响应、工具结果和 fallback 之间保持消息一致性。
2. 工具池必须同时处理内置工具、MCP 工具、模式过滤、deny 规则和缓存稳定性。
3. 长任务需要任务状态、输出文件、取消和子代理边界；`src/Task.ts:44-76` 将这些概念抽象为共享契约。
4. 项目级指令、技能、记忆和远程连接需要进入同一会话上下文，但不能无条件污染所有模式。

## Organizational Motivation

官方产品动机只能从官方文档确认到“跨终端/IDE/桌面/Web 的统一 coding assistant”。镜像仓库的组织动机是保存和研究从 npm sourcemap 获得的源码，但这不是 Anthropic 对该 commit 的官方解释。商业战略、内部 feature flag 的真实动机和发布流程：未找到，待验证。

## Research Gaps

- 未找到当前 commit 的官方发布版本、依赖清单、构建脚本和测试报告。
- 未找到能证明 `USER_TYPE`、`bun:bundle feature()` 在外部发行构建中的最终取值的配置。
- 未对其他同类仓库执行固定 commit 对比，因此竞品章节只做定位，不作实现优劣断言。
