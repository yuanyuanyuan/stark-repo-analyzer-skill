# ADR-0004 阶段五 sub-agent 上下文孤岛与叙事线漂移

## Status

Proposed (Round 2)

## Context

PLAN.md §6 阶段四"模块清单 + 叙事线",由一个独立 sub-agent 通过阶段三输出 + 阶段二 12 维切片推断出模块清单(预计 3~5 章叙事线)与每个模块的 tier(核心 / 重要 / 次要)。

§7 阶段五按模块清单**并行**起 N 个 sub-agent,每个 agent 独立输出 `analysis/drafts/06-module-XXX.md`。

**风险 1 — 模块清单的双源不一致**:
阶段三 §4"项目特征识别"也会推断模块(虽然不是为了 narrative),阶段四 §6 的"模块清单"独立做一次推断。两套独立推断可能给出不同的模块边界。

**风险 2 — 上下文孤岛**:
阶段五 sub-agent 只看到"自己的模块切片 + 自己模块的上下文",**看不到其他模块在写什么**。后果:
- 术语漂移:Agent A 写"前置条件",Agent B 写"输入参数"。
- 重复定义:两个 agent 都解释同一个工具函数。
- 引用断裂:Agent A 引用 `[[Agent B 模块名]]`,但 wikilink 字符串不一致。

**风险 3 — 叙事线无从校验**:
叙事线是阶段四的产物,阶段五 sub-agent **不感知**自己负责的模块在叙事线里属于哪章、按什么顺序出现。最终 ANALYSIS_REPORT 把 6 个 module.md 拼起来时,**叙事线被遗忘**。

## Decision (提议)

**1. 阶段三 = 项目特征识别(单一来源真相)**

阶段三输出 `analysis/03-repo-profile.md`,显式声明**模块候选清单**。阶段四不重新推断,只读取该清单并**做叙事线排序 + tier 分配**。模块边界先于叙事线确定。

**2. 阶段五 sub-agent 二次 cross-reference**

每个 module sub-agent 完成 draft 后:
- 阶段五内部增加 **lightweight pass-2**:sub-agent 读其他 module 的 draft,扫一遍"术语表 / wikilink",输出一份 `analysis/drafts/07-cross-ref-checks.md`,列出冲突项。
- 该 pass-2 是**自动化的、串行**的(顺序 fetch 所有 drafts 后,单 agent 综合)。

**3. 阶段五产物的 wikilink 命名空间**

所有 module drafts 必须使用 `[[module_<id>]]` 而非中文标题或自由命名;`module_<id>` 由阶段三 `03-repo-profile.md` 锁定,阶段四、阶段五、阶段七共享同一份 ID map(`analysis/05-module-ids.yaml`)。

## Alternatives Considered

- **D1. 全并行 + 不交叉**:简单,但风险持续。
- **D2. 全部串行**:失去并行收益,token 量没减少。
- **D3. 单源真相 + 交叉校验(本 ADR)** :多出一次串行 pass,工程量增加约 15%,但保证术语 / wikilink / 引用 一致。

## Consequences

- 阶段三输出 schema 增加:`03-repo-profile.md` 必须包含 `modules[]`(id / name / tier / storyline_position / summary)。
- 阶段五增加 pass-2,内含 1 次串行 sub-agent 调用。
- 阶段七 §9 报告拼装时使用 wikilink ID map,改模块名不需要重渲染 module drafts。
- 验收 §10 增加自动化检查项:wikilink 一致性、模块 ID 唯一性。

## Open Questions

- [ ] Cross-ref pass 是应该放在阶段五内还是阶段六门控前?放阶段五让模块作者自己看,但有"球员兼裁判"嫌疑;放阶段六能让门控更严,但延迟发现。
- [ ] 5 章叙事线 > 5 章次要模块 vs 8 个模块全打平,哪个 ROI 更高?(需要 case 数据)

## Linked

- Q4(Round 2 第四问)
- 阶段四 §6
- 阶段五 §7
- 阶段六 §8
- 阶段七 §9
