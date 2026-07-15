# Harness 导航清晰度与完成语义防误读 Roadmap

状态：`completed`

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义修正 ADR 索引漂移、完成语义一眼表、Graphify 无 wiki 措辞与 harness 防回退校验的方向与完成口径 |
| 当前状态 | `completed`；配对 plan Judge pass + audit |
| 当前结论/入口 | 修协作真源与完成语义可扫描性；不重做 harness P0 产品面 |
| 何时读取 | 审查本导航清晰度交付或改 ADR 索引/绿勾语义时 |
| 何时更新 | 目标、非目标或完成口径变化时 |
| 关联真源 | 本地 spec：`.scratch/harness-navigation-clarity/SPEC.md`；执行见 plan/progress；背景 ADR-0025/0028 |

## 北极星目标

维护者与 Agent 不会因过期 ADR 索引误判 0025 未实施，不会把 Judge/harness/安全扫描/Release 绿勾当成可 ship，且无 wiki 时有明确 Graphify 降级路径；索引回退可被 harness 契约校验机械抓住。

## 非目标

- 不跑真实回归 UAT、不公开发版、不触 marketplace
- 不改 analyzer 用户分析行为
- 不生成 graphify wiki；不新建 `docs/ai-harness/`
- 不把导航基建写入 Skill 核心交付包

## 可观察成功标准

1. ADR 索引：0025 在已实现基线；「尚未实施 + proposed」组合消失；基线含 0025/0028；marketplace/G5 边界仍可读。
2. Harness 校验对过期 0025 表述失败、对当前绿路径成功；单测覆盖。
3. AGENTS 与/或 version-release 有绿勾≠ship 短表；保留 Judge≠真实回归 UAT 硬句。
4. Graphify 文案：wiki 可选；不要求 wiki 文件。
5. 可选：安装包 ≠ 仓库基建一行边界。
6. 完整门 + 独立 Judge pass 后才可 `completed`；Judge pass ≠ 真实回归 UAT。

## 阶段

| 阶段 | 退出 |
|---|---|
| N1 索引与文档 | ADR/AGENTS/version-release/boundaries 按 tickets 落地 |
| N2 校验防回退 | validate-agent-harness + 单测 |
| N3 收口 | awaiting-judge → 独立 Judge → control-plane audit → completed |

## 完成口径

导航清晰度与机械防回退满足 tickets/SPEC 验收；不要求真实回归 UAT。

## 主线总结

修真源漂移与完成语义误读，不扩产品分析面。
