# V1 固定 Graphify code-only

## 决策

当前 V1 将 Graphify 固定为 `0.9.13+` 的 `graphify extract <target> --code-only --no-cluster --out <WORK_DIR>`。V1 不调用 semantic extraction、LLM provider、模型探测或 semantic chunking。`cluster-only --no-label --no-viz` 只负责本地社区/报告整理，不改变这一边界。

## 原因

此前的 semantic extraction 在大型仓库上引入了 provider 配置、响应格式、分块进度和长时间无产物等非确定性失败。V1 的职责是为源码阅读提供可审计的结构导航，而不是让 Graphify 代替 Agent 解释业务语义。code-only 把网络、密钥和模型输出从强制路径移除，缩小了失败面并使 baseline 更容易复现。

## 证据边界

- `graphify-code-only` 只证明本地代码结构候选、来源位置和社区导航，不证明业务意图、运行时行为或跨文件关系全部正确。
- 源码阅读 Agent 仍负责模块边界、Why > What、交叉验证和最终报告。
- raw 产物命名为 `raw-code-only-graph.json` 与 `raw-code-only-GRAPH_REPORT.md`，不得伪装成 `raw-deep-*`。
- 旧 semantic physical/reference runs 保留为历史对照，不计入当前 V1 code-only P4 结果。

## 取代关系

本决策取代 ADR-0004、ADR-0005、ADR-0007、ADR-0010、ADR-0013 和 ADR-0015 中关于当前 V1 执行方式的假设。这些文件继续作为早期 semantic 设计的历史记录保留，不做删除。
