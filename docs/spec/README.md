# Spec 目录

spec 是 specification，即“产品可验证合同”。它定义调用方能够依赖的输入、输出、状态和失败语义；它不解释每日任务，也不能只写愿景。

## 快速入口

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 固定产品对外和跨模块可观察行为 |
| 当前入口 | 人类先读 [input-output-contract.md](input-output-contract.md)；程序按需读取 JSON Schema |
| 人类怎么读 | 先找适用范围、输入、必需流程、失败合同和报告合同 |
| Agent 怎么读 | 先选相关合同，再定位字段/不变量及对应测试；不要从 roadmap 推导未写入 spec 的行为 |
| 何时更新 | 输入、输出、默认值、状态、退出码、失败或兼容语义变化时 |
| 关联真源 | 架构原因回到 ADR；实现顺序回到 plan；验收方法回到 dev-rules |

## 当前合同索引

| 文件 | 读者 | 负责内容 |
|---|---|---|
| [input-output-contract.md](input-output-contract.md) | 人类与 Agent | analyzer 的触发、输入、工作区、流程、失败与最终报告合同 |
| [graphify-gate-status.schema.json](../../skills/repo-analyzer/references/contracts/graphify-gate-status.schema.json) | 程序与 Agent | Skill 核心交付包内的 Graphify gate `0/10/30` 终态、阶段、工件与失败摘要 |

机器合同正文只存在于 Skill 核心交付包；`docs/spec/` 只保留解释与链接，不再存放第二份 schema 正文。Markdown 合同与 bundled JSON Schema 必须一致；冲突时阻塞并修复合同。修改前仍须同时检查活动 roadmap、plan 和相关 ADR。

## 什么时候创建

当一项行为需要被用户、调用方、测试或多个模块稳定依赖时创建 spec，例如：

- 接受哪些输入，默认值是什么；
- 输出哪些文件、字段或状态；
- 失败时返回什么，哪些情况禁止重试或降级；
- 兼容范围和必须保持的不变量。

探索性设想先写 roadmap/research；只有准备成为可验证行为时才进入 spec。

## 怎么创建

按合同边界使用 `{主题}-contract.md`；需要机器校验时配套 `{主题}-schema.json`。首屏至少写明：

```markdown
# 合同名称

状态：proposed | active | superseded
适用范围：谁在什么场景依赖本合同
关联决策：ADR 链接

## 输入
## 正常行为
## 输出
## 失败语义
## 不变量与禁止行为
## 验证方式
```

## 怎么维护

1. 产品可观察行为变化前，先更新 spec 和必要 ADR，再修改实现。
2. 同一刀同步更新 schema、示例、测试和验收规则；不能只改叙述文本。
3. 删除或重命名字段时明确兼容与迁移策略。
4. 旧合同被替代时保留历史并指向新合同，不让两个 active 合同定义同一行为。
5. plan/progress 可以链接合同，但不能覆盖合同或把“计划完成”当成行为已经生效。

## 主线总结

先从本索引选择与变更相关的合同：人类用 Markdown 理解边界，Agent 和程序再用 schema 定位字段。行为变化必须让文档、schema、测试和验收同步，发生冲突时停止并修合同，而不是猜测权威。
