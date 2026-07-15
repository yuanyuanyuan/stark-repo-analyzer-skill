# Harness 导航清晰度执行计划

状态：`completed`

- 质量门：完整门
- 独立Judge：必须
- 对应 roadmap：[harness-navigation-clarity-roadmap.md](../roadmap/harness-navigation-clarity-roadmap.md)
- 进度记录：[harness-navigation-clarity-progress.md](harness-navigation-clarity-progress.md)
- 关联决策：ADR-0025（已落地基线）、ADR-0028（harness 不平行 ai-harness）

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义导航清晰度 tickets 的顺序、范围、验证与收口 |
| 当前状态 | `completed`；独立 Judge pass + control-plane audit |
| 当前结论/入口 | T1–T5 已实现并提交；等待独立 Judge |
| 何时读取 | 实施或审查本任务前 |
| 何时更新 | 状态、验证或阻塞变化时 |
| 关联真源 | SPEC/tickets 在 `.scratch/harness-navigation-clarity/`；事实见 progress |

## 当前主线

按 tickets T1→T2（T3/T4/T5 并行）修正 ADR-0025 索引、扩展 harness 防回退、绿勾≠ship 表、Graphify 无 wiki 措辞、安装面边界。

## 目标关

### 目标

1. ADR 索引与 skill-distribution completed 事实一致；基线含 0025/0028。
2. harness 校验抓住 0025 回退；单测覆盖红绿路径。
3. 完成语义对照表 + 保留 Judge 硬提醒。
4. Graphify wiki 可选措辞。
5. 安装包 ≠ 仓库基建边界句。

### 非目标

见 roadmap。不发 GitHub Issue；不跑真实回归 UAT。

### 完成条件

- `python tools/release/validate-agent-harness.py` exit 0
- `python -m pytest tests/unit/test_validate_agent_harness.py -q` 通过
- tickets T1–T5 验收点可读于 diff
- 独立 Judge `Verdict: pass` 或合格豁免
- 收口前 `validate-control-plane.py --mode audit` 通过

## 启动关

- 质量门：完整门
- 独立Judge：必须
- 工作区：实现已于 commit `022d7b7` 落地（含先前 harness P0 与本清晰度增量）
- 拥有范围见审查包 `owned_files`

## 任务关

| ID | 内容 | 状态 |
|---|---|---|
| T1 | ADR-0025 索引与基线 | 已做 |
| T2 | harness 防回退 + 单测 | 已做 |
| T3 | 绿勾≠ship 表 | 已做 |
| T4 | Graphify 无 wiki | 已做 |
| T5 | 安装 vs 基建边界 | 已做 |
| CLOSE | 独立 Judge + audit | 完成 |

## 验证关

- 必跑：`validate-agent-harness.py`；`pytest tests/unit/test_validate_agent_harness.py`；`git diff --check`（相对基线）
- 收口：独立 Judge 后 `validate-control-plane.py --mode audit`
- 不跑：真实回归 UAT、发版

## 风险

- 过早把 harness OK 当成 ship → 对照表与硬提醒防误读
- Judge 必须独立重跑廉价检查，不得采信 Worker 数字

## 主线总结

文档与校验防误读；完整门收口走 awaiting-judge → Judge → audit。
