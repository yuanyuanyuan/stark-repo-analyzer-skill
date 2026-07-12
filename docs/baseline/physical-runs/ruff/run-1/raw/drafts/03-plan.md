# 阶段 3：分析计划

## 模式与范围

- 用户已固定选择 `standard`；未运行参考流程中的 AskUserQuestion，原因是本次是
  非交互 physical baseline。该要求记为 **not performed**，不是用户确认。
- 规模：对 `crates/` 中非测试、非 benchmark 的 Rust 文件执行 `wc -l`，获得
  665,641 行。这是粗略物理行统计，未扣除注释/生成代码，故不等同于“有效代码”。
- 该规模大于参考指引的 50,000 行阈值，采用 bounded scope：三个核心交付路径，
  每个要求至少 60% 实际读取覆盖率；其他模块只作生态定位。

## 纳入的核心模块

| 模块 | 业务边界 | 为什么纳入 |
|---|---|---|
| CLI 与配置编排 | 命令解析、文件发现、设置解析与 check/format 分派 | 它定义统一工具的用户可见契约 |
| Lint 分析与修复 | lint 驱动、诊断汇集、fix 策略 | 它承载多规则兼容和安全修改的核心价值 |
| Python 格式化管线 | Python AST 格式化、注释定位、文档 IR 与打印 | 它承载 Black 兼容与统一工具链的另一半 |

## 明确排除（未覆盖，不代表不重要）

- ty 的类型检查器及其语言服务器；
- 大多数 `ruff_linter` 规则实现；
- parser、AST、语义模型、缓存、notebook、WASM、LSP server、发布/CI、fuzz 与
  Python 支持脚本；
- 性能基准、运行时行为和完整测试结果。

## 已识别的探索问题

1. “最近配置 + 显式 extend”如何避免大型仓库中隐式层叠带来的不可预测性？
2. 规则广度和安全自动修复如何在同一个 lint 运行中保持可解释性？
3. Black 兼容目标如何限制 formatter 的配置面，并影响其内部文档/打印架构？

## 验证策略

- 静态源码阅读由三个独立模块草稿完成，主 agent 随后抽查跨模块结论。
- 不运行测试：`AGENTS.md` 的建议命令带 `INSTA_UPDATE=always` 与
  `MDTEST_UPDATE_SNAPSHOTS=1`，会修改源树，违反本次不修改源树约束。
- 不运行 cargo/clippy：环境中 `cargo`、`rustc` 均不可用（exit 127）。
