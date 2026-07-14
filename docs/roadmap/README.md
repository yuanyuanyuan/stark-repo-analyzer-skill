# Roadmap 目录

本目录存放产品和架构方向文档。roadmap 可以直觉地理解为“目的地和沿途关卡”，它回答为什么做、做到什么程度以及哪些不做；类比的边界是，roadmap 不是每日行程表，不能承载逐文件操作日志。

## 快速入口

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 定义方向、目标、非目标、阶段和完成口径 |
| 当前状态 | 当前无 `active`；最近完成 [GitHub v1.1.1/v1.1.2 发布](github-v1.1.1-release-roadmap.md)、[GitHub v1.1.0 发布](github-v1.1.0-release-roadmap.md) 与 [代码地图导航](code-map-navigation-roadmap.md) |
| 人类怎么读 | 先看“北极星目标、非目标、当前阶段、完成口径” |
| Agent 怎么读 | 先解析生命周期；只有 `active` roadmap 才能授权沿链接执行，`completed` 只提供最近完成背景 |
| 何时更新 | 目标、边界、阶段或阶段退出条件发生变化时 |
| 关联真源 | 产品行为回到 `docs/spec/`，架构理由回到 `docs/adr/`，实际进度回到 `docs/exec-plans/` |

## 应包含什么

一份 roadmap 必须定义：

- 当前 initiative，也就是这项持续工作的主题，以及它要解决的问题；
- 目标结果和可观察的成功标准；
- 明确的非目标与产品边界；
- 阶段、依赖和阶段退出条件；
- 验收边界，以及权威 spec 或 ADR 的链接。

roadmap 不能变成命令日志、逐文件实现清单或日常进度记录，这些内容属于 exec plan 和 progress。

## 状态合同

每份 roadmap 必须在标题附近声明一种状态：

- `proposed`：仍在讨论，尚未授权实现；
- `active`：当前获得授权的方向；
- `completed`：目标结果和必需验收均已完成；
- `superseded`：已被另一份具名 roadmap 或决策取代。

仓库主线只能有一份 `active` roadmap。新 roadmap 取代旧文档时，双方都要互相链接，并由旧文档明确声明 `superseded`。

## 命名

initiative 使用 `{主题}-roadmap.md`；只有某个阶段需要独立负责的方向文档时，才使用 `{主题}-{阶段}-roadmap.md`。

## 创建与维护

创建新 roadmap 时：

1. 先以 `proposed` 状态写清目标、非目标、可观察结果和阶段退出条件。
2. 链接需要约束的 spec 与关键 ADR；不要在 roadmap 内复制合同正文。
3. 获得维护者确认后才改为 `active`，同时创建或指定对应 exec plan。
4. 如果取代旧方向，新旧文档互相链接，旧文档标记 `superseded`。

维护期间只修改方向性事实。每日进度、命令输出、文件清单和失败日志写入 progress；公开产品行为变化则同步修改 spec，不能只改 roadmap。

## 最近完成 Roadmap

- [`graphify-simplification-roadmap.md`](graphify-simplification-roadmap.md)：已完成 G0-G4 实施主线。
- [`github-v1-release-roadmap.md`](github-v1-release-roadmap.md)：已 `completed`；覆盖首次 `v1.0.0` GitHub 源码 Release 与公开边界（真实外部 marketplace 另计）。
- [`skill-distribution-architecture-roadmap.md`](skill-distribution-architecture-roadmap.md)：已 `completed`；真实外部 marketplace 与 G5 不在该完成口径内。

当前无活动 roadmap。最近完成含 [`github-v1.1.1-release-roadmap.md`](github-v1.1.1-release-roadmap.md)（`v1.1.2` 纠正发布）与 [`github-v1.1.0-release-roadmap.md`](github-v1.1.0-release-roadmap.md)。被取代的目标文档保留在 `docs/archive/v1-control-plane/`。

## 最近完成（本轮）

- [`github-v1.1.1-release-roadmap.md`](github-v1.1.1-release-roadmap.md)：`completed`；pre-release security scan 门 + `v1.1.2` 纠正源码 Release（`v1.1.1` 时序缺口已披露）。
- [`code-map-navigation-roadmap.md`](code-map-navigation-roadmap.md)：`completed`；产品功能→分层→源码入口的代码地图、dev-rule、AGENTS 导航与提醒 hook。
- [`default-judge-review-roadmap.md`](default-judge-review-roadmap.md)：默认独立 Judge、审查包、调度边界与验证已完成。

## 主线总结

roadmap 管方向和完成边界，不管每日动作。它必须唯一、可验收，并把操作细节交给 exec plan。
