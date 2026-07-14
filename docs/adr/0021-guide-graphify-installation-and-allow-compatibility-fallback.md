# 引导安装 Graphify 并允许原版兼容流程

Agent 检测到 Graphify 缺失或版本不兼容时，只提供官方安装或升级指引，不代替用户修改本机环境；用户暂不安装时，可以显式进入参考 repo-analyzer 的纯源码兼容流程，并在结果中标记没有 Graphify 导航增强。若兼容 Graphify 已可用且增强流程已经开始，建图为空、产物无效或来源不可定位仍必须终止，不能用兼容流程掩盖真实的 Graphify 执行失败。

## 取代关系

本决定取代 ADR-0003 中“Graphify 不可用时也禁止回退”的全局强制语义，以及 ADR-0013 中“Agent 可自动安装或升级 Graphify”的 Bootstrap 语义。

## 影响

- Graphify 是增强流程的必需项，不再是基础 repo-analyzer 可用性的绝对前提。
- 安装行为始终由用户执行；Agent 负责诊断、展示指引，并让用户明确选择安装后复检或仅本次进入原版兼容流程，不能自动回退。
- 兼容流程必须可见且可审计，不能声称使用了 Graphify，也不能生成伪造的 Graphify 产物。
- 兼容流程保留 `standard` 与 `deep` 的覆盖率和交互合同，唯一能力差异是没有 Graphify 导航 map。
