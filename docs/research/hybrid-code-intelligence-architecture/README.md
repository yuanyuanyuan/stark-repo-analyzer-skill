# 开源混合代码智能架构方案

调研日期：**2026-07-13**

状态：**研究与设计稿，不是实现，不是 V1 契约变更，也不是真实 UAT 通过证明。**

## 结论

建议把初稿修正为：

> **Git 源码索引常驻 + Graphify `--code-only` 本地静态关系图常驻 + Repomix 按热点打包 + Agent 直接读取精确源码；只有疑难符号关系才调用 OSS LSP，只有明确的数据流/安全问题才进入 Joern 深度模式。**

不建议第一阶段自己重建一套完整的 Tree-sitter 跨文件图引擎。Graphify `0.9.13` 已经使用 Tree-sitter 提取代码 AST，并提供 import、call、inheritance、路径、影响分析和社区聚类。Click 固定源码上的只读实验显示，`--code-only` 在约 **3.0 秒**内处理 89 个代码文件，AST 阶段约 2.5 秒，语义阶段为 0.0 秒；这与旧版 `0.9.8` 将文档语义提取混入标准流程后出现的数分钟乃至无法完成的运行，不是同一种成本模型。

因此，当前问题更准确地说是：**旧流程把无必要的非代码语义提取放进了强制前置路径**，而不是 Graphify 的代码图本身必然昂贵。

## 推荐流程

```text
Git Source Universe
  tracked + untracked-not-ignored + dirty fingerprint
                    |
                    v
Graphify 0.9.13 --code-only
  local Tree-sitter AST + cross-file relations + communities
                    |
                    v
Deterministic Hotspot Ranker
  centrality + cross-boundary edges + entrypoints + change + question relevance
                    |
          +---------+----------+
          |                    |
          v                    v
Optional OSS precision     Repomix context pack
Serena LSP / ctags /       compressed neighborhood,
ast-grep                   strict token budget
          |                    |
          +---------+----------+
                    v
Agent direct source-range reads
  exact implementation and evidence adjudication
                    |
                    v
Business-module plan -> subagents -> cross-validation -> coverage -> report

Explicit deep mode only:
Joern CPG / CFG / PDG / dataflow
```

## 为什么不是“只按目录分层”

Git-aware 目录索引值得保留，但它只能可靠解决文件枚举、忽略规则、规模统计、源码身份和粗粒度导航。它不能可靠推导业务边界、调用链、插件注册、依赖倒置、运行时分派或共享核心模块。

当前仓库已有反例：Codex 的真实 Agent 分析最终使用 6 个责任/数据流模块，而不是 9 个顶层目录。把目录直接分给子代理会产生三类风险：

- 同一共享文件被多个代理重复读取，成本转移而非消失；
- 跨目录业务流被拆断，得到稳定但错误的模块图；
- 复杂性只有在关系追踪后才暴露，晚触发 Graphify 会导致重规划和废弃草稿。

目录结构应当是 `HotspotRanker` 的一个弱特征，不能成为模块划分结论。

## 工具角色与开源约束

| 工具 | 许可证 | 部署方式 | 方案角色 | 默认状态 |
|---|---|---|---|---|
| Git | GPL-2.0 | 本地 | 源码全集、ignore、commit/dirty 身份 | 必选 |
| Graphify `0.9.13` | MIT | 本地 CLI | Tree-sitter 代码图、跨文件关系、社区、路径/影响查询 | 必选候选，先 shadow |
| Tree-sitter `0.26.x` | MIT | 本地库 | Graphify 底层解析；特殊语法查询和未来替代基础 | 扩展，不重建全图 |
| Repomix `1.16.1` | MIT | 本地 CLI | 精确文件清单的压缩上下文包与 token 闸门 | 推荐 |
| Serena `1.5.3` | MIT | 本地 MCP + OSS LSP | 疑难热点的定义/引用/声明精确解析 | 可选 |
| Universal Ctags | GPL-2.0 | 本地 CLI | 不支持语言的定义/作用域兜底清单 | 可选 |
| ast-grep `0.44.1` | MIT | 本地 CLI | 装饰器、注册、结构模式等确定性查询 | 可选 |
| Joern `4.0.579` | Apache-2.0 | 本地 CLI | CPG、CFG、PDG、数据流深度分析 | 显式 deep-only |

Serena 的付费 JetBrains 后端不允许进入本方案；只允许经许可证审核的开源 language server。CodeQL、商业 Semgrep 跨文件能力、闭源 SaaS、未核验许可证的 SCIP indexer 均不进入依赖集合。

## 对 V1 的影响

本方案不直接替换当前 V1。V1 的 goal、ADR、doctor、`raw-deep-*` 产物和真实 UAT 规则都把 Graphify semantic/deep 流程写成强制契约。直接切换会让已有基线失效。

正确迁移路径是建立 **V2 证据契约**并先做 shadow A/B：

1. V1 保持默认和可回滚。
2. V2 单独记录 `graphify-code-only`，不把它伪装成 `raw-deep`。
3. 六个固定仓库上分别运行 V1/V2，各自两次独立执行。
4. 同时测量总耗时、所有模型/Agent token 与费用、重复源码读取、引用有效性、业务模块质量和人工介入。
5. 只有达到预先声明的 go/no-go 阈值，才进入小流量 canary。

## 文档导航

- [完整模块与证据设计](architecture.md)
- [安装、版本和命令配置](configuration.md)
- [Repomix 配置样例](repomix-hotspot.config.example.json)
- [开源工具选择与排除项](oss-tool-selection.md)
- [实验记录](experiments.md)
- [迁移、A/B 评估和回滚](rollout-and-evaluation.md)
- [Graphify、Tree-sitter、Repomix 一手来源调研](tool-research.md)

## 决策摘要

- **接受**：Git 索引先行，用于确定源文件全集和缓存身份。
- **接受**：按热点组织上下文和子代理工作，但热点必须来自关系图与确定性特征，不是目录深度。
- **接受**：Graphify 只跑 `--code-only`，不在默认代码路径调用 LLM。
- **接受**：Repomix 负责方向性上下文；最终结论回到精确源码范围。
- **条件接受**：Serena 仅使用开源 LSP 后端，按疑难热点调用并记录查询证据。
- **条件接受**：Joern 只在用户明确要求数据流/污点/安全深挖时运行。
- **拒绝**：第一阶段自研完整 Tree-sitter 跨文件解析与解析器生态。
- **拒绝**：把目录结构直接当作业务模块或子代理所有权。
- **拒绝**：任何闭源、SaaS-only、付费后端或许可证不明确的关键依赖。
