# Tickets: v2.2 Beats-v1.0（Insight Probe · Delivery · 验收锁）

- parent_issue: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/19"
- requirement_ref: "docs/specs/v2.2-beats-v1.0-insight-probes-delivery.to-spec.md"
- labels: ready-for-agent
- source: "to-tickets from grill-with-docs + to-spec #19"
- saved_at: "2026-07-11T20:30:00+08:00"
- note: "第一交付切片 P1+P2+P3；P4 deep reference Tooling Debt 不在本批。三包齐备前不得宣称 Beats-v1.0。速度非必达。"

术语与 ADR：见根目录 `CONTEXT.md` 与 `docs/adr/0001`–`0009`。

Work the **frontier**：blocker 全完成后可开做。建议顺序 T19-1 →（T19-2 ∥ T19-4）→ T19-3 → T19-5。

---

## T19-1 · Probe Schema + Process Gate

- id: "T19-1"
- title: "Insight Probe 结构化产物与 Process Gate"
- blocked_by: none
- package: P1（机械层）

### what_to_build

让 Acceptance Auditor 与 Agent Consumer 能从工作目录**机械判断**探针流程是否完成：存在合法 `insight-probes.json`、Catalog 三类均有结论；缺失则 Mechanical Gate 失败、不得 Full Delivery。`status=miss` 不导致失败。不实现 LLM 判定逻辑本身。

### acceptance_criteria

- [ ] 约定并文档化 `insight-probes.json` 最小 schema：`version`、`mode`、`probes[]`，每项含 `category` / `status(hit|miss|n_a)` / `summary` / `anchors` / `report_ref`（及可选 `candidates_considered`）。
- [ ] Catalog 三类 id 稳定：`ui_promise_runtime_path`、`multi_source_rules`、`config_dual_write_dead_impl`。
- [ ] `quality-gate-report.json` 增加探针流程检查（语义名 `insight-probe-process` 或等价）：缺文件、缺类别、非法 status/字段 → fail。
- [ ] 三类均为合法 `miss`（或合法 `n_a`+理由字段按合同）且其他门绿时，**不因探针内容**导致 `allowed_to_synthesize=false`。
- [ ] `allowed_to_synthesize` 仍表示是否允许 **Full** Delivery（全检查 pass）；本票不改变「gate 红是否写终稿」的 skill 行为（见 T19-4）。
- [ ] 单元测试覆盖：缺文件 fail；缺一类 fail；合法 miss 全集不因探针 fail。

### test_plan

#### unit

- 扩展 gate 夹具：有/无 `insight-probes.json`、缺类别、非法 status、三类 miss。
- 执行 `npm test`（及既有 typecheck 若适用）。

#### e2e

- N/A 或轻量：prepareArtifacts 风格附 probes 文件后跑 gate CLI，断言 JSON 检查项。

#### uat

- N/A（本票纯机械门）；真实 UAT 留待 T19-5。

---

## T19-2 · Candidate Enum + Skill Probe Obligation

- id: "T19-2"
- title: "候选枚举与 Skill 探针义务"
- blocked_by: "T19-1"
- package: P1（执行层）

### what_to_build

让分析过程**默认跑完**跨仓三类 Insight Probe：确定性步骤只枚举候选入口；LLM 沿候选判定并写入 `insight-probes.json`。禁止纯自觉跳过；禁止仅用正则定罪。`n_a` 必须带仓库形态理由。

### acceptance_criteria

- [ ] skill/rules 明确 standard/deep 默认启用三类探针与执行顺序（在证据/模块分析阶段可集成，不得整段省略）。
- [ ] 提供确定性候选枚举能力或强制步骤说明：覆盖 UI/选项类、多规则定义类、配置/平行实现类候选（跨语言启发式可粗，但须可审计）。
- [ ] 候选列表不得直接写成 `hit`；判定结论由 agent 写入 schema 合法 JSON。
- [ ] `n_a` 必须含非空理由（形态/无适用表面）。
- [ ] 未产出 probes 文件或缺类别时，T19-1 的 Process Gate 会挡住 Full（联调可测）。
- [ ] 文档声明：探针不绑定单一 demo 业务名词；类别保持通用。

### test_plan

#### unit

- 若有候选枚举纯函数：夹具仓上候选非空/稳定烟测。
- 无独立模块则 unit 以 schema/文档契约 + `npm test` 回归为主。

#### e2e

- 可选：夹具仓跑枚举步骤，断言产出候选结构（非 hit）。

#### uat

- docs-only 或 skill 文本核对：强制探针步骤可定位；禁止「可跳过」措辞。

---

## T19-3 · Hit 进入终稿叙事

- id: "T19-3"
- title: "探针 hit 必须进入终稿风险与改造优先级"
- blocked_by: "T19-2"
- package: P1（对 Primary Reader 可见）

### what_to_build

保证 `status=hit` 不只留在 JSON：Human Decision Reader 在终稿/报告草稿的风险与改造优先级中看得见；Agent Consumer 能通过 `report_ref` 对齐。禁止吞没硬伤。

### acceptance_criteria

- [ ] skill 规定：每个 `hit` 必须写入报告风险/限制与具体改进建议（或等价章节），并填写可核对的 `report_ref`。
- [ ] `miss` / `n_a` 在报告或结构化摘要中可发现（避免「没写=没问题」的歧义）；`n_a` 展示理由。
- [ ] 不得将 hit 仅写在 subagent 草稿而不进入融合后的 `report.md` / 终稿路径。
- [ ] 若实现机械抽检：hit 缺 `report_ref` 或报告中无法解析引用时，记为流程/质量失败（至少 skill 强约束；能进 gate 则更好）。

### test_plan

#### unit

- 若有 report_ref 校验：夹具 hit 无 ref → fail；有 ref 且报告含锚点 → pass。
- 否则 unit 以 skill 契约测试/文档勾选 + 回归 `npm test`。

#### e2e

- 构造含 hit 的 `insight-probes.json` + 缺对应段落的 `report.md`，断言校验失败（若已实现）。

#### uat

- 对照仓或夹具叙事抽检：人为 hit 必须出现在可读报告章节。

---

## T19-4 · Full / Degraded Delivery + Synthesis Rule

- id: "T19-4"
- title: "Full/Degraded 同路径终稿与 Synthesis Rule"
- blocked_by: "T19-1"
- package: P2

### what_to_build

主用户在 Mechanical Gate 失败时仍拿到可用终稿：统一 `ANALYSIS_REPORT.md`；`delivery_status=full|degraded`；degraded 含文首横幅、失败门禁、结论边界。废止「`allowed_to_synthesize=false` 禁止任何 ANALYSIS_REPORT」。完整通过仍只认 full。可与 T19-2 并行。

### acceptance_criteria

- [ ] skill 合成规则改为 Synthesis Rule：全绿 → full；未放行 → 仍写同路径 degraded 终稿，不得宣称产品分析完整通过。
- [ ] 终稿元数据含 `delivery_status`；degraded 文首可见横幅；列出失败检查项。
- [ ] UAT/真实UAT 规格同步：区分过程有效 / Full Delivery / Degraded Delivery；删除「gate 红禁止写 ANALYSIS_REPORT」绝对禁令。
- [ ] 「产品分析完整通过」判定不因「存在 ANALYSIS_REPORT 文件」而成立，须 full + 规格要求的其他条件。
- [ ] Agent 默认可读同一路径；不引入 `.degraded.md` 作为主路径。

### test_plan

#### unit

- 若有交付状态辅助校验：full/degraded 元数据与横幅规则。
- 文档+契约为主时：`npm test` 回归不破既有 gate。

#### e2e

- 门红场景：按 skill 合同应存在 `delivery_status=degraded` 的终稿（可用脚本/清单断言文件与 front matter）。

#### uat

- 更新 UAT checklist：gate 红 → degraded 有稿；gate 绿 → full；完整通过文案不被 degraded 骗过。

---

## T19-5 · Gold Sample + Rubric + Agent Smoke

- id: "T19-5"
- title: "Beats-v1.0 验收锁：金样、Rubric、Agent Smoke"
- blocked_by: "T19-3, T19-4"
- package: P3（切片完成定义）

### what_to_build

证明相对 v1.0 在**有用、质量、准确**三维过线（速度不验）：Gold Sample Set v1（G1–G4）必中且进终稿；Reader Rubric 对照；Agent Smoke 可解析关键字段。本票完成前不得宣称 Beats-v1.0。

### acceptance_criteria

- [ ] 落盘 Gold Sample Set v1 说明：G1 UI Promise→Runtime、G2 Multi-Source Rules、G3 Config Dual-Write/Dead Impl、G4 非 UI 形态 n_a 或 hit；含期望与终稿可见性要求。
- [ ] Accuracy Bar：在约定对照流程下 G1–G3 不回归漏检；G4 不静默跳过。
- [ ] Reader Rubric：主链清晰、改造可执行有锚点、双主用户可消费、去模板灌水、hit 进优先级、边界清楚；相对 v1.0 对照清单可执行。
- [ ] Agent Smoke：可解析 `delivery_status`、`insight-probes.json` 各类 status、hit anchors、终稿存在性。
- [ ] 验收记录明确：三包齐备后才可声称 Beats-v1.0；P4 未完成不得声称 deep Full 若 reference 仍红。

### test_plan

#### unit

- Agent Smoke 脚本或测试：对样例工件解析字段（fixture）。

#### e2e

- 可选：最小夹具跑 smoke。

#### uat

- 真实UAT或对照仓：按金样与 Rubric 勾选；输出验收摘要（通过/缺口列表）。
- 基线：`npm test` 绿。

---

## 依赖图

```text
T19-1 ─┬─► T19-2 ─► T19-3 ─┬─► T19-5
       └─► T19-4 ──────────┘
```

## Out of this batch

- P4 deep Graphify/reference `refs_status` 接线（另开票；禁止靠放宽 reference-quality 装绿）。
- 速度必胜 v1.0。
- 纯脚本跨语言自动定罪。
