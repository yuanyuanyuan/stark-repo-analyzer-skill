# 用 doctor 作为低侵入的 Graphify 侧车

所有程序化检测集中在 doctor：`doctor.sh preflight` 在建图前检查 Graphify、LLM、路径、工作区和依赖；`doctor.sh post-graph` 在建图后检查产物、JSON、图谱健康、来源与输出隔离。Graphify 只生成 `drafts/01-graphify-map.md` 作为附加导航上下文；参考 repo-analyzer 的阶段、设计逻辑、判断方式和最终报告责任保持不变。

## Consequences

- 原 skill 不新增安装检查、环境诊断、JSON 解析或图谱健康分支；它只在 doctor 成功后的既有工作流中读取 Graphify map。
- preflight 或 post-graph 非零退出码阻断分析，但阻断语义由 doctor 统一定义。
- Graphify 增强可被整体移除或升级，而不需要改变原 skill 的核心流程。
