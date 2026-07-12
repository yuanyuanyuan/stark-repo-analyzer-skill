# 质量落差诊断与纠偏方案

> **状态（2026-07-11 grill-with-docs 收口）**  
> 本文为质量落差**研究草案/背景叙事**，不再是执行 SSOT。  
> **冲突时以以下为准**：`docs/adr/0010`–`0033`、`CONTEXT.md`、`docs/benchmarks/density-baselines.md`（见 ADR-0033）。  
> 正文若仍出现裸 `P0`–`P5` 纠偏编号，对应 **QC-0…QC-5**（ADR-0015）。  
> 已拍板修正摘要：质量合同不默认 hard gate；Slice A = 结构层 + 可比密度层；锚点硬升用**合同表面**；`risk_count` 仅结构化；probe/主链/claim 用终稿标记；`quality_contract` 由脚本盖戳；检查对象仅 `ANALYSIS_REPORT.md`。


- 日期：2026-07-11
- 范围：`spec-v2.2-standard-deep-modes-and-rules-based-to` worktree
- 状态：研究草案（未宣称已落地 Beats-v1.0）
- 读者：产品 owner / 二次开发执行者
- 相关证据：
  - `测试证据/v1.0没改造前/ANALYSIS_REPORT.md`
  - `测试证据/real-uat-standard-20260711-1855/`
  - `测试证据/real-uat-regression-20260711-213622/`
  - `测试证据/real-uat-deep-20260711-1855/`
  - `测试证据/real-uat-deep-wired-20260711-220005/COMPARE_STANDARD_V1.md`
  - `docs/adr/0003-accuracy-bar-gold-samples.md`
  - `docs/adr/0004-usefulness-quality-bars.md`
  - `CONTEXT.md`（Primary Reader / Mechanical Gate / Beats-v1.0 Bar）

---

## 1. 问题陈述

按 Evidence-First 建议路线，本 worktree 已落地：

- doctor / scan / summarize / units / gate 确定性 CLI
- coverage units + module evidence matrix
- semantic source review
- insight probes（流程门）
- standard / deep 模式与 rules SSOT
- Graphify → refs 接线后 deep Full 可过门

但真实读者体感与对照指标显示：**分析结果质量相对 v1.0 仍强差人意**。

核心现象：

> **Mechanical Gate 更容易全绿，报告却更薄、锚点更稀、洞见密度低于 v1.0。**

不是「建议完全做错」，而是 **把审计地板当成了质量终局**，agent 学会了**合规地浅写**。

---

## 2. 关键对照数据（已落盘）

摘自 `测试证据/real-uat-deep-wired-20260711-220005/COMPARE_STANDARD_V1.md`：

| 报告 | 行数 | 唯一锚点≈ | 备注 |
|---|---:|---:|---|
| v1.0 | 136 | **62** | 锚点密、主题覆盖强 |
| standard 213622 | 204 | **20** | 更长但更稀 |
| deep wired 220005 | 226 | **24** | 略好于 standard，仍远低于 v1.0 |

解读：

1. deep 接线解决的是 **Full Delivery 能力门禁**，不是自动恢复 v1.0 洞见密度。
2. 「比 v1.0 薄」**不能**只靠换 deep 解决。
3. gate 13/13 与「压过 v1.0」是两个目标，不可混谈。

其他过程事实：

| 轮次 | mode | gate | 终稿 | 墙钟量级 |
|---|---|---|---|---|
| real-uat-standard-1855 | standard | 12/12 放行 | 有 ANALYSIS_REPORT | ~3 min |
| real-uat-deep-1855 | deep | reference-quality 失败 | 无（当时合同） | ~6 min |
| real-uat-regression-213622 | standard | 13/13 放行（含 probes） | 有 | ~2.5 min |
| real-uat-deep-wired-220005 | deep | 13/13 放行 | 有 | ~3.5 min |

对比：v1.0 重跑量级约 **9+ 分钟** 且终稿锚点显著更密。  
当前系统在极短时间内凑齐工件，天然偏向**结构正确、正文浅**。

---

## 3. 已生效 vs 未生效

### 3.1 已生效（值得保留）

| 能力 | 效果 |
|---|---|
| Doctor 能力合同 | 能力不足时 fail-closed，避免假 deep |
| Units + coverage 双硬条件 | 降低「空口覆盖率」 |
| Module Evidence Matrix | 结论可机读、可复查 |
| Gate 阻断假 Full | 审计地板上升 |
| Insight Probe 流程 | 金样类硬伤可被点状命中（Export/SEO 等） |
| Semantic Source Review | 对抽样锚点掺水有一定抑制 |
| Degraded Delivery 方向（ADR-0001） | 门红时主用户不必空手（合同演进中） |

### 3.2 未生效 / 反向效果

| 期望 | 现实 |
|---|---|
| 更可审计 ⇒ 更有用 | 更可审计，但读者洞见不升反降 |
| deep Full ⇒ 压过 v1.0 | deep Full 只证明能力链通 |
| report-depth 保证 Why>What | 实为关键词/结构存在性检查，可被一段权衡散文过门 |
| coverage% 代表理解深度 | 代表关键单元勾选达标，不代表多跳推理 |
| probes hit ⇒ 终稿更强 | 常停在 `insight-probes.json` 侧车，未系统性抬升全文密度 |
| 并行 subagent ⇒ 更深 | 若 core 仍是单个巨大 `src`，并行只是填表分工 |

---

## 4. 根因分析

### R1. 优化了错误 proxy（最主因）

成功被操作化为：

- `allowed_to_synthesize: true`
- checks 全 pass
- 工件清单齐全

而真正要对 Primary Reader 成立的是 CONTEXT 中的：

- **Accuracy Bar**（金样必中且进终稿）
- **Usefulness Bar**（人可执行改造 + agent 可解析）
- **Quality Bar**（主链、锚点一致、去灌水）

Mechanical Gate 只应决定 **Full / Degraded**，不应被当成 **Beats-v1.0**。

### R2. `report-depth` 过浅，可被合规骗过

`src/gate.js` 的 report-depth 以「是否出现动机/权衡/替代方案等模式」为主。  
agent 可写**单段密散文**过门，而不必产出 v1 级「多条独立风险 + 每条推理链 + 高锚点密度」。

### R3. JSON / 工程流程注意力税过高

真实 UAT 常见 2–4 分钟内完成：

doctor → scan → units 回填 → matrix → coverage 勾选 → subagent 合并 → probes → gate → 终稿

结果：

- 过程工件厚
- 读源码与多跳推理时间被挤占
- 稳定产出「合规浅报告」

### R4. 模块粒度退化成单 core `src`

`module-evidence/src.json` 把会话 / Worker / 算法 / 导航 / 导出揉成一个模块：

- 对 gate 方便（一套覆盖率、一个 matrix）
- 对叙事有害（失去模块过渡、分块风险、分块权衡）

v1 的强项恰恰是**业务模块拆分 + 过渡叙事 + 分主题深挖**。

### R5. 探针补点不补面

在长截图样例仓上，probes 能 hit：

- UI Promise → Runtime Path（导出高级选项未贯通）
- Multi-Source Rules（SEO 多源）
- Config Dual-Write / Dead Implementation（平行实现；不同轮次 hit/miss 有波动）

这证明 P1 方向正确，但 COMPARE 仍显示总锚点 ~24 vs v1 ~62：

> **3 个点状硬伤 ≠ 重建全主链密集取证。**

### R6. 建议本身的边界（需诚实记录）

Evidence matrix / gate / doctor / unparsed / semantic review 的本质是：

- 拉高**下限**（防胡说、防无依据、防假覆盖）
- **不自动**拉高上限（洞见密度、锚点密度、改造可执行性）

若把它们当质量充分条件，就会得到当前系统：

**更诚实、更可审计、常常更干、更短视、更像合规报告。**

---

## 5. 目标函数纠偏

### 5.1 保留

- doctor / units / matrix / gate / probes
- rules SSOT 与 standard/deep 能力合同
- Full / Degraded Delivery 语义
- 真实UAT 分档回归

### 5.2 改掉

| 旧默认 | 新默认 |
|---|---|
| gate 全绿 = 分析成功 | gate 全绿 = 允许 Full Delivery |
| 工件齐全 = 质量过线 | Reader Bar 过线 = 质量过线 |
| 追 coverage% | 追独立 claim 数 + 锚点密度 + 改造可执行性 |
| 单 `src` core 可过 | core 必须业务拆分后叙事 |
| probes 有 JSON 即可 | probe hit 必须升格进终稿优先级 |

### 5.3 成功标准（Beats-v1.0，三必达）

1. **Accuracy**  
   Gold Sample Set v1（G1–G3）按规则必中；命中必须进入终稿风险/改造优先级。  
   仅 `insight-probes.json` hit 不算过线。

2. **Usefulness**  
   Human Decision Reader：主链清晰 + 可执行改造清单（含锚点）。  
   Agent Consumer：稳定抽取 `delivery_status`、锚点、探针结论、改造项。

3. **Quality**  
   主链完整、判断与锚点一致、少模板灌水。  
   **相对 v1 baseline，unique anchors 与独立架构 claim 数不得系统性偏低。**

速度：**本阶段不作为必达 KPI**（与 ADR-0004 / CONTEXT 一致）。

---

## 6. 纠偏方案（按质量 ROI）

### P0 · 终稿质量合同（最高杠杆）

对 `ANALYSIS_REPORT.md`（及合成前 `report.md`）增加硬交付合同，**优先于再加更多机械 check 花活**：

1. **主链 N 段不可缺**（可配置，默认 5）  
   泛化：入口 → 核心变换 → 状态 → 边界/守卫 → 输出  
   长截图示例：上传 → Worker/算法 → 状态落库 → 导航/会话 → 导出

2. **独立架构 claim 下限**  
   - standard：建议 ≥ 12  
   - deep：建议 ≥ 20  
   每条 claim 绑定**互不相同**的 `file:line`（允许同文件不同行，鼓励跨文件）

3. **风险 / 改造条目下限**  
   每条必须含：现象 + 影响 + 锚点 + 改造方向  
   standard 建议 ≥ 5；deep 建议 ≥ 8

4. **Probe 升格强制**  
   每个 `status=hit` 的 probe 必须在终稿「风险与改造优先级」中出现  
   仅有 `report_ref` 指向草稿锚点但终稿无条目 → 质量合同失败（可先做 soft fail + UAT 红，再进 gate）

5. **禁止用单段权衡散文冒充多 claim**  
   claim 需可枚举（列表/小节），便于 Agent Smoke 与对照脚本计数

> 说明：P0 的一部分可用确定性脚本做 smoke（计数锚点/标题/probe 映射）；「claim 是否真有洞察」仍需 Reader Rubric + 金样，不能全靠 regex。

### P1 · 把 JSON 税从 agent 手里拿开

确定性 CLI / 脚手架自动生成：

- coverage 候选与 skip 模板
- module-evidence 骨架字段
- probe 候选枚举（候选入口列表）

agent **只填判断字段**：

- why / 权衡 / 替代代价
- risk finding + impact
- probe 结论与升格文案
- 叙事过渡

目标：同样墙钟内 **读源码比例 ↑，填表比例 ↓**。

### P2 · 恢复业务模块叙事

强制：

- core 逻辑模块 ≥ 3（按业务能力/数据流，不按顶层目录凑数）
- 每个 core 模块独立 narrative 小节 + 过渡句
- 允许底层仍合并部分 matrix 文件，但**终稿不得只有一个「src 大章」糊弄**

禁止：

- 单一 `module-evidence/src.json` 作为 standard/deep 唯一 core 叙事单元（可作聚合索引，不可作唯一正文）

### P3 · 最小深读预算（反「3 分钟假 Full」）

对非玩具仓：

- Evidence Plan 必须列出关键路径文件的计划 Read span
- 未达深读预算 → 只能 Degraded，或显式 `timeboxed=true`，**禁止宣称 Beats-v1.0**
- UAT 记录墙钟与深读完成率

避免系统奖励「最快凑齐工件」。

### P4 · 对照指标产品化

将 `COMPARE_STANDARD_V1.md` 指标固定为每次真实UAT 必出：

| 指标 | 用途 |
|---|---|
| unique anchors | 密度 |
| 独立 claim 数 | 结构深度 |
| 风险/改造条数 | 可执行性 |
| 主题命中（时序脆弱、边界、导出、配置分叉…） | 面覆盖 |
| probe hits → 终稿映射率 | 准确度落地 |
| delivery_status | Full/Degraded 诚实性 |
| 相对 v1 回归表 | Beats-v1.0 判定 |

没有这张表，只看 gate 13/13 会产生幻觉胜利。

### P5 · Reader Rubric + Agent Smoke（已有 ADR，需执行闭环）

落地 ADR-0003 / 0004：

- 金样集固定仓库 + 期望表达
- 人工/半自动 Reader Rubric 对照 v1
- Agent Smoke：解析终稿字段是否可被下游 agent 消费

**全部 P0–P4 完成前，不得宣称 Beats-v1.0。**

---

## 7. 建议实施切片

### Slice A（研究后第一刀，最小闭环）

1. 终稿质量合同文档化（本文件 + skill/references 短节）
2. 对照脚本：unique anchors / probe→report 映射 / claim 粗计数
3. 真实UAT standard 重跑同一目标仓，出 COMPARE 表
4. **不做**更多 doctor 能力扩张

验收：

- 相对当前 standard 213622，unique anchors 与风险条数上升
- probe hit 100% 出现在终稿改造优先级
- 仍诚实报告 Full/Degraded

### Slice B

1. CLI 生成 matrix/coverage/probe 骨架，降低 JSON 税
2. 强制 ≥3 core 业务模块叙事
3. 深读预算字段进入 Evidence Plan

### Slice C

1. 金样回归自动化（G1–G3）
2. Reader Rubric 清单固化进 `docs/benchmarks/`
3. 评估是否将「终稿质量合同」部分条款升为 gate soft/hard（慎用 hard，防再次激励骗检）

---

## 8. 明确不优先做的事

- 再堆章节模板、固定十分制打分表
- 只提高 coverage 阈值（会激励刷勾选）
- 用放宽 reference-quality 换 deep 假绿
- 用更长 report 灌水换「看起来厚」
- 在 Beats-v1.0 未证明前大范围宣传「已压过 v1」

---

## 9. 与既有 ADR 的关系

| ADR | 关系 |
|---|---|
| 0001 Degraded Delivery | 保留；门红仍应对 Primary Reader 有标记终稿 |
| 0002 Uncapped Insight Probes | 保留探针深度；本方案补「升格进终稿」 |
| 0003 Gold Samples | 本方案的 Accuracy 过线器 |
| 0004 Usefulness/Quality Bars | 本方案的 Reader 过线器 |
| 0005 deep reference tooling debt | 已部分偿还（wired）；**不**等于质量过线 |
| 0008 Probe Process Gate | 只保证流程产物；本方案补命中落地 |
| 0009 First Delivery Slice | P1+P2+P3 交付切片；本诊断解释「为何切片后仍差」 |

本文件**不替代**上述 ADR；它解释执行偏差，并给出下一阶段质量合同。

---

## 10. 一句话决策

**Gate 负责不撒谎；质量合同负责有洞见；Beats-v1.0 只认 Reader 三维，不认 checks 全绿。**

下一步最小动作：执行 §7 Slice A，用同一目标仓证明锚点密度与改造可执行性相对当前 v2.2 报告上升，再谈是否升 gate。

---

## 11. 附录：建议的终稿骨架（研究用）

```markdown
# 标题
- delivery_status: full|degraded
- mode / commit / gate 摘要

## 问题场景
## 项目全景
## 设计哲学（可短）
## 主链（强制 N 段，每段有锚点）
## 模块深潜（≥3 业务模块 + 过渡）
## 关键设计决策（可枚举 claims）
## 风险与改造优先级（含全部 probe hits）
## 开放问题 / Unsupported
## 对读者的启发（可选，防灌水）
```

## 12. 附录：质量对照检查清单（UAT 后人工 10 分钟）

- [ ] 不看目录也能说出主数据流
- [ ] 至少 5 条风险/改造可直接开 issue
- [ ] 每条改造都有 `file:line`
- [ ] probe hit 未消失在 JSON 里
- [ ] 与 v1 比：不是「更长」，而是「更密、更可执行」
- [ ] Full 时无降级横幅；Degraded 时边界清楚
- [ ] 无大段可换仓复用的套话

