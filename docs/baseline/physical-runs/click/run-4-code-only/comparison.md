# Click code-only V1 对比结果

对比对象：

- 原始 reference：`docs/baseline/reference-runs/click/`
- 新 V1 pilot：本目录 `run-4-code-only/`
- 源码：同一固定 HEAD `b67832c2167e5b0ff6764a8c04a0a9087e697b5a`

## 结果摘要

新 V1 在“可复核的标准基线执行”上明显优于原始 reference：Graphify 结构侧车、doctor
健康门、真实 subagent 分配、任务状态和最终合同校验都已经形成闭环。它没有证明语义
结论自动更准确，因为 code-only Graphify 只提供结构导航，Why 分析仍来自源码阅读和
主 agent 交叉验证。

| 维度 | 原始 reference | 新 V1 code-only | 判断 |
|---|---|---|---|
| Graphify | reference 目录没有 Graphify/doctor 证据 | Graphify 0.9.13；raw 1910 nodes/3916 edges，normalized 1907/3916；两阶段 doctor PASS | 新 V1 可复核性更强 |
| LLM/semantic extraction | 未形成可审计的禁用边界 | `--code-only --no-cluster`，semantic extraction disabled，backend/model 为 null | 新 V1 更确定、无模型等待 |
| subagent | `checks.md` 明确记为未执行 | 4 个独立 subagent 均 completed；`06-module-tasks.json` 已回写 completed | 新 V1 完成了 skill 的并行要求 |
| 核心阅读覆盖率 | 100% | 100% | 持平 |
| 次要阅读覆盖率 | 77.7% | 77.7% | 持平；平台分支仍需明确限制 |
| 最终报告 | 104 行，8.9 KB | 913 行，约 74.5 KB | 新 V1 细节明显更多，但长度本身不是质量证明 |
| 阶段 7/8 产物 | 有草稿和报告 | 有源码裁决、Graphify 边界、覆盖率汇总、洞察和合同 manifest | 新 V1 证据闭环更完整 |
| 动态验证 | 未运行完整 pytest/真实 shell/Windows | 同样未运行 | 未改善，保持诚实限制 |

## 质量结论

1. **最强的改进是执行确定性。** Graphify 从语义/LLM 路径改为本地 code-only，运行时间
   约 3.23 秒，且 raw graph、normalized graph 和 source references 都被保存。doctor
   能在 preflight/post-graph 两处阻止空图或不可定位图继续进入分析。
2. **最强的报告改进是可追溯性。** 新报告把四个业务模块、源码路径/行号、跨模块裁决和
   覆盖率边界集中归档；原始 reference 的核心洞察仍然保留，但新报告不再依赖“没有
   Agent 工具”的降级说明。
3. **没有夸大 code-only 的能力。** Graphify 仍产生 inferred/community 关系，且有 94
   个 normalized 节点没有可定位 symbol source reference；这些只作为导航风险，不作为
   架构事实。Windows、真实 shell、pager/editor 和竞品实现级比较仍未完成。

## 下一步判定标准

Click pilot 可以作为扩展到完整 standard baseline 的通过样本。扩展到其他项目时，至少
需要保持：Graphify 两阶段 doctor PASS、code-only 产物完整、subagent task manifest 全部
completed、核心/次要覆盖率门槛通过、阶段 7/8 草稿无 pending，以及源码仓库保持只读。
