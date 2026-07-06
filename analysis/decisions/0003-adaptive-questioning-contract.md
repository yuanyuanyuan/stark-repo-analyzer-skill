# ADR-0003 阶段三"自适应提问"的契约缺失

## Status

Proposed (grilling Round 1)

## Context

PLAN.md §4 阶段三描述了"项目特征识别 + 自适应提问",包括:
- 自适应提问 1: 用户优先关心的方向(架构 / 性能 / 安全 / 业务模块 / 全栈)
- 自适应提问 2: 报告主要受众(技术负责人 / 业务方 / 个人学习)
- 自适应提问 3~4: 用法假设、未来扩展

但以下契约信息全部缺失:

1. **谁来识别项目特征**?(子 agent / 主 agent / repomix 自动推断?)
2. **向谁提问**?(通过 Skill 输入参数 / AskUserQuestion hook / 配置文件 / 推断?)
3. **提问交互形态**:多轮对话 / 单次问答 / 自动跳过?
4. **答案如何 feed 到 §6 阶段四"动态报告结构"?** 阶段三产出是什么文件?
5. **降级路径**:用户说"别问,直接跑"怎么办?

这是一个 **deterministic 工作流文档**(阶段零到阶段七顺序固定)与 **non-deterministic 交互环节**的耦合点,契约不明确会导致 skill 在不同 runtime 下行为不一致(Claude Code / Codex / Cursor 等)。

## Decision (提议)

**明确化"自适应提问"为确定性 + fallback 双轨**:

1. **正常路径**:阶段三开始时,主 agent 调用 `AskUserQuestion` 或等价机制,**一次性**抛出 4 道题(用户优先级、受众、用法假设、未来扩展)。
2. **skip 路径**:若用户在前置指令中显式说明 `--no-question` 或 `mode: autonomous`,则跳过交互,使用**默认值**:
   - 用户优先方向 = `architecture`(最高通用性)
   - 受众 = `tech-lead`
   - 用法假设 = 空数组
   - 未来扩展 = 空数组
3. **产出契约**:无论何种路径,阶段三**必须输出** `analysis/03-question-answers.md`(包含 4 道题的答案或默认值),作为阶段四的输入。
4. **互校验**:阶段三开始时做一次 sanity check——若 `03-question-answers.md` 已存在,直接跳到阶段四;若 `--resume` 标志打开,从该文件读取。

## Alternatives Considered

- **C1. 全交互式**:永远 AskUserQuestion。风险:在 non-interactive agent 运行时(Codex CI、server deployment)直接挂掉。
- **C2. 全默认**:永远跳过提问。风险:失去定制化价值,§7 报告千人一面。
- **C3. 双向契约 + fallback(本 ADR)** :双轨,运行时自选。

## Consequences

- 阶段三需要新增 `03-question-answers.md` 输出契约,与阶段一/二已有的 `00-context.md`、`01-pragmatic.md`、`02-slices-manifest.md` 一起成为输入目录的"自描述"层。
- 阶段四读取 `03-question-answers.md` 后,渲染模板时按答案选择映射:`architecture → 标准 7 章模板`、`security → 加 §6 安全态势章`。
- Skill 入口需要支持 `--mode interactive|autonomous` 与 `--no-question` 两种 flag。

## Open Questions

- [ ] Skip 路径的默认值是否需要做成可配置?例如用户可以预设 `~/.config/repo-analyzer/defaults.yaml`。
- [ ] 阶段三的"项目特征识别"是基于 **阶段一压缩 overview** 还是 **阶段二 12 维精切**?这两种信号源得到的特征可能有冲突。
- [ ] AskUserQuestion 在 Claude Code、Codex CLI、Cursor 等运行时的支持度参差,是否应该改用 InquirerPy / Commander 自行实现?

## Linked

- Q3(Round 1 第三问)
- 阶段三 §4
- 阶段四 §6 动态报告结构
- 阶段十二 §12 开关与默认值
