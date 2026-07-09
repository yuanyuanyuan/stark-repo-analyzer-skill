---
name: stark-repo-analyzer
version: 0.2.0
description: 仓库分析底料流程：当用户要分析/审计/理解 git/GitHub 仓库、生成架构报告、梳理模块/依赖/入口，或要求 agent 基于仓库做判断时使用；先跑确定性 analysis，再基于底料判断。
---

# Stark Repo Analyzer

底料先行：确定性扫描用脚本做，agent 只读底料、补判断。

## 用户最短用法

普通用户不需要写 UAT 级长 prompt。只要能识别目标仓库，就按默认模式执行；用户明确要求"完整智能闭环 / 深度智能分析 / subagent 深挖 / 独立审稿"时，启用 agent 模式。

可接受的短请求示例：

- `$stark-repo-analyzer https://github.com/bradautomates/claude-video`
- `$stark-repo-analyzer 分析这个仓库`
- `$stark-repo-analyzer 帮我看一下 ../some-repo`
- `$stark-repo-analyzer 分析 https://github.com/org/repo 输出到 ./repo-analysis`

默认行为：

- 用户只给 URL 或路径时，把它当作 `TARGET`。
- 用户没有指定输出目录时，使用当前工作目录下的 `.stark-repo-analyzer`。
- 用户没有指定报告模式时，生成总览 + `tech-lead`、`business`、`learning` 三份受众报告。
- **`--agent-mode` 默认为 `codex`**（T09）：codex 可用时自动运行完整智能闭环；不可用时自动降级到 `deterministic`，并在 `config-effective.json` 中记录 `agent_mode_degraded: true`。
- 运行时预检（T09）在分析开始前检查 `git`、`npx`、`target`、`codex`/`agent_command` 5 项，打印到 stderr。
- 进度输出（T10）以 `[N/M]` 格式打印到 stderr，运行日志写入 `logs/run-YYYYMMDD-HHMMSS.md`。
- 用户没有提出具体问题时，最终回复只给概览、验收状态、关键报告路径和可继续追问的方向。

## Steps

### 1. 接收任务并定界

- 从用户请求中提取目标仓库，记为 `TARGET`。`TARGET` 可以是本地 git 仓库路径、`https://...` git URL 或 `git@...` URL。
- 从用户请求中提取输出目录，记为 `OUTPUT`。用户未指定时使用当前工作目录下的 `.stark-repo-analyzer`。
- 将 `<skill-dir>` 设为本 `SKILL.md` 所在目录；不要假设当前 shell 就在 skill 目录。
- 判断用户是否只要技术报告。默认生成 `tech-lead`、`business`、`learning` 三份报告；用户明确只要技术报告时才用单报告模式。
- 判断运行分支，记为 `RUN_MODE`：
  - `default`：用户未明确指定 agent 深挖或纯确定性时使用。
  - `agent`：用户明确要求"完整智能闭环 / 深度智能分析 / subagent 深挖 / 独立审稿"时使用。
  - `deterministic`：用户明确要求不运行 agent、离线确定性扫描或只要脚本产物时使用。

Completion criterion: `TARGET`、`OUTPUT`、`<skill-dir>`、报告模式、`RUN_MODE` 都已明确，且能唯一对应 Step 2 的一条命令。

### 2. 启动扫描

- 对默认模式（codex 可用时自动运行完整智能闭环），运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --mode all --no-question
```

- 对完整智能闭环模式（显式指定），运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --mode all --no-question --agent-mode codex
```

- 对纯确定性模式（不运行 agent），运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --mode all --no-question --agent-mode deterministic
```

- 对单技术报告模式，运行：

```bash
python3 "<skill-dir>/scripts/repo_analyzer.py" "$TARGET" --output "$OUTPUT" --no-question
```

- 可选配置：脚本会读取 `~/.config/repo-analyzer/defaults.yaml`，支持 `extends:` 继承；CI 可用 `REPO_ANALYZER_MODE`、`REPO_ANALYZER_SLA_BUDGET_MINUTES`、`REPO_ANALYZER_TARGET_COVERAGE_CORE`、`REPO_ANALYZER_TARGET_COVERAGE_MINOR`、`REPO_ANALYZER_COVERAGE_ENGINE`、`REPO_ANALYZER_AGENT_MODE` 覆盖；需要复用上次偏好时加 `--use-last-pref`，需要保存本次偏好时加 `--save-pref`。
- **运行时自适应（T03）**：在 `claude-code` / `codex` / `cursor` 三种运行时下，脚本通过 `REPO_ANALYZER_RUNTIME` 环境变量或进程特征（`CLAUDECODE` / `CODEX` / `CURSOR`）自动识别运行时并向用户提问；交互不可用、超时或未知运行时自动降级到 `defaults.yaml`。`cursor` 运行时采用"写 `questions.json` + 等待 `--resume`"流程，可由 `REPO_ANALYZER_ANSWERS_FILE` 指向的答案 JSON 回填。
- **运行时预检（T09）**：脚本启动时先执行 5 项预检（git/npx/target/codex/agent_command），结果打印到 stderr。codex 不可用时自动降级 `agent_mode: codex → deterministic`，在 `config-effective.json` 中记录 `agent_mode_degraded: true`。
- **进度输出（T10）**：运行时以 `[N/M] stage_name` 格式向 stderr 打印进度，agent 调用结果也实时输出。运行日志写入 `OUTPUT/logs/run-YYYYMMDD-HHMMSS.md`。
- **外部调研（T07）**：默认关闭；显式加 `--research` 才运行外部调研阶段并写入 `OUTPUT/data/research.md`、在报告中插入 `{{ research_section }}`。离线（`--offline`）或当前环境无联网源时自动 SKIP，不抛异常、不污染主流程。
- **切片维度外置（T02）**：仓库类型与各切片维度已外置到 `config/repo-types.yaml`，由 `RepoTypeLoader` 在运行时加载；新增/调整切片只需改 YAML，无需改代码。`repo-types.yaml` 的 `version` 与 `SKILL.md` 的 `version` 绑定，不一致会直接报错。
- 让脚本完成所有确定性动作：必要时浅克隆远程仓库、清空并重建 `OUTPUT`、枚举非二进制源码文件、识别仓库类型、用 repomix 生成切片、生成模块候选、生成受众报告、生成验收脚本和索引。
- 完整智能闭环模式下，脚本还会写入 `OUTPUT/agent-runs/`，保存批量模块深挖 agent、必要的 coverage 修复 agent 和独立审稿 agent 的 prompt、stdout、stderr、attempt metadata 和 result；Codex 子会话使用 read-only 沙箱，只返回 Markdown，由主脚本统一写入生成产物。
- 不手工替代脚本的扫描结果；脚本失败时不要继续编造报告。

Completion criterion: 已按 `RUN_MODE` 只运行一条命令；命令退出码为 0，stdout 显示 `分析完成: <output>`，且 `<output>` 与 `OUTPUT` 指向同一目录。

### 3. 确认核心产物存在

- 检查 `OUTPUT/reports/README.md`，确认它列出了本次分析的仓库名、repo type、报告模式和报告文件。
- 检查 `OUTPUT/data/meta.txt`，确认 git 元数据、文件数量和语言统计已生成。
- 检查 `OUTPUT/data/repo-type.yaml`，确认 repo type 和切片维度已生成。
- 检查 `OUTPUT/data/manifest-card.md`，确认 10KB 项目名片已生成。
- 检查 `OUTPUT/diagnostics/slices/`，确认至少有文档/代码/依赖/历史热点等与 repo type 匹配的切片。
- 检查 `OUTPUT/data/module-ids.yaml` 和 `OUTPUT/diagnostics/module-drafts/`，确认模块候选和模块草稿已生成。
- 检查 `OUTPUT/diagnostics/cross-ref-checks.md`，确认模块引用校验已生成。
- 检查 `OUTPUT/data/coverage.md`、`OUTPUT/data/expected-symbols.json`、`OUTPUT/data/coverage-symbols.json` 和 `OUTPUT/reports/STATE_REPORT.md`，确认覆盖率门控和状态报告已生成。
- 检查 `OUTPUT/reports/SLA_REPORT.md`、`OUTPUT/reports/PERFORMANCE_REPORT.md`、`OUTPUT/data/config-effective.json` 和 `OUTPUT/data/agent-summary.json`，确认本次 SLA、慢因诊断、生效配置和 agent 模式已记录。
- 如果启用了完整智能闭环，检查 `OUTPUT/agent-runs/` 和 `OUTPUT/diagnostics/cross-ref-agent-review.md`。单模块且 deterministic cross-ref 已 PASS 时，Codex cross-ref reviewer 会写入 `SKIPPED_SINGLE_MODULE`，避免无价值的独立审稿子会话。
- 检查 `OUTPUT/reports/ANALYSIS_REPORT.md`；默认模式还要检查 `OUTPUT/reports/ANALYSIS_REPORT.tech-lead.md`、`OUTPUT/reports/ANALYSIS_REPORT.business.md`、`OUTPUT/reports/ANALYSIS_REPORT.learning.md`。
- 检查 `OUTPUT/acceptance/check.sh` 存在且可执行。

Completion criterion: 以上核心产物全部存在；缺失时停止并列出缺失路径。

### 4. 运行验收脚本

```bash
"$OUTPUT/acceptance/check.sh"
```

- 脚本先做本地硬断言（245+ 项），再依次调用 3 个扩展验收执行器并汇总：
  - `acceptance/04-link.sh`：外链可达性与 GitHub commit 引用校验；离线时整体 SKIP。
  - `acceptance/05-mermaid-judge.sh`：用 mermaid-cli 渲染全景图；缺失/失败时 WARN（非 `--strict`），`--strict` 时 FAIL。
  - `acceptance/llm-judge.sh` → `scripts/llm_judge.py`：用 `codex exec`（默认不指定 `--model`，由 codex 决定）对报告做内容准确度 / 受众匹配度 / 受众区分度评分，阈值 `accuracy>=7`、`jaccard>=0.30`；`codex` 未安装或调用失败非 `--strict` 时 SKIP。
- 最后打印一行汇总：`TOTAL:N PASS:P FAIL:F WARN:W SKIP:S`。`FAIL>0` 时退出码为 1。
- 严格模式：传入 `--strict` 让 mermaid / LLM-judge 的不达标项升级为 FAIL（默认 WARN/SKIP 不致命）。

```bash
"$OUTPUT/acceptance/check.sh" --strict
```

- 如果验收通过，记录 `TOTAL:` 汇总行和通过状态。
- 如果验收失败，读取失败检查名、输出文本和 `TOTAL:` 汇总行，不修改生成产物来掩盖失败。
- 如果验收失败，停止后续分析，只报告失败项、已确认事实和可重跑命令。

Completion criterion: 验收状态已知；通过时已记录 `TOTAL:` 汇总行；失败时已保存失败检查名、失败输出与 `TOTAL:` 汇总行。

### 5. 读取索引和项目名片

- 先读 `OUTPUT/reports/README.md`，确认本次产物入口和报告文件。
- 再读 `OUTPUT/data/manifest-card.md`，获得项目名、仓库来源、语言构成、Git 信息、代码规模、许可证、依赖摘要、运行命令、README 摘要和目录概览。
- 再读 `OUTPUT/data/repo-type.yaml`，确认本次仓库类型；后续只读与该类型相关的切片。
- 需要判断底料可靠性时，读 `OUTPUT/data/coverage.md` 和 `OUTPUT/reports/STATE_REPORT.md`。

Completion criterion: 已掌握仓库类型、入口报告、主要语言/框架、底料完整性。

### 6. 按用户问题读取最小切片

- 用户要总体架构：读 `reports/ANALYSIS_REPORT.md`、`data/module-ids.yaml`、`diagnostics/module-drafts/`、`diagnostics/slices/02-backend.xml`、`diagnostics/slices/09-dependencies.xml`、`diagnostics/slices/history-hotspot.txt`。
- 用户要技术负责人视角：读 `reports/ANALYSIS_REPORT.tech-lead.md`、`data/module-ids.yaml`、`diagnostics/module-drafts/`、`diagnostics/slices/02-backend.xml`、`diagnostics/slices/09-dependencies.xml`。
- 用户要业务视角：读 `reports/ANALYSIS_REPORT.business.md`、`data/manifest-card.md`、`diagnostics/slices/04-docs.xml`。
- 用户要学习路径：读 `reports/ANALYSIS_REPORT.learning.md`、`diagnostics/slices/04-docs.xml`、`diagnostics/module-drafts/`。
- 用户要接口/API/MCP 工具：读 `diagnostics/slices/02-backend.xml`、`diagnostics/slices/09-dependencies.xml`、`data/mcp-tools.json`，再在报告中核对工具名或入口函数。
- 用户要风险或深挖点：读 `data/coverage.md`、`reports/STATE_REPORT.md`、`diagnostics/slices/history-hotspot.txt` 和相关模块草稿。
- 用户要核对可信度或为什么慢：读 `diagnostics/cross-ref-checks.md`、`diagnostics/cross-ref-agent-review.md`、`data/coverage-symbols.json`、`data/agent-summary.json`、`reports/SLA_REPORT.md`、`reports/PERFORMANCE_REPORT.md` 和 `acceptance/check.sh` 输出。
- 用户问题不明确：只读 `reports/README.md`、`data/manifest-card.md`、`reports/ANALYSIS_REPORT.md`，先给概览并说明可继续深挖的方向。

Completion criterion: 每个实质判断都能追到已读取的底料文件；追不到的内容明确标为 agent 判断。

### 7. 组织最终回复

- 开头写明 `OUTPUT` 路径和验收状态。
- 简述仓库类型、主入口、核心模块、依赖/外部接口。
- 按用户问题给结论；需要时列风险、缺口和下一步深挖点。
- 引用关键底料文件名，让用户能复查来源。
- 如果脚本或验收失败，只输出已确认事实、失败检查名和下一步修复建议。

Completion criterion: 最终回复没有脱离底料的事实断言；用户能从回复追到产物文件。

## Reference

### 输出目录结构（T08）

```
OUTPUT/
├── data/              # 结构化数据（JSON/YAML/TXT）
├── reports/           # 人读 Markdown 报告
├── diagnostics/       # 诊断中间产物（切片/草稿/cross-ref）
├── logs/              # 运行日志（T10）
├── acceptance/        # 验收脚本
└── agent-runs/        # agent 调用证据
```

主要产物：

- `data/meta.txt`：git 与文件元数据。
- `data/repo-type.yaml`：仓库类型与动态切片清单。
- `data/manifest-card.md`：10KB 项目名片（T07），含 Git 信息、代码规模、许可证、依赖摘要、运行命令、README 前 4000 字符。
- `diagnostics/slices/`：按类型生成的 XML/TXT 切片。
- `data/module-ids.yaml`：模块候选清单。
- `diagnostics/module-drafts/module-*.md`：模块深度分析底稿；agent 模式下包含 `Agent 深度分析` 和可能的 `Agent 覆盖率修复`。
- `diagnostics/cross-ref-checks.md`：模块引用与重复章节校验。
- `diagnostics/cross-ref-review-input.md` / `diagnostics/cross-ref-agent-review.md` / `agent-runs/modules-batch/` / `agent-runs/repair-*/` / `agent-runs/cross-ref-repair-*/` / `agent-runs/cross-ref-review-final/` / `data/agent-summary.json`：完整智能闭环的批量模块深挖、压缩审稿包、coverage 修复、cross-ref 修复、独立复审、prompt/result 证据和 agent 状态。
- `data/coverage.md` / `data/expected-symbols.json` / `data/coverage-symbols.json`：符号覆盖率门控。
- `reports/STATE_REPORT.md`：状态报告（PASS/FAIL + 失败模块明细）。
- `reports/SLA_REPORT.md`：SLA 报告（通过/失败 + 耗时 + agent 参数）。
- `reports/PERFORMANCE_REPORT.md` / `data/performance-report.json`：性能诊断报告。**PERFORMANCE_REPORT 是事后诊断工具，不是实时监控**——判断 SLA 通过/失败读 `SLA_REPORT.md`，判断产物完整性和覆盖率读 `STATE_REPORT.md`，定位慢因读 `PERFORMANCE_REPORT.md`。报告内含定位说明和"如何阅读本报告"指引。
- `data/config-effective.json`：生效配置记录，含 `agent_mode` 和 `agent_mode_degraded`（T09）。
- Codex 子代理默认使用 `--model 5.4` 与 `model_reasoning_effort="medium"`；如果要复现实验，应在 `data/config-effective.json`、`reports/SLA_REPORT.md`、`reports/PERFORMANCE_REPORT.md` 和 `agent-runs/*/attempt-*/metadata.json` 中核对生效参数。
- `data/report-data.json` / `reports/ANALYSIS_REPORT*.md`：模板渲染数据与受众报告；可用 `scripts/render_report.py --template all --data <OUTPUT>/data --output-dir <OUTPUT>/reports` 单独重渲染。
- `reports/README.md`：索引页。
- `acceptance/check.sh`：本地硬断言入口，并串联 `04-link.sh` / `05-mermaid-judge.sh` / `llm-judge.sh` 三个扩展执行器，输出 `TOTAL:` 汇总行。
- `logs/run-YYYYMMDD-HHMMSS.md`：运行日志（T10），含阶段耗时表、agent 调用表和汇总信息。
- `config/repo-types.yaml`：仓库类型与切片维度配置（T02），由 `RepoTypeLoader` 加载，`version` 绑定 `SKILL.md` 版本。
- `config/defaults.example.yaml`：交互问题默认值示例（T04），首次运行自动复制到 `~/.config/repo-analyzer/defaults.yaml`。
- **Token 用量（T05/T06）**：agent 在返回文本中以 `<!-- TOKENS: in,out -->` 声明用量，脚本解析后写入 `agent-runs/*/attempt-*/metadata.json`，并汇总到 `reports/SLA_REPORT.md`、`reports/PERFORMANCE_REPORT.md`、`data/performance-report.json` 与 `data/config-effective.json`（预算 500K，命令模式 `mode=0`，按绿/黄/红三档评估）。

边界：

- 不读取或写入 `graphify-out/`。
- 不把确定性扫描交给 LLM 猜。
- 不安装额外依赖。
- 不手改生成产物来"修验收"；验收失败时停止并报告失败项。
- Coverage gate 默认 `auto`：本机有 `tree-sitter` CLI 时优先用 grammar query 抽取关键符号，并记录串行 parse、query 与大文件跳过统计；query 不可用或无结果时退回确定性正则符号提取，不把可选依赖变成硬失败。
- `--agent-mode` 默认为 `codex`（T09）；codex 不可用时自动降级到 `deterministic`，用户无需手动指定 `--agent-mode deterministic`。
- 完整智能闭环变慢时，不要先加短 timeout。先读 `reports/PERFORMANCE_REPORT.md` 的阶段耗时和 agent attempt 排名；若慢点集中在 `codex exec` 子会话，优先减少子会话数量或合并 prompt，而不是把限时当成根因修复。
