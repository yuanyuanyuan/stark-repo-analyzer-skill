# Skill 原子交付架构路线图

状态：`completed`

执行计划：
[`skill-distribution-architecture-plan.md`](../exec-plans/skill-distribution-architecture-plan.md)

关键决策：
[`ADR-0025：以 Skill 核心交付包作为唯一分发真源`](../adr/0025-use-the-skill-bundle-as-the-single-distribution-source.md)

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 定义 repo-analyzer 从多套安装 interface 收敛到单一 Skill 核心交付包的目标、边界和阶段 |
| 当前状态 | `completed`；Skill 核心交付与 adapter 迁移已落地；真实外部 marketplace/G5 不在完成口径内 |
| 当前结论/入口 | 实现真源为 `skills/repo-analyzer/`；安装 adapter 见 Claude/Codex/npx/手动；gate 调用以 `SKILL_ROOT` 规则为准 |
| 何时读取 | 修改 Skill 目录、Claude/Codex plugin、gate 交付方式、版本或安装验收前 |
| 何时更新 | 支持运行时、交付包内容、迁移阶段或退出条件发生变化时 |
| 关联真源 | 术语见 `CONTEXT.md`，架构理由见 ADR-0025，产品行为见 `docs/spec/`，验收等级见 `docs/dev-rules/real-uat-regression/` |

## 北极星目标

让 Claude Code 与 Codex 通过不同安装 adapter 获得同一份可运行的 Skill 核心交付包。调用者只需理解 Skill 的分析 interface 和 bundled gate 的稳定调用方式，不再需要知道 Python package、完整仓库 checkout 或多套重复 metadata。

## 目标结果

- `skills/repo-analyzer/` 成为唯一 Skill 核心交付包，包含 `SKILL.md`、运行所需 references、`scripts/graphify_gate.py` 和 gate status schema。
- 仓库根保持单插件包；Claude 与 Codex 分别拥有 adapter manifest，但不复制 Skill 实现。
- Codex plugin 使用 `.codex-plugin/plugin.json`，Codex marketplace 使用 `.agents/plugins/marketplace.json`；Claude 保留独立 manifest 与 marketplace 文件。
- gate 的稳定调用方式收敛为 `python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>`。
- 调用 gate 的 Agent/宿主负责在构造命令前解析 `SKILL_ROOT`；唯一来源是当前实际加载的 `SKILL.md` 绝对路径，其父目录就是 `SKILL_ROOT`。它不是传给 gate 的 CLI 参数。宿主无法提供来源路径时必须在启动子进程前给出可操作错误并停止，不得猜测 plugin 根、当前工作目录、完整仓库根或 `src/`。
- Python `3.10+` 与 Graphify CLI 都是外部依赖；Skill 负责检测、解释和用户选择，不打包解释器或自动安装依赖。
- 根 `VERSION` 是唯一版本真源，根 `CHANGELOG.md` 记录发布变化；D2 先用轻量校验确认各 adapter 投影一致，完整 metadata renderer 只有出现真实重复维护成本后才进入 P1。
- `tools/release/core-package-files.txt` 冻结四种安装方式必须共同交付的文件级合同，安装测试只依据这份清单判断等价，不把整个仓库 checkout 当作核心包。
- 验证结构收敛为 `tests/unit/`、`tests/contract/` 和 `tests/install/`；静态文案匹配不再冒充产品行为验收。
- README 的正式支持范围只包含 Claude Code 与 Codex，不再承诺 OpenClaw 或所有 Skills 运行时。

## 非目标

- 本路线图不改变 repo-analyzer 的 `standard`、`deep`、覆盖率、Graphify 证据边界或单一报告合同。
- gate 迁移阶段不按文件长度拆分其 deep module，不同时重写内部阶段或失败分类。
- 不发布本仓库自己的 npm package，不继续公开 Python wheel 或 console script；`package.json` 是否保留为 npx/Skills 生态的最小 identity 文件由真实安装证据决定。
- 不新增 `plugins/repo-analyzer/` 复制树，也不强迫 Claude 与 Codex 共用同一 marketplace schema。
- 不把 `docs/`、`tests/`、`vendor/` 或发布工具纳入 Skill 核心交付包。
- proposed 状态不授权删除 `src/`、`acceptance/`、`package.json` 或旧调用方式。

## 目标目录

```text
repo-analyzer/
├── .claude-plugin/
├── .codex-plugin/
│   └── plugin.json
├── .agents/plugins/
│   └── marketplace.json
├── skills/repo-analyzer/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── graphify_gate.py
│   └── references/
│       └── contracts/
│           └── graphify-gate-status.schema.json
├── tests/
│   ├── unit/
│   ├── contract/
│   └── install/
├── tools/release/
│   ├── core-package-files.txt
│   └── validate-release-metadata.py
├── docs/
├── vendor/
├── VERSION
├── CHANGELOG.md
├── package.json                     # 可选；由 npx 安装证据决定保留或删除
├── pyproject.toml
├── README.md
├── README.zh.md
└── CONTEXT.md
```

`pyproject.toml` 只承载开发工具配置，不再声明可发布 Python 产品或 console script。上图中的 `package.json` 是证据驱动的候选 identity 文件，不代表终态必然保留。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| D0 合同与控制面 | 固定支持范围、交付词汇、目标目录和迁移边界 | roadmap、plan、progress、ADR 与索引接入完成；当前/目标行为区分明确 |
| D1 核心交付包 | 无行为变化地迁移 gate 与 status schema | 唯一 `SKILL_ROOT` 规则、核心包文件清单、新 gate、thin shim、测试 import 和 schema 单真源同时落地；原 gate 单元行为通过 |
| D2 安装与发布 adapter | 接入 Claude/Codex manifests、marketplace、版本与发布 metadata | 四种安装方式得到等价核心包；所有 manifest 版本与根 `VERSION` 一致 |
| D3 验证与旧入口收口 | 重组测试、执行安装 UAT，并删除不再需要的交付入口 | unit/contract/install 通过；发布前真实安装 smoke 有证据；旧 `src/`、`acceptance/` 与 console interface 才可删除；`package.json` 按 npx 证据删除或收缩 |

## 验收边界

- 日常 CI 只证明 manifest、渲染结果、核心包文件和 gate 行为；它不能证明外部 marketplace 安装成功。
- 发布前分别真实执行 Claude Plugin、Codex Plugin、`npx skills add` 和手动安装，并在隔离环境检查 Skill 发现、gate 启动和 status schema。
- 每个安装 adapter 固定执行五步：隔离安装、定位 `SKILL.md`、按唯一规则解析 `SKILL_ROOT`、对 fixture target 启动 gate、用 bundled schema 校验终态。
- Claude Code 与 Codex 是正式支持的运行时；Claude Plugin、Codex Plugin、`npx skills add` 和手动安装只是四种安装 adapter。四种安装通过不扩张运行时支持范围。
- analyzer 产品的聚焦 UAT 与真实回归 UAT 仍遵守 `docs/dev-rules/real-uat-regression/README.md`，不能由安装 smoke 替代。
- 未执行某个安装 adapter 时，只能报告其他 adapter 的实际结果，不能声明完整安装矩阵通过。

## 激活条件

维护者确认开始实现后，才把本 roadmap 与关联 plan 同时改为 `active`。激活前必须对 `skills/`、`src/`、`tests/`、`acceptance/` 和 plugin manifest 路径建立 diff 快照与文件所有权清单，确认 D1 不覆盖用户已有改动；不要求工作树干净、提交或 reset。激活同一刀必须更新目录索引，并在 progress 写明第一阶段、所有权范围和下一刀；在此之前不得依据本文件执行迁移。

README 已收缩到 Claude Code 与 Codex 正式支持范围；OpenClaw 与“所有 Skills 运行时”承诺已移除。

## 收口说明（尚未 completed）

- 阶段 D0-D3 的必需实现与仓库内验证已完成。
- 已执行：unit/contract/install、核心包清单校验、release metadata 校验、四种 adapter 的隔离五步 smoke。
- 未执行：Claude/Codex/npx 在真实宿主 marketplace 中的外部安装，以及 analyzer 真实回归 UAT（G5）。这些不能由隔离 smoke 提升证据等级。
- 完成度分母：roadmap 阶段 4/4；plan P0 必需任务 14/14。真实外部 marketplace 与 G5 不计入本 initiative 完成分母。

## 主线总结

一个 deep Skill 核心交付包现在服务 Claude、Codex、npx 与手动四类安装 adapter。后续发布宣称前仍需按 real-uat-regression 执行外部安装与真实回归。
