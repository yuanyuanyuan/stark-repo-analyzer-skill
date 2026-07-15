# Code Map · 本仓库代码地图规则

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 规定代码地图的真源、更新触发、无影响声明、Graphify 协助边界与 hook 行为；不承载产品分析合同 |
| 当前状态 | `active` |
| 当前结论/入口 | 语义真源 [`docs/code-map/map.yaml`](../../code-map/map.yaml)；阅读说明 [`docs/code-map/README.md`](../../code-map/README.md)；架构权衡 [ADR-0027](../../adr/0027-repo-code-map-with-graphify-assist-and-reminder-hooks.md) |
| 何时读取 | 修改功能入口/职责分层、维护 map、改 code-map hook，或接到跨模块任务需要定位读改点时 |
| 何时更新 | 更新触发条件、schema 字段、hook 事件或与 Graphify 边界变化时 |
| 关联真源 | 地图正文 → `docs/code-map/`；术语 → 根 `CONTEXT.md`「代码地图」；导航入口 → 根 `AGENTS.md` |

## 一、职责边界

代码地图回答：**做某类任务时，应先读哪、改哪**。它不是：

- 用户分析目标仓库时的交付物；
- Skill 核心交付包的一部分；
- Graphify `graph.json` 的替代品或自动投影；
- 可以阻断编辑的硬门禁。

直觉：地图像大楼的楼层指示牌；Graphify 像详细消防平面图。指示牌写「电梯/卫生间/会议室在哪」，平面图写墙和管道怎么连。类比边界：指示牌过期时仍应允许进门维修，只是需要有人提醒去改牌子。

## 二、真源与 schema

| 路径 | 角色 |
|---|---|
| `docs/code-map/map.yaml` | **唯一语义真源**（feature、layer、entrypoints、watch_paths） |
| `docs/code-map/README.md` | 人类/Agent 阅读说明；不复制可变路径全表 |
| 本规则 | 何时改 map、如何声明无影响、hook 如何提醒 |

`map.yaml` 约定字段：

- `version`：schema 版本整数。
- `layers[]`：职责层（约五层）；`id` / `name` / `summary`。
- `features[]`：可导航功能单元（初版约 8–15 条 `active`）。
  - `id`、`name`、`status`（`active` \| `deprecated`）、`summary`
  - `task_hints[]`：何种任务应命中本 feature
  - `layers`：map layer id → `{ entrypoints: [相对仓库根路径…] }`
  - `watch_paths[]`：变更时需要复核地图的路径前缀或文件

禁止再维护第二份「完整路径 Markdown 表」作为真源。README 可以举例，但以 YAML 为准。

## 三、更新触发

出现任一情况时，**同一交付**内更新 `map.yaml`（或见下一节无影响声明）：

1. 新增、删除或移动产品/开发**功能入口**（Skill 正文、gate 脚本、公开合同、关键 CLI/工具入口）。
2. 功能的**职责分层**变化（例如实现从 skill 脚本迁到 tools，或合同从 README 升为 spec）。
3. 重命名或拆分 feature，导致任务导航会指错目录。
4. 新增需要 Agent 优先定位的跨模块能力，且现有 feature 无法覆盖。

小改（文案、注释、纯测试夹具、与入口无关的实现细节）默认不强制改 map；若 hook 误报，用无影响声明解释即可。

## 四、无影响声明

当改动触及 `watch_paths` 但**不改变**任务导航语义时，允许不改 `map.yaml`，但必须在 progress、PR 或最终回复中显式写：

```text
code-map 无影响：<一句话原因>
```

hook V1 **不解析**自然语言声明，仍可能提醒；人工声明用于审查与收口，不用于自动消警。

## 五、Graphify 协助边界

允许：

- 用 `graphify query` / `path` / wiki 发现候选路径，再人工写入 `map.yaml`；
- 抽查 entrypoints 是否仍存在于结构图或文件系统。

禁止：

- 把 `graph.json` 当作 feature 语义真源；
- 默认 pipeline 从图谱整表生成/覆盖 `map.yaml`；
- 因图谱 dirty 而跳过代码地图维护。

## 六、Hook 行为

实现：`.codex/hooks/code_map_gate.py`，由 `.codex/hooks.json` 挂到：

- `PostToolUse` matcher：`apply_patch|Edit|Write`
- `Stop`

行为合同：

1. 读取 `docs/code-map/map.yaml` 的 `watch_paths` 并集。
2. 从 tool 载荷和/或 `git status` 推断本回合触及的路径。
3. 若触及监控路径且**未**同步修改 `docs/code-map/map.yaml`，输出 `systemMessage` 提醒同步地图或写无影响声明。
4. **不得**因地图过期而 `deny` 编辑或 `continue: false`。
5. 与 `control_plane_gate.py` **并列**，禁止耦合进 control-plane 校验脚本。
6. 宿主未 trust hooks 时提醒不运行；规则与地图仍然有效。

## 七、任务导向加载

Agent 在理解用户目标后、**大范围搜索或跨模块改文件前**：

1. 打开 `docs/code-map/README.md` 与 `map.yaml`。
2. 用任务关键词匹配 `task_hints` / feature `summary`。
3. 只深读命中 feature 的 entrypoints，再按需扩展。
4. 需要结构关系时再查 Graphify；需要产品行为时再读 spec/ADR。

不要把整份 map 背进上下文后仍全仓盲搜。


## 七、与 Product Map / Agent Harness 的边界

- **代码地图**（本规则 + `map.yaml`）：本仓功能→分层→入口。
- **Product Map**（`docs/spec/product-map.md`）：用户分析场景导航；不是本 map 的第二真源。
- **Agent Harness**：短路由 + 按任务加载 + `validate-agent-harness.py`；见 ADR-0028。改 harness 导航文件时跑 harness 校验；改功能入口时仍按本规则更新 `map.yaml`。

## 主线总结

代码地图用 YAML 钉死「功能与入口」，用本规则钉死「何时改、何时声明无影响」，用提醒 hook 降低过期概率，用 Graphify 只做结构协助。它服务本仓库协作定位，不改变产品分析与 UAT 证据等级。
