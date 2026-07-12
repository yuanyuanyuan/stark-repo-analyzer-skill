# 03 Research：Codex 的问题、定位与组织动机

## 项目解决的核心问题

固定 commit 的 README 将 Codex CLI 定义为“在本地计算机运行的 coding agent”（\`README.md:1-8\`）。具体问题是：开发者希望把自然语言任务转成代码修改、命令执行、测试验证和可恢复会话，但又不能把终端权限完全交给不可解释的自动化脚本。

代码中的解决路径不是单一聊天客户端，而是一个本地 agent runtime：会话接收 submission，产生 event；turn 负责上下文、模型采样、工具结果和后续采样；exec/sandboxing 决定副作用边界；TUI 和 app-server 分别提供终端与程序化客户端接口（\`core/src/session/mod.rs:387-398\`、\`core/src/session/turn.rs:143-150\`）。

## 定位

- 产品形态：本地优先、终端优先的 coding agent，同时暴露 app-server 和 TypeScript SDK 适配面。
- 架构取向：Rust workspace 多 crate 分层；把 agent loop、协议、安全执行、展示层分开。
- 设计哲学（从代码归纳）：显式状态和事件边界、默认受控的副作用、上下文增量构建、接口适配与核心循环解耦。AGENTS.md 明确要求模型上下文增量构建、有硬上限且不能无界注入（\`AGENTS.md:91-100\`）。

## 同类对比

以下只作为当前公开生态背景，不是固定 commit 的代码证据：

| 项目/路线 | 主要交互 | 设计取向差异 |
|---|---|---|
| Claude Code | 终端 agent | 更强调终端工作流和产品级 agent 体验 |
| Aider | 终端/聊天式代码修改 | 更轻量，核心边界通常集中在模型对话与 git 修改 |
| OpenHands | 可编排 agent 平台 | 更偏平台化、浏览器/容器化执行 |
| GitHub Copilot coding agent | 云端托管 | 把执行和仓库集成放到服务端 |
| Codex | 本地 CLI + app-server | 把执行安全、事件协议、TUI 和可复用服务接口放在同一 runtime |

GitHub 官方仓库元数据（通过 agent-reach/gh，2026-07-12读取）将 \`openai/codex\` 描述为“Lightweight coding agent that runs in your terminal”；该描述与固定 commit README 的 CLI 定位一致。官方文档首页还把 Codex 文档、配置、开发者、安全和管理分成独立入口，说明产品边界已超出单一 CLI，但不能据此推断固定 commit 的全部实现。

## 为什么需要单独做这个项目

把模型 API、shell、git 和一个终端 UI 拼接起来可以得到原型，但会遗漏三个系统性问题：

1. 工具调用和用户输入会并发交错，需要 submission/event 队列和 turn 状态。
2. 自动执行不能只靠 UI 确认，需要执行策略、sandbox policy、网络策略和审批状态形成一致边界。
3. 同一 agent 能力需要服务 TUI、app-server、MCP 和 SDK；如果核心直接依赖某个展示层，扩展会形成耦合。

因此，Codex 的独特价值不只是“调用模型写代码”，而是将 agent 运行时的状态、权限、工具和客户端协议工程化。

## 组织动机

从固定 commit 可验证的资料看，OpenAI 维护了 CLI、app-server、MCP 接口、技能/插件和多平台沙箱。README 的安装/文档链接（\`README.md:12-71\`）、SECURITY.md 的安全入口（\`SECURITY.md:15-17\`）和 app-server/MCP 文档说明了面向多种客户端和受控执行环境的组织需求。商业战略、团队规模和历史演进未在本次证据范围内找到，不作事实推断。

## 待验证

- 当前 commit 对应的线上产品功能与本地源码是否完全一致：待验证。
- 各竞品在同一时间点的内部安全实现：未研究，不作结论。
- 远程控制、桌面 app、云端 Codex 与本地 runtime 的完整边界：当前资料不足。
