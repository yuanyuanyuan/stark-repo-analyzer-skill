# ADR-0001 阶段一压缩包与阶段二 12 维精切的信号冲突

## Status

Proposed (grilling 进行中,Round 1)

## Context

PLAN.md §2 阶段一"宏观认知建模"使用 `repomix` 压缩,带着 IGNORE_GLOB(过滤掉 `*.lock` 与 `.claude/**`、`.codex/**`、`AGENTS.md`、`CLAUDE.md` 等),目的是喂给 4+1 个子 agent 输出一份 overview。

§3 阶段二"12 维精细切片(不压缩 + XML)"中,锁文件与 AI Agent 配置被列为**例外放行**,单独 `--include` 进 `09-lockfiles.xml` 与 `05-agent-config.xml`。

下游 §4 阶段三"项目特征识别"、§6 阶段四"动态报告结构"、§7 阶段五"业务模块并行深度分析"都明确依赖:
- 锁文件 → 判断依赖锁定范围、版本基线(B 模块依赖、阶段七报告 §4)
- AGENTS.md / CLAUDE.md / `.claude/**` → 判断已有 agent 上下文、定制规则

也就是说,阶段一 subagent 在生成 overview 时,**完全看不到这些被阶段二单独 include 的关键信号**。

## Decision (提议)

**保留双阶段,但显式标记阶段一输出为 low-confidence,阶段二覆盖重写关键字段。** 具体:
1. §2 阶段一生成的 `00-overview.xml` 在阶段二开始时**不删除**,但阶段二产出的 `01-...xml` 至 `12-*.xml` 是真实信号源;
2. 阶段三在做"项目特征识别"时,优先信任阶段二 12 维的 05/06/09 子集;
3. 阶段一 overview 仅作为"主 subagent 的工作记忆"保留,不参与最终报告生成。

## Alternatives Considered

- **A1. 砍掉阶段一**:直接 stage-2 起手,把宏观认知下沉到 12 维精切之后做合并。风险:子 agent 在没有全局视野时可能 over-fit 自己那一片;且单次 12 维输出体量巨大,主 subagent 上下文窗口压力大。
- **A2. 阶段一也加 include**:把 `*.lock`、`AGENTS.md`、`CLAUDE.md` 不做 IGNORE,放进 repomix。风险:压缩率上升,overview 信号被噪音淹没。
- **A3. 双阶段+置信度标记(本 ADR)** :保留现状,显式标注信任边界。

## Consequences

- 阶段二成为 single source of truth,阶段一仅做 development aid。
- 需要在阶段三增加"信号优先级排序"步骤——这是个新增工作量。
- 报告 §0 TL;DR 中需要明确说明"信号源 = 阶段二 12 维"。

## Open Questions

- [ ] 阶段一 overview 是否真的不可信,还是说只要主 subagent 能在 prompt 里明确列出"已知信号缺失清单"也能用?
- [ ] 阶段二若 fail 退化为阶段一,需要怎样的 fallback 路径?

## Linked

- Q1(Round 1 第一问)
- 阶段三 §4 项目特征识别
- 阶段五 §7 子 agent 输入清单
