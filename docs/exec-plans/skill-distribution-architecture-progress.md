# Skill 原子交付架构进度记录

文档类型：`progress-log`

关联计划：
[`skill-distribution-architecture-plan.md`](skill-distribution-architecture-plan.md)

继承状态：关联 plan 当前为 `proposed`。

## 当前快照

- 当前阶段：D0 设计、控制面建立与激活前评审。
- 已完成：架构审计、逐项 grilling、领域词汇修正、目标目录与迁移边界确认、proposed 控制面建立、D0-2 执行合同补强。
- 未开始：gate/schema 迁移、plugin adapter、版本工具、测试重组、安装 UAT、旧入口删除。
- 阻塞：激活前仍需完成 D0-3 路径 diff 快照与文件所有权审计。
- 下一刀：执行 D0-3；审计通过并激活后，从 D1-0 核心包文件清单开始。

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
