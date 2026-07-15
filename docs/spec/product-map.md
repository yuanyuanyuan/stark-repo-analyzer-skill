# Product Map · 用户场景 → 产物 → 入口

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 维护本 skill 时使用的「用户场景 → 触发/产物/主入口/证据上限」导航；**不**替代 skill / 行为合同字段细则 |
| 当前状态 | `active`（导航文档；行为真源仍是 skill + input-output-contract） |
| 当前结论/入口 | 先按场景选行，再沿链接打开合同与代码；冲突以 skill / `docs/spec/input-output-contract.md` 为准 |
| 何时读取 | 理解用户分析路径、改触发方式/主产物/证据上限声明、或核对场景是否覆盖时 |
| 何时更新 | 用户路径/触发/主产物集合/证据上限变化时同一交付更新；否则写 `product-map 无影响：…` |
| 关联真源 | 行为合同 → [input-output-contract.md](input-output-contract.md) 与 `skills/repo-analyzer/`；决策 → [ADR-0028](../adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md)；术语 → 根 `CONTEXT.md` |

## 边界（必读）

- 服务**维护本 skill** 时理解用户路径，不是对目标仓库的分析交付物。
- 不进入 Skill 核心交付包。
- 不复制退出码表、覆盖率数字、schema 字段全文；那些只属于合同。
- 与 [代码地图](../code-map/README.md) 分工：code-map = 本仓功能→分层入口；本文件 = 用户分析场景导航。

## 场景 1 — Graphify 增强分析

| 维度 | 内容 |
|---|---|
| 触发 | 用户请求分析仓库；本机 Graphify `0.9.13+` 可用 |
| 用户意图 | 用结构导航加速模块发现，最终仍要源码裁决 |
| 关键产物 | 工作区 `ANALYSIS_REPORT.md`（用户唯一正式交付）；支撑：图谱、导航 map、草稿（均在 `$WORK_DIR`） |
| 主入口 | `skills/repo-analyzer/SKILL.md`；gate：`skills/repo-analyzer/scripts/graphify_gate.py` |
| 合同/ADR | [input-output-contract.md](input-output-contract.md)；ADR-0016/0018/0021 等 |
| 证据上限 | 开发改导航/gate 语义时用聚焦 UAT；**发布级**才要求真实回归 UAT（见 real-uat-regression） |

## 场景 2 — 原版兼容流程（无 Graphify）

| 维度 | 内容 |
|---|---|
| 触发 | Graphify 缺失/不兼容 → 用户明确选择「本次原版兼容」；或安装后复检失败仍选兼容 |
| 用户意图 | 无结构导航 map 时仍完成参考式纯源码分析 |
| 关键产物 | 仍只交付 `ANALYSIS_REPORT.md`；必须披露未使用 Graphify；不得伪造图谱 |
| 主入口 | skill 默认执行合同中的兼容分支；**不得**在 gate 已开始增强后的失败上自动切兼容 |
| 合同/ADR | input-output-contract；ADR-0021 |
| 证据上限 | 同场景 1；兼容路径变更属产品行为，发布前走真实回归规则 |

## 场景 3 — standard 分析档位

| 维度 | 内容 |
|---|---|
| 触发 | 用户未明确要求深度分析（默认） |
| 用户意图 | 常规覆盖、少交互、输入无实质歧义时一键执行 |
| 关键产物 | `ANALYSIS_REPORT.md`；覆盖率分母与门槛以合同为准（勿在此复制数字） |
| 主入口 | skill「默认执行合同」与模式章节 |
| 合同/ADR | input-output-contract 模式表 |
| 证据上限 | 改模式交互/覆盖率语义 → 产品变更；导航句变化才改本表 |

## 场景 4 — deep 分析档位

| 维度 | 内容 |
|---|---|
| 触发 | 用户明确要求深度分析 |
| 用户意图 | 扩大阅读与验证深度；扫描后**一轮**集中确认范围，不再二次确认提纲 |
| 关键产物 | 同 final report；过程询问与范围披露见合同 |
| 主入口 | skill deep 路径；CONTEXT「deep 分析档位」 |
| 合同/ADR | input-output-contract |
| 证据上限 | 同 standard；交互步骤变则同步本场景行 |

## 场景 5 — 超大仓有界分析

| 维度 | 内容 |
|---|---|
| 触发 | 仓库过大，必须显式选择模块/目录集合以保证可执行 |
| 用户意图 | 在声明范围内完成分析，不把范围内覆盖率说成全仓 |
| 关键产物 | 报告必须列出纳入、排除、理由与覆盖率分母 |
| 主入口 | skill + ADR-0023；input-output-contract 报告合同 |
| 证据上限 | 有界语义变更 = 产品合同变更 |

## 场景 6 — subagent 能力降级

| 维度 | 内容 |
|---|---|
| 触发 | 运行时无 subagent；在模块深度分析前 |
| 用户意图 | 知情选择顺序执行或停止；质量门不降低 |
| 关键产物 | 运行记录 `parallelism: degraded`（若继续）；最终仍一份报告 |
| 主入口 | skill 阶段 6；ADR-0024 |
| 证据上限 | 禁止静默降级；同意边界见 real-uat-regression / 合同 |

## 场景 7 — 开发验收与公开发版（协作侧）

| 维度 | 内容 |
|---|---|
| 触发 | 维护者改 skill/gate/合同，或准备 tag/Release |
| 用户意图 | 开发交付可收口；发布可核验 |
| 关键产物 | plan/progress、Judge Review、校验输出；发布另有 tag/Release |
| 主入口 | [task-quality-gates](../dev-rules/task-quality-gates/README.md)、[dual-agent-review](../dev-rules/dual-agent-review/README.md)、[real-uat-regression](../dev-rules/real-uat-regression/README.md)、[version-release](../dev-rules/version-release/README.md) |
| 证据上限 | Judge pass ≠ 真实回归 UAT；发版不替代 UAT |

## 同步规则（摘要）

见 grill B3 / ADR-0028：行为细节只在合同；本表只导航。路径/触发/主产物/证据上限声明变化 → 同交付更新；否则 `product-map 无影响：…`。

## 主线总结

先选场景行，再进合同与 skill。本文件防 Agent 迷路，不防合同漂移——漂移靠合同测试与真实回归规则。
