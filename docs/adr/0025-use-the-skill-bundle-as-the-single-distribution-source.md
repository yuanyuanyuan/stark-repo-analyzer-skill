# 以 Skill 核心交付包作为唯一分发真源

状态：`accepted`

## 决策

`skills/repo-analyzer/` 是 repo-analyzer 唯一的 Skill 核心交付包，必须自包含 `SKILL.md`、运行所需 references、bundled Graphify gate 和 gate status schema。仓库根保持单插件包，Claude Code 与 Codex 通过各自 manifest 和 marketplace adapter 指向同一核心包，不复制 Skill 实现。

gate 的稳定调用 interface 是：

```text
python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>
```

`SKILL_ROOT` 只表示当前被加载的 `SKILL.md` 所在目录。调用 gate 的 Agent/宿主负责从该文件的绝对路径解析它，随后把解析结果写入命令路径；`SKILL_ROOT` 不是 gate 的 CLI 参数。宿主无法提供 Skill 来源路径时必须在启动子进程前停止并给出可操作错误，不允许依次猜测 plugin 根、当前工作目录、完整仓库 checkout 或 `src/`；否则新 interface 仍会泄漏安装布局。

Python `3.10+` 与 Graphify CLI 都是外部依赖。项目不再把 Python wheel、console script、npm package 或完整仓库 checkout 作为 gate 可用性的前提。正式支持范围只包括 Claude Code 与 Codex，不承诺 OpenClaw 或所有 Skills 运行时。

根 `VERSION` 保存唯一产品版本，根 `CHANGELOG.md` 保存发布记录；维护侧先用轻量校验保证不同 adapter 的版本投影一致，只有出现真实重复维护成本后才引入 metadata renderer。机器合同随 Skill 交付，`docs/spec/` 负责解释和链接，而不保留第二份 schema。

## 原因

当前 Skill 会调用只由 `pyproject.toml` 暴露的 gate，但推荐的 Skill/plugin 安装方式不必然安装 Python package。调用者因此需要理解 console script、`PYTHONPATH`、仓库根和源码布局，交付 seam 泄漏到 Skill interface。

Claude 与 Codex 是两个真实 adapter，值得保留各自 schema；它们应复用同一 deep Skill module，而不是通过复制目录获得兼容。把运行资产放回 Skill 目录，也符合 Skill 以 `SKILL.md`、scripts 和 references 形成可移植工作流的结构。

## 备选方案

- 继续以 Python package 为 gate 真源：拒绝，因为它要求第二次安装，并让 Skill 安装与运行能力分离。
- 为 Claude 与 Codex 分别复制完整 plugin 目录：拒绝，因为实现和机器合同会漂移，locality 更差。
- 让两个运行时共用一个 marketplace 文件：拒绝，因为 adapter schema 与必需字段不同；统一发布 metadata 足以避免事实漂移。
- 把 gate 按内部函数拆成多个公开 module：暂不采用；现有外部 interface 已经 deep，交付迁移不应同时改变实现 seam。
- 继续承诺 OpenClaw 和所有 Skills 运行时：拒绝，因为当前没有对应的安装与验收证据。

## 影响

- 未来迁移会在四种安装 adapter 验证后删除 `src/`、公开 Python console command、顶层 `acceptance/` 和临时 thin shim。`package.json` 不预设删除：真实 npx 安装不依赖它时删除，存在依赖时收缩为最小 identity 文件。
- `pyproject.toml` 可以继续承载开发工具配置，但不再声明可发布产品或版本。
- tests 将通过 gate interface、status schema 和实际安装结果验证产品；固定中文句子匹配只保留少量 lint 角色。
- D1 必须先冻结核心包文件清单，并用 thin shim 证明新旧入口同输入具有相同 code 和关键 status 字段；不能把“旧入口暂留兼容”只写成计划口号。
- 关联 roadmap/plan 已完成迁移：Skill 核心交付包、Codex/Claude adapter、`SKILL_ROOT` 调用规则与 schema 单真源已落地。真实外部 marketplace 安装与 G5 真实回归仍属发布前工作，不由本 ADR 单独证明。

## 取代关系

本 ADR 不取代 ADR-0016 至 ADR-0024 的 Graphify、控制面、兼容流程或验收决定；它细化 ADR-0017 所保留 Graphify gate 的交付 seam，不改变该 gate 的控制面职责。
