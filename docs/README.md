# 文档地图

本目录按“活动方向、活动执行、产品合同、开发证据、历史归档”分层。维护者应先判断文档属于哪一层，再决定写入位置。

## 60 秒读取入口

不需要从上到下读完整个 `docs/`。先根据当前问题选择最短路径：

| 你要了解什么 | 必读入口 | 读到什么就可以开始行动 |
|---|---|---|
| 当前是否有实施主线 | [roadmap 索引](roadmap/README.md) → [exec plan 索引](exec-plans/README.md) | 当前无 `active`；最近完成 [GitHub v1.1.1/v1.1.2 发布](roadmap/github-v1.1.1-release-roadmap.md) 与代码地图导航 |
| 最近主线做了什么 | [已完成 roadmap](roadmap/graphify-simplification-roadmap.md) → [progress](exec-plans/graphify-simplification-progress.md) | 找到 `5/5` 完成口径、实际验证和未执行的发布验收 |
| 产品必须怎样表现 | [spec 索引](spec/README.md) → 相关合同 | 找到输入、输出、失败语义和不变量 |
| 为什么选择当前架构 | [ADR 索引](adr/README.md) → 相关当前决策 | 找到决策、原因、边界和取代关系 |
| 如何验证或声明完成 | [dev-rules 索引](dev-rules/README.md) → 适用规则 | 找到允许使用的验证方式和证据上限 |
| 本仓库该改哪（代码地图） | [code-map](code-map/README.md) → [map.yaml](code-map/map.yaml) | 命中 feature 的 entrypoints 后即可定点阅读 |

人类可以先扫本表和目标文档首屏；Agent 应按链接读取，不得用文件名猜测权威，也不需要为了“保险”全量加载历史 ADR、archive 或 baseline。

Agent 对上述目录的强制创建、维护和冲突处理动作见
[`dev-rules/document-control/README.md`](dev-rules/document-control/README.md)。目录 README 负责帮助快速理解，document-control 负责约束实际行为，两者不能互相替代。

## 活动文档

| 目录 | 职责 | 是否具有活动权威 |
|---|---|---|
| [`roadmap/`](roadmap/) | 北极星目标、非目标、阶段与退出条件 | 是，仅允许一份主线 roadmap 为 `active` |
| [`exec-plans/`](exec-plans/) | P0/P1/P2 任务、进度、验证、阻塞与下一刀 | 是，仅允许一份主线 plan 为 `active` |
| [`spec/`](spec/) | 产品输入、输出和数据合同 | 是，从目录 README 选择相关合同 |
| [`adr/`](adr/) | 架构决策及取代关系 | 是，从目录 README 选择当前决策，历史 ADR 不自动生效 |
| [`dev-rules/`](dev-rules/) | 开发操作、验收和协作配套规则 | 是，由根 `AGENTS.md` 指定适用范围 |
| [`aiprompts/`](aiprompts/) | 可复用 Agent 操作提示 | 否，不能覆盖合同或规则 |

## 支撑材料

| 目录 | 职责 | 边界 |
|---|---|---|
| [`research/`](research/) | 架构与工具研究 | 非规范性输入，结论需回挂 spec 或 ADR 才生效 |
| [`../tests/baseline/`](../tests/baseline/) | 历史 baseline 的 Git 外归档入口 | 只负责定位与校验外部材料，不再是当前 acceptance 输入 |
| [`archive/`](archive/) | 已取代的控制面、执行记录和经验材料 | 只读历史，不指导当前实现 |

仓库级 AI 硬规则见根目录 `AGENTS.md`，开发和验收规则见 `docs/dev-rules/`，领域词汇真源见根目录 `CONTEXT.md`。小型参考实现语料位于 `vendor/repo-analyzer-reference/`，不属于产品运行路径。

## 读取顺序与关系

1. 先读根 `AGENTS.md`：它会首先路由到 [`dev-rules/output-style/`](dev-rules/output-style/)，随后确定仓库级行为约束、控制面状态以及本次变更必须读取的验收规则。
2. 从 roadmap 与 exec plan 目录索引确认是否存在 `active` 文档；当前无活动主线；GitHub v1.1.1/v1.1.2 发布与代码地图导航等已是 `completed`。
3. 只有存在活动控制面时才沿 roadmap、plan 和 progress 确认本轮任务；新的跨多轮工作必须先建立控制面，不能从已完成计划自行推断下一刀。
4. 涉及产品行为时先读 `CONTEXT.md`、`spec/README.md` 和 `adr/README.md`，再只读取与当前变更相关的合同和 ADR。
5. 涉及实现或验收声明时读 `dev-rules/`：它定义验证方法和哪些证据允许声明通过。
6. `aiprompts/`、`research/`、`tests/baseline/` 和 `archive/` 只提供辅助、研究、外部证据索引或历史材料，不能覆盖前述活动权威。

`AGENTS.md` 不直接定义 analyzer 产品行为。它的作用是识别控制面生命周期、约束 Agent 的执行方式，并强制把回复、文档、代码注释和特定变更路由到 `docs/dev-rules/`。其中 output style 是所有任务的首读规则，真实 UAT 等规则则按变更类型加载。roadmap 或 plan 如果要改变公开产品语义，必须先同步 spec 或 ADR；任何文档都不能绕过 dev-rules 降低通过标准。

## 禁止新增的并行结构

- 不再创建 `docs/goals/`、`docs/plan/`、`docs/templates/` 或 `docs/agents/`。
- 不在仓库根目录新增活动 `goals.txt`、`tasks.txt`、运行日志、Graphify 输出或缓存。
- 不以新目录名复制现有合同；需要改变权威位置时必须同时更新本索引和 `AGENTS.md`。
