# 真实 UAT 回归测试

本规则定义怎样验证普通用户触发 repo-analyzer 后的实际行为。直觉上，聚焦 UAT 像“单项路考”，只证明某个分支；真实回归 UAT 像“完整路考”，必须从用户入口一直走到最终报告。类比的边界是，两者都必须运行真实 Skill，静态文件和内部函数直调都不能冒充其中任何一种。

## 两种验收层级

| 层级 | 何时执行 | 可以证明什么 | 不能声称什么 |
|---|---|---|---|
| 聚焦 UAT | 开发期间，相关行为变化后 | 被测模式或失败/选择分支符合合同 | 完整仓库分析、完整产品回归或发布就绪 |
| 真实回归 UAT | 发布前或用户明确要求时 | 用户等价入口到最终报告的完整流程通过 | 未覆盖组合也通过 |

不得将静态 fixture、手写/复制报告、内部 Python 入口直调、只有目录结构的输出、中断运行，或停在任一门前的运行称为真实回归通过。

## 产品模式与交互合同

- 未指定模式时使用 `standard`，输入没有实质歧义时直接执行。
- 用户明确要求深度分析时使用 `deep`；快速扫描后只允许一轮集中询问，用于确认范围、重点和必要裁决。
- 不提供快速模式。
- 两种模式共享 Graphify `0.9.13+` code-only gate；`deep` 不能改变 Graphify 提取模式。
- Graphify 缺失或不兼容时必须等待用户选择安装后复检或本次兼容流程。
- subagent 不可用时必须等待用户同意顺序执行，不能自动降级。

## 开发期聚焦矩阵

相关合同发生变化时，只运行能证明本次风险的场景，但至少要覆盖受影响的行：

| 场景 | 最小断言 |
|---|---|
| 默认 `standard` | 不展示模式菜单；无实质歧义时直接开始；使用 60%/30% 覆盖率门 |
| 显式 `deep` | 只集中询问一次；使用 90%/60% 覆盖率门；Graphify 仍为 code-only |
| Graphify 缺失/不兼容 | Agent 不安装；展示指引；未获用户选择前不继续 |
| 用户选择兼容流程 | 明确记录未使用 Graphify；不生成伪造图谱；继续保持源码阅读质量门 |
| Graphify 执行/健康失败 | 增强流程停止；不自动切换兼容流程；不补造成功工件 |
| subagent 不可用 | 模块深度分析前暂停；用户同意后才顺序执行；质量门不降低 |
| 大仓库有界范围 | 披露纳入、排除、理由和覆盖率分母；范围内覆盖率不冒充全仓覆盖率 |
| 单一用户输出 | 用户只接收 `ANALYSIS_REPORT.md`；内部证据不扩张为第二套正式报告 |

聚焦 UAT 可以在目标分支得到真实证明后停止，不要求为了日常改动完成整份仓库分析。收尾必须明确写出“通过的具体分支”和“未验证的完整流程”。

## 发布级真实回归矩阵

发布前完整执行三条用户流程：

1. Graphify 增强 `standard`。
2. Graphify 增强 `deep`，包含并记录唯一一轮集中询问及用户回答。
3. 无 Graphify 的 `standard` 兼容流程，包含并记录用户明确选择。

无 Graphify 的 `deep` 组合使用聚焦 UAT 验证交互与兼容边界，不再额外执行第四次完整仓库分析。三条完整流程中任一条未运行或未通过时，只能报告实际状态，不能声明发布级真实回归通过。

## 用户等价驱动

标准模式使用不暴露内部流程的最小输入：

```text
$repo-analyzer 分析 https://github.com/browser-use/video-use
```

深度模式只显式表达用户意图：

```text
$repo-analyzer 深度分析 https://github.com/browser-use/video-use
```

自动触发场景可以使用 `分析 GitHub 仓库 https://github.com/browser-use/video-use`。prompt 不得指定工作目录、Graphify、doctor、模块、报告模板或失败处理；这些都是 Skill 的责任。

UAT 驱动必须委托独立 Agent 进程，例如：

```bash
codex exec '$repo-analyzer 分析 https://github.com/browser-use/video-use'
```

涉及 `deep` 集中询问、Graphify 选择或 subagent 同意时，驱动必须在同一会话中记录问题、用户回答和继续执行结果。外层不得用内部 CLI、gate 函数或验收脚本替代 Skill 委托；运行结束后可以执行只读工件检查。

## Graphify 增强路径

Skill 通过单一 Graphify gate 完成以下确定性职责：

```text
检查 Graphify 0.9.13+
code-only extract + cluster-only
保留 raw code-only 图/报告
规范化来源路径并记录过滤计数
验证规范化图非空且来源可定位
生成导航 map 和健康/失败摘要
```

不得启用 semantic extraction、LLM provider、模型探测或 semantic chunking。Graphify 产物只可位于 `<WORK_DIR>/graphify-out/`，目标源码仓库在整个运行中必须保持未修改。

原始图允许包含可被规范化过滤的噪声，但必须保留用于诊断并记录过滤数量。只有规范化后的 `graph.json` 与 `GRAPH_REPORT.md` 仍包含非空、来源可定位的节点和关系时才能继续。`EXTRACTED` 关系仍须回到源码裁决；`INFERRED` 仅为待验证；`AMBIGUOUS` 只能作为风险或问题。

## 证据合同

每次 UAT 至少保留：

- 最小用户输入、完整会话转录、Agent 进程退出状态、开始/结束时间；
- 实际模式、用户交互与回答、固定源码 commit、目标源码前后状态；
- Graphify 可用性、版本、gate 结果、失败分类和实际内部命令摘要；
- 最终 `ANALYSIS_REPORT.md`，或失败点之前真实产生的最小证据。

增强流程还必须能够定位 raw code-only 图/报告、规范化图/报告、过滤计数、导航 map 和健康摘要。兼容流程必须明确记录用户选择和“未使用 Graphify”，并确认没有伪造上述工件。

草稿、metadata、checks 或 manifest 可以作为开发验收证据，但不是普通用户必须接收的正式交付物，也不能仅凭存在就证明分析通过。大型原始证据按 ADR-0019 保存在 Git 外，仓库只保留可核验摘要和定位/校验信息。

门禁失败的运行只能证明对应失败边界。不得补写不存在的健康摘要、模块草稿、最终报告或成功状态。静态源码阅读覆盖率、测试覆盖率和运行时验证是三种不同指标，必须分别记录。

## 2026-07-13 受阻诊断：browser-use/video-use

此前运行以旧内部控制面直调 `https://github.com/browser-use/video-use`，工作目录为
`/Users/chuzu/repo-analyses/video-use-20260713`，固定 commit 为
`92c2b34e44c205cbc2acae7f6ca7c1c219d5dd66`。Graphify `0.9.13` 的 code-only extract 和
`cluster-only` 均以退出码 `0` 完成，原始图包含 89 个节点和 150 条边。

该运行因来源路径规范化缺陷以 `graphify-artifact` 停止，未产生 post-graph、模块草稿、
最终报告或成功 manifest。它是有效的控制面诊断，不符合本规则的完整 UAT，也不是通过结果。
修复后仍须按当前发布级矩阵从用户等价入口运行新的端到端 UAT，才能声称对应回归通过。

## 主线总结

开发期用聚焦 UAT 证明受影响分支，发布前再执行三条完整真实回归。所有 UAT 都必须从用户等价的 Skill 入口开始；Graphify 始终使用 code-only，用户选择和失败边界必须真实保留。只有发布矩阵全部通过，才能声明发布级真实回归通过。
