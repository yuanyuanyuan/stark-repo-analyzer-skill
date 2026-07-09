# 用户痛点分析 + 对抗性 Review：stark-repo-analyzer 是否真的解决痛点

> 审查日期：2026-07-09
> 方法：只读源码 + 配置核实（基于 `scripts/`、`config/`、`templates/`、`SKILL.md`、`references/ELEVATOR_PITCH.md`、`references/PRD_UNFINISHED_FEATURES.md`）
> 结论：**方向对、兑现打折**。三大卖点里只有"动态切片降维"扎实兑现；"覆盖率硬门控"度量信噪比低；"多受众报告"默认路径下链接全断、深度依赖外部 codex。

---

## 一、这个仓库是什么

`stark-repo-analyzer` 是一个"仓库分析底料"流程 skill：输入一个 git/GitHub 仓库，确定性脚本先做扫描/切片/模块候选/覆盖率门控，再（可选）让 agent 补主观判断，最终产出多份可复查的 Markdown 报告 + 验收脚本。

它的直接竞品/对标对象在 `references/ELEVATOR_PITCH.md` 里写得很清楚：**yzddmr6/repo-analyzer**——把仓库压成一份 AI 摘要，一步到位、快、便宜、但粗。

---

## 二、声称解决的 3 大用户痛点

来自 `ELEVATOR_PITCH.md` 与 `SKILL.md`：

| 痛点 | yzddmr6 的现状（被攻击点） |
|---|---|
| **P1 工序空跑** | 固定 8/12 道工序在非 Web 仓库下空跑，浪费算力与时间 |
| **P2 模型自评** | 模块覆盖率全靠模型自评，不可信、不可复查 |
| **P3 单报告不通吃** | 一份报告给老板看不下去、给学习者看不懂改不动 |

对应解法（卖点）：

- **S1 动态切片**：先识别仓库类型，再选 5~7 道工序（而非硬套 12 维），`config/repo-types.yaml` 驱动。
- **S2 覆盖率硬门控**：`tree-sitter` + `grep` 算**符号级覆盖率**，核心模块硬性 ≥80%、次要 ≥20%，"不再让 LLM 自我报告"。
- **S3 多受众 + 可重放**：一次产 3 份按受众重写的报告（tech-lead / business / learning），模板与数据分离，换受众不重跑。

---

## 三、对抗性 Review：是否真的解决

### 痛点 P1（工序空跑）→ S1 动态切片

**证据（已核实）**
- `config/repo-types.yaml` 确实存在 6 类 repo + fallback，`RepoTypeLoader.load(type)` 按类型返回不同维度：`web-fullstack` 7 维、`single-lang-CLI` 6 维、`single-lang-lib`/`multi-agent-config`/`monorepo`/`embedded-kernel` 各 5 维、未知类型回退 `fallback` 12 维。
- `analyzer_slicing.write_slices()` 调用 `_LOADER.load(repo_type)` 后逐维度跑 repomix。

**判定：部分解决（真实降维，但"绝不空跑"是夸大）**

对抗反驳：
1. **"绝不空跑"不成立**。维度数量减少 ≠ 切片非空。每个维度仍按 `patterns` 跑 repomix；若仓库没有测试/示例/数据库，`06-tests.xml` / `10-examples.xml` / `03-database.xml` 仍会产出**空 XML**。空跑从"12 维"降为"少数维度"，并未消除。
2. **类型识别是单点故障，且未被验收覆盖**。`write_slices` 完全信任 `repo_type`；若类型识别错（如把 monorepo 误判成 single-lang-lib），维度选择就错，反而漏掉关键维度。`acceptance/check.sh` 不校验 `repo-type` 与仓库实际结构是否一致。
3. **`version` 绑定是硬编码而非自动同步**。`RepoTypeLoader.VERSION_BIND = 1` 写死，而 `SKILL.md` 已到 `version: 0.2.0`、yaml 写 `version: 1`。当前不触发，但 SKILL 升到 0.3.0 时 loader 仍期望 1，存在静默漂移隐患（与文档"version 与 SKILL.md 绑定"的描述不符）。

---

### 痛点 P2（模型自评）→ S2 覆盖率硬门控

**证据（已核实）**
- `analyzer_coverage.symbol_coverage()`：`expected` = 从源码提取的符号（tree-sitter `auto` 或 regex）；`covered` = 符号名在模块草稿文本中 `\b<name>\b` 出现；`ratio = covered/expected`；`core(前3模块)≥0.8`、`minor≥0.2` 才 PASS。默认 `coverage_engine="auto"`。
- 阈值默认 `target_coverage_core=0.8`、`target_coverage_minor=0.2`（与卖点一致）。

**判定：形式上解决（确定性、不靠 LLM 自报），但度量的是"名字出现"而非"被真正分析"**

对抗反驳：
1. **门控信号弱：名字出现即算覆盖**。草稿只要把符号名列一遍（例如 `关键符号：foo, bar, baz`）就能 100% 通过，无需任何分析。门控只挡得住"完全空白的草稿"，挡不住"只列名字不分析的浅草稿"。这与卖点"确保模块被真正分析"之间存在实质 gap——把"模型自夸"换成了"名字出现即算数"，并没有证明分析质量。
2. **core/minor 的"核心"定义不可靠**。`tier = "core" if index <= 3`，而 `module_rows()` 按顶层目录**文件数**排序。一个 3 行的顶层目录若排前三就被要求 ≥80%；真正核心的第 4 个模块只需 ≥20%。"核心模块硬性 ≥80%"的"核心"是文件数代理，不是重要性。
3. **越冷门的语言越容易满分**。`source_symbols`（regex 兜底）只覆盖 JS/TS/Python 的函数与 class；Go/Rust/Java 等若 tree-sitter 不可用或无对应 query，符号提取退化为有限正则 → 期望集偏小 → 分母小 → 容易凑出高覆盖率。即：覆盖率门控对"主流语言更严、冷门语言更松"，与"质量门禁"的直觉相反。

---

### 痛点 P3（单报告不通吃）→ S3 多受众 + 可重放

**证据（已核实）**
- 4 个模板（`ANALYSIS_REPORT.{tech-lead,business,learning,overview}.tmpl.md`）章节结构**确实不同**：business 讲用户价值/采用成本/业务风险，learning 讲心智模型/阅读顺序/练习题，tech-lead 讲架构全景/模块/依赖。
- `report_data()` 注入受众专属变量 + `agent_insights()` 的 agent 结论。
- 代码实际产出路径（`analyzer_metadata/analyzer_modules/analyzer_coverage/analyzer_slicing`）：`data/manifest-card.md`、`data/module-ids.yaml`、`diagnostics/module-drafts/module-*.md`、`data/coverage.md`、`diagnostics/slices/...`。

**判定：半成品（结构真分化、链接全断裂、深度靠 codex）**

对抗反驳：
1. **致命：4 个模板引用的全是重构前旧路径**。`T01-T12` 重构已把产物迁到 `data/`、`diagnostics/slices/`、`diagnostics/module-drafts/` 并去掉编号前缀，但模板仍写：
   - `02a-manifest-card.md`（实为 `data/manifest-card.md`）
   - `05-module-ids.yaml`（实为 `data/module-ids.yaml`）
   - `drafts/06-module-*.md`（实为 `diagnostics/module-drafts/module-*.md`）
   - `08-coverage.md`（实为 `data/coverage.md`）
   - `slices/04-docs.xml`（实为 `diagnostics/slices/04-docs.xml`）
   - `--output analysis`（实为 `--output .stark-repo-analyzer`）
   → **渲染出的 4 份报告里每一条内部交叉链接都指向不存在的文件**。这直接击穿核心卖点"证据可追到文件与行号 / 可重放可复查"。
2. **根因：验收不查内部链接**。`acceptance/04-link.sh` 只校验**外链(http)** 与 github commit 引用；`05-mermaid-judge.sh` / `llm-judge.sh` 也不校验报告内相对路径。所以陈旧模板能溜过 245 项验收——这正是文档自己说的"245+ 验收是安全网"的盲点。
3. **深度差异化在确定性模式下塌缩**。`analyzer_agent.agent_insights()` 在 `mode == "deterministic"`（或 codex 不可用降级）时 `enabled=False`，返回 `business_markdown=""`、`learning_markdown=""`、`summary_markdown=""`。即默认若 codex 不可用（且 codex 对抗审查发现降级只覆盖"二进制不存在"，auth/模型错误不降级），三份报告里所有受众专属段全空，退化为同一套确定性数据（readme_points / tool_lines / commands / module_table / symbols）只换了章节标题和几句引导语。本机当前 codex 未接通，实际跑出来就是塌缩版。
4. **死代码/双路径**。`analyzer_reports.report_body()` 与 `overview_report_body()` 是手写多受众生成器，但 `write_reports()` 实际走 `report_data()` + `render_report.py` 模板——这两个函数已不被调用（仅 `.pyc` 残留引用）。两套并行生成路径 = 维护隐患，且存在"测试验错路径"的风险。

---

## 四、综合判定

| 痛点 | 声称解法 | 是否真解决 | 关键依据 |
|---|---|---|---|
| P1 工序空跑 | 动态切片降维 | **部分解决** | 维度确实从 12 降到 5~7；但空切片未消除、类型识别正确性无验收 |
| P2 模型自评 | 符号级覆盖率硬门控 | **形式上解决 / 实质上未解决** | 确定性门控真实存在，但度量是"名字出现"，core 判定用文件数代理，冷门语言易满分 |
| P3 单报告不通吃 | 3 份受众报告 + 可重放 | **半成品** | 章节结构真分化；但模板链接全断、深度依赖外部 codex、确定性模式塌缩、存在死代码 |

一句话结论：工程化/可复现/防 LLM 瞎编的"底料"层方向是对的，但用户最在意的"真的能解决痛点"目前是 **方向对、兑现打折**——只有"动态切片降维"是扎实兑现的。

---

## 五、若要真正闭环，建议优先级

1. **P0 修模板链接（直接击穿卖点）**：把 4 个模板路径对齐到 `data/`、`diagnostics/slices/`、`diagnostics/module-drafts/`，去掉编号前缀；并加一条 `acceptance` 断言校验报告内相对链接存在（防再次漂移）。
2. **P1 强化覆盖率门控**：把"名字出现"升级为"名字 + 上下文/定义/调用出现"或抽样 LLM 复核；`core` 判定改为显式重要度（而非文件数排序）；对 tree-sitter 不支持的语言明确标注覆盖率置信度。
3. **P1 受众差异化兜底**：确定性模式下也应注入基于确定性数据的受众专属结论（如 business 报告直接从 manifest/工具数推导采用成本），而不是留空等 codex。
4. **P2 类型识别加验收**：assert `repo-type` 与仓库实际结构一致（如 monorepo 应含多个 `package.json`），避免错误类型导致维度选错。
5. **P2 清理死代码**：删除 `report_body()` / `overview_report_body()`，统一到 `report_data()` + 模板单路径，避免双实现漂移。

---

## 附：已核实的事实索引

- `config/repo-types.yaml` 维度分布（Loader 实跑）：web-fullstack 7 / single-lang-CLI 6 / 其余 5 / fallback 12
- `analyzer_coverage.symbol_coverage()`：`covered` 用 `\b<name>\b` 在草稿文本匹配；`tier` 由 `module_rows` 排序 index<=3 决定
- `analyzer_config.py:222-223`：core=0.8、minor=0.2 默认值
- 模板旧路径：`02a-manifest-card.md` / `05-module-ids.yaml` / `drafts/06-module-*.md` / `08-coverage.md` / `slices/*.xml` / `--output analysis`
- `analyzer_agent.agent_insights()`：deterministic 模式返回 `business_markdown=""` `learning_markdown=""` `summary_markdown=""`
- `acceptance/04-link.sh`：仅校验外链(http) 与 github commit，不校验内部相对链接
- `RepoTypeLoader.VERSION_BIND = 1`（硬编码，非从 SKILL.md 0.2.0 自动读取）
