# v2 模块分析指南

## 核心目标

模块分析按业务能力和数据流划分，不按目录机械切割。每个模块都要回答：

1. 它为什么存在，服务项目哪个核心目标？
2. 去掉它后系统会失去什么约束或能力？
3. 它与其他模块通过什么契约协同？
4. 当前方案为何优于可选方案，代价是什么？

确定性扫描结果只用于定位候选证据。最终判断必须由源码锚点、项目文档或外部一手来源验证。

## 核心模块双交付

每个 core 模块必须先写机器可读 Evidence Matrix：

```text
$WORK_DIR/module-evidence/{module}.json
```

再写叙事草稿：

```text
$WORK_DIR/drafts/06-module-{module}.md
```

JSON Matrix 是 `gate` 的契约输入，叙事草稿负责 Why > What 的解释；两者必须表达一致，不能互相替代。字段模板见 [evidence-first-v2.md](evidence-first-v2.md)。

## Evidence Matrix 要求

核心模块 JSON 必须包含：

| 字段 | 要求 |
|---|---|
| `module_role` | 模块为何存在、服务什么目标 |
| `entry_points` | `文件:行号` 入口或调用边界 |
| `core_data_structures` | 理解设计必需的结构、类型或状态 |
| `main_flow` | 主流程及关键控制/数据转换 |
| `cross_module_dependencies` | 依赖两端、共享状态或契约；可为空数组 |
| `key_design_decisions` | 动机、权衡和替代方案代价 |
| `risk_areas` | 每条包含 category、evidence、finding、impact |
| `source_evidence` | 可审计的 `文件:行号` 锚点 |
| `open_questions` | 未验证问题；可为空数组 |
| `narrative` | 与后续草稿一致的模块叙事摘要 |

跨模块推断只有在两端都被验证时才能写成确定性结论。`refs_status` 为 `partial` 或 `missing` 时，相关推断必须进入 `open_questions` 或最终报告的 Unsupported Area。

## 关键单元回填

模块分析只能修改 `coverage-units.json` 的 `status`、`anchor`、`judgment` 和 `skip_reason`：

- 已分析：`status: analyzed`，同时填写 `文件:行号` 和角色/流程/权衡判断。
- 未分析：保持 `status: unanalyzed`，填写一行未覆盖原因。
- 不得删除单元、改变稳定 ID 或改写枚举器字段。

状态、锚点和实质判断三项缺一，质量门都不会计入覆盖率。

## 风险抽样

每个核心模块至少抽样一条实际相关风险路径。优先考虑：

- 错误处理与恢复
- 配置加载与默认值
- 插件或扩展点
- 缓存、一致性与失效
- 并发、队列与资源生命周期
- 权限与安全边界
- generated/vendor/test 边界

每条抽样必须写抽样对象、源码锚点、发现和对架构评价的影响。风险类别不适用时写明理由，不得只列“可能有风险”。

## 分析模式

| 模式 | 核心/次要覆盖阈值 | 模块证据边界 | 风险抽样 |
|---|---:|---|---|
| standard | 60% / 30% | 核心模块、关键边界和主要决策 | 重要边界追加抽样 |
| deep | 90% / 60% | 次要模块、边缘路径和替代方案 | 多路径增强抽样 |

模式改变深度与成本，不改变 Matrix、锚点、风险记录和质量门要求。

## 核心模块 Agent Prompt

```text
你是一位资深架构师，负责分析 {项目名} 的 {模块名} 模块。

上下文：
- 项目定位：{定位}
- 整体设计哲学：{设计哲学}
- 模块在系统中的位置：{位置}
- 当前模式与预算：{mode、time、token、证据预算、报告长度}
- Evidence Plan：{架构问题、候选关键单元、候选文件、风险路径}

执行约束：
1. 只读取回答 Evidence Plan 所需的关键单元 span、紧邻上下文和跨文件引用两端。
2. 扫描候选不是结论；所有确定性判断必须有源码锚点。
3. 至少完成一条相关风险路径抽样。
4. refs_status 不完整时，把跨模块推断保留为开放问题。
5. 先写 {work_dir}/module-evidence/{module}.json，再写 {work_dir}/drafts/06-module-{module}.md。
6. 回填 coverage-units.json 的分析字段，不得删除或改写枚举字段。

叙事草稿必须解释：
- 模块角色和业务问题
- 核心数据结构及其设计意义
- 主流程与 Mermaid 图
- 跨模块协同
- 关键设计决策、替代方案和权衡
- 风险抽样对架构评价的影响
- 业界对比、亮点、问题和开放问题
```

## 次要模块

次要模块也受 coverage 分母约束，但可批量分析。至少记录职责、入口或涉及文件、代表性源码锚点、特别设计判断、风险或开放问题。快速模式可以保留较多未覆盖单元，但必须填写原因并满足 10% 阈值。

## 并行与串行降级

有 subagent 时按 Evidence Plan 的问题边界并行，不按文件数量切分；相互依赖的证据范围应串行。无 subagent 时主 Agent 按相同顺序串行执行，并在 Evidence Plan 写 `parallelism: degraded`。无论并行还是串行，Evidence Matrix、覆盖率和 gate 契约完全相同。

## 合成前自检

- JSON Matrix 字段完整且源码证据为 `文件:行号`。
- 叙事中的关键判断能回指 Matrix 和关键单元。
- 每个核心模块完成风险抽样。
- 未覆盖单元有原因，未解析 core 路径进入 Unsupported Area。
- 开放问题没有在叙事中被静默写成已验证结论。
- `repo-analyzer gate` 通过后才进入最终合成。
