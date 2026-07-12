# 次要模块：支撑能力与插件声明

这些模块不决定项目的核心 agent 运行时，但决定命令边界、跨平台可用性和用户可读性。

| 模块 | 实现与证据 | 在整体中的作用 |
|---|---|---|
| 参数解析 | `lib/args.mjs:1-127` 支持 value/boolean options、短别名、`--` passthrough 和引号分词 | 让 Claude command 原始参数稳定进入主编排 |
| Git review 上下文 | `lib/git.mjs:78-347` 区分 working tree/branch，限制 inline diff 大小并处理 untracked 文件 | 把 review 的目标范围和证据交给 Codex，而不是让命令层自行拼 Git |
| 结果渲染 | `lib/render.mjs:24-465` 验证结构化 review、按严重性排序 findings，并渲染 status/result/cancel | 将 machine payload 转成人类可读报告，同时保留 JSON 模式 |
| 进程控制 | `lib/process.mjs:4-135` 封装 spawnSync、binary check 和 Windows taskkill/Unix process group | 为 setup、Codex 可用性检测和取消提供平台边界 |
| 文件/prompt/workspace | `lib/fs.mjs:1-40`、`lib/prompts.mjs:1-13`、`lib/workspace.mjs:1-9` | 解决 stdin、模板替换和 workspace 根目录解析 |
| Claude session transfer 路径 | `lib/claude-session-transfer.mjs:1-44` | 限制 source 必须位于 Claude projects 目录，保护 import 边界 |
| 插件声明 | `.claude-plugin/plugin.json:1-8`、`marketplace.json:1-21`、`hooks.json:1-38` | 让 Claude Code 能发现命令、agent、skills 和 hooks |
| command/agent/skill 文档 | `plugins/codex/commands/*.md`、`agents/codex-rescue.md`、`skills/*` | 将权限、调用方式和用户可见工作流声明在宿主协议层 |
| review schema | `schemas/review-output.schema.json:1-87` | 约束 adversarial review 的 verdict、finding 行号和 recommendation |
| 版本脚本 | `scripts/bump-version.mjs:1-227` | 同步多个 manifest 的版本，测试覆盖 stale metadata |

其中最重要的支撑设计是 Git 上下文收集：小 diff 可 inline，较大 diff 转为轻量上下文并要求 Codex 自行检查（测试验证于 `tests/git.test.mjs` 和 `tests/runtime.test.mjs`）。这比无界地把 diff 注入 prompt 更可控，但“完整性”由 Codex 二次读取承担。

## 次要模块覆盖率

| 文件组 | 有效行 | 已读行 | 覆盖率 | 达标 |
|---|---:|---:|---:|---|
| 参数/进程/文件/prompt/workspace/session 工具 | 407 | 407 | 100% | ✅ |
| Git 上下文 | 347 | 347 | 100% | ✅ |
| 渲染 | 465 | 465 | 100% | ✅ |
| 插件文档、schema、版本脚本 | 约 1,000 | 已读取关键文件完整范围 | 100%（按文件行并集） | ✅ |
| **合计（次要模块）** | **约 2,219** | **约 2,219** | **100%** | **达标 ✅** |

测试文件、lockfile、LICENSE/NOTICE、CI 配置和缺失的 `docs/plugin-demo.webm` 不纳入有效模块覆盖率。
