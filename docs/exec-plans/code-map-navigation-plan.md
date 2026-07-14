# 代码地图导航执行计划

状态：`completed`

- 质量门：完整门
- 独立Judge：必须
- 对应 roadmap：[code-map-navigation-roadmap.md](../roadmap/code-map-navigation-roadmap.md)
- 进度记录：[code-map-navigation-progress.md](code-map-navigation-progress.md)
- 关键决策：[ADR-0027](../adr/0027-repo-code-map-with-graphify-assist-and-reminder-hooks.md)（accepted）

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义代码地图落地的顺序、所有权、验证与风险；不定义 analyzer 产品合同 |
| 当前状态 | `completed`；重审 Judge 独立重跑 pytest 后 pass |
| 当前结论/入口 | 先 M0 冻结合同与 ADR，再填 map 初版，再挂 AGENTS 与 hook |
| 何时读取 | 实施或审查本 initiative 的任意一刀前 |
| 何时更新 | 任务顺序、依赖、验证方式或阻塞变化时 |
| 关联真源 | 方向见 roadmap；术语见 `CONTEXT.md`；原因见 ADR-0027；事实见 progress |

## 当前主线

M0–M3 与独立 Judge 已完成。成果：YAML 语义地图 + dev-rule + AGENTS 任务导航 + PostToolUse/Stop 提醒 hook；Graphify 仅只读协助。

## 目标关

### 目标

1. 建立本仓库代码地图语义真源与阅读说明。
2. 建立维护规则，使边界变更必须同步地图或声明无影响。
3. 在 AGENTS 中提供任务定位导航，避免盲搜。
4. 用 Codex hooks 提醒 Agent 同步地图，不拦截正常编辑。
5. 用 ADR 固定架构权衡。

### 非目标

- 不修改 `skills/repo-analyzer` 对用户可见的分析行为合同（除非发现地图描述与事实不符时仅改地图/文档）。
- 不把 map 或 hook 打进 Skill 核心交付包清单。
- 不实现 graph→map 自动生成器（可选 suggest 脚本默认不做）。
- 不把 Judge pass 写成产品 UAT 通过。

### 完成条件

1. `docs/code-map/map.yaml` 与 `README.md` 可导航（档 B，约 8–15 feature）。
2. `docs/dev-rules/code-map/README.md` 与 `docs/dev-rules/README.md` 索引已登记。
3. `AGENTS.md` 含权威表/启动按需路由。
4. `.codex/hooks.json` 挂载 `code_map_gate.py`（PostToolUse edit + Stop）。
5. ADR-0027 accepted 并进入 `docs/adr/README.md` 索引。
6. 控制面索引双向链接正确；`validate-control-plane` 与约定测试通过；独立 Judge pass。

## 启动关

### Blindspot Pass

- 当前无 `active` 控制面；本 plan 在 `proposed` 时不得实施产品/hook 代码，激活后才动 M1+。
- 已有 `CONTEXT.md` 中「代码地图」词条来自 grill，必须保留并与 ADR/规则一致，不得回滚为无关改写。
- 现有 `.codex/hooks.json` 已有 Graphify hook-check 与 control_plane_gate；新 hook 必须并列，禁止塞进 control-plane 脚本耦合。
- hook 在未 trust 前可能不跑；progress 需记录「需用户 `/hooks` 信任」为宿主侧步骤，不能假装已全局强制。
- 地图过期提醒可能误报（例如只改测试注释）；dev-rule 允许「code-map 无影响」人工声明，hook V1 不解析自然语言。
- 勿将 `docs/code-map/` 误写入 skill 分发清单或 core-package-files。

### 关键假设

| 假设 | 置信度 | 验证方式 |
|---|---|---|
| Codex 支持对 PostToolUse / Stop 输出 `systemMessage` 提醒 | 高 | 对照 hooks 文档 + 与现有 control_plane_gate 行为一致 |
| 可从 apply_patch/Edit/Write 的 hook 载荷或 git status 推断触及路径 | 中 | 实现后用模拟 stdin 夹具验证 |
| 初版 feature 列表可从现有 skills/docs/tests 树手工归纳 | 高 | 路径存在性检查 |
| 本任务不改变用户分析行为，故无需真实回归 UAT | 高 | 变更范围审查 |

### 工作区基线

- 基线命令：`git status --short`（创建本控制面时执行）。
- 已知已有改动：`CONTEXT.md` 已增加「代码地图」词条（grill 产物），纳入本任务拥有范围。
- 本任务拥有范围（激活后实施）：`docs/code-map/**`、`docs/dev-rules/code-map/**`、`docs/dev-rules/README.md`、`docs/roadmap/code-map-navigation-*`、`docs/exec-plans/code-map-navigation-*`、相关目录 README、`docs/adr/0027-*`、`docs/adr/README.md`、`AGENTS.md`、`.codex/hooks.json`、`.codex/hooks/code_map_gate.py`、必要单测、`CONTEXT.md`。
- 排除：无关用户改动；`vendor/`；skill 运行时行为代码（除非仅只读核对路径）。

## 执行计划

| ID | 动作 | 依赖 | 输出 | 验证 |
|---|---|---|---|---|
| M0 | 冻结 ADR-0027、dev-rule 正文、schema 说明；更新 dev-rules/docs/adr 索引；确认术语 | 控制面 active | ADR、dev-rule、索引 | 链接检查、与 roadmap 共识 diff |
| M1 | 编写 `docs/code-map/map.yaml` 初版 + README；Graphify 只读抽查 | M0 | 可导航地图 | 路径存在；feature 数量约 8–15 |
| M2 | 更新 `AGENTS.md`；实现 `code_map_gate.py` 并挂 PostToolUse+Stop | M1 | 导航 + hook | 夹具/模拟提醒；不 deny；不破坏 control_plane_gate |
| M3 | 单测/文档校验、control-plane audit、progress、独立 Judge 收口 | M2 | 证据 + Judge | 见验证合同 |

## 验证合同

- 必跑：`git diff --check`；`python tools/release/validate-control-plane.py`（激活后 bootstrap/audit 按适用模式）；针对 `code_map_gate` 的单元或 stdin 模拟测试（若新增）。
- 文档：相对链接、目录 README 状态唯一性（仅一份拟议/活动主线表述正确）。
- 路径：`map.yaml` 中 entrypoints 抽样 `test -e` 或脚本检查。
- 不跑：真实回归 UAT、外部 marketplace、Graphify 全量重建（除非抽查需要且本机可用）。
- 收口：独立 Judge + 审查包；Worker 不得自判 pass。

## 失败与人工决策

- 无法从 hook 载荷稳定解析路径：降级为 Stop 时基于 `git status` 提醒，并在 progress 记录限制。
- 用户拒绝 trust hook：地图与规则仍有效，提醒能力降级；不阻塞文档交付，但 Boundary Check 必须写明。
- 发现地图与产品代码严重不符：先修 map/文档，不借机改产品行为（产品改动另开控制面）。

## 主线总结

本 plan 已 `active`，按 M0→M3 实施。完整门 + 默认 Judge；产品 UAT 不在完成口径内。
