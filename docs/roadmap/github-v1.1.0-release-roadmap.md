# GitHub v1.1.0 发布路线图

状态：`completed`

执行计划：[github-v1.1.0-release-plan.md](../exec-plans/github-v1.1.0-release-plan.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义 `v1.1.0` 源码 Release 的目标、边界与完成口径 |
| 当前状态 | `completed`；GitHub `v1.1.0` 源码 Release 已公开 |
| 当前结论/入口 | 在 `main` 已含 code-map 与默认 Judge 的基础上发布 `v1.1.0` |
| 何时读取 | 修改发布元数据、打标签或创建 GitHub Release 时 |
| 何时更新 | 发布边界或版本号变化时 |
| 关联真源 | 版本见 `VERSION`；执行见 plan/progress；产品合同未改 |

## 北极星目标

将 `1.0.0` 之后已完成的协作基建（默认 Judge、代码地图导航与提醒 hook）随源码发布为 GitHub `v1.1.0`，版本元数据一致，发布说明不越级宣称产品 UAT。

## 非目标

- 不改变 analyzer 用户分析行为或 Graphify gate 合同。
- 不发布二进制/npm/PyPI 工件，不声称真实 marketplace 或 G5 真实回归 UAT 已通过。
- 不把 code-map 打进 Skill 核心交付包清单。

## 阶段与退出条件

| 阶段 | 退出条件 |
|---|---|
| S0 元数据 | `VERSION` 与 adapter/`package.json` 均为 `1.1.0`；CHANGELOG 已写 |
| S1 验证 | 单元测试与 release/control-plane 校验通过 |
| S2 发布 | 远端 `main`、`v1.1.0` 标签与 GitHub Release 指向同一提交 |
| S3 收口 | progress 记录证据；独立 Judge 或用户书面豁免后 `completed` |

## 完成口径

GitHub 源码 Release `v1.1.0` 公开且元数据一致；未执行的真实 marketplace/G5 在 notes 中披露。
