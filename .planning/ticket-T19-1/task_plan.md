# Task Plan · T19-1

- ticket_id: T19-1
- title: Insight Probe 结构化产物与 Process Gate
- requirement_ref: docs/specs/v2.2-beats-v1.0-insight-probes-delivery.to-spec.md
- parent_issue: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/19
- branch_policy: user override — **不新建分支**；在当前 `yuanyuanyuan/spec-v2.2-standard-deep-modes-and-rules-based-to` 交付
- Current Phase: P5 G3+PR
- updated: 2026-07-11

## Phases

| Phase | Status | Notes |
|-------|--------|-------|
| P0 Restore | complete | ticket/memory/spec/gate 现状已读 |
| P1 Goalpro+G1 | complete | G1 用户 a 批准 |
| P2 Meta route+G2 | complete | no_branching_choice；owner=main-thread + $implement；verification=npm test+typecheck |
| P3 Branch+Implement | complete | 无新建 branch；gate+schema+tests 已落地 |
| P4 Review+Verify+UAT | complete | code-review 无高危；npm suites 绿；机械 UAT 过 |
| P5 G3+PR | in_progress | 准备 commit + PR |
| P6 Loop | pending | |

## Goal (locked draft, pending G1)

交付机械层 Insight Probe 产物合同：`insight-probes.json` 最小 schema + Catalog 三类 id + gate 检查 `insight-probe-process`；合法 miss 不挡门；单测覆盖缺文件/缺类/非法 status/三类 miss。

## Non-goals

- 不实现 LLM 探针判定
- 不改 T19-4 Synthesis/Degraded 写稿语义
- 不实现 T19-2/3/4/5
- 不宣称 Beats-v1.0

## Decisions

- branch: 用户会话覆写「不需要新建分支」→ 跳过 feat/T19-1 创建
- dirty tree: CONTEXT.md / docs/adr / issue-19 tickets / to-spec / T19-1 prompt 视为 #19 需求材料，纳入本票提交（非无关脏树）
- owner: main-thread + $implement（无独立 execution owner 可派发时）
- verification: npm test + typecheck；机械 UAT 按 AC 核对
