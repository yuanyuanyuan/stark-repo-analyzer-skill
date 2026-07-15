# Spec: Harness 导航清晰度与完成语义防误读

状态：`ready-for-agent`
本地 tracker：本目录；工单见同目录 `tickets.md`
关联背景：Agent Harness 渐进披露已 `completed`（ADR-0028）；本 spec 修游走审查中的索引漂移与完成语义误读，不重做 harness P0。

## Problem Statement

维护者与 Agent 在仓库内游走时，会同时看到：已完成的 Skill 分发与 harness 交付、多处「绿勾」校验，以及过期的 ADR 索引表述。结果是：（1）以为 ADR-0025 仍未实施而走错迁移/分发路径；（2）把 Judge pass、Harness 契约校验或安全扫描当成「可宣称产品就绪 / 可发版」；（3）按 AGENTS Graphify 路由找 `wiki/index.md` 做宽导航，但现场常只有 `graph.json` / `GRAPH_REPORT.md`。问题在协作真源与完成语义的可扫描性，不在 analyzer 产品运行时。

## Solution

修正 ADR 目录索引，使 ADR-0025（及已落地的 ADR-0028）与已完成控制面、核心包事实一致，并保留 marketplace/G5 未纳入原完成口径的边界。在 Agent 首读与发版入口增加「绿勾 ≠ ship」一眼对照表。收紧 Graphify 宽导航在无 wiki 时的降级措辞。可选补一行「Skill 核心交付包 ≠ 仓库开发基建」。用既有 Harness 契约校验做最小机械防回退，不新建平行校验入口，不进 Skill 核心交付包。

## User Stories

1. As a 维护者, I want ADR 索引与已完成 skill-distribution 控制面一致, so that 我不会把已落地的核心包分发当成「尚未迁移」。
2. As an Agent, I want 「已实现基线」包含 ADR-0025 与 ADR-0028, so that 分发与导航脚手架决策会被正确加载。
3. As an Owner, I want 一眼看到 Judge / harness 校验 / 安全扫描 / Release 各自不等于真实回归 UAT, so that 我不会误判可 ship。
4. As a 发版执行者, I want version-release 入口也能看到同一完成语义, so that 只读 SOP 时不会漏掉不等关系。
5. As an Agent, I want 无 wiki 时仍有明确宽导航降级路径, so that 我不会空等 `graphify-out/wiki/index.md`。
6. As a 维护者, I want 误把 ADR-0025 写回「尚未实施」时 harness 校验失败, so that 索引回退能被机械抓住。
7. As an Agent, I want 安装包与仓库基建边界仍清楚, so that 我不会把 dev-rules/code-map 当成用户安装面去改。
8. As a 审查者, I want 本变更不要求真实回归 UAT 且 progress 诚实披露, so that 证据等级不被抬高。
9. As a 文档读者, I want 0025 完成口径仍写明外部 marketplace/G5 未做, so that 「已实施」不等于「外部安装与发布级回归已验」。
10. As an Agent, I want archive/baseline/vendor 默认非权威的规则不被削弱, so that 防错税仍在。
11. As a Worker, I want 沿用既有 Harness 契约校验与单测形态, so that 不必引入第三套 linter。
12. As an Orchestrator, I want 工单阻塞边清晰且可本地 frontier 开工, so that 可按 T1→… 逐张 `/implement`。
13. As a Judge, I want 验收可核对「索引事实 / 对照表存在 / 校验行为」, so that 审查包范围小且可独立重跑廉价检查。
14. As a 维护者, I want 「当前主线只采用…」类过期句子同步更新, so that 0028 不会被索引后文漏掉。
15. As an Agent, I want AGENTS 上既有「Judge pass ≠ 真实回归 UAT」句保留, so that 不因重构收口段而丢失硬提醒。
16. As a 开发者, I want 本 spec 明确不改 analyzer 用户分析行为, so that 无需启动发布级真实回归矩阵。
17. As a 维护者, I want 可选 T5 仅一行边界、不扩核心包清单, so that 分层设计不被破坏。
18. As an Agent, I want Graphify 路由仍优先 query/path 且脏 graphify-out 不跳过, so that 与现有 Graphify 硬习惯一致。
19. As a 文档维护者, I want product-map / workflows 不被本 spec 改成第二行为真源, so that ADR-0028 分散补强不被推翻。
20. As an Owner, I want 本地 tickets 与 spec 同目录可发现, so that 不依赖 GitHub Issue 也能 AFK 捡工单。

## Implementation Decisions

- **主测试 seam**：扩展既有 Harness 契约校验（不新建第二 doc-linter 脚本）。
- **真源冲突处理**：ADR 目录索引必须服从已完成 roadmap/plan 与仓库内核心包事实；不得保留「0025 + proposed + 尚未迁移」的过期组合。
- **ADR-0025 呈现**：从「已接受但尚未实施」迁入已实现/已落地基线叙述；显式保留「真实外部 marketplace 与 G5 真实回归不在原完成口径内」。
- **ADR-0028**：出现在已实现基线列表/「当前采用」表述中，避免索引后文停在 0027。
- **完成语义**：「绿勾 ≠ ship」短对照表（至少覆盖 Judge pass、Harness 契约校验、安全扫描、GitHub Release 与真实回归 UAT / 产品就绪宣称的不等关系）；挂在根 AGENTS 收口与/或 version-release 首屏；不复制 dual-agent/real-uat 长文。
- **Graphify 宽导航**：文案明确 wiki **可选**；无 wiki 时用 scoped query/path，宽览才读 GRAPH_REPORT；不要求仓库必有 `wiki/index.md`。
- **可选边界句**：Skill 核心交付包路径清单 ≠ 全仓 docs/dev-rules/code-map/harness 校验（安装面 vs 仓库基建）。
- **不进核心包**：本 spec 交付的文档与校验扩展仍属仓库协作基建。
- **控制面**：建议完整门 + 默认独立 Judge；本地 tickets 为执行切片，是否另建 active roadmap 由实施时 document-control 决定（小修复可挂轻量 Delivery + 书面说明，但默认完整门）。
- **术语**：使用 CONTEXT 中 Agent Harness、Product Map、Harness 契约校验、真实回归 UAT、Skill 核心交付包、Worker/Judge 等既有词。

## Testing Decisions

- **好测试**：只测外部可观察行为（校验 exit code、必存在结构/关键词组合、禁止的过期短语组合），不锁散文修辞全文。
- **覆盖模块**：Harness 契约校验及其单元测试；文档链接人工/既有相对链接检查。
- **Prior art**：`tests/unit/test_validate_agent_harness.py` 临时树夹具；`validate-control-plane.py` audit 模式（收口时，不替代 harness 语义测试）。
- **夹具期望示例**（决策形状，非实现抄录）：
  - 绿路径：当前仓库索引 + 现有 harness 必填文件 → exit 0。
  - 红路径：ADR README 再现「尚未实施」且声称 0025 关联 plan 均为 proposed → exit ≠ 0。
- **不测**：真实回归 UAT 矩阵、marketplace 安装、生成 wiki、skill 分析输出合同字段。

## Out of Scope

- 真实回归 UAT、公开发版 tag/Release、外部 marketplace
- 生成或提交 `graphify-out/wiki/`
- 修改 analyzer 用户可见分析行为或 Graphify gate 产品合同
- 削弱 archive / baseline / vendor 默认非权威规则
- 新建 `docs/ai-harness/` 或平行 evidence-map 百科
- 在 GitHub Issues 发布 ticket（本交付仅本地）
- 把 harness/导航资产写入 Skill 核心交付包清单

## Further Notes

- 审查来源：grill 后 harness P0 已落地；后续游走清单条目 4、5、6、7、8/9 的判定见会话结论——仅 4 为必须修的真源漂移；8/9 为聚合不足；5 为措辞/期望缝；6/7 为有意设计。
- 本地路径：`.scratch/harness-navigation-clarity/SPEC.md` 与 `tickets.md`。`.scratch/` 通常不进产品权威；实施改动的权威落点仍是 `docs/adr/`、`AGENTS.md`、`docs/dev-rules/` 与 `tools/release/validate-agent-harness.py`。
- 捡工单：对 frontier 票使用 `/implement`；票间清上下文。
