---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q4)
---

# ADR-0004 阶段五内自检 + 阶段六独立 cross-ref 双层质检

## Context

PLAN.md §7「阶段五：业务模块并行深度分析」按模块清单并行起 N 个 sub-agent，每个 agent **只看自己的模块切片 + 自己上下文**——**看不到其他模块在写什么**。

具体翻车模式：

1. **模块清单双源**：阶段三 §4 做「项目特征识别」也推断模块，阶段四 §6 独立再做一次。两套可能不一致，谁覆盖谁？
2. **术语漂移**：A 分析师写「前置条件」(precondition)，B 分析师写「输入参数」(input param)。同一概念两个名字。
3. **引用断裂**：A 写 `[[Agent B 模块名]]` 实际 wikilink 字符串不一致。
4. **叙事线遗忘**：阶段四做了 3~5 章叙事线，阶段五 sub-agent **不感知**自己模块在叙事线里属于第几章，§7 拼装时叙事线被遗忘。

## Decision

**双层质检，分工明确**：

1. **阶段五内自检（低成本挡 70% 错误）**：
   - 每个 module sub-agent 写完 `drafts/06-module-<id>.md` 后，**自检脚本自动跑**：
     - `grep` 抓自己 draft 中的所有术语，与 ADR-0004 维护的「术语表」对比
     - `grep` 抓自己 draft 中的所有 wikilink，与 ADR-0004 维护的 `05-module-ids.yaml` 对比
     - 自我一致性 + 自引用闭合检查
   - 自检不通过的 draft 标 `[NEEDS_REWRITE]` 子段，禁止进入阶段六
   - 自检耗时 < 5 秒/sub-agent

2. **阶段六门前独立 cross-ref（高成本挡 30% 残留错误）**：
   - 新增 `analysis/drafts/07-cross-ref-checks.md` 挑刺清单
   - **独立 sub-agent 只读不写**，依次读所有 `06-module-*.md`，输出：
     - 冲突术语清单（同概念异名）
     - 断裂 wikilink 清单（`[[xxx]]` 找不到 target）
     - 重复定义清单（多个模块重复解释同一函数 / API）
     - 引用核实清单（模块间互相引用的字符串是否对齐）
   - 独立 cross-ref sub-agent 与原 module sub-agent **不能是同一个**，避免「运动员兼裁判」
   - 独立 cross-ref 耗时约 30-60 秒，< 主 sub-agent 5% 预算

3. **回退阈值**：
   - 若 `07-cross-ref-checks.md` 中冲突术语 > 维度**总数 10%**，自动回退阶段五：
     - 把冲突模块 sub-agent 重启一次（**不是全部重启**）
     - 附带 `07-cross-ref-checks.md` 作为改稿 prompt 上下文
     - 重启后重新走自检 + cross-ref
   - 若冲突 ≤ 10%，放过，进入阶段六覆盖率门控
   - 防止无限循环：单模块最多重试 **3 次**，超过标 `FAILED` 不再回退，留给人工处理

4. **命名空间锁定**（同步落实）：
   - 阶段三产出 `analysis/05-module-ids.yaml`：
     ```yaml
     modules:
       - id: module_001
         name: CLI Surface
         tier: core
         storyline_position: 1
       - id: module_002
         name: Configuration Loader
         tier: core
         storyline_position: 2
     ```
   - 所有 module drafts 必须使用 `[[module_xxx]]` 而非自由命名
   - 阶段四、阶段五、阶段七共享同一份 ID map，改名不动 draft

## Alternatives

- **D1. 全并行不交叉**——简单，风险持续。
- **D2. 全串行**——失去并行收益。
- **D3. 单源真相 + 双层质检（本 ADR）**——多两次自检 + 1 次独立 cross-ref，工程量 +15%。
- **D4. 仅独立 cross-ref，不自检**——独立但缓慢。

## Consequences

- 阶段三 schema 必须增加 `modules[]`（id / name / tier / storyline_position / summary），落地 `05-module-ids.yaml`。
- 阶段五每个 sub-agent prompt 末尾追加自检脚本调用说明。
- 阶段六内部新增独立 cross-ref sub-agent 调用，约多花 5-15% token。
- §10 验收标准增加自动化检查项：
  - wikilink 一致性（grep 抓所有 `[[module_xxx]]`）
  - 模块 ID 唯一性（yaml 解析后 assert `len(ids) == len(set(ids))`）
- 阶段五与阶段六之间可循环 0-3 次，受 ADR-0007 SLA 预算约束。

## Open Questions

- [ ] 独立 cross-ref sub-agent 是否应该使用**更廉价模型**（如 haiku-4.5），降低 5% 预算占用？
- [ ] 冲突术语清单的去重策略：把「前置条件」「输入参数」统一改成哪个？需要有命名规范文档。
- [ ] 单模块重试 3 次后标 `FAILED`，是否要让阶段七报告「本期未完成模块清单」单独成章？

## Linked

- ADR-0005（覆盖率门控在 cross-ref 通过后才进）
- ADR-0007（重试受 SLA 预算约束）
- 阶段四 §6 / 阶段五 §7 / 阶段六 §8
