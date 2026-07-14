# GitHub v1.1.1 发布路线图

状态：`active`

执行计划：[github-v1.1.1-release-plan.md](../exec-plans/github-v1.1.1-release-plan.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义 `v1.1.1` 源码 Release 的目标、边界与完成口径 |
| 当前状态 | `active`；授权发布含发布前安全扫描门的 `v1.1.1` |
| 当前结论/入口 | 在 `main` 已含 pre-release security scan 规则的基础上发布 `v1.1.1` |
| 何时读取 | 修改发布元数据、打标签或创建 GitHub Release 时 |
| 何时更新 | 发布边界或版本号变化时 |
| 关联真源 | 版本见 `VERSION`；执行见 plan/progress；安全门见 [pre-release-security-scan](../dev-rules/pre-release-security-scan/README.md) |

## 北极星目标

将发布前密钥/敏感资料扫描规则随源码发布为 GitHub `v1.1.1`，版本元数据一致，且本发布自身先通过该安全门；发布说明不越级宣称产品 UAT。

## 非目标

- 不改变 analyzer 用户分析行为或 Graphify gate 合同。
- 不发布二进制/npm/PyPI 工件，不声称真实 marketplace 或 G5 真实回归 UAT 已通过。
- 不把安全扫描实现成强制 CI（规则已要求发布操作者手动执行，直到 CI 补齐）。

## 阶段与退出条件

| 阶段 | 退出条件 |
|---|---|
| S0 元数据 | `VERSION` 与 adapter/`package.json` 均为 `1.1.1`；CHANGELOG 与控制面已写 |
| S1 验证 | 单元测试、release/control-plane 校验通过；**发布前安全扫描 PASS** |
| S2 发布 | 远端 `main`、`v1.1.1` 标签与 GitHub Release 指向同一提交 |
| S3 收口 | progress 记录证据；独立 Judge 或用户书面豁免后 `completed` |

## 完成口径

GitHub 源码 Release `v1.1.1` 公开且元数据一致；发布前安全扫描 PASS 有 progress 证据；未执行的真实 marketplace/G5 在 notes 中披露。
