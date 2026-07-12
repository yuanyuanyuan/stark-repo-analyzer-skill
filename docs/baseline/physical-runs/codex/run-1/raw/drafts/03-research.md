# 研究草稿

## 证据来源与限制

- 已读一手资料：仓库 `README.md`、`codex-rs/Cargo.toml`、`codex-rs/app-server/README.md`、顶层 `AGENTS.md`。
- 固定源码版本：`9e552e9d15ba52bed7077d5357f3e18e330f8f38`。
- 外部检索（3--5 次 WebSearch）**未执行**：本次运行未提供 WebSearch/WebFetch 工具；因此不将外部观点、市场份额或第三方评价作为事实。
- Git 历史研究**未执行**：用户明确禁止使用 Git history。

## 核心问题

Codex CLI 面向本地开发环境中的编码代理工作流。README 将其定义为本地运行的 coding agent；其 Rust workspace 则把 CLI、核心运行时、app-server、沙箱、工具、模型客户端等拆为独立 crate。核心痛点不是单次文本生成，而是将长生命周期的线程、模型交互、工具调用、权限与多种宿主界面协调为可演进的本地系统。

## 同类方案定位（仅基于项目内文档与通用生态知识）

| 方案 | 定位差异 | 本项目可验证的差异 |
|---|---|---|
| Aider | 面向终端的代码协作工具 | 本分析未读取其源码；仅作为同类终端代理，不作功能断言。 |
| Claude Code | 面向终端的编码代理 | 未作外部调研；不作实现层比较。 |
| Cursor/IDE agents | IDE 内嵌的代理交互 | Codex 通过 app-server JSON-RPC 将代理内核与宿主分离，见 `codex-rs/app-server/README.md`。 |

## 为什么单独构建

仓库的架构信号表明，项目把“代理运行时”与“承载它的界面”分离：`core` 承担共享会话能力，app-server 暴露 JSON-RPC，CLI/TUI 或其他宿主可通过稳定边界接入。这种拆分增加协议维护成本，但避免把代理状态机锁死在单一终端 UI 中。

## 研究待证事项

- 会话上下文、工具调用与模型流式事件如何在 `core` 中编排。
- app-server 如何把线程/回合操作投射为版本化 JSON-RPC API。
