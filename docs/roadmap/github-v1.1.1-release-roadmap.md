# GitHub v1.1.1/v1.1.2 发布路线图

状态：`completed`

执行计划：[github-v1.1.1-release-plan.md](../exec-plans/github-v1.1.1-release-plan.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义 pre-release security scan 源码 Release（`v1.1.1` 初版 + `v1.1.2` 纠正）的目标、边界与完成口径 |
| 当前状态 | `completed`；完成口径 **`v1.1.2` 纠正发布**（`v1.1.1` 时序缺口已披露；独立 Judge pass） |
| 当前结论/入口 | 可安装纠正版本为 `v1.1.2`（`main`/tag/Release 同提交；先扫后 tag） |
| 何时读取 | 修改发布元数据、打标签或创建 GitHub Release 时 |
| 何时更新 | 发布边界或版本号变化时 |
| 关联真源 | 版本见 `VERSION`；执行见 plan/progress；安全门见 [pre-release-security-scan](../dev-rules/pre-release-security-scan/README.md) |

## 北极星目标

将发布前密钥/敏感资料扫描规则随源码发布；因 `v1.1.1` 在完整全历史扫描证据完成前已打 tag，完成口径改为 GitHub **`v1.1.2` 纠正发布**：版本元数据一致、**先**完成工作树+全历史 gitleaks PASS **再** tag/Release；发布说明披露 `v1.1.1` 时序缺口且不越级宣称产品 UAT。

## 非目标

- 不改变 analyzer 用户分析行为或 Graphify gate 合同。
- 不发布二进制/npm/PyPI 工件，不声称真实 marketplace 或 G5 真实回归 UAT 已通过。
- 不把安全扫描实现成强制 CI（规则已要求发布操作者手动执行，直到 CI 补齐）。

## 阶段与退出条件

| 阶段 | 退出条件 |
|---|---|
| S0 元数据 | 纠正发布：`VERSION` 与 adapter/`package.json` 均为 `1.1.2`；CHANGELOG 记录 v1.1.1→v1.1.2 |
| S1 验证 | 单元测试、release/control-plane 校验通过；**打 tag 前**安全扫描 PASS |
| S2 发布 | 打 tag 当刻远端 `main`、`v1.1.2` 标签与 GitHub Release 指向同一提交；收口文档可后推 `main` |
| S3 收口 | progress 记录证据与 v1.1.1 时序披露；独立 Judge 或用户书面豁免后 `completed` |

## 完成口径

GitHub 源码 Release **`v1.1.2`** 公开且元数据一致；先扫后 tag 的安全扫描 PASS 有 progress 证据；发布提交上 tag/Release 与当时 main 一致（收口文档提交可不在 tag 上）；`v1.1.1` 时序缺口已披露；未执行的真实 marketplace/G5 在 notes 中披露。
