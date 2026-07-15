# Agent Harness 渐进披露执行计划

状态：`completed`

- 质量门：完整门
- 独立Judge：必须
- 对应 roadmap：[agent-harness-progressive-disclosure-roadmap.md](../roadmap/agent-harness-progressive-disclosure-roadmap.md)
- 进度记录：[agent-harness-progressive-disclosure-progress.md](agent-harness-progressive-disclosure-progress.md)
- 关键决策：[ADR-0028](../adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义 harness 渐进披露落地的顺序、所有权、验证与风险；不定义 analyzer 产品行为合同 |
| 当前状态 | `completed`；独立 Judge pass + harness 校验 |
| 当前结论/入口 | 先 H0 冻结 ADR/术语/索引，再 H1 三件套与路由，再 H2 校验与 code-map，再 H3 Judge 收口 |
| 何时读取 | 实施或审查本 initiative 的任意一刀前 |
| 何时更新 | 任务顺序、依赖、验证方式或阻塞变化时 |
| 关联真源 | 方向见 roadmap；术语见 `CONTEXT.md`；原因见 ADR-0028；事实见 progress |

## 当前主线

按 grill 共享理解实施 P0：分散补强 Agent 导航脚手架 + 独立 harness 契约校验。

## 决策摘要（grill 锁定）

1. 优化冷启动与渐进披露；保留 Judge / document-control / code-map / control-plane。
2. 不平行 `docs/ai-harness/`；product-map 在 `docs/spec/product-map.md`。
3. 新建 workflows 与 agent-boundaries；角色沿用 Worker/Judge/Orchestrator。
4. 同类失败 ≥2 回 Thinking；独立 `validate-agent-harness.py`；不硬挂 PreToolUse。
5. product-map 与 skill/spec：行为细节归合同；路径/触发/产物/证据上限变则同交付同步 map。
6. 全局短必读 + 按任务加载；冲突优先级：spec/skill > roadmap/plan > 质量门/Judge > workflows > 导航地图 > 文风。
7. 不建常青 evidence-map；本摘要 + ADR-0028 即可。

## 目标关

### 目标

1. 落地 Product Map、workflows、agent-boundaries 与 AGENTS/目录路由。
2. 落地 Harness 契约校验与单测。
3. 登记 code-map feature 与 cheat sheet；写入 CONTEXT 术语与 ADR-0028。
4. 完整门收口：awaiting-judge → 独立 Judge → control-plane audit。

### 非目标

- 不改 skill 用户分析行为；不进核心交付包；不做真实回归 UAT/发版；不平行 ai-harness；不硬挂 hook 拦截。

### 完成条件

见 roadmap 可观察成功标准 1–6。

## 启动关

### Blindspot Pass

- 当前启动前无 active 主线；本 plan 激活后为唯一 active plan。
- product-map 不得抄写退出码/覆盖率数字当真源。
- 校验器不得耦合进 `validate-control-plane.py`。
- 新增文档不得写入 `core-package-files.txt`。
- 冷启动不得因新文件变成「每次通读」——workflows 必须写清按任务加载。

### 关键假设

| 假设 | 置信度 | 验证方式 |
|---|---|---|
| 场景导航可从 skill + input-output-contract 归纳且不改产品行为 | 高 | 对照链接、无改 skill 正文行为 |
| harness 校验可用 pathlib + 单测夹具完成 | 高 | pytest |
| 用户已授权 active 控制面并实施 P0 | 高 | 本会话确认 |

### 工作区基线

- 基线命令：`git status --short`（启动时为空闲）。
- 本任务拥有范围：`AGENTS.md`、`CONTEXT.md`、`docs/spec/product-map.md`、`docs/spec/README.md`、`docs/code-map/**`、`docs/dev-rules/workflows/**`、`docs/dev-rules/agent-boundaries/**`、`docs/dev-rules/README.md`、`docs/dev-rules/code-map/README.md`、`docs/roadmap/agent-harness-*`、`docs/exec-plans/agent-harness-*`、`docs/roadmap/README.md`、`docs/exec-plans/README.md`、`docs/README.md`、`docs/adr/0028-*`、`docs/adr/README.md`、`tools/release/validate-agent-harness.py`、`tests/unit/test_validate_agent_harness.py`。
- 排除：用户无关改动、`vendor/`、skill 运行时行为代码（只读引用）、`core-package-files.txt`（确认不加入）。

## 执行计划

| ID | 动作 | 依赖 | 输出 | 验证 |
|---|---|---|---|---|
| H0 | ADR-0028、CONTEXT 术语、roadmap/plan/索引 | 控制面 active | 决策与术语 | 链接与状态唯一性 |
| H1 | product-map、workflows、agent-boundaries、AGENTS/dev-rules/spec/docs 路由 | H0 | 三件套 + 路由 | harness 校验（落地后） |
| H2 | validate-agent-harness.py、单测、map feature、cheat sheet | H1 | 校验器 + 地图 | pytest + 校验 exit 0 |
| H3 | progress、awaiting-judge、独立 Judge、control-plane audit | H2 | 收口证据 | Judge pass + audit |

## 验证合同

- 必跑：`python tools/release/validate-agent-harness.py`；`python -m pytest tests/unit/test_validate_agent_harness.py -q`；`git diff --check`；收口前 `python tools/release/validate-control-plane.py --mode audit`（仅 Judge pass/豁免后）。
- 文档：相对链接、唯一 active roadmap/plan。
- 不跑：真实回归 UAT、发版、Graphify 全量重建。
- 收口：独立 Judge + 审查包；Worker 不得自判 pass。

## 失败与人工决策

- 与既有 dev-rules 冲突：以 dual-agent / quality-gates / document-control 为准，修 workflows 编排而非改状态机。
- 场景与合同不一致：先修 product-map 或暴露冲突，不改产品行为蒙混。

## 主线总结

H0 冻结合同 → H1 导航三件套 → H2 机械校验与地图 → H3 Judge 收口。全程不平行 ai-harness、不降 Judge、不碰产品分析合同。
