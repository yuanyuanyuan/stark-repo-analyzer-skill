# Domain Glossary

本词汇表只描述本次基线分析中的领域概念，不记录实现细节。

| 术语 | 本次基线中的精确定义 | 证据/边界 |
|---|---|---|
| Query loop | 一次用户请求从准备上下文、调用模型、处理流式消息到工具结果回填并继续迭代的闭环 | `src/query.ts:219-239`、`src/query.ts:241-307` |
| Tool pool | 当前会话可提供给模型的内置工具与 MCP 工具集合，受模式、环境变量和 deny 规则过滤 | `src/tools.ts:193-327`、`src/tools.ts:345-388` |
| ToolUseContext | 工具执行和查询循环共享的会话上下文，承载消息、应用状态、权限、取消信号和工具选项 | `src/Tool.ts:158-300` |
| Task | 可被列举、追踪和终止的后台或子代理工作单元 | `src/Task.ts:6-76` |
| Skill | 可被发现、解析为 prompt command、按需直接执行或 fork 到子代理的扩展能力 | `src/skills/loadSkillsDir.ts:185-316`、`src/tools/SkillTool/SkillTool.ts:118-130` |
| Context | 注入模型请求的系统信息、用户项目指令和会话记忆，不等同于完整 transcript | `src/context.ts:113-189` |
| Standard baseline | 在固定源码版本上生成、可复核且显式标注覆盖率与限制的架构分析结果 | 本输出目录的 `metadata.json` 与 `drafts/08-coverage.md` |

## Resolved Boundary

- “项目问题/定位”与“当前实现事实”分开：前者可以引用公开文档，后者必须有源码路径和行号。
- “核心模块”按业务数据流划分，而不是把 `src/services` 或 `src/utils` 直接当成一个模块。
- “覆盖率”只统计实际读取过的行，不用文件名、导入关系或目录存在来代替读取。
