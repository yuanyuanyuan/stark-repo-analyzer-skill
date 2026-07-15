# Agent Boundaries · 硬规则、边界、暂停

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 索引式收敛「立刻要遵守/要停」的边界；**不**复制各 dev-rules 细则正文 |
| 当前状态 | `active` |
| 当前结论/入口 | 先扫硬规则与暂停条件；细则点真源链接 |
| 何时读取 | 不确定能否改某类文件、是否该暂停、或收口是否越权时（按需，非每次通读） |
| 何时更新 | 新增仓库级硬边界或暂停条件时；细则变更优先改真源再改本索引一行 |
| 关联真源 | 各行链接的 dev-rules / ADR；编排见 [workflows](../workflows/README.md)；包装决策 [ADR-0028](../../adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md) |

## 1. 硬规则（违反即停或立即纠正）

| 规则 | 真源 |
|---|---|
| `AGENTS.md` 只做路由，细则下沉 | 根 `AGENTS.md`、document-control |
| 只有 `active` 控制面能授权跨轮实施；`completed` 只作背景 | document-control、roadmap/plan |
| 默认 Delivery Task 须独立 Judge；禁止 Worker 自过 `completed` | dual-agent-review、ADR-0026 |
| Judge 廉价本地检查须独立重跑；不得以沙箱为由采信 Worker 后 pass | dual-agent-review |
| 真实回归 UAT 证据上限不得用聚焦 UAT / 静态扫描冒充 | real-uat-regression |
| 密钥与敏感资料不上 git；发版前安全扫描 | pre-release-security-scan、version-release |
| Graphify 结构问题优先 graphify query/path；改代码后 `graphify update .` | 根 AGENTS Graphify 路由 |
| 源码裁决产品结论；图谱只导航 | CONTEXT、skill 合同 |
| subagent 降级须用户明确同意，禁止静默 | ADR-0024、skill |
| 不自动安装 Graphify / 不代替用户选兼容流程 | ADR-0021 |
| archive / baseline / vendor 默认不改 | document-control、AGENTS |
| 代码地图 YAML 唯一路径真源；不进 Skill 核心包 | code-map 规则、ADR-0027 |
| harness 导航不平行 `docs/ai-harness/`；不进核心包 | ADR-0028 |
| 改 harness 导航相关文件后必须跑 `validate-agent-harness.py` | workflows、ADR-0028 |
| README 英/中产品入口行为合同同步 | output-style、根 README 约定 |

## 2. 边界表

| 范围 | 状态 | 说明 |
|---|---|---|
| `skills/repo-analyzer` 用户可见行为 | ⚠️ 先合同后实现 | 同步 spec/测试/验收规则 |
| `docs/spec` 行为合同 | ⚠️ 高风险 | 与实现同交付 |
| `docs/archive`、`tests/baseline`、`vendor` | ❌ 默认禁止 | 除非活动控制面明确重新引入 |
| Skill 核心交付清单 | ⚠️ 慎改 | 见 `tools/release/core-package-files.txt` / `skills/repo-analyzer/`；≠ 全仓 docs/dev-rules/code-map/harness 校验——导航基建不进安装面（ADR-0027/0028） |
| 用户已有、任务范围外改动 | ❌ 禁止擅自改 | 审查包排除 |
| 公开发版 tag/Release | ⚠️ 走 version-release SOP | 禁止跳步 |
| 平行 `docs/ai-harness/` | ❌ 禁止 | ADR-0028 |
| 新建第三套计划格式替代 plan/progress | ❌ 禁止 | task-quality-gates |
| PreToolUse 因 harness/map 过期 deny 编辑 | ❌ 默认不做 | 提醒型；ADR-0027/0028 |

## 3. 暂停条件

遇到任一条，**停止当前执行路径**并向用户或 Orchestrator 暴露：

1. 产品行为未在 active 合同/授权控制面中，却要改用户可见语义。
2. 活动 roadmap/plan/spec 互相冲突且无法判断真源。
3. 工作区有相关未归属改动，无法划分拥有范围。
4. 审查包缺字段，无法启动合规 Judge。
5. 需要真实密钥操作、破坏性删数据、或用户未授权的外部发布。
6. subagent 不可用且用户尚未选择继续/停止。
7. Graphify 增强已开始后失败——不得静默切兼容。
8. **Same-Type Failure Design Gate**：同一根因类别连续失败 ≥2 次——回 Thinking 重设计，禁止再同层 patch。
9. Judge `blocked` 或三轮 revise 仍未通过——交用户决策。

## 4. 错误升级（摘要）

| 类型 | 第一动作 | 升级 |
|---|---|---|
| 单测失败 | 读完整失败输出 | 同类 ≥2 → 设计门 |
| harness 校验失败 | 按脚本输出补文件/链接 | 仍 fail → 拆小步，勿 --no-verify 心态 |
| control-plane audit 失败 | 补 Judge/豁免字段 | 禁止假 completed |
| 规则冲突 | 列出冲突点与真源 | 问用户；不接受静默覆盖 |

## 主线总结

本文件是指示牌上的红字：先知道什么不能做、何时停，再回真源读细则。
