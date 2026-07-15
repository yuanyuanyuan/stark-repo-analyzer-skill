# ADR-0028：Agent 导航采用分散补强渐进披露，不平行引入 docs/ai-harness

状态：`accepted`

## 决策

吸收参考仓 video-know-it 的 harness 设计思想时，采用**分散补强**而非平行知识包：

1. **短入口**：根 `AGENTS.md` 只做问题路由与最短启动顺序，不复写细则。
2. **按任务渐进加载**：Product Map、workflows、agent-boundaries、代码地图按问题打开，不是每次任务通读。
3. **落点**：
   - 用户场景导航 → `docs/spec/product-map.md`
   - 作业流编排 → `docs/dev-rules/workflows/`
   - 硬边界与暂停 → `docs/dev-rules/agent-boundaries/`
   - 功能→分层入口 → 既有 `docs/code-map/map.yaml`
4. **Harness 契约校验**：独立脚本 `tools/release/validate-agent-harness.py`，与 `validate-control-plane.py` 并列，不耦合；默认不 PreToolUse 硬拦截。
5. **不**新建 `docs/ai-harness/` 作为第二套权威树；不引入 planner/test_review 正式术语（映射到 Worker/Judge/Orchestrator）。
6. **不**把上述导航资产打进 Skill 核心交付包；不改变 analyzer 产品行为合同。

## 原因

本仓已有比参考仓更强的 document-control、双角色 Judge 与质量门。若整包复制 `docs/ai-harness/`，会与 `docs/dev-rules/`、roadmap/plan、code-map 形成双真源与双角色语言。需要的是 OpenAI harness 意义上的「短入口 + progressive disclosure + doc-gardening linter」，而不是目录名同构。Product Map 放在 `docs/spec/` 旁，避免与「代码地图 = 本仓开发定位」语义拧巴，同时明确其不替代行为合同。

## 备选方案

- **平行 `docs/ai-harness/` 五件套**：与参考仓同构，迁移成本低，但与现有 dev-rules/控制面重复，长期双维护。
- **只改 AGENTS.md 加长**：冷启动更差，违反短入口。
- **把导航校验并入 control-plane 校验**：少一个入口，但把「状态机收口」与「指示牌完整性」耦死，失败语义混乱。
- **不做机械校验**：文档最快腐烂，progressive disclosure 不可维持。

## 影响

- 新增/更新：Product Map、workflows、agent-boundaries、ADR-0028、CONTEXT 术语、AGENTS 与目录路由、`validate-agent-harness.py`、code-map feature `agent-harness-navigation`。
- 改 harness 导航相关文件或本 initiative 收口时必须跑 harness 校验；完整门仍走 Judge 与 control-plane audit。
- 产品分析 skill/spec 行为不变；真实 UAT 证据上限不变。

## 取代关系

不取代现有 ADR。与 ADR-0026（默认 Judge）、ADR-0027（代码地图）正交：本决策约束 Agent 导航脚手架的包装与校验边界，不扩展产品 Graphify 控制面。
