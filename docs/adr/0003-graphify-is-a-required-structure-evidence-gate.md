---
status: superseded
superseded_by: ADR-0021
---

# Graphify 是强制结构证据闸门

> 此决定已被 [ADR-0021](0021-guide-graphify-installation-and-allow-compatibility-fallback.md) 取代。以下正文保留历史原貌。

V1 的最小纵向链路在规模扫描之前必须成功构建并验证 Graphify 图谱；图谱缺失、为空或健康检查不可用时，该次分析中止，不能静默降级为普通源码分析。Graphify 只提供结构导航和待验证线索，核心执行路径、关键边界与跨模块契约仍必须通过源码阅读确认。

## 影响

- `click` 试点必须先证明能拒绝空图，再证明能接受含有效节点、边和社区的图谱。
- 图谱的证据等级、输出契约和源码交叉验证属于 V1 规格，不能在实现完成后补充。
- Graphify 失败会成为正式的运行失败状态，并写入 metadata、日志和检查表。
