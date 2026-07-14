# 源码裁决 Graphify 冲突

Graphify 只作为结构导航层：`EXTRACTED` 关系仍需验证核心路径，`INFERRED` 必须标为待验证，`AMBIGUOUS` 只能作为风险或疑问。任何图谱与源码不一致的发现必须写入 `drafts/07-cross-validation.md`；最终架构结论以源码和可定位的一手文档为准，不能直接复述 `GRAPH_REPORT.md` 或图谱推断。

## 影响

- 模块任务必须拿到相关 Graphify context，但仍要阅读核心源码主线。
- 最终报告只能将已验证的图谱发现转写为结论；未验证关系保留在限制或风险中。
- 交叉验证成为图谱层与报告层之间的强制质量门，而非可选润色。
