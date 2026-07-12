# Codex standard 基线执行日志

## 1. 范围确认

- 源码目录存在：\`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/codex\`
- 固定 HEAD：\`9e552e9d15ba52bed7077d5357f3e18e330f8f38\`
- \`git status --short\`：空，源码工作树干净。
- 输出目录：\`docs/baseline/reference-runs/codex\`
- 本次未修改源码仓库，也未修改当前项目共享文档。

## 2. 实际读取过程

1. 读取根 README、AGENTS.md、package.json、codex-cli/package.json、codex-rs/Cargo.toml。
2. 读取 \`codex-rs/cli/src/main.rs\` 的模块声明、主入口、TUI/app-server 分发和若干诊断路径。
3. 读取 \`codex-rs/core/src/lib.rs\`、\`session/mod.rs\`、\`session/turn.rs\` 的会话队列、spawn、submit、事件和 turn loop。
4. 读取 protocol 的模型/事件/权限定义，以及 exec、execpolicy、sandboxing 的边界代码。
5. 读取 TUI 的模块声明、App/ChatWidget 状态入口；读取 app-server 的线程请求处理入口。
6. 读取 MCP 连接管理、skills loader、plugins manager 的接口和关键实现片段。
7. 读取 \`codex-rs/config.md\`、\`codex-rs/docs/protocol_v1.md\`、\`codex-rs/docs/codex_mcp_interface.md\`、app-server README、SECURITY.md。
8. 使用 agent-reach 的 GitHub 后端读取 \`openai/codex\` 公开仓库元数据，并用 Jina Reader 读取 OpenAI Codex 官方文档首页作为定位背景。

## 3. 失败与限制

- 仓库生产 Rust 代码约 690524 行，TUI、core、app-server 含大量大文件；本次没有逐文件覆盖整个工作区。
- 参考 skill 要求 Agent 并行启动 subagent；当前运行时没有暴露 Agent/subagent 工具，因此改为主 agent 负责各模块，并记录该偏差。
- \`gh search repos\` 可用，但返回的是当前搜索结果，不与固定 commit 同步；仅用于竞品/定位背景，不用于证明当前实现。
- 官方文档页面包含当前站点导航和产品信息，未将其当作固定 commit 的实现证据。
- 没有运行 Codex 构建或完整测试；依赖、平台沙箱、认证和外部服务均未做运行时验证。
- app-server、TUI、plugins 的大文件只读取了入口和关键路径，未读部分在覆盖率表中保留。

## 4. 覆盖率口径

覆盖率使用“本次实际请求的源码行范围 / 纳入该逻辑模块的生产代码行数”估算；测试、lock、生成文件和明确排除的外围 crate 不进入模块分母。由于超大型仓库不可能在一次 standard 基线中逐行阅读，报告将“模块覆盖率”和“全仓库覆盖率”严格区分。

## 5. 结论

本次结果是可复核的 bounded standard baseline，不是全仓库形式化证明。所有未能由固定 HEAD 直接支持的产品背景均标为“背景”或“待验证”。
