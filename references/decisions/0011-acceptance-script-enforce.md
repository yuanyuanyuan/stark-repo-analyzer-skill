---
Status: Accepted
Date: 2026-07-06
Round: 5 (R5-Q1)
---

# ADR-0011 阶段十 §10 验收全 13 条硬断言（含 8 条 LLM-judge）

## Context

PLAN.md §10 列了 13 条验收目标，大多是"软目标"而非"硬断言"：

- 跨章术语一致
- 模块覆盖度
- 引用链可点
- 没有夸大
- 内容准确度
- 受众匹配度
- 等等

这些老板看一眼点头，但**电脑没法跑这套清单**。R5-Q1 任务：把这 13 条至少 5 条改成"脚本可断言"。用户选了 **B 全 13 条硬断言**，包括 8 条主观条改用 LLM-judge。

## Decision

**全 13 条硬断言，分为 5 类执行器**：

### A. `grep` 文本断言（3 条）

| # | 验收条目 | 脚本 |
|---|---------|------|
| 1 | wikilink 引用链可点 | `grep -hoE '\[\[module_[0-9]+\]\]' analysis/ \| sort -u` vs `05-module-ids.yaml` 列表 |
| 2 | 无断裂 `[[xxx]]` 引用 | `grep -hoE '\[\[.+\]\]' drafts/ \| sort -u` vs `05-module-ids.yaml` ∪ glossary |
| 3 | Markdown 内部 anchor 全部 `#xxx` 真实存在 | `grep -hoE '\(#[^)]+\)' analysis/*.md` vs Markdown heading 列表 |

### B. AST 解析断言（2 条）

| # | 验收条目 | 脚本 |
|---|---------|------|
| 4 | 跨章术语一致 | tree-sitter 解析 draft 抽出名词短语集合，三个变体取交集 ≥ 90% |
| 5 | 没有夸大（关键 API 数量匹配） | draft 中提到的 API 数量 vs tree-sitter 导出的数量，差 ≤ 5% |

### C. JSON Schema 断言（2 条）

| # | 验收条目 | 脚本 |
|---|---------|------|
| 6 | 模块清单完整 | `05-module-ids.yaml` 用 `jsonschema` 校验（id 唯一 + 必含字段 tier / storyline_position） |
| 7 | 风险表完整 | `08-coverage.md` + `08-coverage-failure.md` schema 校验（reasons[] / modules[] 必填） |

### D. 外部 link check（2 条）

| # | 验收条目 | 脚本 |
|---|---------|------|
| 8 | 参考资料真实可达 | `curl -I -L --max-time 10` 检查所有 `[xxx](url)` 200 + 非 5xx |
| 9 | GitHub commit 引用真实存在 | `gh api repos/{owner}/{repo}/commits/{sha}` 200 |

### E. Mermaid 渲染 + LLM-judge（4 条）

| # | 验收条目 | 脚本 |
|---|---------|------|
| 10 | Mermaid 全景图存在且无语法错 | `mermaid-cli` 渲染，失败 throw |
| 11 | 内容准确度（LLM-judge） | 第二 LLM（haiku）读 draft 后打 0-10 分，阈值 ≥ 7 |
| 12 | 受众匹配度（LLM-judge） | 第二 LLM 按受众 prompt（"若你是 tech-lead，这章讲清楚了吗？"） |
| 13 | 受众区分度（LLM-judge） | 三变体两两对比 Jaccard 距离 ≥ 0.30 |

### 集成位置

```bash
# 阶段十 §10 验收脚本入口
analysis/acceptance/check.sh
├── 01-grep.sh          # A 类
├── 02-ast.sh           # B 类
├── 03-schema.sh        # C 类
├── 04-link.sh          # D 类
└── 05-mermaid-judge.sh # E 类
```

每个子脚本独立输出 `PASS|FAIL|<details>`，主入口汇总 ≥ 80% PASS 才算通过。

## Alternatives

- **B1. 至少 5 条硬断言**（grep + AST + schema + link + mermaid）—— 200 行 Python。
- **B2. 全 13 条硬断言（本 ADR）** —— 约 500 行 Python + 8 个 LLM-judge 调用 ≈ 20 万 token 预算。
- **B3. 仅 3 条关键断言** —— grep + schema + link check。

## Consequences

- 阶段十 §10 验收从主观题全变客观题。
- 单次验收新增约 20 万 token（8 条 LLM-judge）+ 2-3 秒 grep + AST + schema + link + mermaid。
- 需新增 `analysis/acceptance/` 目录（5 个 .sh + 1 个 check.sh 入口 + 1 个 configs/schema.yaml）。
- ADR-0007 SLA 预算收紧：原 30 分钟 / 500K token 中，token 预算可能被验收吃掉 4%；需要在 SLA 计算时 `-4%` 留给验收。
- §10 验收清单 13 条全部从【目标】变成【断言通过条件】，书写格式变为 YAML。

## Open Questions

- [ ] LLM-judge 用 haiku-4.5 还是 sonnet-4.6？精度 vs 成本的平衡。
- [ ] Mermaid 渲染失败时 throw，是否在 SKILL 失败 / 报警告？需要设计 fallback。
- [ ] Acceptance `01-grep.sh` 误报率高（重复 `[xxx]`、`! [xxx]()` 图片语法），需先清洗输入。

## Linked

- ADR-0004（wikilink ID Map 是 grep 断言的对照源）
- ADR-0005（tree-sitter 是 AST 断言的引擎）
- ADR-0007（SLA 预算需为验收让出 4%）
- 阶段十 §10
