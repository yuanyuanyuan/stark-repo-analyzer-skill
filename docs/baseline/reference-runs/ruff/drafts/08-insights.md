# Ruff 架构洞察

## 贯穿的设计哲学

1. **统一接口，分离执行策略**：CLI 将 lint、format、server 放在同一 command surface，但下游保持不同职责；这降低用户心智负担，同时避免把 linter 和 formatter 强行合成一个算法。
2. **先建立共享事实，再做消费者决策**：配置/文件发现和 parser/source range 先形成事实，规则、formatter 和 printer 后消费。这样缓存、诊断、fix 和编辑器可以共享基础数据。
3. **性能目标通过边界设计实现**：Rust workspace、文件级并行、缓存、document IR 和增量 ty DB 分别减少不同类型的重复工作；但每种优化都增加状态、契约或调试成本。

## 亮点

- CLI 对 `Generate/Apply/Diff` 的明确状态机让自动修复具有可预测的副作用边界（`crates/ruff/src/lib.rs:296-319`）。
- resolver 把层级配置、文件发现、package root 和 exclusions 集中处理，适合 monorepo 场景（`crates/ruff_workspace/src/resolver.rs:315-580,730-960`）。
- formatter IR 将 Python 语法规则与通用打印器分开；这是兼容 Black 风格同时保留未来扩展空间的合理抽象（`crates/ruff_formatter/src/format_element.rs:21-459`）。
- linter 以文件为并行边界并最后排序诊断，兼顾吞吐和稳定输出（`crates/ruff_linter/src/linter.rs:119-238`）。

## 问题与改进建议

- 规则实现规模极大，单次架构分析很难使读者知道“公共 pipeline 哪些假设被所有规则依赖”。建议后续生成 rule metadata 索引和按类别抽样的行为矩阵。
- `args.rs`、configuration/options 和 ty semantic 都很大；建议在分析工具中提供“核心控制流覆盖”和“规则/数据表覆盖”两个独立指标，避免一个总百分比掩盖风险。
- watch、LSP 和 ty 都有长生命周期状态。后续应添加事件序列/取消/增量失效的可执行样例，而不是只依赖静态调用链。
- 本轮没有运行性能基准；不能把 README 的 10-100x 或公开 testimonial 当作此 commit 的实测结果。应使用固定输入、固定硬件和 `cargo bench`/CLI wall time 形成可复核数字。

## 如果重新设计

不会先拆掉现有 crate 边界；更实际的改进是给跨模块契约建立显式架构测试：配置解析产出的 settings snapshot、parser range 与 diagnostics/fix 的 round-trip、formatter IR 的宽度决策，以及 watch/LSP 的状态转换。这样既保留性能路径，又让大型 workspace 的行为更容易被新实现复刻。
