# PLAN 实现合规基线

本文把 [`PLAN.md`](PLAN.md) 及 ADR 中的承诺拆成三类：

1. **v1 必须实现**：当前 skill 要作为可用交付物成立，必须稳定具备的能力。
2. **已废弃 / 已改写**：后续 ADR 已明确裁剪、替换或禁止实现的能力。
3. **延后实现**：PLAN 仍有价值，但不属于当前最小可用版本，后续按优先级补。

> 口径说明：这里评估的是“功能承诺覆盖”，不是代码覆盖率。当前实现以 `scripts/repo_analyzer.py` 的确定性 CLI、`SKILL.md` 的用户调用说明、`tests/test_repo_analyzer_cli.py` 的公共接口测试，以及 `uat-evidence/run-003` 的 UAT 证据为准。

## 结论

当前版本不是完整实现 `PLAN.md` 的 full-spec 方案，而是实现了一个 **v1 最小可用 skill**：

- 已能被用户用短提示调用，分析 GitHub 或本地仓库。
- 已能生成分析底料、模块候选、模块深度分析底稿、cross-ref 校验、符号覆盖率门控、tree-sitter 可用性/parse 记录、受众报告、状态报告、SLA/配置记录、env/defaults/last-session 配置链和本地验收入口。
- 已通过 `claude-video` 的 UAT 回路，并修复了主报告重复、prompt 过长、Markdown 验收等问题。
- 尚未实现 PLAN 中成本最高的完整智能闭环：真正的模块 subagent 深挖、独立 cross-ref 审稿、tree-sitter grammar query 符号提取、token/retry 预算、13 条硬断言里的 LLM judge / Mermaid / 外链检查。

因此当前状态应标记为：

```text
v1 可用性: PASS
full PLAN 合规: PARTIAL
```

## 当前覆盖率总览

| 类别 | 条目数 | 当前状态 |
|---|---:|---|
| v1 必须实现 | 13 | 12 已实现，1 部分实现 |
| 已废弃 / 已改写 | 5 | 5 已由 ADR 明确处理 |
| 延后实现 | 14 | 7 已最小实现，7 延后 |

## 1. v1 必须实现

这些能力是当前 skill 作为 v1 版本成立的最低边界。

| # | 能力 | 当前覆盖 | 证据 | 缺口 |
|---|---|---|---|---|
| 1 | 通过 Codex skill 规则触发，用户可用 `$stark-repo-analyzer` 短提示调用 | 已实现 | [`SKILL.md`](../SKILL.md) | 无 |
| 2 | 支持 GitHub URL 和本地路径作为目标仓库 | 已实现 | [`checkout_target`](../scripts/repo_analyzer.py) | 无 |
| 3 | 克隆远程仓库时不污染当前工作区 | 已实现 | 使用 `tempfile.TemporaryDirectory` | 无 |
| 4 | 确定性环节用脚本执行，而不是让 LLM 猜 | 已实现 | [`scripts/repo_analyzer.py`](../scripts/repo_analyzer.py) | 无 |
| 5 | 生成基础元数据 `00-meta.txt` | 已实现 | `write_meta()` | 无 |
| 6 | 生成 Phase-2a repo 类型与 5KB 名片 | 已实现 | `02a-repo-type.yaml`、`02a-manifest-card.md` | repo 类型规则目前写在代码里 |
| 7 | 按 repo 类型动态生成切片 | 部分实现 | `SLICES` 与 `write_slices()` | 未外置为 `config/repo-types.yaml` |
| 8 | 生成用户问题答案文件，支持无交互默认值 | 部分实现 | `03-question-answers.md` | 还没有真正的 `ask_user()` 运行时适配层 |
| 9 | 生成模块候选清单 | 已实现 | `05-module-ids.yaml` | 文件名与原 PLAN 的 `05-modules-plan.md` 不一致，当前更适合机器读 |
| 10 | 生成模块深度分析底稿 | 已实现 | `drafts/06-module-*.md` | 当前是确定性深度底稿，不是真 subagent 判断 |
| 11 | 生成覆盖率、cross-ref 与状态报告 | 已实现 | `drafts/07-cross-ref-checks.md`、`08-coverage.md`、`expected-symbols.json`、`coverage-symbols.json`、`STATE_REPORT.md` | 当前 tree-sitter 负责 parse 可用性与大文件保护记录，符号提取仍用正则 fallback |
| 12 | 生成最终报告和三类受众报告 | 已实现 | `ANALYSIS_REPORT.md`、`ANALYSIS_REPORT.tech-lead.md`、`ANALYSIS_REPORT.business.md`、`ANALYSIS_REPORT.learning.md` | 模板逻辑内嵌在脚本中 |
| 13 | 提供本地验收入口 | 已实现 | `acceptance/check.sh` | 已覆盖产物、链接、受众差异、cross-ref、coverage、SLA；未含 LLM judge / Mermaid render / 外链检查 |

## 2. 已废弃 / 已改写

这些不是“漏做”，而是后续决策已经改变了原 PLAN。

| 原 PLAN 承诺 | 当前分类 | 决策来源 | 说明 |
|---|---|---|---|
| 阶段一 `repomix --compress` 宏观认知建模 | 已废弃 | [ADR-0001](decisions/0001-phase-1-cut.md) | 改为 Phase-2a 生成 5KB 名片，减少一次压缩和多 subagent 调用 |
| 阶段一 4+1 overview subagent 并行写 `overview.md` | 已废弃 | [ADR-0001](decisions/0001-phase-1-cut.md) | 不再保留 `overview.md` 作为 v1 必需产物 |
| 固定 12 维切片 | 已改写 | [ADR-0002](decisions/0002-phase-2a-dynamic.md) | 改为先识别 repo 类型，再按类型生成 N 维切片 |
| `--max-context` / `--max-history` 等阶段一遗留开关 | 已废弃 | [ADR-0001](decisions/0001-phase-1-cut.md) | 阶段一移除后，这两个开关不再有明确用途 |
| 与 graphify 共享索引或读写 `graphify-out/` | 禁止实现 | [ADR-0013](decisions/0013-graphify-decoupled.md) | repo-analyzer 与 graphify 完全解耦 |

## 3. 延后实现

这些是 full PLAN 的真实缺口。它们没有被 ADR 废弃，但当前 v1 没有实现。

| 优先级 | 能力 | 来源 | 当前状态 | 延后原因 |
|---|---|---|---|---|
| P0 | 模块 subagent 深度分析 | `PLAN.md` 阶段五 | 部分实现 | 已生成确定性深度底稿；缺少真 subagent 判断型深挖 |
| P0 | cross-ref 双层质检 | [ADR-0004](decisions/0004-cross-ref-two-stage.md) | 部分实现 | 已生成 `07-cross-ref-checks.md`；缺少独立审稿 subagent 和回退循环 |
| P0 | tree-sitter + grep 覆盖率门控 | [ADR-0005](decisions/0005-coverage-tree-sitter.md) | 部分实现 | 已有 `auto` engine、`expected-symbols.json`、tree-sitter parse 统计和 5MiB 大文件跳过；未做 grammar query 级符号抽取 |
| P0 | ADR-0011 全 13 条硬断言 | [ADR-0011](decisions/0011-acceptance-script-enforce.md) | 部分实现 | 已扩展本地硬断言；未实现 LLM judge / Mermaid render / 外链检查 |
| P1 | `ask_user()` 三运行时适配器 | [ADR-0003](decisions/0003-ask-user-api.md) | 未实现 | 当前只支持默认答案与 `--no-question` 语义 |
| P1 | `config/repo-types.yaml` 外置切片模板 | [ADR-0002](decisions/0002-phase-2a-dynamic.md) | 未实现 | 当前切片模板内嵌在 `SLICES` 常量里 |
| P1 | 三受众模板与 `render_report.py` 分离 | [ADR-0006](decisions/0006-templates-three-audiences.md) | 未实现 | 当前报告渲染内嵌在一个 Python 文件里 |
| P1 | SLA 预算、token/time 统计、3 次重试 | [ADR-0007](decisions/0007-sla-budget.md) | 部分实现 | 已记录时间 SLA 和 resume；未统计 token 或自动重试 |
| P1 | 失败模块详细 schema 与报告 `§9` | [ADR-0015](decisions/0015-failed-module-section.md) | 部分实现 | `STATE_REPORT.md` 有 `failed_modules: []`，但无失败详情渲染 |
| P2 | 外部调研 `03-research.md` | `PLAN.md` 阶段三半 | 未实现 | 原计划默认 OFF，v1 暂未接入 web research |
| P2 | env 覆盖、`defaults.yaml extends:`、`last-session.json` | [ADR-0012](decisions/0012-compromise-config.md) | 已实现 | 已支持默认配置、显式 `--config`、`REPO_ANALYZER_*` 覆盖、`extends:` 继承、`--save-pref` / `--use-last-pref` |
| P2 | tree-sitter chunked 5MB 与 benchmark | [ADR-0014](decisions/0014-treesitter-chunked.md) | 部分实现 | 已串行扫描并跳过 ≥5MiB 文件；未补三仓库 benchmark |
| P2 | Mermaid 渲染、外链检查、LLM-judge | [ADR-0011](decisions/0011-acceptance-script-enforce.md) | 未实现 | 成本高，且需要额外运行依赖/模型预算 |
| P2 | 原始 smart-search-mcp 终验收路径 | [`docs/goals/implement-plan-with-ponytail-tdd.md`](../docs/goals/implement-plan-with-ponytail-tdd.md) | 未完成到最新 UAT | 最新 UAT 改为 `claude-video`，不能替代原目标仓库验收 |

## 最小补齐顺序

如果继续补 full PLAN，不建议一次性补所有延后项。最小顺序如下：

1. **升级到 tree-sitter grammar query coverage**
   - 当前 auto engine 已能记录 tree-sitter 是否可用、parse 文件数和大文件跳过情况。
   - 下一步再把 expected-symbols 从正则提取升级为 grammar query 提取。

2. **补真 subagent 审稿**
   - 当前 `07-cross-ref-checks.md` 是确定性校验。
   - 下一步再接独立审稿 subagent 和失败回退循环。

3. **补失败模块 §9**
   - 当前 `STATE_REPORT.md` 已有 `failed_modules`，但最终报告没有条件渲染失败模块专章。
   - 下一步补 ADR-0015 的报告章节和验收 schema。

4. **补高成本 acceptance**
   - 当前已覆盖本地硬断言。
   - 下一步只在需要 full PLAN 合规时补 LLM-judge、Mermaid render、外链检查。

## 维护规则

- 修改 `scripts/repo_analyzer.py` 的可观察行为后，同步更新本文件的覆盖状态。
- 如果某个延后项被明确放弃，必须新建 ADR 或更新对应 ADR，再移动到“已废弃 / 已改写”。
- UAT 通过只能证明当前测试场景可用，不能自动视为 full PLAN 合规。
