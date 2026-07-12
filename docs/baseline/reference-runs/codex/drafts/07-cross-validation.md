# 07 Cross-validation：交叉验证

## 验证矩阵

| 结论 | 第一证据 | 第二证据 | 结果 |
|---|---|---|---|
| 核心是 Submission -> Event runtime | core session 的 Codex 队列字段（session/mod.rs:387-398） | protocol 类型在 session 中直接使用（session/mod.rs:360-381） | 通过 |
| turn 是模型/工具循环而非一次请求 | run_turn 主循环（session/turn.rs:143-150、225-370） | turn 前加载扩展和上下文（turn.rs:176-208） | 通过 |
| compact 是模型上下文约束下的一等流程 | pre-sampling compact（turn.rs:798-823） | mid-turn token 检查和 compact（turn.rs:298-370） | 通过 |
| TUI 不是唯一客户端 | CLI 的 TUI/app-server 分发（cli/main.rs:2236-2290） | app-server/MCP 的 codex/event 文档（docs/codex_mcp_interface.md:95-103） | 通过 |
| 权限不应只存在于 UI | protocol 中的 SandboxPolicy/permissions 类型 | SECURITY.md 指向 agent approvals & security | 部分通过，外部安全细节未映射到固定 commit |
| 扩展进入模型上下文 | turn 的 build_skills_and_plugins 调用 | core-skills loader 与 plugins manager 的接口 | 通过 |
| codex-core 有演进压力 | AGENTS.md:72-83 明确提醒避免继续膨胀 | session/mod.rs 大型编排文件 | 通过，问题是维护风险而非功能缺陷 |

## 交叉结论

1. **统一 runtime 得到验证**：TUI、app-server、MCP 文档都围绕同一 Event/EventMsg 和 thread/turn 语义，未发现第二套模型循环。
2. **安全边界是纵向链路**：protocol 表达权限，session 决定调用，执行层实施策略，客户端收集决定；没有证据表明 TUI 可以绕开最终执行器。
3. **扩展与上下文有耦合**：skills/plugins 在 sampling 前注入，这让扩展具备一等能力，也使扩展扫描、缓存和上下文大小成为同一风险面。
4. **规模限制是本轮主要不确定性**：未读的 app-server handlers、平台 sandbox、tool handlers 和 TUI 子模块可能改变局部结论；最终报告只保留已交叉验证的系统级判断。

## 抽查结果

- session/mod.rs:387-398 与 turn.rs:143-150 的队列/循环叙述一致。
- turn.rs:248-295 与 AGENTS.md:91-100 的上下文稳定性要求一致。
- docs/codex_mcp_interface.md:120-127 的审批响应形状与 protocol 权限主题一致，但未逐一追到每个 server handler。
- README.md:1-8 的本地 CLI 定位与公开仓库描述一致；公开描述仅作背景校验。

## 未能验证

- 所有平台（macOS Seatbelt、Linux Landlock、Windows sandbox）的实际等价性。
- 所有 app-server request processor 对错误/取消/恢复的完整行为。
- plugins 与 MCP 刷新在并发 turn 中的所有顺序保证。
