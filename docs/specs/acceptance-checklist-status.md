# Acceptance Checklist 验证状态同步

更新时间：2026-07-10

本文件同步 `测试证据/v1.6/ACCEPTANCE_RESULT.md` 的最新人工验收结论，用于快速查看 v1.1-v1.7 checklist 当前验证状态。各版本原始 checklist 仍保留为验收模板和通过条件定义。

## 最新验证对象

- 目标仓库：`yuanyuanyuan/Long_screenshot_splitting_tool`
- 本地源码：`/tmp/Long_screenshot_splitting_tool`
- 测试证据目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.6`
- 模式：标准分析
- 验收结果来源：`测试证据/v1.6/ACCEPTANCE_RESULT.md`

## 汇总状态

| Checklist | 当前状态 | 证据 | 说明 |
|---|---|---|---|
| `v1.1-acceptance-checklist.md` | 通过 | `测试证据/v1.6/ACCEPTANCE_RESULT.md` | 核心结论有源码锚点；无锚点内容降级；行覆盖率仅作规模参考。 |
| `v1.2-acceptance-checklist.md` | 通过 | `测试证据/v1.6/drafts/05-modules-plan.md` | 4 个核心模块均有 Evidence Plan，并被模块草稿回应。 |
| `v1.3-acceptance-checklist.md` | 通过 | `测试证据/v1.6/drafts/06-module-*.md` | 4 个核心模块草稿均包含 Markdown Evidence Matrix。 |
| `v1.4-acceptance-checklist.md` | 通过 | `测试证据/v1.6/drafts/07-cross-validation.md` | Unsupported Claims 已在交叉验证中记录，未验证内容进入限制或开放问题。 |
| `v1.5-acceptance-checklist.md` | 通过 | `测试证据/v1.6/drafts/06-module-*.md`、`07-cross-validation.md` | 每个核心模块均包含风险路径抽样，风险发现进入最终评价。 |
| `v1.6-acceptance-checklist.md` | 部分通过 | `测试证据/v1.6/drafts/03-plan.md`、`05-modules-plan.md`、`07-cross-validation.md`、`08-insights.md` | 标准模式预算目标、计划影响和执行摘要已验证；快速/深度模式未运行，因此三模式对比项未验证。 |
| `v1.7-acceptance-checklist.md` | 通过 | `测试证据/v1.6/drafts/02-repo-map.md`、`05-modules-plan.md` | Repo Map 存在且只写候选信号，并驱动 Evidence Plan 与阅读范围。 |

## v1.6 未完全通过的原因

`docs/specs/v1.6-acceptance-checklist.md` 的完整通过条件要求分别运行快速、标准、深度三种模式，并比较 evidence 数量、风险抽样强度和报告长度。本次 `v1.6` 测试证据只运行了标准模式，因此：

- 已通过：预算目标记录、模式影响 Evidence Plan 与 subagent 输入、标准模式核心覆盖、实际执行摘要、未引入自动 token 或新 CLI。
- 未验证：快速模式减少 evidence 和篇幅、深度模式增加风险和替代方案。

因此当前同步状态应保持为：**v1.6 部分通过**，不能写成完全通过。

## 后续补全条件

要把 v1.6 从“部分通过”更新为“通过”，需要补充两次同仓库同口径运行：

1. 快速模式运行目录：应能证明 evidence 数量和报告篇幅少于标准模式，同时保留核心锚点、Evidence Plan、Evidence Matrix、风险抽样和 Unsupported Claims。
2. 深度模式运行目录：应能证明比标准模式增加次要模块、边缘路径、替代方案或更充分风险抽样。
3. 更新 `测试证据/v1.6/ACCEPTANCE_RESULT.md` 与本状态文件，将 v1.6 第 3、5 项从“未验证”改为实际结论。

## 不改变的内容

- 本文件不修改各 checklist 的验收标准。
- 本文件不把综合 v1.6 流程中的后续能力反向要求到 v1.1-v1.3 的最小验收中。
- 本文件不引入自动 gate、JSON schema、LLM judge、精确 token 计量或新 CLI。
