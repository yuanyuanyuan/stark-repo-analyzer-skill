# Graph Report - analysis  (2026-07-06)

## Corpus Check
- 15 files · ~8,618 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 200 nodes · 185 edges · 20 communities (18 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a461274`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]

## God Nodes (most connected - your core abstractions)
1. `video-use 仓库分析方案 v2（基于 repomix + repo-analyzer 框架）` - 16 edges
2. `Glossary — `repo-analyzer` skill` - 14 edges
3. `ADR-0010 三角度融合 elevator pitch：相比 yzddmr6/repo-analyzer 的差异化定位` - 10 edges
4. `Decision` - 8 edges
5. `ADR-0001 砍掉阶段一压缩 repomix，改在 Phase-2a 顺手产 5KB 名片` - 7 edges
6. `ADR-0002 Phase-2a：先识别仓库类型，再动态生成切片清单` - 7 edges
7. `ADR-0003 Skill 内 `ask_user()` 抽象 + 运行时适配器` - 7 edges
8. `ADR-0004 阶段五内自检 + 阶段六独立 cross-ref 双层质检` - 7 edges
9. `ADR-0005 覆盖率门控 = `tree-sitter` API 名 + `grep` draft 符号名 交集比` - 7 edges
10. `ADR-0006 三受众模板 + 数据层 / 视图层分离` - 7 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (20 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (34): A, Adapter, Adaptive Slicing（自适应切片）, Audience Template（受众模板）, B, Backward-Compatible Selector, C, Coverage Gate（覆盖率门控） (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (27): 0. 环境与目录约定, 10. 验收标准（核心 80% / 次要 20% 模式）, 11. 完整执行顺序, 12. 开关与默认值, 13. 反馈记录（供未来复用）, 1. 阶段零：克隆 + 元数据采集, 4.1 识别项, 4.2 自适应提问（AskUserQuestion） (+19 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (14): ADR-0009 风险登记表：R1~R6 + 预算耗尽兜底, Alternatives, Consequences, Context, Decision, Linked, Open Questions, R1 — Token 爆炸 (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (11): 5 个「内部变量」（写到 `~/.config/repo-analyzer/defaults.yaml`）, 5 个「真开关」（透传 runtime argv）, ADR-0008 阶段十二开关分类：5 真开关（透传运行时）+ 5 内部变量（读 `defaults.yaml`）, Alternatives, Consequences, Context, Decision, Linked (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (12): 2.1.1 机制：repomix `--compress` 内部做了什么, 2.1.2 原理：为什么"宏观认知建模"能成立, 2.1.3 与 overview.md 14 项的对应关系, 2.1.4 失效边界：什么场景下压缩机制不够用, 2.1 宏观认知建模的机制与原理, 2.2.1 分组策略（按"信息源"切，不是按"项号"切）, 2.2.2 Subagent Prompt 模板, 2.2.3 执行流程 (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (10): ADR-0010 三角度融合 elevator pitch：相比 yzddmr6/repo-analyzer 的差异化定位, Alternatives, Consequences, Context, Decision, Linked, Open Questions, 三角度关联 (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (7): ADR-0001 砍掉阶段一压缩 repomix，改在 Phase-2a 顺手产 5KB 名片, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (7): ADR-0002 Phase-2a：先识别仓库类型，再动态生成切片清单, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 8 - "Community 8"
Cohesion: 0.25
Nodes (7): ADR-0003 Skill 内 `ask_user()` 抽象 + 运行时适配器, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 9 - "Community 9"
Cohesion: 0.25
Nodes (7): ADR-0004 阶段五内自检 + 阶段六独立 cross-ref 双层质检, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): ADR-0005 覆盖率门控 = `tree-sitter` API 名 + `grep` draft 符号名 交集比, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 11 - "Community 11"
Cohesion: 0.25
Nodes (7): ADR-0006 三受众模板 + 数据层 / 视图层分离, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 12 - "Community 12"
Cohesion: 0.25
Nodes (7): ADR-0007 激进 SLA 预算：30 分钟 / 500K tokens / 3 次失败回退, Alternatives, Consequences, Context, Decision, Linked, Open Questions

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (6): Elevator Pitch — `repo-analyzer` skill, 三档稿件 vs ADR 关联, 中版本（~100 字 · 用于 README 顶部 / GitHub repo description）, 套用规约, 短版本（< 30 字 · 用于 Twitter / Slack / 朋友圈）, 长版本（≥ 200 字 · 用于企业 deck / 公众号 / 知乎 / 推广文）

### Community 14 - "Community 14"
Cohesion: 0.40
Nodes (5): R, Repo Type Tagger, Repo-Types YAML, Resume Token, Round（grilling 轮次）

### Community 15 - "Community 15"
Cohesion: 0.40
Nodes (5): S, SLA Budget（SLA 预算）, STATE_REPORT.md, Storyline Module, Sub-agent Mode

### Community 16 - "Community 16"
Cohesion: 0.40
Nodes (5): 14.1 R4 全部决策一览（10/10 完成）, 14.2 修订后流程变化摘要, 14.3 配套产物索引, 14.4 仍开放问题（建议 Round 5 主题）, 14. R4 grilling 决策修订记录（2026-07-06）

### Community 17 - "Community 17"
Cohesion: 0.40
Nodes (5): 3.0 共享资源, 3.1 切片清单, 3.2 维度 12 的 git log 聚合脚本, 3.3 并行调度, 3. 阶段二：12 维精细切片（不压缩 + XML，**并行执行**）

## Knowledge Gaps
- **147 isolated node(s):** `graphify`, `graphify`, `短版本（< 30 字 · 用于 Twitter / Slack / 朋友圈）`, `中版本（~100 字 · 用于 README 顶部 / GitHub repo description）`, `长版本（≥ 200 字 · 用于企业 deck / 公众号 / 知乎 / 推广文）` (+142 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `video-use 仓库分析方案 v2（基于 repomix + repo-analyzer 框架）` connect `Community 1` to `Community 16`, `Community 17`, `Community 4`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `Glossary — `repo-analyzer` skill` connect `Community 0` to `Community 14`, `Community 15`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `2. 阶段一：宏观认知建模（压缩 repomix）` connect `Community 4` to `Community 1`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **What connects `graphify`, `graphify`, `短版本（< 30 字 · 用于 Twitter / Slack / 朋友圈）` to the rest of the system?**
  _147 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._