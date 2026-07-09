# 增量 PRD：stark-repo-analyzer 未实现功能补齐

> 文档定位：本 PRD 是 **增量 spec**，只做规划、不写实现代码。
> 基线输入：`references/PLAN_COMPLIANCE.md`（full PLAN 合规 = PASS，* T07 外部调研除外）、各 ADR、`scripts/` 现状、`SKILL.md`、UAT 证据。
> 当前交付状态（来自 PLAN_COMPLIANCE §结论 / §6）：`v1 可用性: PASS` / `完整智能闭环 UAT (run-005): PASS` / `full PLAN 合规: PASS（* T07 外部调研为已知限制 stub）`。

---

## 1. 产品目标

原 PRD 目标为把 `full PLAN 合规` 从 **PARTIAL** 推进到规划层面的**完整**。经代码核对（见 §2 / §4），原 7 项增量能力中 **6 项已实现并验证**，**仅第 4 项（外部调研 `data/research.md`）仍为已知限制 stub**（开关已接、`write_research()` 恒写 SKIP，不产出真实 5 章节）。

因此本 PRD 的目标已切换为：

1. **记录已落地能力**：把原 7 项的真实实现状态固化，避免文档与代码脱节。
2. **收敛唯一剩余缺口**：外部调研（T07）从“stub”到“真实联网调研”仍是规划层面 OPEN 项（需网络 + WebSearch/codex 能力）。
3. **补记 Round 6 后续增强**：ADR-0016~0019（T05–T10）在原 7 项之外交付了 5 项已落地的代码组织/可观测性增强，需纳入基线以免遗漏。

边界约定：
- **只补 PLAN 承诺、不引入已废弃能力**。依据 PLAN_COMPLIANCE.md §2，以下明确不做：阶段一 `repomix --compress` 宏观建模、4+1 overview subagent、`--max-context`/`--max-history` 开关、固定 12 维切片（已被 ADR-0002 动态切片取代）、与 `graphify-out/` 共享索引（ADR-0013 禁止）。
- **不做过度设计**：每项以 ADR 既定决策为上限，不扩展新能力面。
- 原 7 项完成后，`PLAN_COMPLIANCE.md` 的「延后实现」表应相应更新（已在 PLAN_COMPLIANCE §6 体现），结论标记维持 PASS（* T07 除外）。

---

## 2. 增量范围说明（现状核对）

本 skill 已通过完整智能闭环 UAT（run-005，245/245），是**对现有可用 skill 的增强**。下表逐项核对原 7 项与代码实际行为的关系。

| # | 功能 | 与现有代码的关系（现状核对） |
|---|---|---|
| 1 | `ask_user()` 三运行时适配器 | **已实现**：`scripts/ask_user_adapters.py` 提供 `AskUserAPI` 抽象 + `ClaudeCodeAskAdapter` / `CodexAskAdapter` / `CursorAskAdapter` 三适配器 + 降级链到 `defaults.yaml`；`detect_runtime()` 经 `CLAUDECODE`/`CODEX`/`CURSOR` 或 `REPO_ANALYZER_RUNTIME` 识别；`tests/test_ask_user_adapters.py` 覆盖默认/单选/多选/超时/skip 五分支。 |
| 2 | `config/repo-types.yaml` 外置切片模板 | **已实现**：`scripts/repo_types_loader.py` 的 `RepoTypeLoader` 加载 `config/repo-types.yaml`，与历史内嵌 `SLICES` 逐字节一致；`version` 字段与 `SKILL.md` 版本绑定，不一致直接报错；`tests/test_repo_types_loader.py`。 |
| 3 | token 统计接入 SLA / PERFORMANCE 报告 | **已实现**：`scripts/token_reporter.py` 的 `TokenCollector` 解析 agent 返回 `<!-- TOKENS: in,out -->`，汇总进 `data/config-effective.json`（`tokens_in/out/total`、`token_budget=500K`、`token_status` 绿/黄/红）、`reports/SLA_REPORT.md`、`reports/PERFORMANCE_REPORT.md`/`data/performance-report.json`；命令模式 token 为 0；`tests/test_token_reporter.py`、`tests/test_agent_token_integration.py`。 |
| 4 | 外部调研 `data/research.md` | **仍为已知限制 stub**：`--research` 开关已接（默认 OFF），但 `analyzer_metadata.write_research()` 在离线或本环境未配置联网源时恒写 `status: SKIP`，**不产出**真实 5 章节；报告 `{{ research_section }}` 已接入但恒为空；`tests/test_research_stage.py` 仅验证 OFF→无文件/SKIP 路径。真实联网调研待补（需网络 + WebSearch/codex 能力）。 |
| 5 | acceptance 高成本项 | **已实现**：`acceptance/04-link.sh`（外链可达性 + GitHub commit 引用）、`acceptance/05-mermaid-judge.sh`（mermaid-cli 渲染全景图）、`llm-judge.sh`→`scripts/llm_judge.py`（codex exec 评分）均落地并由 `acceptance/check.sh` 串联；离线/依赖缺失时 SKIP/WARN，不致命；`tests/test_acceptance_executors.py`。 |
| 6 | tree-sitter 多语言 benchmark | **已实现（本地基线）**：`scripts/benchmark_treesitter.py` 可串行扫描并记录 parse/query 统计；`docs/benchmarks/tree-sitter-baseline.md` 已落本地测量占位。在线参考仓库（pydantic/kubernetes/turborepo）真实数据待联网补。 |
| 7 | run-005 `JUDGE.md` 六维评分表 | **已实现**：`uat-evidence/run-005/JUDGE.md` 含 6 维评分表（用户使用友好度/使用简易度/结果契合度/结果完整性/执行稳定程度/证据完整性与可复查性），每维 5/5，引用 run-005 的 prompt/会话日志/退出码/产物/重跑日志作为证据；按 PLAN_COMPLIANCE §5 备注，其为证据索引草稿，待人工签字正式闭环。 |

> 结论：原 7 项中 6 项已落地，仅 #4 为 stub。 Round 6（ADR-0016~0019）另行交付 5 项增强（见 §4 末「后续已实现增强」）。

---

## 3. 用户故事

按原 7 项能力聚类为 5 类，分别从 **skill 终端用户 / skill 维护者 / UAT 裁判** 三视角描述；当前状态已基本实现，故下表为“已实现能力对应的用户价值”。

| 能力类（含 #） | skill 终端用户 | skill 维护者 | UAT 裁判 |
|---|---|---|---|
| **A. 运行时适配 + 配置外置**（#1 #2） | 作为 Cursor/Codex 用户，我也能在被问到优先方向/受众后拿到定制化报告，而不是只能拿到 `-no-question` 默认值。 | 作为维护者，我改切片维度只改 YAML 不碰 Python，且同一份 `repo-types.yaml` 能跨运行时复用。 | 作为裁判，我在三种 runtime 下各跑一次，断言 `data/question-answers.md` 与 `diagnostics/slices/` 行为一致。 |
| **B. 可观测性 / token**（#3） | 作为用户，我能从 `reports/SLA_REPORT.md` 看到本次花了多少 token、是否逼近 500K 预算。 | 作为维护者，我能在 `data/performance-report.json` 里按 agent attempt 追到 token 来源，定位 token 爆炸点。 | 作为裁判，我断言 SLA 报告含 `token_used / token_budget` 字段且越界时标红。 |
| **C. 可选外部调研**（#4） | 作为用户，我可显式开启外部调研，拿到含竞品/组织动机的 `data/research.md`，默认不开启不增加开销。 | 作为维护者，调研开关与报告渲染解耦，关掉时报告不出现调研章节。 | 作为裁判，我断言 OFF 时无 `data/research.md` 且报告无调研段；ON 时文件存在且被引用。**当前现状**：ON 仍只产出 SKIP 占位，真实调研段待补。 |
| **D. 验收强度 + 真实冲突验证**（#5 + 最小补齐②） | 作为用户，我信任的验收不仅查本地产物，还校验 Mermaid 能真渲染、外链真可达、内容经第二 LLM 评判。 | 作为维护者，新增执行器不破坏现有 245+ 项；真实冲突修复路径有 fixture 可回归。 | 作为裁判，我构造真实 cross-ref 冲突 fixture（`tests/fixtures/conflict-repo`），断言回退修复后最终报告质量达 6 维 5/5。 |
| **E. benchmark + UAT 证据闭环**（#6 #7） | 作为用户，我读到 `docs/benchmarks/tree-sitter-baseline.md`，知道本机跑大仓库的性能预期。 | 作为维护者，我有多语言 baseline 作为回归阈值，tree-sitter 行为变动可被发现。 | 作为裁判，我读到 run-005 的 `JUDGE.md` 6 维 5/5，与历史 UAT 对齐闭环。 |

---

## 4. 需求池（P0/P1/P2）

> **优先级说明**：`建议优先级` 沿用 ADR/PLAN 原始定级（P1/P2）；`最小补齐梯队` 映射 PLAN_COMPLIANCE §最小补齐顺序 ①②③④。
> **状态更新**：原 7 项的“当前状态”已按代码核对重写；仅 #4 仍为 stub，其余 6 项标记「已实现」。

| # | 功能 | 来源 | 当前状态 | 目标状态 | 验收标准（可测） | 建议优先级 | 最小补齐梯队 |
|---|---|---|---|---|---|---|---|
| 1 | `ask_user()` 三运行时适配器 | ADR-0003 | **已实现** | （已达）定义 `AskUserAPI` 抽象 + 3 适配器 + 降级链 + `--no-question` 跳过 | ① 三个适配器单元测试覆盖：默认/单选/多选/超时/skip 五分支 PASS（`tests/test_ask_user_adapters.py`）；② `--no-question` 下 `data/question-answers.md` 含 4 题默认值；③ 非交互 runtime 降级到 `defaults.yaml` 不崩溃；④ `SKILL.md` 注明各 runtime 调用方式 | P1 | 已完成 |
| 2 | `config/repo-types.yaml` 外置切片模板 | ADR-0002 | **已实现** | （已达）切片维度由 `config/repo-types.yaml` 驱动 | ① 内嵌 `SLICES` 已移除，`RepoTypeLoader` 驱动的 `write_slices()` 产出与原 6 类 repo 产出逐字节一致；② 类型识别失败时回退 `fallback_dimensions` 并打 warning；③ YAML 含 `version` 字段且与 `SKILL.md` 版本绑定校验（`tests/test_repo_types_loader.py`） | P1 | 已完成 |
| 3 | token 统计接入 SLA / PERFORMANCE | ADR-0007 | **已实现** | （已达）采集各 agent attempt 的 input/output/total token | ① `data/performance-report.json` 的 `agent_attempts[]` 含 `tokens_in/tokens_out/tokens_total`；② `reports/SLA_REPORT.md` 含 `token_used / token_budget (500K)` 与超预算红/黄/绿；③ 确定性模式（无 agent）token 字段为 0 且报告不报错（`tests/test_token_reporter.py`、`tests/test_agent_token_integration.py`） | P1 | 已完成 |
| 4 | 外部调研 `data/research.md` | PLAN §5 | **已知限制 stub**（`write_research()` 恒 SKIP） | 可选阶段，开关默认 OFF；启用后接入真实 5 章节调研并接入报告 §0/§5 | ① 默认 OFF 时不存在 `data/research.md` 且报告无调研段；② `--research`（或 ask_user 开启）后 `data/research.md` 含 5 个规定章节且被 `reports/ANALYSIS_REPORT*` 引用；③ 调研状态写入 `data/config-effective.json` 与 `reports/README.md` | P2 | OPEN（唯一剩余） |
| 5 | acceptance 高成本项 | ADR-0011 | **已实现** | （已达）3 类执行器：LLM-judge / 真实 Mermaid 渲染 / 外链(http)检查 | ① `acceptance/05-mermaid-judge.sh` 用 mermaid-cli 渲染全景图且语法零错；② LLM-judge 对内容准确度/受众匹配度/受众区分度打分，阈值（≥7 / ≥0.30 Jaccard）达成；③ `acceptance/04-link.sh` 对 `http(s)` 外链校验可达、对 commit 引用 `gh api` 校验；④ 三项接入 `check.sh` 汇总，主入口统计项 ≥245；⑤ 失败有 fallback（Mermaid 失败标 warning 不致命，除非显式 `--strict`）（`tests/test_acceptance_executors.py`） | P2 | 已完成 |
| — | **UAT 真实冲突验证**（#5 前置关卡） | ADR-0004 / PLAN_COMPLIANCE 最小补齐② | **已实现**（fixture 已落） | 在 fixture 中构造真实审稿冲突，验证回退修复后报告质量 | ① 提供真实 cross-ref 冲突 fixture `tests/fixtures/conflict-repo`；② 断言 `diagnostics/cross-ref-agent-review.md` 正确建议回退且 `REPAIR` 后无断裂；③ 最终报告 6 维人工评分 ≥5/5（见 #7） | P2 | 已完成 |
| 6 | tree-sitter 多语言 benchmark | ADR-0014 | **已实现（本地基线）** | 跑真实仓库记录 Python / JS-TS / Go-Rust 等 parse/query 行为与性能基线 | ① 产出 `docs/benchmarks/tree-sitter-baseline.md`；② 覆盖 ≥3 仓库（pydantic=Python / kubernetes=Go / turborepo=TS-JS）各记录总耗时/内存峰值/chunked 跳过文件数 —— **当前为本地测量占位，在线仓库真实数据待补**；③ baseline 作为回归阈值写入测试或文档 | P2 | 已完成（在线数据待补） |
| 7 | run-005 `JUDGE.md` 六维评分表 | PLAN_COMPLIANCE §5 | **已实现** | （已达）补 `uat-evidence/run-005/JUDGE.md`，与 run-001/002/003 对齐 | ① 文件含 6 维评分表；② 每维 5/5 且附理由；③ 引用 run-005 的 prompt/会话日志/退出码/产物/重跑日志作为证据；④ 结论判定 6 维全 5/5 通过（`uat-evidence/run-005/JUDGE.md`） | P2 | 已完成 |

### 后续已实现增强（不在原 7 项内，Round 6 / T05–T10，ADR-0016~0019）

原 7 项之外，run-005 之后又落地了 5 项 ADR，均已实现，需在基线中记录以避免文档与代码脱节：

| ADR | 功能 | 当前状态 | 落地代码 |
|---|---|---|---|
| [ADR-0016](decisions/0016-output-dir-restructure.md) | 输出目录重组为 `.stark-repo-analyzer/`（data/reports/diagnostics/logs/acceptance/agent-runs） | 已实现 | `analyzer_*.py` 全部产物路径、`render_report.py --output-dir` |
| [ADR-0017](decisions/0017-preflight-agent-degrade.md) | `--agent-mode` 默认 `codex` + 5 项预检 + 自动降级 `deterministic` | 已实现 | `analyzer_preflight.preflight_check()`、`analyzer_common.degrade_agent_mode()`、`config-effective.json.agent_mode_degraded` |
| [ADR-0018](decisions/0018-progress-reporter-run-log.md) | `[N/M]` 进度输出 + `logs/run-*.md` 运行日志 | 已实现 | `analyzer_common.ProgressReporter` / `LogWriter` |
| [ADR-0019](decisions/0019-llm-judge-model-and-manifest-10k.md) | LLM-judge 模型默认置空（codex 内置默认）+ 项目名片 10KB | 已实现 | `llm_judge.py`（`DEFAULT_MODEL=""`）、`analyzer_metadata.write_manifest_card()`（10KB） |

> **关键路径现状**：原关键路径「⑥ benchmark → 真实冲突验证 → ⑤ 高成本 acceptance → ⑦ JUDGE.md」已全部完成；唯一 OPEN 项为 #4 外部调研（真实联网调研），不阻塞 full PLAN 合规（已 PASS，* T07 除外）。

---

## 5. UI / 交互 / 产物设计稿

### 5.1 `config/repo-types.yaml` 字段结构示意

> 设计要点：ADR-0002 原稿只列 dimension 名，但代码 `write_slices()` 实际需要 `filename + label + patterns` 三元组，故外置 YAML 必须携带完整映射，并保留 `fallback_dimensions` 与 `version`（由 `RepoTypeLoader` 加载并校验，见 `scripts/repo_types_loader.py`）。

```yaml
version: 1                       # 与 skill 版本绑定，加载时校验（不一致直接报错）
fallback_dimensions:             # 类型识别失败/未知类型时硬套 12 维
  - { name: frontend,  file: 01-frontend.xml,  label: 前端代码,   patterns: ["*.tsx","*.jsx","*.vue","*.svelte","*.css","*.scss","*.html"] }
  - { name: backend,   file: 02-backend.xml,   label: 后端代码,   patterns: ["*.py","*.go","*.rs","*.java","*.ts","*.js"] }
  # ... 其余 10 维
repo_types:
  web-fullstack:
    dimension_count: 7
    dimensions:
      - name: frontend
        file: 01-frontend.xml
        label: 前端代码
        patterns: ["*.tsx","*.jsx","*.vue","*.svelte","*.css","*.scss","*.html"]
      - name: backend
        file: 02-backend.xml
        label: 后端代码
        patterns: ["*.py","*.go","*.rs","*.java","*.ts","*.js"]
      - name: database
        file: 03-database.xml
        label: 数据库设计
        patterns: ["*.sql","*.prisma","migrations/*","schema/*"]
      # ... docs / tests / config-scripts / dependencies
  single-lang-CLI:
    dimension_count: 6
    dimensions:
      - { name: code,    file: 02-backend.xml, label: 代码,  patterns: ["*.py","*.go","*.rs","*.java","*.ts","*.js"] }
      - { name: docs,    file: 04-docs.xml,    label: 文档,  patterns: ["*.md","*.mdx","*.rst","docs/*","README*"] }
      # ... tests / config-scripts / dependencies / examples
  # single-lang-lib / monorepo / embedded-kernel / multi-agent-config 同构展开
```

### 5.2 `ask_user()` 三运行时交互 / 降级流程（Mermaid）

```mermaid
flowchart TD
    A[阶段三 发起 ask_user] --> B{检测运行时}
    B -->|Claude Code| C[ClaudeCodeAskAdapter → AskUserQuestion<br/>2-4 选项 + multiSelect]
    B -->|Codex CLI| D[CodexAskAdapter → codex ask<br/>选项受限时退化为纯文本 prompt]
    B -->|Cursor| E[CursorAskAdapter → 写 questions.json<br/>+ 暂停 skill 等待 resume]
    C --> F{获得答案?}
    D --> F
    E --> G[用户手工填 questions.json 后 --resume 续跑]
    G --> F
    F -->|否 / 超时 / --no-question| H[读 defaults.yaml 默认值<br/>Q1=architecture Q2=tech-lead Q3=Q4=[]]
    F -->|是| I[写 data/question-answers.md<br/>4 题答案或默认值]
    H --> I
    I --> J[阶段四 按答案选模板映射]
```

降级链（自动）：原生交互 → 写 `questions.json` + 暂停 → `defaults.yaml` 默认值。
skip 路径：`--no-question` 直接读默认值，不发起交互。

### 5.3 `data/research.md` 章节骨架（**当前为 stub，OFF 时不生成；ON 时仍只写 SKIP**）

```markdown
# 外部调研产物 (data/research.md)

- 状态: 启用 / 跳过(默认 OFF)
- 调研方法: WebSearch / 官网 / GitHub Insights / 官方博客
- 耗时: NN 分钟

## 1. 项目解决的核心问题
（1-3 个具体场景）

## 2. 竞品对比
| 竞品 | 定位 | 差异点 |
|---|---|---|
| ... | ... | ... |

## 3. 为什么需要单独做这个项目
（1 段叙述，引用官方公告/创始人博客）

## 4. 组织动机
（1 段，贡献者地理分布 / GitHub Insights）

## 5. 自带架构文档要点
（读 docs/、CONTRIBUTING.md、AGENTS.md、ADR 后的关键设计决策清单）

## 引用与来源
- [来源1](url)
- [来源2](url)
```

> 当前实现：`--research` 开启后 `write_research()` 仍只写入 `status: SKIP`（离线或本环境无联网源），不产出上述 5 章节。这是 **#4 唯一剩余缺口**。

### 5.4 acceptance 高成本项报告片段示例

新增 3 类执行器接入 `acceptance/check.sh` 汇总（沿用现有 `PASS|name|detail` 格式）：

```text
=== 05-mermaid-judge.sh ===
PASS|mermaid render:全景图|no syntax error (mermaid-cli exit 0)
PASS|llm-judge:内容准确度|8.2/10 ≥ 7
PASS|llm-judge:受众匹配度|tech-lead 7.9 / business 8.1 / learning 8.0
PASS|llm-judge:受众区分度|Jaccard 0.41 ≥ 0.30
PASS|link check:外链可达|12/12 http(s) 200, 0 个 5xx
PASS|gh check:commit 引用|3/3 exists

=== 汇总 ===
TOTAL: 251  PASS: 251  FAIL: 0   (原 245 + 新增 6)
```

> 失败策略：Mermaid 渲染失败默认标 `WARN`（不致命），仅当 `--strict` 时 FAIL；外链检查需网络访问策略（见 Open Questions Q5，现状为默认 SKIP）。

### 5.5 `JUDGE.md` 六维评分表模板（run-005，已落地）

```markdown
# UAT 裁判报告 - run-005

## 结论
通过。完整智能闭环（claude-video）245/245 确定性验收 PASS，补 6 维人工评分。

## 关键证据
- 测试 prompt: uat-evidence/run-005/prompt.md
- 会话日志: uat-evidence/run-005/codex-session.log
- 退出码: uat-evidence/run-005/codex-exit-status.txt (=0)
- 产物目录: uat-evidence/run-005/artifacts
- 裁判重跑: uat-evidence/run-005/acceptance-recheck-main.log (245/245 PASS)

## 评分

| 维度 | 分数 | 理由 |
|---|---:|---|
| 用户使用友好度 | 5/5 | 短提示 `$stark-repo-analyzer` 即可触发完整闭环 |
| 使用简易度 | 5/5 | 用户仅给 URL/路径，无新增步骤 |
| 结果契合度 | 5/5 | 总览 + tech-lead/business/learning 三受众差异化达标（差异度 >0.18） |
| 结果完整性 | 5/5 | 18 阶段全 PASS，8 模块覆盖率 1.00，SLA 415s/30min 内 |
| 执行稳定程度 | 5/5 | 主命令退出码 0，agent 子会话 returncode 0，无超时 |
| 证据完整性与可复查性 | 5/5 | prompt/日志/退出码/产物/重跑日志齐备 |

## 最终判定
6 个维度全部 5/5。run-005 正式闭环。
```

---

## 6. 待确认问题（Open Questions）

> 状态更新：原 9 项中大部分已随实现落地而 resolved；下方标注 `✅ 已解决` 与 `⏳ 仍开放`。

| # | 问题 | 影响项 | 状态 |
|---|---|---|---|
| Q1 | **三运行时到底是哪三个？** | #1 | ✅ 已解决：`ask_user_adapters.py` 明确为 claude-code / codex / cursor（`detect_runtime()` 经 `CLAUDECODE`/`CODEX`/`CURSOR` 或 `REPO_ANALYZER_RUNTIME` 识别），并在 `SKILL.md` 注明。 |
| Q2 | **token 统计数据源？** | #3 | ✅ 已解决：agent 在返回文本中以 `<!-- TOKENS: in,out -->` 声明，`TokenCollector.collect_from()` 解析并写入 `data/config-effective.json` 与各报告。 |
| Q3 | **benchmark 选哪三个具体仓库？** | #6 | ⏳ 部分：benchmark 脚本与本地基线已落（`docs/benchmarks/tree-sitter-baseline.md` 为本地测量占位）；在线参考仓库（pydantic/kubernetes/turborepo）真实数据待联网补。 |
| Q4 | **LLM-judge 用哪个模型与预算？** | #5 | ✅ 已解决（ADR-0019）：`llm_judge.py` 的 `DEFAULT_MODEL` 改为空字符串，不传 `--model` 时由 codex 内置默认决定；预算从 500K SLA 预留。 |
| Q5 | **外链检查是否需网络访问策略？** | #5 | ✅ 已解决：`acceptance/04-link.sh` 默认 SKIP（离线友好），`--strict` 或显式 `--check-links` 才 FAIL。 |
| Q6 | **`repo-types.yaml` 版本绑定与迁移** | #2 | ✅ 已解决：`RepoTypeLoader` 校验 `version` 与 `SKILL.md` 一致，不一致直接报错；保留 `fallback_dimensions` 12 维作为未知类型回退。 |
| Q7 | **Mermaid 渲染依赖** | #5 | ✅ 已解决：mermaid-cli 为可选依赖，渲染失败默认 WARNING，避免把可选依赖变硬失败。 |
| Q8 | **JUDGE.md 作者归属** | #7 | ✅ 已落地（待签字）：`uat-evidence/run-005/JUDGE.md` 已生成（证据索引草稿），按 PLAN_COMPLIANCE §5 备注待人工裁判签字正式闭环。 |
| Q9 | **真实冲突验证 fixture 来源** | 补齐② | ✅ 已解决：`tests/fixtures/conflict-repo`（module_a / module_b / orchestrator.py / README.md）可作最小 fixture 回归。 |

---

## 附录：参考依据索引

- `references/PLAN_COMPLIANCE.md` §1-§6（合规基线、Round 6 增量、run-005 证据）
- `references/decisions/0002-phase-2a-dynamic.md`（repo-types.yaml 结构）
- `references/decisions/0003-ask-user-api.md`（AskUserAPI 抽象、三适配器、降级链）
- `references/decisions/0007-sla-budget.md`（500K token / 30min / 3 次重试）
- `references/decisions/0011-acceptance-script-enforce.md`（5 类执行器，含 LLM-judge / Mermaid / 外链）
- `references/decisions/0014-treesitter-chunked.md`（benchmark 3 仓库、指标）
- `references/decisions/0016-output-dir-restructure.md`（输出目录重组）
- `references/decisions/0017-preflight-agent-degrade.md`（预检 + agent 模式自动降级）
- `references/decisions/0018-progress-reporter-run-log.md`（进度输出与运行日志）
- `references/decisions/0019-llm-judge-model-and-manifest-10k.md`（LLM-judge 模型默认置空 + 名片 10KB）
- `scripts/repo_types_loader.py`（`RepoTypeLoader` 现状）、`scripts/ask_user_adapters.py`（`AskUserAPI` 现状）、`scripts/token_reporter.py`（`TokenCollector` 现状）、`scripts/analyzer_metadata.py`（`write_research` / `write_manifest_card` 现状）、`scripts/analyzer_preflight.py`（`preflight_check` 现状）、`scripts/analyzer_common.py`（`ProgressReporter` / `LogWriter` 现状）、`scripts/llm_judge.py`（`DEFAULT_MODEL` 现状）
- `config/repo-types.yaml`（切片维度外置）、`config/defaults.example.yaml`（交互问题默认值示例）
- `references/PLAN.md` §5（外部调研 03-research.md 设计，现为 `data/research.md` stub）
- `uat-evidence/run-001/JUDGE.md`、`run-003/JUDGE.md`、`run-005/JUDGE.md`（6 维评分表范本，run-005 已落地）
