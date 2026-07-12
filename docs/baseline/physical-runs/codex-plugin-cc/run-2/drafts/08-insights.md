# 阶段 8：架构洞见

## 设计哲学

这个插件最鲜明的选择是**不把 Claude 和 Codex 折叠为一个模糊的代理层**。Claude 命令承担用户交互和宿主后台能力；Codex App Server 承担模型回合、thread 与 review；本地 state 则把长任务变成可恢复的产品对象。其收益是每种身份都有唯一所有者，代价是跨进程状态必须具备比普通 CLI 更严格的一致性。

## 真正的亮点

1. **传输与回合语义分离。** JSON-RPC client 只保证 framing/request，而 `TurnCaptureState` 将乱序通知、协作子 agent、最终消息和文件变化聚合为用户的一次回合（`lib/app-server.mjs:57-176`; `lib/codex.mjs:303-610`）。这避免了将“最后 stdout”误当完成信号。
2. **共享运行时不是硬依赖。** broker 不可达或 busy 时按精确故障回落直连（`lib/codex.mjs:613-642`）。这把性能优化从可用性前提降为可选加速，符合桌面插件环境的脆弱性现实。
3. **审查与修复显式分离。** review commands 保持只读；rescue 是另一条显式写入路径；Stop gate 用小协议阻断而不在 hook 内重现复杂审查渲染。该分离降低“审查 agent 顺手改代码”的责任混乱。

## 优先改进项

1. **先持久化、后 spawn。** 先原子落盘 queued job，再启动 worker；spawn 失败时把同一记录转 failed。它消除最直接的启动竞态。
2. **为终态写入定义单写者或 CAS。** 使用 revision 字段与 compare-and-swap，或由 broker 串行化 cancel/worker completion；并把 cancelled 定义为不可被普通 completion 覆盖。否则 result/status 不具可信性。
3. **将 state 写入改为原子替换并锁定。** 当前 `saveState`、job file 与 broker session 都是直接 `writeFileSync`（`state.mjs:92-115,166-170`; `broker-lifecycle.mjs:89-93`）。多进程读改写会产生丢失更新或半写风险；临时文件 + fsync + rename 与 per-workspace lock 更匹配该设计的并发模型。
4. **把命令契约从 Markdown 部分机械化。** 当前 Markdown 与 companion handler 同时编码 flags/后台规则。机器可读 manifest 生成公共段落，可减少命令文档、参数解析和文本测试漂移。

## 评价

对一个从 Claude Code 协作到 Codex 的小型插件而言，分层与测试意图已经相当成熟，尤其对 review-only 边界和结构化对抗审查的处理克制且可靠。主要短板不是“功能少”，而是其最有价值的承诺之一，即后台任务可追踪/可取消，仍建立在无锁多写者 JSON 状态之上。随着并发后台任务、取消和 SessionEnd 清理同时发生，这会从边缘缺陷变成架构债务。
