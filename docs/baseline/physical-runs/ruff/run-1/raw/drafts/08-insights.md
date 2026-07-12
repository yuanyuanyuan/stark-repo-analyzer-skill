# 阶段 8：综合洞察

## 设计哲学

从本次有界证据看，Ruff 的主线是**用共享的运行边界替代 Python 工具链拼装，
同时把不可共享的语义留在专门引擎中**。CLI/Resolver 统一“哪个文件采用哪组
设置”；lint 用规则选择、共享前处理和可收敛修复处理兼容广度；formatter 用
Python AST、注释归属和通用 document printer 追求 Black 迁移兼容。

这不是“把所有功能塞进一个 crate”。相反，workspace 以扁平 crate 结构分开
`ruff_linter`、`ruff_python_formatter` 与语言无关的 `ruff_formatter`
（`CONTRIBUTING.md`），而 CLI 统一用户入口（`crates/ruff/src/lib.rs:128-264`）。

## 最有价值的权衡

1. **最近配置而非隐式祖先合并。** 这给 monorepo 每个文件清晰的设置来源；代价是
   用户必须用 `extend` 显式表达继承。相比隐式 cascade，Ruff 倾向可复现与可解释
   （`docs/configuration.md`）。
2. **固定点修复而非单遍替换。** 规则交互可能使下一次检查才发现可修复项，故 linter
   重跑并加 100 轮上限；代价是重解析与个别优先级例外，收益是避免把冲突编辑静默
   拼在一起（`linter.rs:576-668`; `fix/mod.rs:29-167`）。
3. **兼容优先的格式化器。** Formatter 不把可选风格数量当竞争点，而选 Black
   近似输出和小配置面；代价是比 YAPF 一类工具少自由度，收益是较低迁移阻力和
   可预测的团队输出（`docs/formatter.md`）。

## 批判性评价

- **优势：** 配置路由、规则调度和格式化打印都有单独的责任边界；对于“一个工具
  替多工具”的产品，避免每个子命令自带配置解析是决定性工程约束。
- **风险：** `Configuration::combine` 的宽对象与 selector 双解析路径均是演进热点；
  新设置或新选择器语义若只在一个分支维护，优先级或诊断解释会漂移。可用组合性质
  测试覆盖配置优先级，并将 selector 的两个解析分支尽可能收束。
- **范围警告：** 此评价不覆盖 199k 行 `ruff_linter` 的具体规则实现，不能据此判断
  规则正确性、兼容度或性能承诺是否成立。

## 如果重新设计

不会建议合并 lint/formatter 内核：它们的安全定义与中间表示不同。优先改善的是
边界的可测试性：为 resolver 的路径/优先级决策建立可查询 trace，为 configuration
combine 建立生成式测试；对 fix 优先级例外建立显式声明表。这样能减少统一入口随
功能增长而变成隐形耦合点的风险。
