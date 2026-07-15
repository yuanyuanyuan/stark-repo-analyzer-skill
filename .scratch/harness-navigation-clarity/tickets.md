# Tickets: Harness 导航清晰度与完成语义防误读

修 ADR 索引漂移、完成语义一眼表、Graphify 无 wiki 路由，并用 Harness 契约校验防回退。Spec：`.scratch/harness-navigation-clarity/SPEC.md`。

Work the **frontier**：阻塞方都完成后即可开工；线性依赖上大致 T1 → T2，T3/T4/T5 可与 T1 并行（若校验要扫对照表则 T3 在 T2 之后或并入 T2）。

标签（本地）：`ready-for-agent`

## T1 · 修正 ADR-0025 索引与已实现基线列表

**What to build:** 打开 ADR 目录索引即可看到：Skill 核心包分发（ADR-0025）已随 skill-distribution 控制面落地；「尚未实施/plan 均为 proposed」过期表述消失；已实现基线包含 0025 与 0028；仍写明外部 marketplace 与 G5 真实回归不在原完成口径内。

**Blocked by:** None — can start immediately

- [ ] ADR 索引不再把 0025 放在「已接受但尚未实施」且声称关联 roadmap/plan 均为 proposed
- [ ] 与 skill-distribution `completed` 及核心包清单事实一致
- [ ] 已实现/当前采用列表覆盖 ADR-0025 与 ADR-0028（消除停在 0027 的过期句）
- [ ] 0025「已落地」不等于 marketplace/G5 已验——边界仍可读

## T2 · 扩展 Harness 契约校验防索引回退

**What to build:** 误把 ADR-0025 写回「尚未实施 / proposed 未迁移」组合时，Harness 契约校验非 0；当前正确索引下校验仍为 0。单测覆盖成功与回退失败。不替代 Judge，不证明真实回归 UAT。

**Blocked by:** T1 · 修正 ADR-0025 索引与已实现基线列表

- [ ] 校验对过期 0025 表述失败、对当前仓库绿路径成功
- [ ] 单元测试覆盖上述分支（行为断言，不锁全文修辞）
- [ ] 文档/注释写明：本检查 ≠ Judge pass ≠ 真实回归 UAT

## T3 · 「绿勾 ≠ ship」一眼对照表

**What to build:** 在 Agent 首读收口与/或 version-release 入口，一眼可见：Judge pass、Harness 契约校验、安全扫描、GitHub Release 各自不等于真实回归 UAT / 可宣称产品就绪。保留既有「Judge pass ≠ 真实回归 UAT」句，不复制长文细则。

**Blocked by:** None — can start immediately（若 T2 要机械检查表存在，则改为 blocked by T2 或与 T2 同批）

- [ ] AGENTS 与/或 version-release 存在短对照表
- [ ] 至少覆盖 Judge、harness 校验、安全扫描、Release 与真实回归 UAT 的不等关系
- [ ] 不删除既有 AGENTS 收口硬提醒句

## T4 · Graphify 无 wiki 时的宽导航措辞

**What to build:** Graphify 路由明确 wiki 可选；无 `wiki/index.md` 时用 query/path，宽览才读 GRAPH_REPORT；不暗示本仓必有 wiki。脏 graphify-out 仍不跳过 Graphify。

**Blocked by:** None — can start immediately

- [ ] AGENTS Graphify 段与「常无 wiki」现场策略一致
- [ ] 校验不要求 wiki 文件必须存在
- [ ] 仍优先 query/path，改代码后 update 约定不变

## T5 · 安装包 vs 仓库基建一行边界（可选）

**What to build:** 在 agent-boundaries 或 AGENTS 权威表旁增加一行：Skill 核心交付包清单路径 ≠ 全仓 docs/dev-rules/code-map/harness 校验；导航基建不进安装面。

**Blocked by:** None — can start immediately

- [ ] 边界句可读且不扩大核心包清单
- [ ] 与 ADR-0027/0028「不进核心包」一致

---

## 建议实施顺序

1. T1（可与 T3、T4、T5 并行）
2. T2（依赖 T1）
3. 若 T3 需进校验，在 T2 中一并断言表关键词，或 T2 后补 T3
4. 收口：`validate-agent-harness`、相关单测、完整门时独立 Judge + control-plane audit

## 非目标（所有票共用）

- 不发布 GitHub Issue
- 不跑真实回归 UAT / 不发版
- 不改 analyzer 用户分析行为
- 不生成 graphify wiki
- 不新建 `docs/ai-harness/`
