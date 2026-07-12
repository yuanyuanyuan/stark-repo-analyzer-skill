# 使用 Graphify headless CLI 进行自动分析

自动化和回归流程使用 `graphify extract <target> --mode deep`，在不传 `--backend` 的前提下由 Graphify 自动探测可用 LLM 引擎。执行前通过 Graphify 的探测逻辑做 LLM 就绪预检；执行后以 CLI 退出码、标准错误输出和结构化产物判断成功，交互式 `/graphify` skill 不进入自动化路径。

## Consequences

- metadata 必须记录 Graphify 版本、实际 backend/model、命令形态、退出码与产物路径，但不记录密钥。
- 回归验证只依赖 headless CLI 的可观测行为，避免依赖宿主 Agent 的会话能力。
- Graphify 的 backend 探测顺序属于上游实现；技能只委托和记录，不复制为本地规则。
