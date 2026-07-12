# 参考输出基线

## Status

测试项目范围、版本和主基线分析模式已确认；6 个项目的 `standard` 参考输出已完成，部分大型项目采用 bounded scope。

## Purpose

在重新实现 `stark-repo-analyzer-skill` 前，使用参考仓库中的 `repo-analyzer` skill 对 6 个具有不同规模和架构特征的代表性项目执行分析，保存可复核的输出，作为后续实现比较用的参考输出基线。

## Confirmed Scope

- 当前项目以当前工作树的清空状态为起点，不考虑 Git 历史。
- 参考仓库是独立的参考语料，不代表当前项目已经实现对应能力。
- 测试集扩展为 6 个项目，分为通用架构组和 Agent 生态组。
- 6 个项目的主基线统一使用参考 skill 的 `standard` 分析模式，以便横向比较。
- 主基线执行参考 skill 的完整流程，包括外部调研、项目文档研读、模块分析、交叉验证和最终报告整理。
- 每个测试项目至少保存输入提示、版本与环境元数据、原始分析报告、执行日志和结构化检查表。

## Local Source Corpus

参考项目源代码保存到当前项目旁的持久目录：

`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/`

每个项目使用独立目录和浅克隆，仅保留用于本地分析的工作树，不将大型上游源码默认纳入当前项目 Git。当前项目只保存获取 manifest、commit 校验结果和复现说明。

## Candidate Matrix

| 分组 | 项目 | 预期类型/规模 | 主要覆盖维度 | 当前公开事实 |
|------|------|---------------|--------------|--------------|
| 通用架构组 | `pallets/click` | 小型 Python CLI 库 | 入口、命令模型、扩展边界 | 默认分支 `main`；最新核验 commit `b67832c2167e5b0ff6764a8c04a0a9087e697b5a` |
| 通用架构组 | `encode/httpx` | 中型 Python 网络库 | 分层设计、同步/异步边界、模块协作 | 默认分支 `master`；最新核验 commit `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` |
| 通用架构组 | `astral-sh/ruff` | 大型 Rust/Python 工具链 | 多 crate、工具链、规模评估和覆盖率 | 默认分支 `main`；最新核验 commit `c588a3f7f57461692652d339936222b4496c5953` |
| Agent 生态组 | `openai/codex-plugin-cc` | 小型 JavaScript 插件 | 插件边界、配置和宿主集成 | 默认分支 `main`；最新核验 commit `db52e28f4d9ded852ab3942cea316258ae4ef346` |
| Agent 生态组 | `yasasbanukaofficial/claude-code` | 中大型 TypeScript Agent 骨架 | Agent 工具调用、终端 UI、骨架型架构 | 默认分支 `main`；最新核验 commit `a371abbe75ffa0d0a3c92290e2bbf56a7ef54367` |
| Agent 生态组 | `openai/codex` | 超大型 Rust/多语言 Agent | 多语言边界、CLI/SDK、复杂仓库分析 | 默认分支 `main`；最新核验 commit `9e552e9d15ba52bed7077d5357f3e18e330f8f38` |

注：上述 commit 已于 2026-07-12 UTC 浅克隆并校验为本地仓库 HEAD。完整获取记录见 [`source-corpus-manifest.json`](./source-corpus-manifest.json)。

## Pending Decisions

- 是否补做大型项目的 `deep` 压力测试。

## Completed Artifacts

- [本地源码 manifest](./source-corpus-manifest.json)
- [参考运行 manifest](./reference-run-manifest.json)
- [跨项目验证](./cross-project-validation.md)
- [重实现验收清单](./reimplementation-acceptance-checklist.md)
- [6 个项目的独立运行结果](./reference-runs/README.md)
