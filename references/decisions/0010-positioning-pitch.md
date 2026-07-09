---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q10)
---

# ADR-0010 三角度融合 elevator pitch：相比 yzddmr6/repo-analyzer 的差异化定位

## Context

PLAN.md 开篇「参考：yzddmr6/repo-analyzer」—— yzddmr6 那份是**1 步 repomix 压缩 + 1 步 LLM** 的简单方案。

用户问：「为什么不直接用 yzddmr6，这个 skill 多做的是什么？」

需要一句话 elevator pitch 答复对外（README、Twitter、Slack 推广）。

候选角度：

- **A 深 vs 浅**——yzddmr6 是 PPT 摘要；我这个是 12 道工序深挖、带覆盖率门控的尽调报告
- **B 单 vs 多受众**——yzddmr6 一份通用报告；我这个一次产 3 份（tech / business / learning）
- **C 黑盒 vs 白盒**——yzddmr6 是黑盒跑完得结果；我这个每一步产物可查、可重放、可调模板

## Decision

**三角度融合的对外稿件**：

> **和 yzddmr6 那份压缩摘要不同——`repo-analyzer` 给的是 *12 道工序深挖的尽调底料*：**
>
> 1. 先扫描仓库类型（web 全栈 / CLI / 库 / monorepo / 嵌入式 / 多 agent 配置）**动态切片**，避免 12 维硬套带来的 8 道空工序；
> 2. 再用 `tree-sitter` 解析代码 + `grep` 抓 draft，跑**符号级覆盖率门控**，核心模块硬性 ≥ 80%、次要 ≥ 20%，**不再让 LLM 自我报告**；
> 3. 阶段五并行模块分析、阶段六独立 cross-ref 审稿，确保术语表 / wikilink / 模块引用跨章节一致；
> 4. **一次性产 3 份报告**——`tech-lead` 看架构、`business` 看价值、`learning` 看重现路径，每一份都按受众重写章节；
> 5. 所有中间产物按 **模板与数据分离**存放：模板在 `templates/`，数据在 `analysis/drafts/`；改模板不动数据，**可重放**、可换受众渲染；
> 6. 30 分钟 / 500K token / 3 次失败重试的 **激进 SLA 预算** 让快速试错可行，超预算后输出 `STATE_REPORT.md` 让用户手动接力。

## 三角度关联

- **A 深 vs 浅** → 角度 1 + 角度 2（动态切片 + 覆盖率门控）
- **B 单 vs 多受众** → 角度 4（三变体同时产）
- **C 黑盒 vs 白盒** → 角度 3（独立 cross-ref）+ 角度 5（模板/数据分离）

## 备选短版本（< 30 字，用于 Twitter / Slack）

> yzddmr6 是摘要；`repo-analyzer` 是 12 道工序深挖 + 跨受众 3 份报告 + 可重放的尽调底料。

## 备选长版本（≥ 200 字，用于 README）

> yzddmr6/repo-analyzer 把仓库压成一份 AI 摘要，一步到位——快、便宜、但粗：8 道工序在非 Web 仓库下空跑，模块覆盖全靠模型自评，单份报告给老板看不下去给学习者看不懂改不动。
>
> `repo-analyzer` 在 yzddmr6 之上加了 3 件事：(1) 动态切片——先识别仓库类型再选 12 道 / 7 道工序，绝不空跑；(2) 硬门控——`tree-sitter` + `grep` 算符号级覆盖率，模型不准自评；(3) 多受众 + 可重放——一次产 3 份按受众重写的报告，模板与数据分离，换受众不重跑。
>
> 加起来总成本 30 分钟 / 500K token / 3 次重试，激进 SLA 让快速试错友好；超预算时输出 STATE_REPORT.md 让用户手动接力。

## Alternatives

- **J1. 单角度 A**——只讲深度，遗漏多受众优势。
- **J2. 单角度 B**——只讲多受众，遗漏动态切片。
- **J3. 单角度 C**——只讲可重放，遗漏深度优势。
- **J4. 三角度融合（本 ADR）**——30 字短 / 100 字中 / 200 字长 3 档稿件齐备。

## Consequences

- 工具 README.md 顶部用「中版本」（约 100 字）。
- Twitter / Slack 推广用「短版本」（< 30 字）。
- 给潜在企业客户的 deck 用「长版本」（≥ 200 字）。
- §0 TL;DR 模板与 `../ELEVATOR_PITCH.md` 长版本互相对齐。
- 后续若加入新功能（如 monorepo 感知）,需要更新短版本（增字 / 删字）。

## Open Questions

- [ ] pitch 主语用第一人称（「我做的是...」）还是工具名（「`repo-analyzer` 是...」）？前者更有温度、后者更适合营销文案。
- [ ] 是否要在 pitch 中显式提「yzddmr6」做对比？避免无意中贬低同行的同时让对比鲜明。
- [ ] 「`tree-sitter`」这种技术词是否需要括号解释？目标读者画像未明。

## Linked

- ADR-0001（角度 1 + 角度 2 落地的两个支撑）
- ADR-0004（角度 3 cross-ref 落地）
- ADR-0006（角度 4 三变体落地）
- ADR-0007（角度 6 SLA 落地）
- `../ELEVATOR_PITCH.md`（独立文件存放最终定稿）
