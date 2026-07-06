# ADR-0006 阶段七"diff-as-input"不可重放 → 模板分离策略

## Status

Proposed (Round 2)

## Context

PLAN.md §7.3 阶段七"多源融合 → 最终报告"描述:
1. 输入:`analysis/drafts/06-module-*.md` × N(`N` 个 module drafts)
2. 还有一个隐含的`7-summary` 草稿
3. 输出:`ANALYSIS_REPORT.md` + `analysis/README.md`

**问题 1 — 阶段七是一次性的**:阶段七把 6 个 module.md 合并到 1 个 ANALYSIS_REPORT.md 时,**文档结构、章节标题、过渡句、表格顺序都被并入这一次合并**。后续若改报告模板(比如"想给客户看 vs 想给团队看"两个版本),无法重渲染。

**问题 2 — diff 不是真正的 diff**:阶段五写 `06-module-*.md`,每次都覆盖;没有"v1 vs v2"的版本差异。`7-summary` 接收的所谓"diff"实际上是"6 份独立文件",**不是 git diff**。

**问题 3 — 模板改一改,一切重来**:阶段七的合并逻辑、风格(语气 / 句式 / 引用风格 / wikilink 渲染)和内容混在一起。

## Decision (提议)

**Jinja2/Mustache 模板分离 + 数据层与视图层分离**:

1. **数据层**:`analysis/drafts/06-module-*.md` + `03-question-answers.md` + `08-coverage.md` + `09-tier-map.yaml`。这些**永远不改结构**,只改内容。

2. **视图层**:`analysis/templates/ANALYSIS_REPORT.tmpl.md` + 多个变体:
   - `ANALYSIS_REPORT.tech-lead.tmpl.md`
   - `ANALYSIS_REPORT.business.tmpl.md`
   - `ANALYSIS_REPORT.learning.tmpl.md`

3. **渲染器**(新增):`render_report.py`(或主 agent 内的一个步骤)用模板 + 数据 → 报告。

4. **§9.1 报告骨架 8 章从"在文档里"改为"在 templates/ 里"**。阶段七只负责 render,不负责内容创作。

5. **多模板并行渲染**成为默认:阶段七一次性产出 3 个变体报告放 `analysis/ANALYSIS_REPORT.*.md`,用户选一个。

## Alternatives Considered

- **F1. 单模板一次性合并**:简单,没有灵活性。
- **F2. 模板分离(本 ADR)** :增加一个 renderer 步骤,但可重放、可多版本。
- **F3. 引入外部工具 mkdocs/pandoc**:把报告当文档站点渲染,过度工程。

## Consequences

- 阶段七从 ~3 个 sub-agent 减少到 0~1 个 sub-agent(渲染是 deterministic)。
- 增加 ~50 行的模板化工程;`templates/` 目录引入 versioning(模板与 skill 版本绑定)。
- 阶段七输出 `ANALYSIS_REPORT.*.md` × N,N≥1。
- 用户切换受众(tech-lead / business / learning)不需要重跑阶段五,只需 `render_report.py --template tech-lead`。

## Open Questions

- [ ] 模板里如果包含 LLM 生成的"过渡句"怎么办?(过渡句无法模板化)→ 可能的方案:阶段七保留 1 个 sub-agent 只生成过渡,模板中留 `{{ transition_block }}` 占位。
- [ ] wikilink 渲染:模板层用 Obsidian-style `[[Title]]` 还是 Markdown `[Title](Title.md)`?Wikilink 在 GitHub / 微信公众号 / Notion 渲染不一致。

## Linked

- Q6(Round 2 第六问)
- 阶段七 §9
- 阶段八 §8
- 验收 §10
