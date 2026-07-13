# 架构洞察与评价

## 系统性设计哲学

Click 采用“显式结构换取可组合一致性”：装饰器降低声明成本，但命令树、参数类型和
Context 并没有被隐藏。执行、help、completion、异常和测试都围绕同一批领域对象工作，
避免为每种表面能力重新推导一份 CLI 语法。

## 最有价值的设计

最关键的是 `Context`。它同时承载父子命令关系、`params`、`obj`、默认映射、参数来源、
终端策略和 `ExitStack`，把“这次命令调用”的边界固定下来（`src/click/core.py:208-712`）。
相比全局配置或 callback 手工传参，这使嵌套命令、测试隔离和资源清理更可组合。

第二个亮点是参数元数据复用：同一个 Parameter/ParamType 既参与解析和转换，也参与
usage、错误、环境变量和 completion。这是 Click 设计中最强的反漂移机制。

## 真实代价

- `core.py` 物理上汇聚 Context、Command、Group、Parameter、Option 和 Argument，逻辑边界
  清楚，但新贡献者必须一次加载较大的上下文。
- Context 的状态面宽，扩展代码如果绕过正常生命周期，容易产生共享状态或清理责任不清。
- 固定的 help 布局提升组合后的可预测性，却牺牲了局部 UI 的完全自由度
  （`docs/documentation.md:1-20`；`docs/design-opinions.md:1-19`）。
- `CliRunner` 的隔离能力不能证明真实 shell、TTY、pager 或 Windows 控制台的行为。

## 如果重新设计

保留公共 `Command/Parameter/Context` 协议，内部可拆成命令树、解析状态机、help 渲染和
执行生命周期四个实现包；同时提供稳定的结构化命令树 schema，供 IDE、文档生成器和
completion 使用。现有 `Context.to_info_dict` 已体现这个方向（`src/click/core.py:528-547`），
但本轮没有找到长期 schema 兼容承诺，因此只能作为改进方向而非现状能力。

## 对 code-only Graphify V1 的判断

本 pilot 表明，去掉 LLM 分块后，Graphify 仍能在 3.23 秒内产出可定位的代码结构图，且
doctor 能用 source references 对图谱健康度做机器校验。它减少了语义分块带来的不稳定和
等待，但不会自动产生 Why 结论；高质量报告仍依赖 skill 的业务模块规划、subagent 源码阅读
和主 agent 交叉验证。code-only 适合作为确定性的导航层，不应被宣传成架构理解器。
