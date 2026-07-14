# 仓库 Agent 规则

本文件只做 **AI 协作的导航路由与仓库级入口约束**。
产品行为、质量门细则、命令细节、任务进度和长篇提示词不得堆在这里，统一下沉到对应权威文档。

`AGENTS.md` 是 Agent 打开仓库后的首读入口，必须保留在仓库根目录，不能移入 `docs/`。

## 权威分层（先记住这个）

| 问题 | 去哪里 |
|---|---|
| 怎么写回复/文档/注释 | [`docs/dev-rules/output-style/`](docs/dev-rules/output-style/) |
| roadmap / plan / spec / ADR 怎么读、建、改、收口 | [`docs/dev-rules/document-control/`](docs/dev-rules/document-control/) |
| 轻量门 / 完整门 | [`docs/dev-rules/task-quality-gates/`](docs/dev-rules/task-quality-gates/) |
| Worker / Judge / `awaiting-judge` / completed 护栏 | [`docs/dev-rules/dual-agent-review/`](docs/dev-rules/dual-agent-review/) |
| 聚焦 UAT vs 真实回归 UAT | [`docs/dev-rules/real-uat-regression/`](docs/dev-rules/real-uat-regression/) |
| 版本发布 SOP / checklist | [`docs/dev-rules/version-release/`](docs/dev-rules/version-release/) |
| 发布前密钥/敏感资料扫描 | [`docs/dev-rules/pre-release-security-scan/`](docs/dev-rules/pre-release-security-scan/) |
| 本仓库代码地图（功能→分层→入口） | [`docs/code-map/`](docs/code-map/)、规则 [`docs/dev-rules/code-map/`](docs/dev-rules/code-map/) |
| 开发规则总索引 | [`docs/dev-rules/README.md`](docs/dev-rules/README.md) |
| 文档地图 | [`docs/README.md`](docs/README.md) |
| 产品行为 | `skills/repo-analyzer/`、[`docs/spec/`](docs/spec/)、`CONTEXT.md`、有效 ADR |
| 当前主线状态 | [`docs/roadmap/README.md`](docs/roadmap/README.md)、[`docs/exec-plans/README.md`](docs/exec-plans/README.md) |

不要根据熟悉的文件名自行推断权威性。`docs/archive/` 与 `tests/baseline/` 默认不是活动权威，除非活动 roadmap/plan 明确重新引入。

## 启动顺序

1. 读 [`docs/dev-rules/output-style/README.md`](docs/dev-rules/output-style/README.md)。
2. 读 [`docs/README.md`](docs/README.md)。
3. 读 [`docs/dev-rules/document-control/README.md`](docs/dev-rules/document-control/README.md)。
4. 开发交付前读 [`docs/dev-rules/task-quality-gates/README.md`](docs/dev-rules/task-quality-gates/README.md)；必须 Judge 时再读 [`docs/dev-rules/dual-agent-review/README.md`](docs/dev-rules/dual-agent-review/README.md)。
5. 从 [`docs/roadmap/README.md`](docs/roadmap/README.md) 与 [`docs/exec-plans/README.md`](docs/exec-plans/README.md) 解析生命周期；**只有 `active` 控制面能授权执行**，`completed` 只作背景。
6. 理解任务目标后、**大范围搜索或跨模块改文件前**，读 [`docs/code-map/README.md`](docs/code-map/README.md) 与 [`docs/code-map/map.yaml`](docs/code-map/map.yaml)，按 feature 打开 entrypoints；维护规则见 [`docs/dev-rules/code-map/`](docs/dev-rules/code-map/)。
7. 编辑前执行 `git status --short`，保留用户已有改动。
8. 涉及产品行为时，读 `CONTEXT.md`、[`docs/spec/README.md`](docs/spec/README.md)、[`docs/adr/README.md`](docs/adr/README.md)，再只读相关合同与当前有效 ADR。
9. 涉及 analyzer skill、Graphify gate、输出合同或验收语义时，编辑前读 [`docs/dev-rules/real-uat-regression/README.md`](docs/dev-rules/real-uat-regression/README.md)。
10. 涉及 VERSION/tag/GitHub Release 或公开发版时，执行前读 [`docs/dev-rules/version-release/README.md`](docs/dev-rules/version-release/README.md)（总 SOP/checklist），并按其中顺序完成 [`pre-release-security-scan`](docs/dev-rules/pre-release-security-scan/README.md) 等子门。

## Graphify 路由

When the user types `/graphify`, or when answering codebase structure questions with an existing graph:

- Prefer `graphify query` / `path` / `explain` when `graphify-out/graph.json` exists.
- Dirty `graphify-out/` after hooks or incremental updates is expected; do not skip Graphify only because graph files are dirty.
- Use `graphify-out/wiki/index.md` for broad navigation when present; read `GRAPH_REPORT.md` only for broad architecture review or when scoped queries are insufficient.
- After modifying code, run `graphify update .` (AST-only).

## 输出与文档路由

- 输出风格细则只以 [`docs/dev-rules/output-style/`](docs/dev-rules/output-style/) 为准；本节不重复正文。
- 文档创建/索引/冲突/状态机细则只以 [`docs/dev-rules/document-control/`](docs/dev-rules/document-control/) 为准。
- Prompt 模板在 [`docs/aiprompts/`](docs/aiprompts/)；Prompt 不是产品合同，不能覆盖 dev-rules、活动 roadmap 或验收规则。
- 根 `README.md`（英文）与 `README.zh.md`（中文）是产品入口例外：改产品说明时必须同步两份行为合同。

## 交付与收口路由

- 是否 Delivery Task、轻量门/完整门：[`task-quality-gates`](docs/dev-rules/task-quality-gates/README.md)
- 独立 Judge、`awaiting-judge`、禁止假 `completed`、校验脚本与 Codex hooks：[`dual-agent-review`](docs/dev-rules/dual-agent-review/README.md)
- 证据等级上限：[`real-uat-regression`](docs/dev-rules/real-uat-regression/README.md)
- 打 tag / GitHub Release / 公开发版：[`version-release`](docs/dev-rules/version-release/README.md)（SOP + checklist）；密钥子门 [`pre-release-security-scan`](docs/dev-rules/pre-release-security-scan/README.md)；均不替代真实回归 UAT
- 开发任务结束时，按 document-control / dual-agent-review 报告：主线目标、关键改动、Worker 验证、Judge verdict 或可省略理由、剩余阻塞/未验证项与下一刀。
- Judge `pass` 不等于真实回归 UAT 通过。

## 主线总结

`AGENTS.md` 负责指路，不负责复写细则。先按上表加载最短规则路径，再改代码；细则冲突时以 `docs/dev-rules/` 与产品合同真源为准，并先修权威文档再继续实现。
