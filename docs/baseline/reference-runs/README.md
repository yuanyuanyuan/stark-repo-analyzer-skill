# Reference Skill Baseline Runs

这些目录保存参考仓库 `repo-analyzer` skill 在固定本地源码上的 `standard` 基线运行结果。

## Run Profile

- 分析模式：`standard`
- 源码来源：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/`
- 源码版本：见 [`../source-corpus-manifest.json`](../source-corpus-manifest.json)
- 流程：规模评估、项目文档研读、外部调研、特征识别、模块分析、交叉验证和最终报告
- 输出语言：中文
- Git 历史：不作为当前源码行为证据

## Per-project Artifacts

每个项目目录应包含：

- `metadata.json`
- `execution-log.md`
- `drafts/03-research.md`
- `drafts/03-plan.md`
- `drafts/05-modules-plan.md`
- `drafts/06-module-*.md`
- `drafts/07-cross-validation.md`
- `drafts/08-insights.md`
- `drafts/08-coverage.md`
- `ANALYSIS_REPORT.md`
- `checks.md`

覆盖率不足、外部调研失败或无法从固定 commit 证明的结论，必须在对应项目的日志和检查表中明确记录。

## Comparison Rule

这些报告是参考实现的输出基线，不是绝对正确答案。后续重实现应比较：

1. 是否覆盖相同的核心问题和模块边界；
2. 是否保留源码证据、Why > What 推理和架构图；
3. 是否明确记录不确定性、限制和覆盖率；
4. 是否在不同规模和 Agent 生态项目上保持一致的质量下限。
