# Agent Harness 渐进披露 Roadmap

状态：`completed`

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义吸收 video-know-it harness 设计思想、优化本仓 Agent 冷启动与渐进披露的方向、非目标、阶段与完成口径；不记录逐文件执行 |
| 当前状态 | `completed`；配对 [exec plan](../exec-plans/agent-harness-progressive-disclosure-plan.md) 已收口 |
| 当前结论/入口 | grill-with-docs 共享理解已锁定；配对 plan 为执行真源 |
| 何时读取 | 实施或审查本 initiative、改 Agent 导航脚手架时 |
| 何时更新 | 目标、非目标、阶段或退出条件变化时 |
| 关联真源 | 术语见 `CONTEXT.md`；执行见 plan/progress；决策见 [ADR-0028](../adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md)；规则见 `docs/dev-rules/workflows/` 与 `agent-boundaries/` |

## 北极星目标

让 Agent 打开仓库后靠短路由与「一个问题进一个文件」快速开工，而不是通读全部 dev-rules 或全仓盲搜；同时保留本仓 document-control、双角色 Judge、质量门与 YAML 代码地图，不平行引入 `docs/ai-harness/`。

## 非目标

- 不新建与现有权威层平行的 `docs/ai-harness/` 包。
- 不削弱或替换 Worker / Judge / Orchestrator、roadmap/plan 状态机或真实回归 UAT 证据上限。
- 不改变 analyzer 用户可见分析行为合同（本轮只加导航与协作脚手架）。
- 不把 harness 导航文件或校验器打进 Skill 核心交付包。
- 不在 `AGENTS.md` 堆叠细则正文；不建常青 evidence-map 百科。
- 不默认用 PreToolUse 硬拦截编辑来强制 harness 校验。
- 本轮不要求真实回归 UAT 或公开发版。

## 可观察成功标准

1. 存在 Product Map、workflows、agent-boundaries，且 `AGENTS.md` / 目录 README 可路由到它们。
2. 存在独立 `tools/release/validate-agent-harness.py`，改导航相关文件或本 initiative 收口时必须可 exit 0。
3. ADR-0028 记录「分散补强、不平行 ai-harness」的权衡。
4. `CONTEXT.md` 含 Agent Harness、Product Map、Harness 契约校验术语。
5. `map.yaml` 登记 feature `agent-harness-navigation`；code-map README 含开发 cheat sheet 一行。
6. 完整门 + 独立 Judge pass 后 plan 才可 `completed`；Judge pass ≠ 真实回归 UAT。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| H0 合同冻结 | 控制面、ADR、术语、索引 | roadmap/plan active；ADR-0028；CONTEXT 术语；目录索引登记 |
| H1 导航三件套 | product-map / workflows / agent-boundaries + AGENTS 路由 | 文件存在；B1 按任务加载语义写清；相对链接可用 |
| H2 校验与地图 | harness 校验器 + 单测 + map feature + cheat sheet | 校验 exit 0；entrypoints 存在；不进核心包 |
| H3 收口 | Worker 自验 + 独立 Judge + control-plane audit | awaiting-judge → Judge pass/豁免 → completed；未执行项如实记录 |

## 完成口径

脚手架可导航、可机读校验、有 ADR 与术语，且通过独立 Judge。不要求真实回归 UAT。不要求 hook 硬拦截。

## 主线总结

吸收的是 progressive disclosure 与 harness 契约门，不是 video 的目录名或产品硬规则。语义分散落在现有权威层；冷启动靠短路由与按任务加载。
