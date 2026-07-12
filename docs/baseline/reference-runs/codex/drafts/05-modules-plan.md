# 05 Modules Plan：按业务功能组织报告

## 模块清单

### 核心模块

1. **Session/turn orchestration**：把 submission 变成会话状态、上下文、采样、工具循环和事件。
2. **Execution safety boundary**：把命令/补丁请求转换为审批、策略判断和平台沙箱执行。
3. **CLI/TUI user loop**：把命令行参数、终端输入、事件流和可视化状态接到核心 runtime。

### 次要模块

4. **Protocol/event contract**：定义跨 crate、TUI、app-server 和 SDK 的请求、事件、权限数据结构。
5. **App-server integration**：把 thread/turn 请求转换为核心 session 操作，并通过 JSON-RPC/transport 暴露。
6. **Extensibility**：MCP、skills、plugins 的发现、加载、注入和刷新。

## 报告大纲

1. 场景化问题与定位
2. 一次 coding turn 的全景
3. Session/turn：可恢复、可 steer 的 agent 状态机
4. Execution safety：模型能力与主机副作用之间的闸门
5. CLI/TUI：事件驱动的终端交互层
6. Protocol/app-server：把同一 runtime 变成可复用服务
7. MCP/skills/plugins：扩展能力如何进入上下文
8. 亮点、问题、替代方案和重设计建议

## 叙事线

\`CLI/TUI 输入\`
→【需要一个不依赖展示层的长期会话】
→ \`Session/turn orchestration\`
→【模型返回 tool call，副作用必须先通过策略与沙箱】
→ \`Execution safety boundary\`
→【执行结果和模型输出必须被不同客户端一致消费】
→ \`Protocol/event contract\`
→【程序化客户端需要请求/响应生命周期】
→ \`App-server integration\`
→【能力需要可发现、可配置、可注入】
→ \`MCP/skills/plugins\`

## 全局设计哲学

Codex 不是把功能堆在 CLI 中，而是围绕“核心 runtime + 显式事件 + 受控执行”组织边界。模块间的自然接口是 \`Submission -> Event\`，安全模块作为工具执行前的策略闸门，客户端只负责把事件翻译成用户体验。
