---
status: superseded
superseded_by: ADR-0016
---

# Graphify 自动探测必需的 LLM 引擎

> 此决定已被 [ADR-0016](0016-graphify-code-only-v1.md) 取代。以下正文保留历史原貌。

每次 `stark-repo-analyzer-skill` 分析都要求 Graphify 自行判定当前环境是否存在可用 LLM 引擎；技能不写死 DeepSeek，也不自行复制或猜测 Graphify 的后端优先级。DeepSeek 只是 Graphify 支持的候选之一，模型与端点仍由 Graphify 的标准环境变量和 provider 配置决定。

## 备选方案

- 固定 `DEEPSEEK_API_KEY` 与 `GRAPHIFY_DEEPSEEK_MODEL`：拒绝，因为会掩盖 Graphify 已支持的自动探测和其他后端。
- 沿用 Graphify 对纯代码仓库的无 LLM AST 快路径：拒绝，因为本技能要求每次分析具备可用语义引擎，即使当前语料恰好只触发 AST 提取。

## 影响

- LLM 就绪检查必须委托 Graphify 的探测逻辑；探测失败是正式失败状态，不得静默只运行 AST。
- 运行 metadata 必须记录 Graphify 实际选中的 backend、model、版本与是否使用受信任自定义 provider，但不得记录密钥。
- 项目本地 provider 配置只能遵循 Graphify 的明确授权机制加载，避免由被分析仓库控制语料和密钥的去向。
