# Skill 原子交付架构执行计划

状态：`completed`

Roadmap：
[`skill-distribution-architecture-roadmap.md`](../roadmap/skill-distribution-architecture-roadmap.md)

进度记录：
[`skill-distribution-architecture-progress.md`](skill-distribution-architecture-progress.md)

关键决策：
[`ADR-0025`](../adr/0025-use-the-skill-bundle-as-the-single-distribution-source.md)

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 定义 Skill 原子交付迁移的顺序、所有权、验证和删除门 |
| 当前状态 | `completed`；独立 Judge `Verdict: pass`；未执行真实外部 marketplace 与 G5，已披露 |
| 当前结论/入口 | 先读 progress 最新快照；未执行真实外部 marketplace 与 G5 回归 |
| 何时读取 | 准备迁移 gate、plugin manifests、版本、测试或旧入口时 |
| 何时更新 | 任务顺序、依赖、输出、验证或阻塞发生变化时 |
| 关联真源 | 方向见 roadmap，原因见 ADR-0025，实际事实见 progress，当前产品行为见 spec |

## 启动关

- 质量门：完整门
- 独立Judge：必须（已 pass）
- 收口阶段：completed
- CLOSE-J1：独立 Judge 只读审查并写入 progress（完成）
- CLOSE-J2：validate-control-plane 通过后 completed（完成）

## 当前主线

主目标：把 `skills/repo-analyzer/` 深化为自包含的 Skill 核心交付包，让 Claude Code 与 Codex adapter 共享同一实现和机器合同。

当前阶段：`completed / D3`。Worker 实现、隔离 smoke 与独立 Judge 均已完成。

下一刀：本 plan 无后续；发布前真实外部安装与 G5 真实回归 UAT 如需执行，另开 plan。

## 执行约束

- 当前工作树包含大量用户已有改动；每刀先执行 `git status --short`，只修改该刀拥有的文件。
- D1 只改变交付位置，不拆分 gate 的 deep module，不重写状态语义。
- 调用 gate 的 Agent/宿主必须在构造命令前，从当前实际加载的 `SKILL.md` 绝对路径解析 `SKILL_ROOT`；它不是 gate 的 CLI 参数。宿主无法提供来源路径时，必须在启动子进程前停止并给出可操作错误，禁止猜测 plugin 根、`cwd`、完整仓库根或 `src/`。
- 旧入口的删除必须晚于 Claude、Codex、npx 和手动安装的等价性验证。
- D1 使用 thin shim 保留旧 Python module/console 路径；shim 只委托新 gate，不复制实现，并在 D3-3 与对应对照测试一起删除。
- `tools/release/core-package-files.txt` 是安装等价性的文件级真源；不得用“完整 checkout 看起来相同”代替清单断言。
- 当前 spec 在实现完成前继续描述现行行为；目标行为不能提前伪装成已交付合同。
- 任何 analyzer Skill、Graphify gate 或验收语义变化都要遵守真实 UAT 规则。
- 日常测试、安装 smoke、聚焦 UAT 和真实回归 UAT 必须分别报告，不能互相提高证据等级。
- Claude Code 与 Codex 是支持运行时；Claude Plugin、Codex Plugin、npx 和手动安装是安装 adapter。adapter 验证不得被表述成新增运行时支持。

## P0 必需任务

| ID | 任务 | 依赖 | 所有权与输出 | 验证 | 状态 |
|---|---|---|---|---|---|
| D0-1 | 建立 proposed 控制面与领域词汇 | - | roadmap、plan、progress、ADR、`CONTEXT.md`、目录索引 | 链接、状态唯一性、`git diff --check` | 完成 |
| D0-2 | 补齐激活前执行合同 | D0-1 | 唯一 `SKILL_ROOT`、D1 shim、核心包清单、测试矩阵、证据驱动删除门 | roadmap/plan/ADR 一致性检查 | 完成 |
| D0-3 | 建立路径所有权与 diff 快照 | D0-2 | `skills/`、`src/`、`tests/`、`acceptance/`、manifest 的已有改动清单和本 initiative 所有权 | 无需干净工作树；每个重叠文件都有保留/合并策略 | 完成 |
| D1-0 | 冻结核心包文件级合同 | D0-3、控制面激活 | `tools/release/core-package-files.txt`，逐项列出 `SKILL.md`、gate、schema 和全部运行所需 references | 清单只覆盖核心包；无隐式目录或完整 checkout 依赖 | 完成 |
| D1-1 | 迁移 gate 并建立 thin shim | D1-0 | 新 `scripts/graphify_gate.py`、旧 `src/.../graphify_gate.py` thin shim、`tests/test_graphify_gate.py` import 更新 | 改 import 后现有 gate unit 全部通过；新旧入口同输入返回同 code/关键 status 字段 | 完成 |
| D1-2 | 切换机器合同唯一真源 | D1-1 | 有意将 `docs/spec/graphify-gate-status-schema.json` 移动并改名为 `skills/repo-analyzer/references/contracts/graphify-gate-status.schema.json`；spec 改为 link-only；同步 `tests/test_graphify_gate.py`、`acceptance/skill-contract-check.sh` 与核心包清单 | `run_gate` 真实产生的 `0/10/30` 三类终态通过 bundled schema；旧文件名和第二份 schema 正文均不存在 | 完成 |
| D1-3 | 更新 Skill 调用与 contract check | D1-1、D1-2 | bundled script 调用；Agent/宿主从当前 `SKILL.md` 绝对路径解析 `SKILL_ROOT`；无法解析时在子进程前失败；更新 Python/Graphify 分支并移除 console/`PYTHONPATH` 文案依赖 | contract check 不再锁死旧路径；正向用例验证构造绝对 gate 命令，负向用例验证不构造命令、不启动子进程且不尝试任何 fallback | 完成 |
| D2-0 | 固定 adapter 规范依据 | D1-3 | Claude/Codex 官方 manifest 文档、最小字段表和实际 validator/校验命令写入任务记录 | 每个字段和命令可追溯；不得凭记忆发明 schema | 完成 |
| D2-1 | 建立最小版本真源 | D2-0 | 根 `VERSION`、`CHANGELOG.md`、轻量版本一致性校验脚本 | Claude/Codex/marketplace 版本投影与 `VERSION` 一致 | 完成 |
| D2-2 | 接入 Codex plugin adapter | D2-1 | `.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json` | 按 D2-0 固定的官方依据校验；临时安装发现 Skill | 完成 |
| D2-3 | 对齐 Claude、npx 与手动 adapter | D2-1 | `.claude-plugin/`、README、npx 与手动安装说明；记录 npx 对 `package.json` 的真实依赖 | 四种方式按核心包清单得到等价文件；明确 `package.json` 保留/删除证据 | 完成 |
| D3-1 | 重组验证目录与旧 acceptance | D2-2、D2-3 | `tests/unit/`、`tests/contract/`、`tests/install/`；逐项标明旧 acceptance 保留为 lint、改写为行为测试或删除 | 单一测试入口；正常文案改写不破坏核心行为验收 | 完成 |
| D3-2 | 执行发布前安装 UAT | D3-1 | Claude、Codex、npx、手动安装的隔离运行证据 | 每个 adapter 完成隔离安装→定位 Skill→解析根→启动 gate→schema 校验五步 | 完成 |
| D3-3 | 删除旧交付入口 | D3-2 | 删除 `src/`、顶层 `acceptance/`、console script 和 thin shim；`package.json` 按证据删除或收缩 | 引用扫描、测试、四 adapter smoke；删除 shim 时同步删除新旧入口对照测试 | 完成 |
| D3-4 | 同步公开合同与收口证据 | D3-3 | README 双语、spec、dev-rules、plan/progress 状态 | 链接、合同、测试；未执行真实回归时明确披露 | 完成 |

## 阶段验证矩阵

| 阶段 | 必跑验证 | 证明范围 |
|---|---|---|
| D1-1 | 改 import 后的现有 gate unit；新 gate 与 thin shim 同输入对照 | 位置迁移没有改变 code 和关键 status 语义 |
| D1-2 | 由 `run_gate` 在现有 fixture/patch 场景中产生的 `0/10/30` 终态进行 schema 验证 | bundled schema 约束真实实现输出；不接受只手写三个成功样本 |
| D1-3 | Skill 调用 contract check 与 `SKILL_ROOT` 成功/失败聚焦测试 | Agent/宿主是解析责任方；成功时构造绝对 gate 命令，缺少当前 Skill 来源路径时在子进程前失败且不尝试 fallback |
| D2 | 版本一致性、manifest 官方校验、临时安装发现 Skill | adapter 不复制实现，版本与最小字段不漂移 |
| D3-2 | 四个 adapter 的隔离安装五步清单 | 实际安装得到核心包并能启动 gate、读取 schema |
| 发布/G5 | `docs/dev-rules/real-uat-regression/` 定义的真实回归 UAT | analyzer 用户分析合同；不由安装测试替代 |

`tests/install/` 的每个用例必须记录隔离根、实际安装命令、发现的 `SKILL.md` 路径、解析出的 `SKILL_ROOT`、gate 命令与退出码、schema 校验结果。任何仍支持的旧入口在删除前都必须参加新旧对照；删除入口时同步删除该对照测试，不能留下永远通过的假兼容门。

## P1 后续改进

- 单独评估 gate 内部终态构造 module 与 `doctor()` shallow seam，不与交付迁移混做。
- 评估是否需要 `plugin-metadata.json` 与 manifest renderer；D2 先只做 `VERSION` 和投影一致性校验，没有实际重复成本前不新增生成框架。
- 在真实使用证据出现后，再决定是否发布到更广泛的公共插件目录。

## 失败与人工决策

- 任一安装 adapter 无法包含 bundled gate 时，停止删除旧入口，先修复交付 seam。
- Claude 与 Codex marketplace schema 不能由同一文件同时合法表达时，保留两个 adapter 文件，不以复制 Skill 实现换取表面统一。
- Python 解释器或 Graphify 缺失属于依赖不可用分支，不得被记录为 gate 执行成功。
- 发现真实外部自动化依赖旧 console command 时，暂停 D3-3，由维护者决定限期 shim 与移除版本。
- npx 安装需要 `package.json` 时，将其收缩为最小 identity 文件并保留；不得为符合目标目录图而破坏真实安装 adapter。
- 工作树已有改动与任务文件重叠且无法安全合并时，记录阻塞并请求维护者裁决，不覆盖用户内容。

## 激活与收尾

本 plan 只有被同状态 `active` roadmap 引用后才能转为 `active`。激活前必须完成 D0-3，证明相关路径可审计；不要求工作树干净或提交。每刀结束必须追加 progress，记录实际完成、实际验证、未执行项、阻塞和下一刀；不得依据任务表把未验证工作标成完成。
