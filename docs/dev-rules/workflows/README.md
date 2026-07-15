# Workflows · Agent 作业流

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 编排「接到任务后按什么顺序做」；**不**重写质量门状态机或 Judge 权限 |
| 当前状态 | `active` |
| 当前结论/入口 | 先认任务类型，再走通用骨架；冲突时以 dual-agent / quality-gates / document-control / real-uat 真源为准 |
| 何时读取 | 开发交付、不清楚启动顺序、多角色协作或失败恢复时（**非**每次任务强制通读） |
| 何时更新 | 任务类型入口、骨架映射或与门禁衔接变化时 |
| 关联真源 | [task-quality-gates](../task-quality-gates/README.md)、[dual-agent-review](../dual-agent-review/README.md)、[document-control](../document-control/README.md)、[agent-boundaries](../agent-boundaries/README.md)、[ADR-0028](../../adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md) |

## 冷启动（最少必读）

1. 根 `AGENTS.md` 权威分层表。
2. 活动 roadmap/plan 生命周期（仅当存在 `active`）。
3. 写用户可见长文前再读 output-style。

Product Map、本文件、agent-boundaries、code-map **按任务加载**，不要每次通读。

## 通用骨架（映射本仓）

| 阶段 | 本仓做什么 | 退出条件 |
|---|---|---|
| Critical | 意图、范围、非目标；读 AGENTS 路由 + 活动控制面 | 1–2 句意图 + 成功标准 |
| Fetch | code-map / product-map（按需）+ graphify（本仓结构）+ 相关 spec/ADR | 入口文件清单 |
| Thinking | 轻量/完整门、文件边界、验证方式 | 任务清单 + 门禁选择 |
| Execution | Worker 实现；改代码后 `graphify update .`（AST-only） | diff + 自验 |
| Review | 独立 Judge（默认 Delivery Task） | pass / revise / blocked |
| Verification | 质量门要求的命令；改导航则 `validate-agent-harness.py` | 命令 exit 与证据上限诚实 |
| Evolution | 回写 plan/progress、code-map/product-map 无影响声明、ADR 如需 | writeback 或 none-with-reason |

### 角色对照（不引入第二套术语）

| 参考仓说法 | 本仓 |
|---|---|
| planner | Orchestrator |
| worker | Worker |
| test_review（独立复测） | Judge 的独立验证义务；纯本地自测仍属 Worker 自验 |

单写者：同一时段只允许一个 Worker 改正式树。

## 任务类型入口

### 1. 只读定位

- 入口：code-map → 命中 feature entrypoints；需要结构关系再 graphify query/path。
- 出口：代码位置 + 测试位置 + 相关合同链接。
- 不要：全仓无目的 `rg`；把只读结论写成已交付。

### 2. 产品行为改动

- 入口：CONTEXT → spec/skill → 相关 ADR；对照 [product-map](../../spec/product-map.md) 是否场景变化。
- 流程：完整门倾向；先合同后实现；real-uat-regression 定证据上限。
- 出口：合同/测试同步；场景变则更新 product-map。
- 不要：只改实现不改合同；用聚焦 UAT 冒充真实回归。

### 3. 控制面改动

- 入口：document-control + 活动 roadmap/plan；dual-agent 状态机。
- 流程：完整门；`awaiting-judge` 后独立 Judge；**禁止** Worker 自过 completed。
- 出口：progress 证据 + Judge + `validate-control-plane.py --mode audit`。
- 不要：假 completed；审查包不足仍强行 review。

### 4. harness 导航改动

- 入口：ADR-0028、本文件、agent-boundaries、product-map、code-map 规则。
- 流程：改 `AGENTS.md` / `docs/code-map/**` / `docs/spec/product-map.md` / `docs/dev-rules/workflows/**` / `docs/dev-rules/agent-boundaries/**` 等后**必须** `python tools/release/validate-agent-harness.py`。
- 出口：校验 exit 0；map feature 如需更新；不进核心包。
- 不要：平行新建 `docs/ai-harness/`；硬挂 PreToolUse deny。

### 5. 公开发版

- 入口：[version-release](../version-release/README.md) + [pre-release-security-scan](../pre-release-security-scan/README.md)。
- 流程：按 SOP 顺序；安全扫描与真实回归互不替代。
- 出口：checklist 条条有证据。
- 不要：跳步 tag；用 Judge pass 代替 UAT 或安全扫描。

## 与校验的衔接

```text
（若适用）validate-agent-harness.py
  → Worker 声明收口 → awaiting-judge
  → 独立 Judge
  →（pass/豁免）validate-control-plane.py --mode audit
  → completed
```

Harness 契约校验不替代 Judge，不证明产品 UAT，不等于 control-plane completed。

## 失败恢复

| 失败 | 第一动作 |
|---|---|
| 测试/校验失败 | 读完整输出；修当前层 |
| 同类失败 ≥2 次 | **Same-Type Failure Design Gate**：停止同层 patch，回 Thinking 重判范围/假设/验证；必要时改 plan |
| Judge revise | 按 findings 修；更新审查包；≤3 轮 |
| 合同与实现冲突 | 停止；以 spec/skill 为准暴露冲突 |
| graphify 漂移（本仓） | `graphify update .`；仍异常则记 progress |

## 主线总结

workflows 管顺序，不管第二真源。按任务类型加载，按骨架推进，按本仓 Judge 与质量门收口。
