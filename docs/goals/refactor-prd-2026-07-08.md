# 增量 PRD：stark-repo-analyzer 用户体验与工程结构重构（2026-07-08）

> 文档定位：本轮是**增量重构 PRD**，基于用户反馈的 12 项问题，对已通过 UAT（run-005，245/245）的现有 skill 做 UX/结构/可维护性增强。
> 基线：`scripts/repo_analyzer.py`（2746 行单文件）+ 5 个已提取模块（`repo_types_loader.py`、`ask_user_adapters.py`、`token_reporter.py`、`render_report.py`、`llm_judge.py`）+ `benchmark_treesitter.py`。
> 与 `PRD_UNFINISHED_FEATURES.md`（7 项功能补齐，已基本实现）**正交不冲突**——那份 PRD 补的是 PLAN 承诺的功能面，本 PRD 补的是用户反馈的体验/结构面。

---

## 1. 产品目标

1. **产物可读性**：消除"26 个文件平铺、人机混在一起"的混乱，让人类和 AI agent 各有清晰的阅读入口。
2. **执行可观测性**：用户不再"等到结束才看到一行输出"，每一步运行情况实时可见，出问题能快速定位。
3. **代码可维护性**：2746 行单文件拆为职责清晰的模块，后续修改不再"在一个文件里翻找"。

---

## 2. 用户故事

| 需求项 | 用户故事 |
|--------|---------|
| REQ-01 输出目录重命名 | 作为用户，我希望分析产物放在 `.stark-repo-analyzer` 而非 `analysis`，并被提醒加入 `.gitignore`，这样产物不会意外提交到我的仓库。 |
| REQ-02 运行时预检 | 作为用户，我希望执行前能看到每一项环境依赖的检查结果（git/npx/tree-sitter/codex 等），某项缺失时明确提示如何修复，而不是跑到一半才报错。 |
| REQ-03 LLM-judge 修复 | 作为用户，我希望验收的 LLM-judge 阶段不会因为默认模型不可用而静默 WARN，失败时能看到模型名和错误摘要以便诊断。 |
| REQ-04 执行进度反馈 | 作为用户，我希望执行期间能看到"正在执行第 N 步：XXX"的进度输出，知道脚本没有卡死、每一步花了多久。 |
| REQ-05 Agent 默认开启 | 作为用户，我希望默认就能获得 agent 模式的深度分析效果，而不需要每次手动加 `--agent-mode codex`；除非我主动关闭。 |
| REQ-06 产物结构重组 | 作为用户，我希望打开产物目录后能立刻分清"哪些是给我看的报告、哪些是给 AI agent 消费的数据"，而不是面对 26 个平铺文件无从下手。 |
| REQ-07 任务运行日志 | 作为用户/维护者，我希望有一个日志目录记录每一步的执行描述、遇到的问题、思考和解决过程、产出的结果，方便事后复盘。 |
| REQ-08 PERFORMANCE_REPORT 定位 | 作为用户，我希望明确知道 `PERFORMANCE_REPORT.md` 是"性能诊断报告"而非"分析结论报告"，打开后一眼看到它的用途说明。 |
| REQ-09 名片扩容 | 作为用户，我希望项目名片从 5KB 扩到 10KB，包含更多项目关键信息（入口点、依赖数、CI 配置、许可证等），减少遗漏。 |
| REQ-10 模块拆分 | 作为维护者，我希望 `repo_analyzer.py` 拆成多个职责单一的模块文件，修改某个功能时只需关注对应模块，而不是在 2746 行里搜索。 |

---

## 3. 需求池（P0/P1/P2）

### REQ-01：输出目录重命名为 `.stark-repo-analyzer` + gitignore 提醒

| 属性 | 值 |
|------|-----|
| 原问题编号 | #1 |
| 优先级 | **P0** |
| 一句话目标 | 将默认输出目录从 `analysis` 改为 `.stark-repo-analyzer`，并提醒用户添加 `.gitignore` 排除 |
| 依赖 | 无（可与 REQ-10 并行；但若与 REQ-06 同批做更高效） |

**验收标准（可测试）：**
1. `build_parser()` 的 `--output` 默认值改为 `.stark-repo-analyzer`。
2. `IGNORE_DIRS` 集合中移除 `analysis`/`analysis-final`/`analysis-judge` 等旧名，新增 `.stark-repo-analyzer`。
3. 执行完成后 stdout 输出包含 gitignore 提示行，例如：`提示：建议将 .stark-repo-analyzer/ 加入 .gitignore`。
4. 若输出目录在被分析仓库内且该仓库有 `.gitignore`，自动追加一行 `.stark-repo-analyzer/`（若尚未存在）。
5. 既有测试中所有硬编码 `analysis` 路径的断言更新为 `.stark-repo-analyzer`，测试全部 PASS。

---

### REQ-02：运行时预检机制

| 属性 | 值 |
|------|-----|
| 原问题编号 | #2 |
| 优先级 | **P0** |
| 一句话目标 | 执行任务前列出每项运行环境依赖的检查结果，不通过则提示修复并中止 |
| 依赖 | 与 REQ-05 有协同（agent 默认开启时需检查 codex 可用性） |

**验收标准（可测试）：**
1. `analyze()` 在 `checkout_target` 之前新增 `preflight_check()` 阶段，逐项检查并输出结果表（✅/❌ + 修复建议）。
2. 检查项至少覆盖：Python 版本 ≥3.10、`git` 可用、`npx`（repomix）可用、`tree-sitter` CLI 可用性（可选，缺失时 WARN 而非 FAIL）、`codex` CLI 可用性（agent 模式下必需，确定性模式下可选）。
3. 任一**必需**检查项 FAIL 时，脚本输出明确修复建议并 `sys.exit(1)`，不继续执行后续阶段。
4. **可选**检查项缺失时输出 WARN 但允许继续（如 tree-sitter 缺失退回 regex 引擎）。
5. 预检结果写入任务运行日志（REQ-07）的第一条记录。
6. 单元测试覆盖：全部通过 / 必需项缺失 / 可选项缺失三种场景。

---

### REQ-03：LLM-judge 默认模型修复

| 属性 | 值 |
|------|-----|
| 原问题编号 | #3 |
| 优先级 | **P0** |
| 一句话目标 | LLM-judge 不再硬依赖 `haiku-4.5`，回退到 Codex CLI 默认模型，失败时输出可诊断信息 |
| 依赖 | 无（已有 `docs/goals/fix-llm-judge-default-model-unsupported.md` 明确验收标准） |

**验收标准（可测试）：**
1. 未设置 `REPO_ANALYZER_LLM_JUDGE_MODEL` 时，`llm_judge.py` 不传 `--model haiku-4.5`，使用 Codex CLI 默认模型。
2. 显式设置不可用模型（如 `haiku-4.5`）时，WARN 详情包含模型名和 Codex stderr 关键错误摘要（而非仅 `codex 退出码 1`）。
3. Codex 返回非零退出码时，`llm_judge.py` 输出可诊断 WARN；非 `--strict` 模式不让 deterministic acceptance 失败。
4. 复跑验证命令通过：`REPO_ANALYZER_LLM_JUDGE_MODEL=gpt-5.5 sh acceptance/llm-judge.sh` 和 `REPO_ANALYZER_LLM_JUDGE_MODEL=haiku-4.5 sh acceptance/llm-judge.sh` 均输出含模型名的诊断信息。

---

### REQ-04：执行进度实时反馈

| 属性 | 值 |
|------|-----|
| 原问题编号 | #4 |
| 优先级 | **P0** |
| 一句话目标 | 执行期间在 stdout 实时输出每一步的进度，包括步骤名、开始/完成状态、耗时 |
| 依赖 | 与 REQ-10 协同（拆分后每个模块可独立报告进度）；可先独立实现 |

**验收标准（可测试）：**
1. `analyze()` 每个阶段开始时输出进度行，格式如：`[3/12] 正在执行：repomix-slices ...`。
2. 每个阶段完成时输出完成行，格式如：`[3/12] repomix-slices 完成 (12.3s)`。
3. agent 模式下每个 agent 子任务（module batch / coverage repair / cross-ref review）开始和完成时输出进度行。
4. 全部完成后输出最终汇总行（总耗时、总步骤数、成功/失败步骤数）。
5. 进度输出写入 stdout（不污染产物文件），同时记录到任务运行日志（REQ-07）。
6. 进度行格式稳定可解析（供 SKILL.md 的主会话读取并转述给用户）。

---

### REQ-05：Agent 模式默认开启

| 属性 | 值 |
|------|-----|
| 原问题编号 | #5 |
| 优先级 | **P0** |
| 一句话目标 | `--agent-mode` 默认从 `deterministic` 改为 `codex`，用户可显式关闭 |
| 依赖 | 与 REQ-02 协同（预检需检查 codex 可用性，不可用时降级） |

**验收标准（可测试）：**
1. `build_parser()` 的 `--agent-mode` 默认值改为 `codex`。
2. 用户可通过 `--agent-mode deterministic` 显式关闭 agent 模式。
3. 预检（REQ-02）发现 codex 不可用时，输出 WARN 并自动降级到 `deterministic` 模式（而非直接中止），降级信息写入 `CONFIG_EFFECTIVE.json` 的 `agent_mode_degraded: true`。
4. SKILL.md 更新：默认命令不再需要 `--agent-mode codex`，"完整智能闭环"变为默认行为。
5. 既有测试中默认 agent-mode 的断言更新为 `codex`，确定性模式测试显式传 `--agent-mode deterministic`。

---

### REQ-06：输出产物目录结构重组（区分人类/AI agent 阅读）

| 属性 | 值 |
|------|-----|
| 原问题编号 | #6, #8, #9 |
| 优先级 | **P0** |
| 一句话目标 | 将 26 个平铺文件重组为分层目录，明确区分"人类阅读"和"AI agent 阅读"两类 |
| 依赖 | **强烈建议在 REQ-10（模块拆分）之后执行**——拆分后每个 `write_*` 函数分布在独立模块中，改路径时 diff 更小更可审查 |

**验收标准（可测试）：**
1. 产物目录从平铺结构重组为分层结构，至少包含以下顶层分区：
   - `reports/`：人类阅读报告（ANALYSIS_REPORT*.md、manifest-card.md、coverage.md、sla-report.md、state-report.md）
   - `data/`：AI agent 消费的结构化数据（AGENT_SUMMARY.json、REPORT_DATA.json、CONFIG_EFFECTIVE.json、repo-type.yaml、module-ids.yaml、coverage-symbols.json、expected-symbols.json、mcp-tools.json）
   - `slices/`：原料切片（保持现有）
   - `drafts/`：模块草稿（保持现有）
   - `agent-runs/`：agent 执行证据（保持现有）
   - `diagnostics/`：诊断报告（meta.txt、PERFORMANCE_REPORT.{md,json}）
   - `logs/`：任务运行日志（REQ-07）
   - `acceptance/`：验收脚本（保持现有）
   - `README.md`：顶层索引页（人类入口，说明各目录用途）
2. `README.md` 顶部有"目录说明"表格，标注每个子目录是"人类阅读"还是"AI agent 阅读"还是"诊断/过程"。
3. `write_acceptance()` 生成的 245+ 断言全部更新为新路径，验收仍全部 PASS。
4. SKILL.md Step 3（确认核心产物存在）的路径全部更新。
5. 既有测试中所有路径断言更新为新结构，测试全部 PASS。

**建议目录结构（供架构师 review）：**

```
.stark-repo-analyzer/
├── README.md                    # 索引页（人类入口）
├── reports/                     # 📖 人类阅读
│   ├── ANALYSIS_REPORT.md
│   ├── ANALYSIS_REPORT.tech-lead.md
│   ├── ANALYSIS_REPORT.business.md
│   ├── ANALYSIS_REPORT.learning.md
│   ├── manifest-card.md         # 10KB 项目名片
│   ├── coverage.md
│   ├── sla-report.md
│   └── state-report.md
├── data/                        # 🤖 AI agent 阅读
│   ├── AGENT_SUMMARY.json
│   ├── REPORT_DATA.json
│   ├── CONFIG_EFFECTIVE.json
│   ├── repo-type.yaml
│   ├── module-ids.yaml
│   ├── coverage-symbols.json
│   ├── expected-symbols.json
│   └── mcp-tools.json
├── slices/                      # 🤖 原料切片
├── drafts/                      # 🤖 模块草稿
├── agent-runs/                  # 🤖 agent 证据
├── diagnostics/                 # 🔧 诊断
│   ├── meta.txt
│   ├── PERFORMANCE_REPORT.md
│   └── PERFORMANCE_REPORT.json
├── logs/                        # 📋 任务运行日志
└── acceptance/                  # ✅ 验收
    ├── check.sh
    ├── 04-link.sh
    ├── 05-mermaid-judge.sh
    └── llm-judge.sh
```

> 注：文件名是否去掉编号前缀（如 `02a-manifest-card.md` → `manifest-card.md`）取决于是否有外部消费者依赖原文件名——需架构师确认后决定。若保留编号前缀则路径变为 `reports/02a-manifest-card.md`。

---

### REQ-07：任务运行日志目录

| 属性 | 值 |
|------|-----|
| 原问题编号 | #7 |
| 优先级 | **P1** |
| 一句话目标 | 新增 `logs/` 目录，记录每一步执行的任务描述、遇到的问题、解决思路、结果 |
| 依赖 | REQ-06（日志目录路径依赖最终目录结构） |

**验收标准（可测试）：**
1. 产物目录下新增 `logs/` 子目录，每次运行生成一份日志（如 `logs/run-YYYYMMDD-HHMMSS.md` 或按 step 拆分）。
2. 日志内容覆盖每个执行阶段：步骤名、开始/结束时间、耗时、状态（成功/失败/跳过）、遇到的问题（如有）、解决方式（如有）、产出物路径。
3. agent 模式下，每个 agent 子任务的 prompt 摘要、退出码、耗时、结果摘要也记入日志。
4. 预检结果（REQ-02）作为日志第一条记录。
5. 进度输出（REQ-04）同步写入日志。
6. 日志格式为 Markdown，人类可直接阅读。

---

### REQ-08：PERFORMANCE_REPORT 定位澄清与改进

| 属性 | 值 |
|------|-----|
| 原问题编号 | #10 |
| 优先级 | **P1** |
| 一句话目标 | 澄清 PERFORMANCE_REPORT 是"性能诊断报告"而非"分析结论"，改进可读性和定位说明 |
| 依赖 | REQ-06（移入 `diagnostics/` 子目录后定位更清晰） |

**验收标准（可测试）：**
1. `PERFORMANCE_REPORT.md` 顶部新增定位说明段落，明确标注："本报告记录各阶段耗时、慢因诊断和 token 用量，用于排查执行性能问题，不是仓库分析结论。分析结论请读 `reports/ANALYSIS_REPORT*.md`。"
2. 报告移入 `diagnostics/` 子目录（与 `meta.txt` 同级），不再与人类阅读报告混在一起。
3. `README.md` 索引页将其标注为"🔧 诊断报告"而非"分析报告"。
4. SKILL.md Reference 段落更新，明确说明 PERFORMANCE_REPORT 的用途和阅读场景。
5. 报告内增加"如何阅读本报告"小节，说明 stage 排名、agent attempt 排名、token 状态的含义。

---

### REQ-09：项目名片扩容至 10KB

| 属性 | 值 |
|------|-----|
| 原问题编号 | #11 |
| 优先级 | **P1** |
| 一句话目标 | 将 `manifest-card.md` 从 5KB 硬截断改为 10KB，增加更多项目关键信息 |
| 依赖 | 无（可独立实现）；文件名/路径随 REQ-06 调整 |

**验收标准（可测试）：**
1. `write_manifest_card()` 的截断从 `card[:5_000]` 改为 `card[:10_000]`。
2. 名片标题从"5KB 项目名片"改为"10KB 项目名片"。
3. 名片内容在现有基础上（项目名/目标/Repo 类型/语言/文件数/顶层快照/README 前 30 行）增加以下字段：
   - 包管理文件摘要（package.json / pyproject.toml / go.mod / Cargo.toml 关键字段：name, version, description, license）
   - 依赖数量统计（dependencies / devDependencies 计数）
   - 入口点识别（main 字段 / `__init__.py` / `main.go` / `index.ts` 等）
   - CI/CD 配置存在性（`.github/workflows/`、`Makefile`、`Dockerfile` 是否存在）
   - 测试框架识别（pytest / jest / go test 等，基于配置文件或目录约定）
   - 最近一次提交信息（commit hash + 日期 + message 首行）
   - 贡献者数量（`git shortlog -sn --all | wc -l`）
   - 目录树深度（展示 2 层目录结构，而非仅顶层 60 个文件）
4. 名片文件大小在 8KB~10KB 之间（内容不足 10KB 时不填充，超过 10KB 时截断）。
5. 验收断言更新：检查名片文件存在且大小 > 5KB。

---

### REQ-10：`repo_analyzer.py` 模块拆分

| 属性 | 值 |
|------|-----|
| 原问题编号 | #12 |
| 优先级 | **P1**（但建议最先执行，作为其他需求的基础） |
| 一句话目标 | 将 2746 行单文件拆为职责清晰的多个模块文件 |
| 依赖 | 无（纯重构，行为不变）；**是 REQ-06 的前置依赖** |

**验收标准（可测试）：**
1. `repo_analyzer.py` 缩减为入口文件（`analyze()` + `build_parser()` + `main()`），行数显著降低（建议 < 200 行）。
2. 原文件中的函数按职责拆分到独立模块，每个模块文件聚焦单一职责。建议拆分方向（供架构师 review）：
   - 配置加载与合并 → `analyzer_config.py`
   - 仓库检出与文件枚举 → `analyzer_checkout.py`
   - repomix 切片生成 → `analyzer_slicing.py`
   - 仓库元数据与名片 → `analyzer_metadata.py`
   - 符号提取与覆盖率 → `analyzer_coverage.py`
   - 模块计划与草稿 → `analyzer_modules.py`
   - cross-ref 校验 → `analyzer_crossref.py`
   - agent 执行与调度 → `analyzer_agent.py`
   - 报告渲染与索引 → `analyzer_reports.py`
   - SLA/性能/状态报告 → `analyzer_reporting.py`
   - 验收脚本生成 → `analyzer_acceptance.py`
3. 拆分后既有 245+ 验收断言全部 PASS（行为不变契约）。
4. 既有测试全部 PASS，无需修改测试逻辑（仅可能需调整 import 路径）。
5. 各模块间无循环依赖。
6. `_LOADER`、`_TOKEN_COLLECTOR` 等全局状态的管理方式在拆分后仍正确（可能需要传递而非全局引用）。

---

## 4. 优先级建议与执行顺序

### 4.1 分阶段执行建议

**Phase 0 — 基础重构（先行，无行为变更）**

| 需求 | 说明 |
|------|------|
| **REQ-10 模块拆分** | 纯重构、行为不变，用现有 245+ 验收做安全网。**必须先做**——后续所有改路径/改逻辑的需求都在拆分后的小模块上操作，diff 更小、review 更容易、冲突更少。 |

**Phase 1 — 独立小项（可与 Phase 0 并行）**

| 需求 | 说明 |
|------|------|
| **REQ-03 LLM-judge 修复** | 改 `llm_judge.py` 一个文件，与 `repo_analyzer.py` 无关，完全独立。 |
| **REQ-09 名片扩容** | 改 `write_manifest_card()` 一个函数，改动范围小。若 Phase 0 已将此函数拆到 `analyzer_metadata.py`，则在拆分后的模块上改。 |

**Phase 2 — 核心体验（Phase 0 完成后并行推进）**

| 需求 | 依赖 | 说明 |
|------|------|------|
| **REQ-01 输出目录重命名** | REQ-10 | 改 `build_parser` default + `IGNORE_DIRS`，小改动。**建议与 REQ-06 合并执行**——目录重命名和结构重组是同一批路径变更。 |
| **REQ-06 产物结构重组** | REQ-10 | 本轮最大改动。需更新所有 `write_*` 函数的输出路径 + `write_acceptance()` 的 245+ 断言 + SKILL.md 路径引用 + 测试路径断言。 |
| **REQ-02 运行时预检** | 无强依赖 | 新增 `preflight_check()` 阶段，插在 `analyze()` 开头。与 REQ-05 协同。 |
| **REQ-04 执行进度反馈** | 无强依赖 | 改 `timed_stage()` 上下文管理器或新增 progress 回调。 |
| **REQ-05 Agent 默认开启** | REQ-02 | 改 `build_parser` default + 降级逻辑。依赖 REQ-02 的预检来判断 codex 可用性。 |

**Phase 3 — 收尾增强（Phase 2 完成后）**

| 需求 | 依赖 | 说明 |
|------|------|------|
| **REQ-07 任务运行日志** | REQ-06 | 日志目录路径依赖最终目录结构。 |
| **REQ-08 PERFORMANCE_REPORT 定位** | REQ-06 | 报告移入 `diagnostics/` 后定位更清晰。 |

### 4.2 依赖关系图

```
REQ-10 (模块拆分) ──────────────────────────────────────┐
  │                                                     │
  ├──> REQ-01 (输出目录重命名) ──┐                       │
  │                              ├──> REQ-06 (结构重组) ──┤
  └──> REQ-09 (名片扩容) ────────┘    │                  │
                                      │                  │
REQ-03 (LLM-judge) ─── 独立 ──────────┤                  │
                                      │                  │
REQ-02 (运行时预检) ──> REQ-05 (Agent默认) ──────────────┤
                                      │                  │
REQ-04 (进度反馈) ─── 独立 ────────────┤                  │
                                      │                  │
                                      ▼                  ▼
                              REQ-07 (任务日志)     REQ-08 (PERF定位)
```

### 4.3 可并行项

- Phase 0 + Phase 1 可完全并行（3 条线同时开工）。
- Phase 2 内部：REQ-02+REQ-05 一条线，REQ-04 一条线，REQ-01+REQ-06 一条线——三条线可并行，只要 Phase 0 已完成。
- Phase 3 的 REQ-07 和 REQ-08 可并行。

### 4.4 关键决策：REQ-10 与 REQ-06 谁先谁后

**结论：REQ-10（模块拆分）先于 REQ-06（结构重组）。**

理由：
1. REQ-06 需要修改 ~15 个 `write_*` 函数的输出路径。在 2746 行单文件中做这些修改，所有改动集中在同一文件，review 困难、容易遗漏、合并冲突风险高。
2. REQ-10 拆分后，路径修改分散到各模块（如 `analyzer_metadata.py` 改名片路径、`analyzer_reports.py` 改报告路径），每个模块的 diff 小而聚焦。
3. REQ-10 是纯重构（行为不变），用现有 245+ 验收做安全网即可验证正确性，风险可控。
4. 若先做 REQ-06 再做 REQ-10，则 REQ-06 的路径变更和 REQ-10 的函数搬迁叠加在同一批改动中，难以区分"路径改对了没"和"函数搬对了没"。

---

## 5. 范围边界

### 5.1 本轮做什么

- 改 `scripts/repo_analyzer.py` 及其拆分模块：输出路径、默认参数、进度反馈、预检逻辑。
- 改 `scripts/llm_judge.py`：默认模型回退与诊断信息。
- 改 `acceptance/check.sh` 生成逻辑（`write_acceptance()`）：更新断言路径。
- 改 `SKILL.md`：Steps 描述、默认行为说明、Reference 路径、产物目录说明。
- 改 `tests/`：更新路径断言、新增预检/进度/降级测试。
- 新增 `preflight_check()` 逻辑和进度反馈机制。
- 新增 `logs/` 日志目录及写入逻辑。

### 5.2 本轮不做什么

- **不改既有 ADR（0001~0015）**：既有 ADR 记录的是已确认的架构决策，本轮不回溯修改。若本轮决策与既有 ADR 有交集（如 agent 默认模式变更），新增 ADR 记录而非改旧的。
- **不改 PLAN.md 分析方法论**：8 阶段分析流程（阶段零~七）不变，只改工具的 UX/结构/可维护性。
- **不引入第三方 Python 依赖**：沿用 stdlib-only 约束（SKILL.md 边界）。
- **不改 `config/repo-types.yaml` 结构**：切片维度配置已外置且稳定，本轮不动。
- **不改 `templates/*.tmpl.md` 的报告内容结构**：报告模板的章节骨架不变，只改产物存放路径。
- **不做 `PRD_UNFINISHED_FEATURES.md` 中的 7 项**：那 7 项已基本实现，与本轮 12 项正交。
- **不改 `benchmark_treesitter.py`**：benchmark 脚本不在本轮范围。

### 5.3 待新增 ADR（建议）

以下决策建议新增 ADR 记录（编号 0016+），供架构师确认后落地：

| 候选 ADR | 决策内容 |
|----------|---------|
| ADR-0016 | 输出目录从 `analysis` 改为 `.stark-repo-analyzer` |
| ADR-0017 | agent-mode 默认从 `deterministic` 改为 `codex`，不可用时自动降级 |
| ADR-0018 | 产物目录从平铺改为分层结构（reports/data/diagnostics/logs/...） |
| ADR-0019 | `repo_analyzer.py` 模块拆分方案（模块边界与职责划分） |

---

## 6. 待确认问题（Open Questions）

| # | 问题 | PM 建议 | 需拍板方 |
|---|------|---------|---------|
| Q1 | **`.stark-repo-analyzer` 放在被分析仓库根目录还是当前工作目录？** 当前 `analysis` 是相对 CWD。若分析远程仓库（克隆到 /tmp），产物放 CWD 合理；若分析本地仓库，用户可能期望放仓库根目录。 | **建议保持相对 CWD**（与现有行为一致，避免远程仓库产物随 /tmp 清理丢失）。仅改目录名，不改放置逻辑。 | 用户 |
| Q2 | **Agent 默认开启后，codex 不可用时如何降级？** 选项：(a) 自动降级到 deterministic + WARN；(b) 中止并提示安装 codex；(c) 询问用户。 | **建议 (a) 自动降级 + WARN**：预检发现 codex 缺失时，输出"codex 不可用，已降级到确定性模式"并继续执行，`CONFIG_EFFECTIVE.json` 记 `agent_mode_degraded: true`。避免因环境问题阻断用户。 | 用户 |
| Q3 | **10KB 名片增加哪些字段？** PM 建议了 8 项（包管理摘要/依赖数/入口点/CI-CD/测试框架/最近提交/贡献者数/目录树深度），是否全部采纳？是否还有其他想要的字段？ | **建议全部采纳**，优先保证"入口点 + 依赖数 + CI/CD + 测试框架"四项（对理解项目最重要），其余为加分项。 | 用户 |
| Q4 | **PERFORMANCE_REPORT 是保留并加定位说明，还是并入别的报告？** | **建议保留并加定位说明**：(a) 移入 `diagnostics/` 子目录；(b) 顶部加"本报告用于性能诊断，非分析结论"说明；(c) README 索引标注为"🔧 诊断报告"。不并入其他报告——它的读者（排查性能问题的维护者）与分析报告的读者（理解仓库的用户）不同。 | 用户 |
| Q5 | **文件名是否去掉编号前缀？** 如 `02a-manifest-card.md` → `manifest-card.md`。去掉更简洁，但可能有外部消费者（如 graphify、用户脚本）依赖原文件名。 | **建议保留编号前缀**（如 `reports/02a-manifest-card.md`），降低对外部消费者的破坏风险。若架构师确认无外部消费者依赖原文件名，则可去掉。 | 架构师 + 用户 |
| Q6 | **模块拆分的边界怎么划？** PM 给了 11 个模块的建议方向，但具体哪些函数归哪个模块、模块间如何传递全局状态（`_LOADER`/`_TOKEN_COLLECTOR`/`performance` dict）由架构师决定。 | **PM 只定"拆分后单文件 < 200 行、各模块职责单一、无循环依赖"的验收标准**，具体边界交架构师设计。 | 架构师 |
| Q7 | **进度输出的格式是纯文本还是结构化（JSON lines）？** 纯文本对人友好，JSON lines 对程序解析友好。 | **建议纯文本**（如 `[3/12] 正在执行：repomix-slices ...`），因为主要读者是 SKILL.md 主会话中转述给用户。若后续有程序化消费需求可再加 `--progress-format json`。 | 用户/架构师 |
| Q8 | **任务运行日志是单文件还是按 step 拆分？** 单文件便于通读，按 step 拆分便于定位。 | **建议单 Markdown 文件**（`logs/run-YYYYMMDD-HHMMSS.md`），内按 step 分节。文件数少、便于通读复盘。 | 用户/架构师 |
| Q9 | **SKILL.md 的 Step 描述是否本轮改？** Step 1~7 引用了大量具体文件路径，目录重组后必须更新。 | **必须改**，且作为最后一道工序（代码改完、路径稳定后再改 SKILL.md）。Step 2 的默认命令、Step 3 的产物路径、Reference 的产物清单都需要同步更新。 | 无（PM 确认必须改） |
| Q10 | **是否需要 `.stark-repo-analyzer` 支持自定义目录名？** 用户可能想用别的名字。 | **建议通过 `--output` 参数支持**（已有），默认值改为 `.stark-repo-analyzer` 即可。用户想自定义时传 `--output my-dir`。 | 无（已有能力） |

---

## 7. 与既有规划的关系

### 7.1 与 `references/PLAN.md` 的关系

**不冲突。** PLAN.md 定义的是 8 阶段分析方法论（阶段零~七：克隆/压缩认知/切片/特征识别/外部调研/模块分析/交叉验证/融合报告）。本轮 12 项问题不改变方法论本身，只改工具的 UX/结构/可维护性：

- REQ-01（输出目录名）、REQ-06（目录结构）、REQ-07（日志）影响的是产物的**组织方式**，不影响分析流程。
- REQ-04（进度）、REQ-02（预检）影响的是**执行体验**，不影响分析流程。
- REQ-10（模块拆分）影响的是**代码组织**，不影响分析流程。
- REQ-05（agent 默认开启）改变的是默认参数，但 PLAN.md §12 的开关表中 `agent-mode` 本就是可配置项，改默认值不违反 PLAN。

### 7.2 与 `references/PRD_UNFINISHED_FEATURES.md` 的关系

**正交不冲突。** 那份 PRD 的 7 项（ask_user 适配器、repo-types.yaml、token 统计、外部调研、acceptance 高成本项、tree-sitter benchmark、JUDGE.md）是**功能补齐**，且已基本实现（代码中 `_LOADER`、`_ask_user`、`_TOKEN_COLLECTOR`、`--research`、acceptance 执行器等均已存在）。

本轮 12 项是**体验/结构重构**，两者维度不同：
- 那份 PRD 补的是"PLAN 承诺但未实现的功能"。
- 本 PRD 补的是"用户用了之后反馈的体验问题"。

唯一交叉点：REQ-03（LLM-judge 修复）涉及 `llm_judge.py`，而 `llm_judge.py` 是那份 PRD #5（acceptance 高成本项）的产物。但本次只修默认模型和诊断信息，不改变 LLM-judge 的架构。

### 7.3 与 `references/ARCH_UNFINISHED_FEATURES.md` 的关系

**自然延伸。** 那份架构文档已提出将部分逻辑提取为独立模块（`repo_types_loader.py`、`ask_user_adapters.py`、`token_reporter.py`、`render_report.py`、`llm_judge.py`），且已落地。本轮 REQ-10（模块拆分）是这一趋势的**进一步延伸**——把剩余在 `repo_analyzer.py` 中的 ~60 个函数也按职责拆出去。

### 7.4 与既有 ADR（0001~0015）的关系

**不回溯修改。** 既有 ADR 记录的是已确认决策。本轮若产生新的架构决策（如输出目录改名、agent 默认开启、目录结构重组、模块拆分方案），建议新增 ADR-0016~0019 记录，而非修改旧 ADR。

特别注意：
- ADR-0008（开关分类）将 `agent-mode` 归为"5 真开关"之一——改默认值不违反 ADR-0008 的分类，只是改了默认值。
- ADR-0014（tree-sitter chunked）不受影响——本轮不改 tree-sitter 逻辑。

---

## 附录：12 项问题与需求项映射表

| 原问题 # | 问题摘要 | 对应需求项 | 优先级 |
|----------|---------|-----------|--------|
| 1 | 产物目录改为 `.stark-repo-analyzer` + gitignore 提醒 | REQ-01 | P0 |
| 2 | 执行前运行时预检 | REQ-02 | P0 |
| 3 | LLM-judge 默认模型不可用修复 | REQ-03 | P0 |
| 4 | 执行进度实时反馈 | REQ-04 | P0 |
| 5 | Agent 模式默认开启 | REQ-05 | P0 |
| 6 | 产物输出太混乱，重新梳理目录结构 | REQ-06 | P0 |
| 7 | 任务运行日志目录 | REQ-07 | P1 |
| 8 | 人类阅读的分析结果产物目录 | REQ-06（合并） | P0 |
| 9 | AI agents 阅读的分析结果产物目录 | REQ-06（合并） | P0 |
| 10 | PERFORMANCE_REPORT 定位澄清 | REQ-08 | P1 |
| 11 | 5KB 名片改 10KB | REQ-09 | P1 |
| 12 | repo_analyzer.py 拆分多个模块 | REQ-10 | P1 |
