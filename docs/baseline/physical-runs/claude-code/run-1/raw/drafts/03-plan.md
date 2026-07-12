# 分析计划

## 固定范围

- 源码根目录：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/claude-code`
- 固定 HEAD：`a371abbe75ffa0d0a3c92290e2bbf56a7ef54367`（已验证）
- 模式：`standard`（由调用方明确指定）
- 只读约束：不使用 Git 历史；不修改源树；全部输出仅落在本工作目录。

## 规模与方法

对 `src/**/*.ts(x)` 的 `wc -l` 统计为 512,664 行。这是从 sourcemap 还原的大型快照，包含大量 UI、命令和服务面。标准模式不声称全仓逐行覆盖；本文把覆盖门控应用到三个主数据流模块（各 >=60%），其余部分只做目录/依赖结构扫描并明确标示。

## 研究限制

外部 Web 搜索与官网遍历：**not performed**。原因：调用方限定“Analyze only”该本地源树。项目自带 README 与源码是本次唯一内容证据；不将 README 的叙述未经源码验证地当作实现事实。

## 核心问题

1. CLI 如何在大量子命令、URI/桥接入口与交互模式之间建立启动边界？
2. 一个交互回合如何从终端输入进入调度循环、模型查询、工具执行并回写终端？
3. MCP 和本地工具如何被接入为动态能力，同时保持连接、审批和权限边界？

## 分析模块

| 模块 | 类型 | 责任范围 | 目标 |
|---|---|---|---|
| 启动与命令边界 | 核心 | `src/main.tsx`, `src/entrypoints/cli.tsx`, `src/cli/**` 中启动/handler 层 | >=60% |
| 交互会话调度 | 核心 | `src/cli/print.ts`, `src/screens/REPL.tsx`, `src/QueryEngine.ts` 的回合控制接口 | >=60% |
| 工具与 MCP 能力面 | 核心 | `src/tools/**`, `src/services/mcp/**`, MCP 命令/连接层 | >=60% |

## 验证策略

- 子代理仅阅读其分配文件并写入各自模块草稿。
- 主代理在所有模块草稿完成后，抽查每个核心模块 2 个结论，验证跨模块契约。
- 不运行构建、测试或 CLI：缺少可复现依赖清单且执行可能产生外部或本地状态；记录为 **not performed**。
