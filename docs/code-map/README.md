# 代码地图

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 说明如何阅读与使用本仓库代码地图；不复制全量路径真源 |
| 当前状态 | `active`（语义真源为 `map.yaml`） |
| 当前结论/入口 | 先读本页 60 秒用法，再打开 [`map.yaml`](map.yaml)；维护规则见 [`docs/dev-rules/code-map/`](../dev-rules/code-map/) |
| 何时读取 | 理解任务后、大范围搜索或跨模块改文件前；登记新功能入口时 |
| 何时更新 | 功能入口、职责分层或 `watch_paths` 变化时改 `map.yaml`；规则变化改 dev-rule |
| 关联真源 | 语义 → `map.yaml`；规则 → dev-rules/code-map；决策 → [ADR-0027](../adr/0027-repo-code-map-with-graphify-assist-and-reminder-hooks.md)；术语 → `CONTEXT.md` |

## 它解决什么问题

接到开发任务时，先定位「读哪、改哪」，而不是从仓库根盲目 `rg`/遍历。
代码地图只服务**本仓库**协作；分析用户目标仓库时不要输出或依赖这里的 map。

## 60 秒用法

1. 用一句话写出任务目标（例如「改 Graphify 健康门失败语义」）。
2. 打开 [`map.yaml`](map.yaml)，在 `task_hints` / `summary` 里匹配 feature。
3. 只打开命中 feature 的 `layers.*.entrypoints`；需要结构关系时再查 Graphify。
4. 若改动触及该 feature 的 `watch_paths` 且导航语义变了，同一交付内更新 `map.yaml`；未变则写 `code-map 无影响：…`。

## 职责层（五层）

| layer id | 含义 |
|---|---|
| `product-entry` | 触发与说明入口 |
| `contracts` | 可依赖合同/schema |
| `runtime` | 实际执行代码 |
| `control-plane` | 开发方向与协作规则 |
| `verification` | 测试与护栏 |

同一 feature 跨多层是正常的：产品入口、合同、实现、规则、验证应能对照，而不是只给一个文件。

## 与 Graphify / Skill 包

- Graphify：只读协助发现路径，不自动重写本 map。
- Skill 核心包：`tools/release/core-package-files.txt` **不得**因本地图而加入 `docs/code-map/`。
- Hook：`.codex/hooks/code_map_gate.py` 仅提醒同步，不拦截编辑。

## 初版覆盖

档 B：约 12 条 `active` feature，覆盖 Skill/gate/合同/分发、文档控制面、质量门与 Judge、UAT 规则、控制面 hook、代码地图自身、领域语言与文风。缺入口时先补 YAML，再改代码。


## 常见任务 cheat sheet

任务类型 → 优先命中的 feature（路径以 `map.yaml` 为准，本表不另建真源）：

| 任务 | feature id | 先打开 |
|---|---|---|
| 改 Skill 触发/默认流程 | `repo-analysis-skill` | `skills/repo-analyzer/SKILL.md` |
| 改 Graphify gate / 退出码 | `graphify-gate` | `skills/repo-analyzer/scripts/graphify_gate.py` |
| 改输入输出合同 | `repo-analysis-skill` / contracts 层 | `docs/spec/input-output-contract.md` |
| 改默认 Judge / 审查包 | （见 dual-agent 相关 feature） | `docs/dev-rules/dual-agent-review/README.md` |
| 改代码地图 / hook | `code-map-navigation` | `docs/code-map/map.yaml` |
| 改 Agent 导航脚手架 / product-map / harness 校验 | `agent-harness-navigation` | `docs/spec/product-map.md`、`docs/dev-rules/workflows/`、`tools/release/validate-agent-harness.py` |
| 改发布 SOP / 安全扫描 | 见 version-release 相关入口 | `docs/dev-rules/version-release/README.md` |

## 主线总结

`map.yaml` 是唯一语义真源；本 README 教人怎么用。先匹配 feature，再按五层打开 entrypoints，最后按规则决定是否更新地图。
