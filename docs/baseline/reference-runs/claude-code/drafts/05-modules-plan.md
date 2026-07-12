# 05 Modules Plan

## Report Outline

1. 证据边界与项目定位
2. 全局架构：CLI 会话如何进入 agent loop
3. Query loop：从消息到模型响应，再回到下一轮
4. Tool runtime：工具池、权限契约、并发和结果一致性
5. Task/agent：把长任务和子代理从主循环中分离
6. Command/skill：把可复用能力装配进提示和 forked agent
7. Context/memory：项目指令、Git 状态、记忆和后台 consolidation
8. 外围模块：MCP、插件、权限、UI、远程和平台服务
9. 评价、重设计建议、未验证事项

## Business Modules

| 模块 | 类型 | 主要文件/目录 | 业务职责 |
|---|---|---|---|
| Query loop | 核心 | `query.ts`, `QueryEngine.ts` | 维持一次 agent turn 的消息与恢复状态 |
| Tool runtime | 核心 | `Tool.ts`, `tools.ts`, `services/tools/*` | 将模型 tool_use 变成受控、可取消、可并发的执行 |
| Task/agent | 核心 | `Task.ts`, `tasks.ts`, `tools/AgentTool`, `tasks`, `coordinator` | 管理后台任务、子代理和多 agent 协作 |
| Command/skill | 核心 | `commands.ts`, `skills/loadSkillsDir.ts`, `SkillTool` | 将本地、项目、插件和 MCP 能力变成模型可发现命令 |
| Context/memory | 核心 | `context.ts`, `state`, `SessionMemory`, `autoDream` | 生成会话可用的项目上下文并维护长期记忆 |
| MCP/plugin | 次要 | `services/mcp`, `utils/plugins`, `services/plugins` | 扩展外部工具、资源、命令和安装来源 |
| Permission/security | 次要 | `utils/permissions`, `BashTool`, `PowerShellTool` | 在工具执行前后限制危险操作和路径范围 |
| Entry/UI | 次要 | `main.tsx`, `setup.ts`, `screens`, `components`, `ink` | 启动、终端渲染、交互和用户可见状态 |
| Remote/IDE | 次要 | `bridge`, `remote`, `server`, `entrypoints/sdk`, `services/lsp` | 将同一会话暴露给远程和 IDE 表面 |
| Platform services | 次要 | `services/api`, `oauth`, `analytics`, `native-ts`, `utils` | 外部 API、认证、遥测、平台差异和基础设施 |

## Narrative Transitions

`Entry/UI` 提供用户输入和会话状态 →[输入需要被组织成可恢复的模型请求]→ `Query loop`。

`Query loop` 得到 tool_use →[模型的能力声明必须映射到实际可用且受策略约束的工具]→ `Tool runtime`。

`Tool runtime` 发现长耗时/递归工作 →[不能让主循环承担所有生命周期]→ `Task/agent`。

`Task/agent` 需要专门化能力 →[能力来源可能是本地文件、项目配置、插件或 MCP]→ `Command/skill`。

`Command/skill` 和 query 都需要项目规则、Git 状态与历史摘要 →[上下文必须有来源、缓存和生命周期]→ `Context/memory`。

`Context/memory` 的输入和输出受企业策略、外部连接及终端/远程表面影响 → `MCP/plugin`、`Permission/security`、`Remote/IDE` 和 `Platform services` 作为边界模块回接主链路。

## Module Questions

- Query loop 如何在流式响应与工具结果之间避免 orphan message？
- Tool runtime 如何表达“可并发”而不把所有工具默认为安全？
- Task/agent 如何让取消、输出和主会话状态一致？
- Skill loader 如何处理来源优先级、重复文件和路径条件？
- Context/memory 如何在缓存收益和最新项目状态之间取舍？
