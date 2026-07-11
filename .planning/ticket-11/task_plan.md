# Task Plan: ticket 11 · standard/deep modes + rules-based tools

## Goal
落地 v2.2 双模式合同（仅 standard/deep）与 rules-based 工具策略，并开出含详细测试证据的 PR。

## Current Phase
P6 Loop complete

## Phases

### P0 Restore
- [x] 读 ticket / memory / execution prompt
- [x] 避坑要点写入 findings
- **Status:** complete

### P1 Goalpro+G1
- [x] Goal + Loop 产出
- [x] G1 用户选 ① 批准
- **Status:** complete

### P2 Meta route+G2
- [x] planning-with-files 初始化
- [x] G2：按合同执行；用户覆写不建 feat/11，在当前分支交付
- **Status:** complete

### P3 Branch+Implement
- [x] 用户覆写：不建 feat/11，在当前分支 yuanyuanyuan/spec-v2.2-standard-deep-modes-and-rules-based-to 交付
- [x] owner 持 $implement 实现 AC1–8
- **Status:** complete

### P4 Review+Verify+UAT
- [x] code-review
- [x] npm test + typecheck
- [x] UAT local-cli 逐步 AC
- **Status:** complete

### P5 G3+PR
- [x] push + gh pr create（body 含 3.8.1 证据）
- **Status:** complete
- PR: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/pull/18

### P6 Loop
- [x] 强制 Loop + memory + planning 收束
- **Status:** complete
- Decision: Done（无阻塞 residual；AC4 类历史并行验收不在本票）

## Key Questions
1. deep 能力如何检测：Graphify 优先 + 能力矩阵，而非固定三件套？
2. standard 路径如何保证忽略增强工具（即使 env 注入）？
3. 报告元数据落在哪些工件（doctor / units / gate / summary）？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| G1 批准 Goal+Loop | 用户回复 ① |
| planning 目录 `.planning/ticket-11/` | 编排强制隔离多票 |
| branch `feat/11` | branch_prefix + ticket_id |
| weapon `$implement` | 编排合同；allow_meta_degraded=false |
| Evolution none-with-reason | 产品票 out_of_scope_for_ticket_pr_pipeline |
| 不建 feat/11 | 用户 G2 覆写；当前分支交付 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       |         |            |

## Notes
- requirement_ref: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/11
- tickets_path: docs/agents/tickets/issue-11.md
- acceptance_env: local-cli
- uat_runner: agent / session-user
