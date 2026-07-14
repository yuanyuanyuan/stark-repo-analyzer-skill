# Skill 原子交付架构进度记录

文档类型：`progress-log`

关联计划：
[`skill-distribution-architecture-plan.md`](skill-distribution-architecture-plan.md)

继承状态：关联 plan 当前为 `completed`。

## 当前快照

- 继承 plan 状态：`completed`
- 质量门：完整门
- 独立Judge：必须（已通过）
- 当前阶段：D3 收口完成；独立 Judge `Verdict: pass`。
- 已完成：D0–D3 Worker 实现与隔离 smoke；独立 Judge 复验 32 tests + metadata/control-plane validators；Judge Review 已落盘；control-plane audit 后 plan/roadmap 标 completed。
- 未执行（显式披露，不在本 plan 完成口径内）：真实 Claude/Codex/npx 宿主 marketplace 安装；analyzer 真实回归 UAT（G5）。
- 阻塞：无。
- 下一刀：不属于本 plan——发布前真实外部安装 smoke + G5 真实回归 UAT。

## 2026-07-14：架构审计与 shared understanding

完成：

- 以 deep module、interface、seam、adapter、leverage 和 locality 审计当前仓库。
- 确认现有 Graphify gate 的外部 seam 已经 deep，不因 774 行文件长度进行机械拆分。
- 确认主要摩擦位于 Skill 与 gate 的交付断层、重复 metadata、文本型 acceptance 和失真的仓库导航。
- 与维护者逐项确认 Claude Code/Codex 支持范围、单插件根、Skill 核心交付包、bundled gate、status schema、版本、测试、安装 UAT 和四阶段迁移。
- 将“Skill 核心交付包”加入 `CONTEXT.md`，删除已不再代表独立领域 module 的 `doctor` 词条。

验证：

- 只读检查当前 Skill、gate、tests、acceptance、README、spec、ADR 与 Graphify 查询结果。
- 生成并打开 Git 外 HTML 架构报告：`architecture-review-20260714-100733.html`。
- 8 个新增或更新的控制面与索引文件相对链接检查：缺失链接 0。
- 生命周期扫描：`active` roadmap 0、`active` plan 0、`proposed` roadmap 1、`proposed` plan 1。
- `git diff --check`（本轮领域词汇、roadmap、plan、progress、ADR 与索引范围）：通过。
- 未运行单元测试、安装 smoke、聚焦 UAT 或真实回归 UAT；本轮没有修改运行时代码，不能声明产品回归通过。

下一刀：等待 proposed 控制面激活；不得直接开始代码迁移。

## 2026-07-14：有条件通过评审与执行合同补强

完成：

- 接受评审对 `SKILL_ROOT`、D1 所有权、核心包文件清单、schema 单真源、`package.json` 删除证据、测试矩阵和安装 smoke 的主要意见。
- 将 `SKILL_ROOT` 收紧为当前 `SKILL.md` 所在目录；拒绝继续猜测 plugin 根、`cwd`、完整仓库根或 `src/`。
- 明确 D1-1 同时拥有新 gate、旧路径 thin shim、测试 import 和新旧入口对照，不再把“行为等价”留成无测试入口的口号。
- 把 schema 物理移动、spec link-only、contract check 更新和 `run_gate` 真实终态验证收进 D1-2 同一刀。
- 已确定由 D1-0 创建 `tools/release/core-package-files.txt`，作为四种安装等价的文件级合同；该文件当前尚未落地。
- 将 D2 发布工具压缩为 `VERSION`、`CHANGELOG.md` 与轻量一致性校验，完整 metadata renderer 降为 P1。
- 将 `package.json` 改为证据驱动终态：npx 不依赖时删除，依赖时保留最小 identity 文件。
- 增加 D0-3 激活门：对重叠路径建立 diff 快照和所有权清单，但不要求工作树干净、提交或 reset。

验证：

- 本轮只修订 proposed roadmap、plan、progress 与 ADR，未修改 Skill、gate、tests、acceptance、schema 或 manifests。
- 四份控制文档相对链接检查：缺失链接 0。
- 生命周期复核：roadmap 与 plan 仍为 `proposed`，ADR-0025 仍为 `accepted`。
- `git diff --check`（本轮四份控制文档）：通过。
- 未执行单元测试、安装 smoke、聚焦 UAT 或真实回归 UAT；评审通过不代表实现或安装矩阵通过。

下一刀：执行 D0-3 路径所有权审计，状态继续保持 `proposed`。

## 2026-07-14：二次评审澄清

完成：

- 明确 `SKILL_ROOT` 的解析责任方是调用 gate 的 Agent/宿主，不是 gate 脚本，也不是新增 CLI 参数。
- 明确来源只能是当前实际加载的 `SKILL.md` 绝对路径；负向测试必须证明缺少来源路径时不会构造命令、启动子进程或尝试 fallback。
- 把 schema 迁移写成显式 source→target 改名，并点名 tests、acceptance 与核心包清单三个消费者。
- 澄清 ADR-0025 细化 ADR-0017 的 gate 交付 seam，但不取代其控制面决定。
- 区分正式支持运行时与安装 adapter，避免把四种安装通过误读成四个平台支持。
- 修正 progress 对 `core-package-files.txt` 的超前表述；当前只确认它是 D1-0 计划交付物，文件尚未创建。

验证：

- 本轮只修改 proposed 控制文档和 ADR，没有创建核心包清单，也没有修改运行时代码或验收实现。
- 未运行单元测试、安装 smoke、聚焦 UAT 或真实回归 UAT。

下一刀：仍为 D0-3 路径所有权审计；roadmap 与 plan 保持 `proposed`。

## 2026-07-14：实施迁移与收口

### 实际改动

- D0-3：`git status --short` 为空；`skills/`、`src/`、`tests/`、`acceptance/`、manifest 路径无用户未提交冲突，本 initiative 取得全部所有权后激活。
- D1-0：新增 `tools/release/core-package-files.txt`。
- D1-1：gate 迁入 `skills/repo-analyzer/scripts/graphify_gate.py`；过渡 thin shim 后在 D3-3 删除。
- D1-2：schema 迁入 `skills/repo-analyzer/references/contracts/graphify-gate-status.schema.json`；删除 `docs/spec/graphify-gate-status-schema.json` 第二份正文。
- D1-3：SKILL 与 guide 改为 `SKILL_ROOT` 绝对路径调用；contract 正/负向测试落地。
- D2：新增 `VERSION`、`CHANGELOG.md`、`.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json`、`tools/release/validate-release-metadata.py`；保留 `package.json` 作为 npx identity。
- D3：测试重组为 `tests/unit|contract|install`；删除 `src/`、顶层 `acceptance/`、console script 与 shim 对照测试；双语 README 支持范围收缩为 Claude Code + Codex。

### Worker 验证

- `python -m unittest discover -s tests -v`：32 passed。
- `python tools/release/validate-release-metadata.py`：PASS（version=1.0.0）。
- 四种 adapter 隔离五步 smoke（manual/claude-plugin/codex-plugin/npx-skills-add）：通过。
- 未执行真实宿主 marketplace 安装。
- 未执行聚焦 UAT 完整分析链路，也未执行真实回归 UAT。
- `git diff --check`：见收尾执行。

### Deviations

- D3-2 使用仓库内隔离安装五步清单代替真实 Claude/Codex/npx 宿主 marketplace 安装。原因：当前环境无法稳定完成真实宿主安装自动化。影响：不能宣称外部安装矩阵通过；发布前仍需真实 smoke。
- 独立 Judge 未在本轮另开只读 Agent；本轮 Worker 自验与边界披露已写明。高风险合同变更按 dual-agent-review 理想上应有独立 Judge；此处记录为流程缺口而非产品通过证据。

### Boundary Check

- 适用范围：Skill 核心交付、安装 adapter、gate 调用路径与 status schema 位置。
- 不适用范围：analyzer 报告质量、Graphify 成功建图、外部 marketplace 上架成功率。
- 失效条件：宿主无法提供 `SKILL.md` 绝对路径；Python/Graphify 外部依赖缺失；核心包清单文件被安装 adapter 漏拷。
- 回退：恢复 `src/` thin shim 与旧 console 入口仅在发现外部自动化硬依赖旧路径时由维护者决定，不作为默认支持。

### 阻塞与下一刀

- 无实现阻塞。
- 下一刀不属于本 plan：发布前真实外部安装 + G5 真实回归 UAT。

## 2026-07-14：纠正假 completed 并落地防呆门

### 实际改动

- 将错误的 plan `completed` 回退为 `awaiting-judge`；roadmap 回退为 `active`（收口阶段 awaiting-judge）。
- 新增 `tools/release/validate-control-plane.py`（audit/bootstrap）。
- 新增 `.codex/hooks/control_plane_gate.py`，接入 PreToolUse / PostToolUse / Stop / SubagentStop。
- 新增 `docs/aiprompts/judge-handoff.md`。
- 更新 AGENTS 与 dev-rules 的硬触发点。

### Worker 验证

- `python tools/release/validate-control-plane.py --mode all`：PASS。
- 模拟 PreToolUse 将 plan 标 `completed`：hook 返回 `permissionDecision=deny`。
- 未执行独立 Judge；hooks 需在 Codex `/hooks` 审查 trust 后才会在真实会话生效。

### Deviations

- 无。此前“披露缺口后仍 completed”已纠正为状态回退。


## 2026-07-14：独立 Judge 与 completed 收口

### 实际改动

- Orchestrator 以 `codex exec --ephemeral -s workspace-write` 启动独立只读 Judge（因测试需写临时目录；正式文件禁止编辑）。
- 首次 `TMPDIR` 误指仓库内 `.tmp-judge/` 导致 gate `work_dir must be outside target` 假失败 9 项；Judge 改用 `TMPDIR=/private/tmp` 后复验通过。
- Worker 机械转录 Judge Review；丢弃审查窗口中出现的未审正式文件改动（`run-independent-judge.py` 与 hooks/dev-rules 未暂存增量）；删除 `.tmp-judge/`。
- 按 Judge 低优先级建议去除 `AGENTS.md` 尾随空白。
- plan/roadmap 在 `Verdict: pass` 与 `validate-control-plane.py` 通过后标 `completed`。

### Worker 验证

- 复验：`python -m unittest discover -s tests -v`：32 passed。
- `python tools/release/validate-release-metadata.py`：PASS（version=1.0.0）。
- `python tools/release/validate-control-plane.py --mode all`：在追加 Judge Review 并改状态后重跑。

### Judge Review
- Verdict: pass
- 刚性约束违规：无。plan/roadmap 仍为 `awaiting-judge` / `active`，未假标 `completed`。
- 问题（按严重级别）：低：`git diff --check c89fefa` 在 `AGENTS.md:3` 报告尾随空白，故 progress 中“`git diff --check` 通过”的表述不准确。
- 缺失验证：未执行真实 Claude/Codex/npx marketplace 安装；未执行 analyzer G5 真实回归 UAT。两项均已正确披露，隔离 smoke 未被抬高为外部或真实回归证据。
- 建议复查范围：修复 `AGENTS.md` 尾随空白并更新 Worker 验证记录；审查期间新出现的 `tools/release/run-independent-judge.py` 与 `.tmp-judge/` 不在初始 Judge 基线内，应另行复查。
- 独立执行的验证及结果：`TMPDIR=/private/tmp python -m unittest discover -s tests -v`，32 passed；`python tools/release/validate-release-metadata.py`，PASS（`1.0.0`）；`python tools/release/validate-control-plane.py --mode all`，PASS。确认 gate/schema 仅在 `skills/repo-analyzer/`，`src/`、顶层 `acceptance/`、旧 schema 和 console script 均已移除；四 adapter 安装测试通过，且基于 `core-package-files.txt`。

### Deviations

- Judge 调度使用 workspace-write 沙箱以允许 unittest 临时目录写入；正式文件编辑被禁止。审查期间工作区曾短暂出现未审文件，Worker 收口前已删除/回退，不纳入本 plan 交付。
- 真实外部 marketplace 安装与 G5 仍未执行（与 plan 完成口径一致）。

### 阻塞与下一刀

- 无阻塞。
- 下一刀：发布前真实外部安装 + G5 真实回归 UAT（新 plan，如需要）。
