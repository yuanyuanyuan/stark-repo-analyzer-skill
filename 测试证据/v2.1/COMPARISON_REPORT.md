# v2.1 与 v2.0 证据对比

| 项 | v2.0 | v2.1 |
|---|---|---|
| 目录 | `测试证据/v2.0` | `测试证据/v2.1`（新建，不覆盖 v2.0） |
| 目标仓 commit | bdee20b… | 相同 bdee20b… |
| 模式 | quick/standard/deep 历史三套 | 本轮主交付 **standard** |
| doctor→units | 有 | **本轮重跑** 有 |
| evidence-plan | degraded | **degraded（重写）** |
| module-evidence | 有 | **重写 src.json** |
| report.md | 有 | **重写** |
| gate | blocked（parallelism+质量） | blocked（parallelism+parse+refs） |
| ANALYSIS_REPORT | 历史存在（旧 gate 时代样例） | **本轮无**（gate 未放行，正确） |
| 总判定 | 部分通过 | **部分通过** |

## 结论

v2.1 证明：**可以在当前工具链下重跑 standard 工件链并留下可审计人工分析**；  
仍不能证明 multi-agent 完整通过，也不能在 parse/refs 不达标时合成最终 ANALYSIS_REPORT。

## multi-agent 轮补充

新增目录 `standard-multiagent/`：

- 证明 **parallelism: active** 可被 gate 接受
- 不证明 parse/reference 质量达标
- 与 `standard/` degraded 轮并存，便于 diff 验收口径
