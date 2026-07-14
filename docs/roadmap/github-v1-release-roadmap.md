# GitHub v1.0.0 发布路线图

状态：`active`

执行计划：
[github-v1-release-plan.md](../exec-plans/github-v1-release-plan.md)

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 定义首次公开 GitHub Release 的目标、边界、阶段与退出条件 |
| 当前状态 | `active`；维护者已确认执行 |
| 当前结论/入口 | 从 `main` 发布 `v1.0.0` 源码型 GitHub Release；统一分发地址与 README 来源致谢 |
| 何时读取 | 准备修改发布元数据、执行真实安装验证、提交、推送、打标签或创建 Release 时 |
| 何时更新 | 发布边界、阶段、支持范围或退出条件变化时 |
| 关联真源 | 产品合同见 `docs/spec/`；发布版本见 `VERSION`；执行事实见关联 progress |

## 北极星目标

将当前已验证的 Skill 核心交付包以 `yuanyuanyuan/stark-repo-analyzer-skill` 的唯一公开身份发布为 GitHub `v1.0.0` 源码 Release，并让公开入口清晰致谢 MIT 参考项目 `yzddmr6/repo-analyzer`。

## 非目标

- 不发布 npm 包、Python wheel、二进制或额外 Release 附件。
- 不把真实 Claude/Codex marketplace 上架、外部 marketplace 安装或 G5 真实回归 UAT 表述为已通过。
- 不扩张正式支持范围；仍只支持 Claude Code 与 Codex。
- 不修改分析模式、Graphify gate 或产品行为合同。

## 阶段与退出条件

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| R0 激活与身份收敛 | 建立任务边界、统一公开 identity、补来源致谢 | roadmap/plan 为 `active`，README 与发布 metadata 不再指向旧 identity |
| R1 发布前验证 | 复验核心包、元数据与真实可执行的安装路径 | 所有实际运行验证有记录；未运行项明确保留 |
| R2 GitHub Release | 提交候选、推送 `main`、创建并验证 `v1.0.0` Release | 远端标签与 GitHub Release 指向同一提交，发布说明无越级宣称 |
| R3 审查收口 | 独立 Judge 审查发布增量与证据 | Judge `pass` 后依控制面规则完成收口 |

## 发布声明边界

该 Release 仅说明 GitHub 源码发布完成、仓库内验证和实际执行的外部验证结果。真实外部 marketplace 安装与 G5 真实回归 UAT 若未执行，必须在 Release Notes、progress 与最终交接中明确列为未验证项。

## 主线总结

本路线图发布已确认的 `v1.0.0` 源码候选，不将未执行的 marketplace 或真实回归包装为通过。激活后才允许进行任何 GitHub 写操作。
