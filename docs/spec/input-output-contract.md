# 输入输出合同

本合同定义 repo-analyzer 接受什么输入、如何隔离运行，以及最终必须交付什么。它是产品边界，不是操作建议：skill、控制面和验收规则都不能用更宽松的行为覆盖它。

## 触发范围

当请求涉及项目/仓库分析、源码分析、架构分析、框架研究、项目评测或两个项目对比时，使用本 skill。单文件代码问答、调试和代码审查不属于本 skill 的范围。

## 输入

请求可以提供以下任一种来源：

- 已存在的本地仓库路径；
- 公开的 GitHub、GitLab 或 Gitee URL；
- `owner/repository` 标识符。

解析后的源码必须保持只读。本地路径直接使用；远程标识符克隆到本次运行工作区，并在分析前记录解析后的 commit。

分析模式只有两种：

| 模式 | 选择方式 | 核心模块最低覆盖率 | 次要模块最低覆盖率 |
|---|---|---:|---:|
| `standard` | 默认模式；输入没有实质歧义时直接执行 | 60% | 30% |
| `deep` | 用户明确要求深度分析时选择；快速扫描后只进行一轮集中询问 | 90% | 60% |

不提供快速模式。`deep` 只改变 Agent 的源码阅读、范围确认和验证深度，不改变 Graphify 提取方式；两种模式都只允许 Graphify code-only。

## 运行工作区

每次运行都拥有一个位于目标仓库之外、可写的 `$WORK_DIR`。下面是支撑分析的典型结构，不是要求用户逐项接收的多份交付物：

```text
$WORK_DIR/
  metadata.json
  execution-log.md
  drafts/
    01-graphify-map.md
    03-research.md
    03-plan.md
    05-modules-plan.md
    06-module-*.md
    07-cross-validation.md
    08-insights.md
    08-coverage.md
  graphify-out/
    raw-code-only-graph.json
    raw-code-only-GRAPH_REPORT.md
    graph.json
    GRAPH_REPORT.md
  ANALYSIS_REPORT.md
  checks.md
```

目标仓库中不得写入 Graphify 输出、缓存、草稿、元数据或报告。直觉上，`$WORK_DIR` 是一次分析的“隔离工作台”；但它仍是可审计运行的一部分，不能被当作随时可丢弃的临时目录。用户正式接收的交付物只有 `ANALYSIS_REPORT.md`，其余内容是运行支撑或开发验收证据。

## 必需流程

1. 规范化输入、选择分析模式并记录源码 commit。
2. 检查 Graphify `0.9.13+` 是否可用。缺失或不兼容时，Agent 只展示官方安装/升级指引，并让用户明确选择“安装后复检”或“本次使用无 Graphify 的原版兼容流程”；Agent 不得代替用户安装，也不得自动回退。
3. Graphify 可用时，通过单一 Graphify gate 执行 code-only 建图、原始证据保留、来源规范化、健康验证和导航 map 生成。gate 内部固定使用 `graphify extract <target> --code-only --no-cluster --out <WORK_DIR>` 与 `cluster-only <WORK_DIR> --no-label --no-viz`，不得启用 semantic extraction、LLM provider、模型探测或 semantic chunking。
4. Graphify 增强流程一旦开始，任何执行失败、空图、规范化后没有可定位节点/关系、越界来源或源码只读边界违规都必须停止，不能切换到兼容流程掩盖失败。
5. 把健康的图谱 map 当作导航上下文；兼容流程则明确记录“未使用 Graphify”。随后由 Agent 完成规模评估、外部调研、模块分析、交叉验证、覆盖率门和报告融合。
6. subagent 不可用时，在模块深度分析前暂停并取得用户同意。用户同意顺序执行后，质量门保持不变。
7. 只向用户交付一份最终 Markdown 报告；运行支撑证据继续留在隔离工作区。

## 失败合同

- `0`：Graphify gate 通过，可以进入增强分析；
- `10`：Graphify 缺失或版本不兼容，需要用户选择安装后复检或本次进入兼容流程；
- `30`：Graphify 已开始执行但被无效目标/工作区、执行失败、空图、无效工件、来源边界或源码只读违规阻断。

退出码 `10` 不是增强流程通过；只有用户明确选择后才能继续。退出码 `30` 不允许自动重试为兼容流程，也不能通过手写图、fixture 或补造工件绕过。

## 报告合同

最终报告默认使用中文，并必须包含项目定位、全局视图、模块分析、Why > What 推理、Mermaid 架构图、源码路径/行号证据、局限和未检查范围。大型仓库采用有界范围时，还必须披露纳入内容、排除内容、选择理由和覆盖率分母。

增强流程的报告还要简述 Graphify 如何影响阅读路径、哪些候选被源码确认或否决；兼容流程必须明确披露未使用 Graphify，不能生成伪造的 Graphify 产物。

`EXTRACTED` 关系只是需要回到源码验证的证据；`INFERRED` 关系保持待验证；`AMBIGUOUS` 关系只能作为风险或问题。发生冲突时，以源码为最终裁决依据。

## 主线总结

默认 `standard` 直接执行，显式 `deep` 只集中询问一次；两者共享同一个 code-only Graphify gate。Graphify 缺失时由用户选择安装或兼容流程，增强流程开始后的失败必须停止。源码始终只读，用户最终只接收一份 `ANALYSIS_REPORT.md`。
