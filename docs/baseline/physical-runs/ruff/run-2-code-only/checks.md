# Checks

- [x] 输出目录包含标准阶段草稿。
- [x] 源码 HEAD 与固定值一致：`c588a3f7f57461692652d339936222b4496c5953`。
- [x] 源树 clean：`git status --short --branch` 仅显示分支信息，无工作区变更。
- [x] Graphify code-only guard：semantic extraction disabled；58118 nodes / 152791 edges / 5098 code files。
- [x] `doctor-post-graph.json` status ready，failures 为空。
- [x] 报告明确 bounded scope，未声称全仓库覆盖。
- [x] 报告中文、含 Mermaid、含路径/行号证据。
- [x] code-only Graphify 与 semantic Graphify 的差异已说明。
- [ ] 外部网络研究：not performed。
- [ ] Git history：not performed。
- [ ] build/test：not performed。
- [ ] P5 动态行为：excluded。
- [ ] subagent：not performed；无调度能力，不伪造并行结果。

## 覆盖率口径

数字只针对通过读取命令实际读取的文件行范围；Graphify 节点/边不是源码行覆盖率。仓库总行数包含测试和生成边界，因此仅作规模参考。
