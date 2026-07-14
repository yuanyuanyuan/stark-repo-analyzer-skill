# 代码地图导航 Roadmap

状态：`completed`

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义本仓库「产品功能 → 职责分层 → 源码入口」代码地图的方向、非目标、阶段与完成口径；不记录逐文件执行 |
| 当前状态 | `completed`；M0–M3 + 独立 Judge pass |
| 当前结论/入口 | 设计共识已在 grill 会话锁定；配对 [exec plan](../exec-plans/code-map-navigation-plan.md)；ADR-0027 已 accepted |
| 何时读取 | 准备落地或修改代码地图、相关 dev-rule、AGENTS 导航或 code-map hook 时 |
| 何时更新 | 目标、非目标、阶段或退出条件变化时 |
| 关联真源 | 术语见 `CONTEXT.md`（代码地图）；执行见 plan/progress；规则见拟议 `docs/dev-rules/code-map/`；决策见拟议 ADR-0027 |

## 北极星目标

让 Agent 与维护者在接到任务后，先通过稳定的代码地图定位「读哪、改哪」，而不是盲猜或全仓遍历搜索；并用 dev-rule + 提醒型 hook 保证地图在边界变更后可维护、不过期后无人理会。

## 非目标

- 不把代码地图打进 Skill 核心交付包，也不作为用户分析目标仓库的交付物。
- 不让 Graphify `graph.json` 成为功能语义真源，也不默认从图谱自动生成整份 `map.yaml`。
- 不用 PreToolUse 因地图过期而 deny 编辑；hook 只提醒。
- 不改变 analyzer 产品行为、真实 UAT 证据等级或 Graphify gate 合同。
- 不在 `AGENTS.md` 堆叠地图细则或全量路径清单。
- 不建立双真源（手写 Markdown 全表 + YAML 各维护一份路径）。

## 可观察成功标准

1. 存在唯一语义真源 `docs/code-map/map.yaml` 与阅读入口 `docs/code-map/README.md`。
2. `docs/dev-rules/code-map/` 规定更新触发、无影响声明、Graphify 协助边界与 hook 行为。
3. `AGENTS.md` 提供任务导向导航：理解目标后、大范围搜索/改文件前先查 code-map。
4. 仓库 `.codex/hooks` 在 `PostToolUse`（edit 类）与 `Stop` 对监控路径变更且未同步 `map.yaml` 时发出 `systemMessage` 提醒。
5. ADR-0027 记录「YAML 语义真源 + Graphify 只读协助 + 提醒 hook」的权衡。
6. 初版地图约 8–15 条 feature（档 B），`entrypoints` 指向仓库内真实路径，覆盖主要产品与 dev 能力。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| M0 合同冻结 | 冻结术语、ADR、dev-rule 骨架与 schema | `CONTEXT.md` 术语、ADR-0027、`docs/dev-rules/code-map/` 与设计共识无冲突；目录索引已登记 |
| M1 地图初版 | 可导航的 `map.yaml` + README | 约 10 条 active feature；路径抽查真实存在；与 Graphify 只读核对无强制自动化写入 |
| M2 导航与 hook | AGENTS 导航 + 提醒 hook | `AGENTS.md` 可路由；PostToolUse/Stop 可对「改监控路径未改 map」给出提醒；不 deny 编辑 |
| M3 验证与收口 | 文档联动、控制面校验、独立 Judge | 链接/索引完整；约定测试或夹具通过；Worker 自验 + 独立 Judge；未执行项如实记录 |

## 完成口径

本 roadmap 完成时：代码地图可被任务定位使用，维护规则与提醒 hook 已落地，架构决策有 ADR，且通过独立 Judge。不要求真实回归 UAT（产品分析行为未变）。不要求 hook trust 在所有宿主上已由用户点击确认（需在 progress 记录宿主侧信任步骤）。

## 主线总结

本 initiative 解决的是**本仓库协作导航**，不是分析器产品能力。语义在 `map.yaml`，结构证据仍归 Graphify，规则在 dev-rules，提醒在 Codex hooks。当前为 `completed`。
