# 模块与叙事计划

## 整体设计哲学（待源码交叉验证）

从 workspace 清单、顶层开发规范和 app-server 文档可见的初步判断是：以 Rust crate 边界管理演进风险，以版本化协议将持久线程代理与多种宿主解耦，并对模型可见上下文、权限与 API 兼容性施加显式约束。

## 叙事线

`会话与回合编排` → [把用户输入、上下文、模型与工具协调为可持久化代理状态] → `App Server 与 v2 协议` → [把该状态机投射给 CLI、IDE/桌面等宿主] → `CLI/JavaScript 包装与发行面`。

## 模块清单

| 模块 | 类型 | 分配范围 | 覆盖目标 | 叙事职责 |
|---|---|---|---:|---|
| 会话与回合编排 | 核心 | `codex-rs/core/src/session/` 与其直接入口/事件映射 | >=60% | 解释代理如何在一次 turn 中维持状态与调度。 |
| App Server JSON-RPC 边界 | 核心 | `codex-rs/app-server/src/`、`app-server-protocol/src/protocol/` | >=60% | 解释代理如何成为可被其他产品承载的服务。 |
| CLI 包装与 JS workspace | 次要 | `codex-cli/`、顶层 `package.json`、`pnpm-workspace.yaml` | >=30% | 说明发行和开发工具链，不将其误作代理内核。 |

## 明确未覆盖

TUI、沙箱实现、MCP、SDK、模型提供商、云功能、执行服务器、测试套件及其余 Rust crate 不在本次有界范围中。
