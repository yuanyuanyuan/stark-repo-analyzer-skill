# PLAN 实现合规基线

本文把 [`PLAN.md`](PLAN.md) 及 ADR 中的承诺拆成三类。当前目标不是停在 v1 最小可用，而是继续补齐 `PLAN.md` 中成本最高的完整智能闭环：repomix 原料切片、判断型模块深挖、独立 cross-ref 审稿、coverage gate、失败回退和最终 UAT。

1. **v1 必须实现**：当前 skill 要作为可用交付物成立，必须稳定具备的能力。
2. **已废弃 / 已改写**：后续 ADR 已明确裁剪、替换或禁止实现的能力。
3. **延后实现**：PLAN 仍有价值，但不属于当前最小可用版本，后续按优先级补。

> 口径说明：这里评估的是“功能承诺覆盖”，不是代码覆盖率。当前实现以 `scripts/repo_analyzer.py` 的确定性 CLI、`SKILL.md` 的用户调用说明、`tests/test_repo_analyzer_cli.py` 的公共接口测试，以及 `uat-evidence/run-005` 的 UAT 证据为准（run-005 即 `claude-video` 完整智能闭环 UAT，`acceptance/check.sh` 245 项与裁判重跑 `acceptance-recheck-main.log` 均 245/245 PASS）。

## 结论

当前版本不是完整实现 `PLAN.md` 的 full-spec 方案，而是一个已通过**完整智能闭环 UAT** 的可用 skill：

- 已能被用户用短提示调用，分析 GitHub 或本地仓库。
- 已能生成分析底料、repomix 动态切片、模块候选、模块深度分析底稿、agent 模块深挖、agent cross-ref 审稿、符号覆盖率门控、tree-sitter 可用性/parse 记录、受众报告、状态报告、SLA/配置记录、性能慢因诊断、env/defaults/last-session 配置链和本地验收入口。
- 已通过 `claude-video` 的**完整智能闭环 UAT（run-005）**：18 阶段全 PASS、`acceptance/check.sh` 245 项与裁判重跑 `acceptance-recheck-main.log` 均 245/245 PASS、8 模块符号覆盖率全 1.00、SLA 预算内（415s / 30min）、三受众报告差异化达标；并修复了主报告重复、prompt 过长、Markdown 验收等问题。
- 完整智能闭环的终验（模块 agent 深挖、coverage 失败修复、独立 cross-ref 审稿、cross-ref 回退修复、tree-sitter grammar query 符号提取、三受众模板渲染）已在 run-005 中**实际跑通并验证通过**，不再是开放缺口；此前成本高、未实现的 7 项能力中 6 项已在后续增量实现（T01–T22）中补齐，**T07 外部调研为已知限制 stub**（`--research` 开关已接但 `write_research()` 硬编码 SKIP，不产出真实 5 章节）：token 统计（T05/T06）、ADR-0011 硬断言扩展的 LLM-judge / 真实 Mermaid 渲染 / 外链(http)检查（T09/T10/T11/T12）、`ask_user()` 三运行时适配器（T03/T04）、`config/repo-types.yaml` 外置（T01/T02）、tree-sitter 多语言 benchmark（T14）；真实跨模块冲突验证见 `tests/fixtures/conflict-repo`（T13）；run-005 的 6 维度人工 `JUDGE.md` 已补齐（T15）。

因此当前状态应标记为：

```text
v1 可用性: PASS
完整智能闭环 UAT (run-005): PASS
full PLAN 合规: PASS（* T07 外部调研为已知限制 stub；LLM-judge / Mermaid / 外链检查在离线或依赖缺失时 SKIP/WARN，不致命）
```

## 当前覆盖率总览

| 类别 | 条目数 | 当前状态 |
|---|---:|---|
| v1 必须实现 | 13 | 13 已实现，0 部分实现 |
| 已废弃 / 已改写 | 5 | 5 已由 ADR 明确处理 |
| 延后实现 | 14 | 13 已实现，1 为已知限制 stub（T07 外部调研） |

> 注：v1 的 13 项均已实现（含第 7 项切片外置 `config/repo-types.yaml` 与第 8 项 `ask_user()` 适配器）；延后实现的 14 项中 13 项已在 T01–T22 增量实现中补齐，T07 外部调研仅接好开关、为 SKIP stub（已知限制）；LLM-judge / Mermaid 渲染 / 外链检查在离线或依赖缺失时按 graceful degradation 降级为 SKIP/WARN。run-005 之后，Round 6（T05–T10 / ADR-0016~0019）又落地 5 项增强（单文件重构为 `analyzer_*.py` 模块、输出目录重组为 `.stark-repo-analyzer/`、运行时预检与 agent 模式自动降级、`[N/M]` 进度与运行日志、LLM-judge 模型默认置空、项目名片扩容至 10KB），均属已落地能力，详见第 6 节，不改变本表的合规判定。

## 1. v1 必须实现

这些能力是当前 skill 作为 v1 版本成立的最低边界。

| # | 能力 | 当前覆盖 | 证据 | 缺口 |
|---|---|---|---|---|
| 1 | 通过 Codex skill 规则触发，用户可用 `$stark-repo-analyzer` 短提示调用 | 已实现 | [`SKILL.md`](../SKILL.md) | 无 |
| 2 | 支持 GitHub URL 和本地路径作为目标仓库 | 已实现 | [`checkout_target`](../scripts/repo_analyzer.py) | 无 |
| 3 | 克隆远程仓库时不污染当前工作区 | 已实现 | 使用 `tempfile.TemporaryDirectory` | 无 |
| 4 | 确定性环节用脚本执行，而不是让 LLM 猜 | 已实现 | [`scripts/repo_analyzer.py`](../scripts/repo_analyzer.py) | 无 |
| 5 | 生成基础元数据 `data/meta.txt` | 已实现 | `write_meta()` | 无 |
| 6 | 生成 Phase-2a repo 类型与 10KB 项目名片 | 已实现 | `data/repo-type.yaml`、`data/manifest-card.md` | 切片维度已外置到 `config/repo-types.yaml`（见行 7）；名片经 [ADR-0019](decisions/0019-llm-judge-model-and-manifest-10k.md) 由 5KB 扩容至 10KB（含 Git 信息 / 代码规模 / 许可证 / 依赖摘要 / 运行命令 / 顶层目录 / README 前 4000 字符） |
| 7 | 按 repo 类型动态生成 repomix 切片 | 已实现 | `RepoTypeLoader`（`scripts/repo_types_loader.py`）、`write_slices()`（`scripts/analyzer_slicing.py`）、`run_repomix_slice()`、`config/repo-types.yaml` | 切片维度已外置到 `config/repo-types.yaml`，由 `RepoTypeLoader` 加载，与历史内嵌 `SLICES` 逐字节一致；`version` 绑定 `SKILL.md`；`RepoTypeLoader` 在 `analyzer_common._LOADER` 中以单例形式被全模块共享 |
| 8 | 生成用户问题答案文件，支持无交互默认值 | 已实现 | `data/question-answers.md`、`ask_user_adapters.py` | 已有 `ask_user()` 三运行时适配层（claude-code/codex/cursor）+ 降级链，离线/未知运行时回落 `defaults.yaml` |
| 9 | 生成模块候选清单 | 已实现 | `data/module-ids.yaml` | 文件名与原 PLAN 的 `05-modules-plan.md` 不一致，当前更适合机器读 |
| 10 | 生成模块深度分析底稿 | 已实现 | `diagnostics/module-drafts/module-*.md`、`agent-runs/modules-batch/`、`data/agent-summary.json` | 默认 deterministic；`--agent-mode codex|command` 会批量执行判断型 agent 并把结果追加进模块草稿 |
| 11 | 生成覆盖率、cross-ref 与状态报告 | 已实现 | `diagnostics/cross-ref-checks.md`、`diagnostics/cross-ref-agent-review.md`、`data/coverage.md`、`data/expected-symbols.json`、`data/coverage-symbols.json`、`reports/STATE_REPORT.md` | agent 审稿已有可运行入口；tree-sitter 负责 parse 可用性、grammar query 符号提取与大文件保护记录；run-005 因本机无 `tree-sitter` CLI（`tree_sitter_available: false`）自动回退 `regex-fallback`，属环境依赖而非功能缺失 |
| 12 | 生成最终报告和三类受众报告 | 已实现 | `data/report-data.json`、`templates/`、`scripts/render_report.py`、`reports/ANALYSIS_REPORT*.md` | 已支持模板与数据分离，可单独重渲染（`render_report.py --output-dir`） |
| 13 | 提供本地验收入口 | 已实现 | `acceptance/check.sh`、`04-link.sh`、`05-mermaid-judge.sh`、`llm-judge.sh` | 已覆盖产物、链接、受众差异、cross-ref、coverage、SLA；并扩展 3 个执行器（外链可达性 / Mermaid 渲染 / LLM-judge），输出 `TOTAL:` 汇总行；离线/缺失依赖时 SKIP/WARN |

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
| P0 | 模块 subagent 深度分析 | `PLAN.md` 阶段五 | 已实现并验证（run-005） | 已有 `--agent-mode codex|command` 批量判断型深挖、prompt/result/attempt 落盘和最多 3 次重试；run-005 完整智能闭环 UAT 245/245 PASS，`modules-batch` 子会话 365.25s read-only 实际跑通，质量已由终验证明 |
| P0 | cross-ref 双层质检 | [ADR-0004](decisions/0004-cross-ref-two-stage.md) | 已实现并验证（run-005） | 已有确定性 `diagnostics/cross-ref-checks.md`、压缩审稿包 `diagnostics/cross-ref-review-input.md`、独立 `diagnostics/cross-ref-agent-review.md` 审稿和 `cross-ref-repair-*` 回退修复；run-005 中确定性校验 + 独立审稿 + repair 均 PASS、无断裂引用；真实冲突质量验证见最小补齐 #2（`tests/fixtures/conflict-repo`） |
| P0 | tree-sitter + grep 覆盖率门控 | [ADR-0005](decisions/0005-coverage-tree-sitter.md) | 已实现并验证（run-005） | 已有 `auto` engine、`expected-symbols.json`、tree-sitter grammar query 抽取、parse/query 统计、5MiB 大文件跳过和 coverage 失败模块 agent repair；run-005 因本机无 `tree-sitter` CLI 自动回退 `regex-fallback`（属环境依赖，非功能缺失）；仍缺真实多语言 benchmark（最小补齐 #1） |
| P0 | repomix 原料切片 | `PLAN.md` 阶段二 | 已实现并验证（run-005） | 动态维度由脚本选择，切片内容由 `npx repomix --style xml` 生成；run-005 真实 repomix 切片 13.18s 验证通过（单元测试仍用 fake `npx` 验证编排） |
| P0 | ADR-0011 验收硬断言 | [ADR-0011](decisions/0011-acceptance-script-enforce.md) | 已实现并验证（run-005，已扩展至 245 项） | 本地硬断言已扩展至 245 项（run-005 `check.sh` 与裁判重跑均 245/245 PASS）；仍缺 LLM judge / 真实 Mermaid render / 外链(http)检查（最小补齐 #3） |
| P1 | `ask_user()` 三运行时适配器 | [ADR-0003](decisions/0003-ask-user-api.md) | 已实现 | `ask_user_adapters.py`（T03/T04）：`detect_runtime()` + claude-code/codex/cursor 适配器 + 降级链到 `defaults.yaml`，支持 `REPO_ANALYZER_ANSWERS_FILE` 回填；`tests/test_ask_user_adapters.py` |
| P1 | `config/repo-types.yaml` 外置切片模板 | [ADR-0002](decisions/0002-phase-2a-dynamic.md) | 已实现 | `config/repo-types.yaml` + `RepoTypeLoader`（T01/T02），运行时加载且与原 `SLICES` 逐字节一致，`version` 绑定 `SKILL.md`；`tests/test_repo_types_loader.py` |
| P1 | 三受众模板与 `render_report.py` 分离 | [ADR-0006](decisions/0006-templates-three-audiences.md) | 已最小实现 | 已新增 `templates/ANALYSIS_REPORT.*.tmpl.md`、`REPORT_DATA.json` 和 `scripts/render_report.py`；主 CLI 仍一键渲染 |
| P1 | SLA 预算、token/time 统计、3 次重试 | [ADR-0007](decisions/0007-sla-budget.md) | 已实现 | 已记录时间 SLA、阶段耗时、agent attempt 耗时、慢因排名、resume 和 agent 最多 3 次重试，并接入 token 统计（T05/T06）：agent 返回 `<!-- TOKENS: in,out -->`，汇总到 `SLA_REPORT.md` / `PERFORMANCE_REPORT.md(json)` / `CONFIG_EFFECTIVE.json`（预算 500K，命令模式=0，绿/黄/红三档）；`tests/test_token_reporter.py` |
| P1 | 失败模块详细 schema 与报告 `§9` | [ADR-0015](decisions/0015-failed-module-section.md) | 已实现 | 失败时三受众报告和总览报告渲染 `§9 未完成模块明细`；PASS 时不渲染 |
| P2 | 外部调研 `03-research.md` | `PLAN.md` 阶段三半 | 已知限制（stub） | `--research` 开关已接（T07/T08，默认 OFF），但 `write_research()` 当前硬编码 `status: SKIP`，**不产出** `03-research.md` 真实 5 章节；报告 `{{ research_section }}` 已接入但恒为空；`tests/test_research_stage.py` 仅验证 OFF→无文件/SKIP 路径。真实联网调研待补（需网络 + WebSearch/codex 能力） |
| P2 | env 覆盖、`defaults.yaml extends:`、`last-session.json` | [ADR-0012](decisions/0012-compromise-config.md) | 已实现 | 已支持默认配置、显式 `--config`、`REPO_ANALYZER_*` 覆盖、`extends:` 继承、`--save-pref` / `--use-last-pref` |
| P2 | tree-sitter chunked 5MB 与 benchmark | [ADR-0014](decisions/0014-treesitter-chunked.md) | 已实现 | 已串行扫描并跳过 ≥5MiB 文件；`scripts/benchmark_treesitter.py` + `docs/benchmarks/tree-sitter-baseline.md` 已补基准（在线参考仓库需联网补真实数据，离线环境用本地测量占位） |
| P2 | Mermaid 渲染、外链检查、LLM-judge | [ADR-0011](decisions/0011-acceptance-script-enforce.md) | 已实现 | `04-link.sh`（外链/commit 校验）、`05-mermaid-judge.sh`（mermaid-cli 渲染）、`llm-judge.sh`→`llm_judge.py`（codex exec 评分）均落地并由 `check.sh` 串联（T09/T10/T11/T12）；离线/依赖缺失时 SKIP/WARN，不致命；`tests/test_acceptance_executors.py` |
| P2 | 原始 smart-search-mcp 终验收路径 | [`docs/goals/implement-plan-with-ponytail-tdd.md`](../docs/goals/implement-plan-with-ponytail-tdd.md) | 已由 `claude-video` 取代 | 最新 UAT 已改为 `claude-video`（run-005 245/245 PASS），原 smart-search-mcp 路径仅作为额外回归候选，不再阻塞 |

## 4. Codex agent 慢因记录

用户明确要求不要用超时掩盖慢问题。最新定位如下：

- 慢点不在脚本自切片；切片已改为 `npx repomix --style xml`。tiny repo 真实 smoke 中 repomix 有约 10-13 秒固定成本，但不是完整智能闭环的主要耗时。
- 早期慢因之一是 `codex exec` 继承 skill 项目根目录，导致子会话可见并读取当前 skill，形成递归式分析路径。当前已改为 `-C <analysis>`，并加 `--skip-git-repo-check`。
- 2026-07-07 的诊断 smoke 证明，错误的 cross-ref fallback 会把 `建议回退模块: 无` 的审稿误判成需要修复，导致 4 个 Codex 子会话、总耗时约 558.751 秒，并因 repair 子会话直接写 analysis 后由父进程再次追加，造成重复 `Agent Cross-ref 修复` 章节。
- 结构修复后，Codex 子会话使用 read-only 沙箱，prompt 明确禁止写文件；回退触发只以显式 `建议回退模块:` 决策行为准；单模块且 deterministic cross-ref PASS 时跳过独立审稿。
- 修复后的 tiny repo 真实 smoke：`agent_attempt_count: 1`，`modules-batch` 用时约 141.005 秒，repomix 用时约 10.579 秒，总耗时约 151.661 秒，acceptance 全 PASS。
- timeout 默认不是解决方案，当前 `agent_timeout_seconds` 默认 0，即 disabled；metadata 会记录 `timeout_seconds: null`，`PERFORMANCE_REPORT.md/json` 会记录阶段耗时、agent attempt 耗时、cwd、command_kind 和慢因排名。
- 测试/UAT 的 Codex 子代理**实际**参数（以 run-005 证据为准）：两个子会话（`modules-batch` 365.25s、`cross-ref-review` 35.17s）均使用 read-only 沙箱、未超时、`returncode 0`；`agent-runs/*/attempt-*/metadata.json` 记录 `model_reasoning_effort="low"`（外层会话用 gpt-5.5/xhigh）。`config-effective.json` 现含 `agent_model` / `agent_reasoning_effort` 字段（默认均为空字符串，由 codex 内置默认模型决定，与 [ADR-0019](decisions/0019-llm-judge-model-and-manifest-10k.md) 的空模型思路一致），可从配置侧判定生效参数。
- 结构性修复是减少子会话数量：模块深挖已从“每个模块一个 Codex 会话”改为 `agent-runs/modules-batch/` 一次批量深挖；cross-ref 审稿改用 `diagnostics/cross-ref-review-input.md` 压缩审稿包，避免 reviewer 自己遍历目录。
- cross-ref 审稿已移动到 coverage/repair 之后，避免在 `data/coverage.md` 生成前启动审稿 agent 造成无效读取和误报。

## 最小补齐顺序

如果继续补 full PLAN，不建议一次性补所有延后项。最小顺序如下：

1. **补 tree-sitter 多语言 benchmark**
   - 当前 grammar query 已有 fake CLI 单元测试。
   - 下一步用真实仓库记录 Python / JS/TS / Go/Rust 等语言的 parse/query 行为和性能。

2. **补 UAT 级真实冲突验证**
   - 当前 cross-ref 回退修复已有模拟测试。
   - 下一步在 `claude-video` 或专门 fixture 中构造/捕获真实审稿冲突，验证回退修复后的最终报告质量。

3. **补高成本 acceptance**
   - 当前已覆盖本地硬断言。
   - 下一步只在需要 full PLAN 合规时补 LLM-judge、Mermaid render、外链检查。

4. **补 run-005 的 `JUDGE.md` 人工 6 维度评分表**
   - run-001/002/003 均有 `JUDGE.md` 裁判节点；run-005 仅有确定性验收（`check.sh` + `acceptance-recheck-main.log`），缺人工 6/6 `5/5` 判定文件。
   - 补 `uat-evidence/run-005/JUDGE.md` 以与历史 UAT 对齐，正式闭环 6 维度评分。

## 5. run-005 UAT 证据更新（2026-07-07）

run-005 取代 run-003 成为最新 UAT 证据，关键事实如下：

- **目标**：`https://github.com/bradautomates/claude-video`（`/watch`，multi-agent-config 插件型仓库），完整智能闭环（`--agent-mode codex --mode all --no-question`）。
- **验收**：`acceptance/check.sh` 245/245 PASS（退出码 0）；裁判重跑 `acceptance-recheck-main.log` 245/245 PASS（退出码 0）。
- **流水线**：18 个阶段全部 PASS，主命令退出码 0。
- **Agent 子会话**：`modules-batch`（365.25s）+ `cross-ref-review`（35.17s），均 read-only、未超时、`returncode 0`；agent 工作量占 400.4s / 415.1s 总时（96.5%）。
- **覆盖率**：8 模块符号覆盖率全部 1.00（core≥0.80 / minor≥0.20）；engine 因本机无 `tree-sitter` CLI 自动回退 `regex-fallback`。
- **状态/SLA**：`STATE_REPORT` = `PASS_DETERMINISTIC_ACCEPTANCE`；`SLA_REPORT` = PASS（415.09s / 30min 预算内）。
- **受众报告差异度**：tech:business=0.79、tech:learning=0.86、business:learning=0.76（>0.18 阈值）。

**相对 run-003 的口径变化**：原文档将多个 P0 项标为“部分实现 / 仍需 `claude-video` UAT”；run-005 即该 UAT 且 245/245 PASS，故这些 P0 项已升级为“已实现并验证（run-005）”（见第 3 节对应行）。

**原 7 项缺口中 6 项已补齐、T07 外部调研为已知限制 stub（T01–T22）**：

- `ask_user()` 三运行时适配器（ADR-0003）→ 已实现（T03/T04，`ask_user_adapters.py`）；
- `config/repo-types.yaml` 切片模板外置 → 已实现（T01/T02，`RepoTypeLoader` 与原 `SLICES` 逐字节一致）；
- token 统计接入 SLA / PERFORMANCE / CONFIG_EFFECTIVE → 已实现（T05/T06，`<!-- TOKENS: in,out -->` + 500K 预算）；
- acceptance 扩展 LLM-judge / 真实 Mermaid 渲染 / 外链(http)检查 → 已实现（T09/T10/T11/T12，离线/缺失依赖降级为 SKIP/WARN）；
- 外部调研 `03-research.md` → 已知限制 stub（T07/T08）：`--research` 开关已接但 `write_research()` 硬编码 SKIP，不产出真实 5 章节，待补真实联网调研；
- tree-sitter 多语言 benchmark → 已实现（T14，`benchmark_treesitter.py` + `docs/benchmarks/tree-sitter-baseline.md`）；
- run-005 6 维度人工 `JUDGE.md` → 已补齐（T15，`uat-evidence/run-005/JUDGE.md` 六维 5/5）。

因此 **full PLAN 合规升级为 PASS（* T07 外部调研除外，为已知限制 stub）**；剩余非阻断项含运行期依赖（LLM-judge 需 `codex` CLI、Mermaid 渲染需 `mmdc`，离线或缺失时按 graceful degradation 降级）与 T07 stub，均不影响主流程与确定性验收（245 项）。

**需注意**：run-005 的 `JUDGE.md`（T15）为人工裁判评分表的**证据索引草稿**，按 Open Question Q8 待人工签字确认后正式闭环。

## 6. run-005 之后的增量实现（Round 6 / T05–T10，ADR-0016~0019）

run-005（2026-07-07）之后，skill 在 Round 6 又落地了 5 项 ADR（2026-07-08），全部已接受并实现。这些不在原始 PLAN / ADR-0001~0015 的合规口径内，但已实质性改变代码组织与运行行为，需同步记录以免文档与代码脱节。

| ADR | 主题 | 落地代码 | 影响 |
|---|---|---|---|
| [ADR-0016](decisions/0016-output-dir-restructure.md) | 输出目录重组 | `analyzer_*.py` 全部产物路径、`.stark-repo-analyzer/` 子目录、`render_report.py --output-dir` | 输出根从 `analysis/` 改为 `.stark-repo-analyzer/`，分 `data/ reports/ diagnostics/ logs/ acceptance/ agent-runs/`；去除数字前缀（`00-meta.txt`→`data/meta.txt`，`06-module-*.md`→`diagnostics/module-drafts/module-*.md`，`08-coverage.md`→`data/coverage.md` 等）；本文 §1/§3/§4 的路径已据此更新 |
| [ADR-0017](decisions/0017-preflight-agent-degrade.md) | 预检 + agent 模式自动降级 | `analyzer_preflight.preflight_check()`、`analyzer_common.degrade_agent_mode()` | `--agent-mode` 默认由 `deterministic` 改为 `codex`；启动前做 git/npx/target/codex/agent_command 5 项预检；codex 缺失时自动降级 `deterministic` 并写入 `config-effective.json.agent_mode_degraded=true` |
| [ADR-0018](decisions/0018-progress-reporter-run-log.md) | 进度输出与运行日志 | `analyzer_common.ProgressReporter` / `LogWriter` | 运行时以 `[N/M]` 打印阶段进度到 stderr；每次运行写 `logs/run-YYYYMMDD-HHMMSS.md`（阶段耗时表 + agent 调用表）；`timed_stage` 保留但不再被主流程使用 |
| [ADR-0019](decisions/0019-llm-judge-model-and-manifest-10k.md) | LLM-judge 模型默认置空 + 名片 10KB | `llm_judge.py`（`DEFAULT_MODEL=""`）、`analyzer_metadata.write_manifest_card()`（10KB） | `llm_judge.py` 不传 `--model` 时由 codex 决定模型；项目名片由 5KB 扩容至 10KB（README 摘要 1500→4000 字符，新增 Git / 规模 / 许可证 / 依赖 / 运行命令 / 顶层目录 8 区块）；验收脚本名片大小检查同步调整 |

**代码组织（T05）**：原 `scripts/repo_analyzer.py` 从约 2746 行单体拆分为 **195 行编排入口** + `analyzer_*.py` 系列模块（`analyzer_checkout` / `analyzer_config` / `analyzer_slicing` / `analyzer_metadata` / `analyzer_modules` / `analyzer_coverage` / `analyzer_crossref` / `analyzer_agent` / `analyzer_reports` / `analyzer_reporting` / `analyzer_acceptance` / `analyzer_preflight` / `analyzer_common`）+ `ask_user_adapters.py` / `repo_types_loader.py` / `token_reporter.py` / `benchmark_treesitter.py` / `render_report.py` / `llm_judge.py`。本文 §1/§3 的“证据”列已按新模块名标注。

**结论更新**：自 run-005 起，full PLAN 合规维持 PASS（* T07 外部调研仍为已知限制 stub）；Round 6 的五项增强均已实现，不改变合规判定，仅强化可维护性、可观测性与默认体验。

## 维护规则

- 修改 `scripts/repo_analyzer.py` 的可观察行为后，同步更新本文件的覆盖状态。
- 如果某个延后项被明确放弃，必须新建 ADR 或更新对应 ADR，再移动到“已废弃 / 已改写”。
- UAT 通过只能证明当前测试场景可用，不能自动视为 full PLAN 合规。
- 最新 UAT 证据为 `uat-evidence/run-005`；本文结论与第 3 节状态已随 run-005 一并更新（详见第 5 节）。
