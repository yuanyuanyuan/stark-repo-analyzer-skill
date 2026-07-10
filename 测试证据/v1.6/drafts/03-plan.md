# v1.6 分析计划与预算档

分析对象：`/tmp/Long_screenshot_splitting_tool`
分析模式：标准分析
输出目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.6`

## 1. 模式选择

选择“标准分析”，原因：

- 目标仓库有 3 个以上核心模块：截图分割流水线、状态与导出、SEO/i18n/导航、构建与共享基础设施。
- 仓库包含测试、构建脚本、配置、共享组件等次要区域，适合标准模式覆盖关键边界，但不需要深度模式逐一展开所有边缘路径。
- 用户要求验证 v1.1-v1.7 acceptance checklist，必须覆盖 Evidence Plan、Evidence Matrix、Unsupported Claims、Risk Sampling、Budget Profiles 和 Markdown Repo Map。

## 2. 预算目标

| 维度 | 标准模式目标 |
|---|---|
| Evidence 深度 | 覆盖核心模块、关键边界和主要设计决策；核心模块关键判断必须带源码锚点。 |
| 风险抽样强度 | 每个核心模块至少 1 条相关风险路径；重要边界可追加抽样。 |
| 报告长度目标 | 完整报告，但控制在可读范围内，优先解释设计取舍，不做文件流水账。 |
| Subagent 数量上限 | 4 个核心模块 subagent；次要模块合并到构建/共享基础设施或最终评价。 |
| 外部调研强度 | 轻量；优先 README/docs，本次不做联网调研，不执行生态命令。 |

## 3. 计划阶段

1. 读取 `repo-analyzer` 技能和验收清单。
2. 使用 graphify 查询本仓库相关上下文，并以源码/文档复核候选结论。
3. 生成 `drafts/02-repo-map.md`，只写候选信号。
4. 生成 `drafts/03-research.md` 与本计划。
5. 生成 `drafts/05-modules-plan.md`，包含核心模块 Evidence Plan。
6. 并行启动 4 个模块 subagent，分别写入：
   - `drafts/06-module-splitting-pipeline.md`
   - `drafts/06-module-state-export.md`
   - `drafts/06-module-seo-i18n-navigation.md`
   - `drafts/06-module-build-shared-infra.md`
7. 主 agent 等待全部模块草稿完成后，做交叉验证、Unsupported Claims 检查和 Budget Profile 执行摘要。
8. 生成最终报告、验收矩阵、历史对比报告和运行日志。

## 4. 成本边界

- 不执行 `npm install`、`npm test`、`npm run build`、`pnpm` 等生态命令。
- 不引入 repo-map JSON、scan CLI、自动质量门、LLM judge 或精确 token 统计。
- 代码统计和文件枚举使用 `find`、`wc`、`awk`、`rg` 等系统命令。
- 源码深读由模块 subagent 聚焦候选入口，避免对测试、lock、工具状态文件做低价值铺读。

## 5. 预期验收产物

| 产物 | 路径 |
|---|---|
| Repo Map | `drafts/02-repo-map.md` |
| 调研摘要 | `drafts/03-research.md` |
| 预算计划 | `drafts/03-plan.md` |
| 模块计划 | `drafts/05-modules-plan.md` |
| 模块草稿 | `drafts/06-module-*.md` |
| 交叉验证 | `drafts/07-cross-validation.md` |
| 洞察与执行摘要 | `drafts/08-insights.md` |
| 最终分析报告 | `ANALYSIS_REPORT.md` |
| 验收结果 | `ACCEPTANCE_RESULT.md` |
| 历史对比 | `COMPARISON_REPORT.md` |
| 运行日志 | `RUN_LOG.md` |
