---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q6)
---

# ADR-0006 三受众模板 + 数据层 / 视图层分离

## Context

PLAN.md §7.3「阶段七：多源融合 → 最终报告」流程：

1. 输入：`analysis/drafts/06-module-*.md` × N 个 module drafts + 隐含的 `7-summary` 草稿
2. 输出：`ANALYSIS_REPORT.md` + `analysis/README.md`

**问题**：

1. **一次性的合并**：阶段七把 N 个 module.md 合并到 1 个 `ANALYSIS_REPORT.md` 时，文档结构、章节标题、过渡句、表格顺序都被并入这一次合并——**不可逆**。
2. **没有真的 diff**：`7-summary` 接收的所谓「diff」实际是「N 份独立 file」，不是 `git diff`。
3. **模板改一改，从头来**：阶段七的合并逻辑、风格、内容耦合在一起，改一个章节要回到阶段五重跑。

而且同一个报告，给三个受众（`tech-lead` / `business` / `learning`）看效果差异巨大——同一份报告，老板看不懂版本依赖；学习者不需要安全态势。

## Decision

**Jinja2/Mustache 模板分离 + 数据层 / 视图层分离 + 三受众默认渲染**：

1. **数据层**（永不重写结构）：
   - `analysis/drafts/06-module-<id>.md` × N（阶段五产出）
   - `analysis/03-question-answers.md`（阶段三产出）
   - `analysis/08-coverage.md` + `analysis/08-coverage-failure.md`（阶段六产出）
   - `analysis/05-module-ids.yaml`（ADR-0004）
   - `analysis/02a-repo-type.yaml`（ADR-0002）

2. **视图层**（3 个变体模板）：
   - `templates/ANALYSIS_REPORT.tech-lead.tmpl.md`
   - `templates/ANALYSIS_REPORT.business.tmpl.md`
   - `templates/ANALYSIS_REPORT.learning.tmpl.md`

3. **三受众默认章节侧重**：

| 章节 | tech-lead | business | learning |
|------|-----------|----------|----------|
| §0 TL;DR | 主架构一句话 + 子模块计数 | 业务成果 / ROI + 团队规模 | 5 秒项目直觉 + 学习曲线 |
| §1 场景化问题引入 | 架构痛点 | 用户场景 | 我能用它做什么 |
| §2 架构全景 | 系统图 + 拓扑 | 关键流程图 | 项目动机 |
| §3 核心模块详解 | 重点 3-5 模块 | 重点 1-2 业务模块 | 入口 + 怎么跑通 |
| §4 第三方依赖与版本基线 | 完整版本号 | **省略** | 关键依赖简介 |
| §5 工程成熟度 | 全套指标 | **省略** | 测试覆盖 / 文档 |
| §6 架构评价 | 技术债 / 风险 | **省略** | 学习陷阱 |
| §7 复现方法 | 从零搭建步骤 | 部署注意事项 | 跟我做一遍 |

4. **共享章节**（3 个模板都包含）：
   - §0 TL;DR
   - §8 附录：模块索引（`05-module-ids.yaml`）+ 类型 tag（`02a-repo-type.yaml`）
   - 元信息：日期 / 仓库版本 / commit ref / 跑时 SLA 报告

5. **渲染器**（新增）：
   - `render_report.py --template tech-lead|business|learning --data analysis/`（或主 agent 内的一个步骤）
   - 默认一次渲染 3 个变体，输出 `analysis/ANALYSIS_REPORT.{tech-lead|business|learning}.md`
   - 渲染时若模板中出现 `{{ transition_block }}` 占位，由 1 个阶段七 sub-agent（按受众选模型）填过渡句，模板与渲染解耦

6. **去模板化触发**：用户 `--template all` 或不指定参数时，自动渲染全部 3 个变体。

## Alternatives

- **F1. 单模板一次性合并**——简单，没灵活性。
- **F2. 三变体模板 + 数据/视图层分离（本 ADR）**——增加 renderer 步骤，但可重放、多版本。
- **F3. mkdocs / pandoc 外部工具**——把报告当文档站点渲染，过度工程。

## Consequences

- 阶段七从 ~3 个 sub-agent 减少到 0~1 个 sub-agent（渲染 deterministic）。
- 新增 `templates/` 目录，3 个 `.tmpl.md` 文件外加 `render_report.py` 约 50 行。
- `templates/` 引入 versioning：模板与 skill 版本绑定，skill 升级时模板同步升级。
- 阶段七输出 `ANALYSIS_REPORT.*.md` × 3（N≥1）。
- 用户切换受众（`--template business`）不需要重跑阶段五，只调 renderer。
- 阶段八 §8 「README 索引」改为 `analysis/README.md` 列出 3 份变体的入口与摘要表。

## Open Questions

- [ ] wikilink 渲染：模板层用 Obsidian-style `[[Title]]` 还是 Markdown `[Title](Title.md)`？Wikilink 在 GitHub / 微信公众号 / Notion 渲染不一致——需选主战场（默认 GitHub？还是 Obsidian？）
- [ ] `{{ transition_block }}` 占位是否需要每个模板 1 次，由 1 个 sub-agent 填？还是全文模板共用 1 次填？
- [ ] renderer 是个真 Python 脚本，还是用 Jinja2 类模板还是 Mustache/Markdown 用占位字符串拼接？

## Linked

- ADR-0002（按类型选 dim 章节）
- ADR-0003（受众来自 `03-question-answers.md` Q2）
- 阶段七 §9 / 阶段八 §8
