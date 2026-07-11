# Findings · ticket 11

## Requirements
- 仅 standard/deep；默认 standard；清除 quick
- standard：基线工具 only；忽略 Graphify/Ctags/ast-grep；heuristic 披露
- deep：能力门禁 graph queries / symbol enumeration / reference edges；缺能力拒绝不降级；可诊断无分析报告
- local rules SSOT + 官方源元数据
- doctor 能力矩阵 + AI 安装 prompt（不改被分析仓）
- 报告/gate 与模式合同一致；测试钉 CLI 行为

## 避坑要点（memory ≤3）
1. PR body 必须 command + log excerpt，不能只写 pass
2. UAT 按 test_plan.uat local-cli AC；勿把 ANALYSIS 当 UAT
3. 勿把 historical parallel degraded 误写成 standard/deep 完整通过

## Research Findings
- 当前 `src/budgets.js` 仍含 quick；`budgetFor` 错误文案列出三模式
- `src/doctor.js` 将 symbol-enumerator 设为 **required=true**，与「standard 可无增强工具」合同冲突
- doctor 无 capability matrix / 安装 prompt / mode availability 输出
- gate/tests 大量 quick 期望（semantic review 全局 2-3、parallelism degraded 等）
- e2e 仍覆盖 quick 路径
- 尚无 `rules/` 目录与 official source 元数据
- CLI 无 mode 门禁（除 gate --mode）；scan/units 始终依赖 requireDoctor（要求 enumerator）

## G1 决策摘要
- 用户：① 批准 Goal+Loop
- 时间：2026-07-11

## Technical Decisions（草案，待 G2 锁定）
| Decision | Rationale |
|----------|-----------|
| doctor 按 mode 评估 | standard 只需基线；deep 才要求三能力 |
| deep 不降级 | fail-closed；诊断工件 ok，分析报告 no |
| rules 目录可分发 | 执行策略 SSOT，SKILL 引用 |
| 去 quick 时改 budgets/gate/tests/docs | 支持面清零 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- docs/agents/tickets/issue-11.md
- docs/agents/execution-prompts/11.md
- src/{cli,budgets,doctor,gate,scan,units,common}.js
- test/{doctor,gate,e2e}.test.js

## G2 决策摘要
- 用户：建议 1（按合同执行），但不用建分支
- 影响：在 `yuanyuanyuan/spec-v2.2-standard-deep-modes-and-rules-based-to` 直接实现与 PR
- 时间：2026-07-11
