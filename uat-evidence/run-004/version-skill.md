---
name: stark-repo-analyzer
version: 0.1.0
description: 仓库分析底料流程：当用户要分析、审计、理解一个 git/GitHub 仓库，生成架构报告，梳理模块/依赖/入口，或让 agent 基于仓库做判断时使用；先生成可复查 analysis，再做必要判断。
---

# Stark Repo Analyzer

底料先行：确定性扫描用脚本做，agent 只读底料、补判断。

## 用户最短用法

普通用户不需要写 UAT 级长 prompt。只要能识别目标仓库，就按默认模式执行；用户明确要求“完整智能闭环 / 深度智能分析 / subagent 深挖 / 独立审稿”时，启用 agent 模式。

可接受的短请求示例：

- `$stark-repo-analyzer https://github.com/bradautomates/claude-video`
- `$stark-repo-analyzer 分析这个仓库`
- `$stark-repo-analyzer 帮我看一下 ../some-repo`
- `$stark-repo-analyzer 分析 https://github.com/org/repo 输出到 ./repo-analysis`

默认行为：

- 用户只给 URL 或路径时，把它当作 `TARGET`。
- 用户没有指定输出目录时，使用当前工作目录下的 `analysis`。
- 用户没有指定报告模式时，生成总览 + `tech-lead`、`business`、`learning` 三份受众报告。
- 默认命令先生成可复查底料；完整智能闭环命令会额外运行 Codex agent 做模块深挖、独立 cross-ref 审稿和 coverage 失败修复。
- 用户没有提出具体问题时，最终回复只给概览、验收状态、关键报告路径和可继续追问的方向。

## Steps

### 1. 接收任务并定界

- 从用户请求中提取目标仓库，记为 `TARGET`。`TARGET` 可以是本地 git 仓库路径、`https://...` git URL 或 `git@...` URL。
- 从用户请求中提取输出目录，记为 `OUTPUT`。用户未指定时使用当前工作目录下的 `analysis`。
- 将 `<skill-dir>` 设为本 `SKILL.md` 所在目录；不要假设当前 shell 就在 skill 目录。
- 判断用户是否只要技术报告。默认生成 `tech-lead`、`business`、`learning` 三份报告；用户明确只要技术报告时才用单报告模式。

Completion criterion: `TARGET`、`OUTPUT`、`<skill-dir>`、报告模式都已明确。

### 2. 启动扫描

- 对默认底料模式，运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --mode all --no-question
```

- 对完整智能闭环模式，运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --mode all --no-question --agent-mode codex
```

- 对单技术报告模式，运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --no-question
```

- 可选配置：脚本会读取 `~/.config/repo-analyzer/defaults.yaml`，支持 `extends:` 继承；CI 可用 `REPO_ANALYZER_MODE`、`REPO_ANALYZER_SLA_BUDGET_MINUTES`、`REPO_ANALYZER_TARGET_COVERAGE_CORE`、`REPO_ANALYZER_TARGET_COVERAGE_MINOR`、`REPO_ANALYZER_COVERAGE_ENGINE`、`REPO_ANALYZER_AGENT_MODE` 覆盖；需要复用上次偏好时加 `--use-last-pref`，需要保存本次偏好时加 `--save-pref`。
- 让脚本完成所有确定性动作：必要时浅克隆远程仓库、清空并重建 `OUTPUT`、枚举非二进制源码文件、识别仓库类型、用 repomix 生成切片、生成模块候选、生成受众报告、生成验收脚本和索引。
- 完整智能闭环模式下，脚本还会写入 `OUTPUT/agent-runs/`，保存批量模块深挖 agent、必要的 coverage 修复 agent 和独立审稿 agent 的 prompt、stdout、stderr、attempt metadata 和 result；Codex 子会话使用 read-only 沙箱，只返回 Markdown，由主脚本统一写入生成产物。
- 不手工替代脚本的扫描结果；脚本失败时不要继续编造报告。

Completion criterion: 命令退出码为 0，且 stdout 显示 `分析完成: <output>`。

### 3. 确认核心产物存在

- 检查 `OUTPUT/README.md`，确认它列出了本次分析的仓库名、repo type、报告模式和报告文件。
- 检查 `OUTPUT/00-meta.txt`，确认 git 元数据、文件数量和语言统计已生成。
- 检查 `OUTPUT/02a-repo-type.yaml`，确认 repo type 和切片维度已生成。
- 检查 `OUTPUT/02a-manifest-card.md`，确认 5KB 项目名片已生成。
- 检查 `OUTPUT/slices/`，确认至少有文档/代码/依赖/历史热点等与 repo type 匹配的切片。
- 检查 `OUTPUT/05-module-ids.yaml` 和 `OUTPUT/drafts/`，确认模块候选和模块草稿已生成。
- 检查 `OUTPUT/drafts/07-cross-ref-checks.md`，确认模块引用校验已生成。
- 检查 `OUTPUT/08-coverage.md`、`OUTPUT/expected-symbols.json`、`OUTPUT/coverage-symbols.json` 和 `OUTPUT/STATE_REPORT.md`，确认覆盖率门控和状态报告已生成。
- 检查 `OUTPUT/SLA_REPORT.md`、`OUTPUT/PERFORMANCE_REPORT.md`、`OUTPUT/CONFIG_EFFECTIVE.json` 和 `OUTPUT/AGENT_SUMMARY.json`，确认本次 SLA、慢因诊断、生效配置和 agent 模式已记录。
- 如果启用了完整智能闭环，检查 `OUTPUT/agent-runs/` 和 `OUTPUT/drafts/07-cross-ref-agent-review.md`。单模块且 deterministic cross-ref 已 PASS 时，Codex cross-ref reviewer 会写入 `SKIPPED_SINGLE_MODULE`，避免无价值的独立审稿子会话。
- 检查 `OUTPUT/ANALYSIS_REPORT.md`；默认模式还要检查 `ANALYSIS_REPORT.tech-lead.md`、`ANALYSIS_REPORT.business.md`、`ANALYSIS_REPORT.learning.md`。
- 检查 `OUTPUT/acceptance/check.sh` 存在且可执行。

Completion criterion: 以上核心产物全部存在；缺失时停止并列出缺失路径。

### 4. 运行验收脚本

```bash
"$OUTPUT/acceptance/check.sh"
```

- 如果验收通过，记录通过状态。
- 如果验收失败，读取失败检查名和输出文本，不修改生成产物来掩盖失败。
- 如果验收失败，停止后续分析，只报告失败项、已确认事实和可重跑命令。

Completion criterion: 验收状态已知；失败时已保存失败检查名。

### 5. 读取索引和项目名片

- 先读 `OUTPUT/README.md`，确认本次产物入口和报告文件。
- 再读 `OUTPUT/02a-manifest-card.md`，获得项目名、仓库来源、语言构成、README 摘要、命令提示和目录概览。
- 再读 `OUTPUT/02a-repo-type.yaml`，确认本次仓库类型；后续只读与该类型相关的切片。
- 需要判断底料可靠性时，读 `OUTPUT/08-coverage.md` 和 `OUTPUT/STATE_REPORT.md`。

Completion criterion: 已掌握仓库类型、入口报告、主要语言/框架、底料完整性。

### 6. 按用户问题读取最小切片

- 用户要总体架构：读 `ANALYSIS_REPORT.md`、`05-module-ids.yaml`、`drafts/`、`slices/02-backend.xml`、`slices/09-dependencies.xml`、`slices/12-history-hotspot.txt`。
- 用户要技术负责人视角：读 `ANALYSIS_REPORT.tech-lead.md`、`05-module-ids.yaml`、`drafts/`、`slices/02-backend.xml`、`slices/09-dependencies.xml`。
- 用户要业务视角：读 `ANALYSIS_REPORT.business.md`、`02a-manifest-card.md`、`slices/04-docs.xml`。
- 用户要学习路径：读 `ANALYSIS_REPORT.learning.md`、`slices/04-docs.xml`、`drafts/`。
- 用户要接口/API/MCP 工具：读 `slices/02-backend.xml`、`slices/09-dependencies.xml`，再在报告中核对工具名或入口函数。
- 用户要风险或深挖点：读 `08-coverage.md`、`STATE_REPORT.md`、`slices/12-history-hotspot.txt` 和相关模块草稿。
- 用户要核对可信度或为什么慢：读 `drafts/07-cross-ref-checks.md`、`drafts/07-cross-ref-agent-review.md`、`coverage-symbols.json`、`AGENT_SUMMARY.json`、`SLA_REPORT.md`、`PERFORMANCE_REPORT.md` 和 `acceptance/check.sh` 输出。
- 用户问题不明确：只读 `README.md`、`02a-manifest-card.md`、`ANALYSIS_REPORT.md`，先给概览并说明可继续深挖的方向。

Completion criterion: 每个实质判断都能追到已读取的底料文件；追不到的内容明确标为 agent 判断。

### 7. 组织最终回复

- 开头写明 `OUTPUT` 路径和验收状态。
- 简述仓库类型、主入口、核心模块、依赖/外部接口。
- 按用户问题给结论；需要时列风险、缺口和下一步深挖点。
- 引用关键底料文件名，让用户能复查来源。
- 如果脚本或验收失败，只输出已确认事实、失败检查名和下一步修复建议。

Completion criterion: 最终回复没有脱离底料的事实断言；用户能从回复追到产物文件。

## Reference

主要产物：

- `00-meta.txt`：git 与文件元数据。
- `02a-repo-type.yaml`：仓库类型与动态切片清单。
- `02a-manifest-card.md`：5KB 项目名片。
- `slices/`：按类型生成的 XML/TXT 切片。
- `05-module-ids.yaml`：模块候选清单。
- `drafts/06-module-*.md`：模块深度分析底稿；agent 模式下包含 `Agent 深度分析` 和可能的 `Agent 覆盖率修复`。
- `drafts/07-cross-ref-checks.md`：模块引用与重复章节校验。
- `drafts/07-cross-ref-review-input.md` / `drafts/07-cross-ref-agent-review.md` / `agent-runs/modules-batch/` / `agent-runs/repair-*/` / `agent-runs/cross-ref-repair-*/` / `agent-runs/cross-ref-review-final/` / `AGENT_SUMMARY.json`：完整智能闭环的批量模块深挖、压缩审稿包、coverage 修复、cross-ref 修复、独立复审、prompt/result 证据和 agent 状态。
- `08-coverage.md` / `expected-symbols.json` / `coverage-symbols.json`：符号覆盖率门控。
- `SLA_REPORT.md` / `PERFORMANCE_REPORT.md` / `PERFORMANCE_REPORT.json` / `CONFIG_EFFECTIVE.json`：SLA、阶段耗时、agent attempt 耗时、慢因诊断与生效配置记录。默认不启用 agent timeout；慢时先看性能报告定位根因。
- `REPORT_DATA.json` / `ANALYSIS_REPORT*.md`：模板渲染数据与受众报告；可用 `scripts/render_report.py --template all --data <OUTPUT>` 单独重渲染。
- `README.md`：索引页。
- `acceptance/check.sh`：本地硬断言入口。

边界：

- 不读取或写入 `graphify-out/`。
- 不把确定性扫描交给 LLM 猜。
- 不安装额外依赖。
- 不手改生成产物来“修验收”；验收失败时停止并报告失败项。
- Coverage gate 默认 `auto`：本机有 `tree-sitter` CLI 时优先用 grammar query 抽取关键符号，并记录串行 parse、query 与大文件跳过统计；query 不可用或无结果时退回确定性正则符号提取，不把可选依赖变成硬失败。
- 用户明确要求完整智能闭环时，不要只跑默认 deterministic 模式；使用 `--agent-mode codex`。
- 完整智能闭环变慢时，不要先加短 timeout。先读 `PERFORMANCE_REPORT.md` 的阶段耗时和 agent attempt 排名；若慢点集中在 `codex exec` 子会话，优先减少子会话数量或合并 prompt，而不是把限时当成根因修复。
