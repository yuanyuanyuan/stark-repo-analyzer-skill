# Graphify 产物隔离在分析工作区

Graphify 使用 `graphify extract <target> --mode deep --out <WORK_DIR>` 运行，全部图谱、缓存和报告写入 `$WORK_DIR/graphify-out/`；被分析仓库始终是只读输入。后续 `query`、`path` 与 `explain` 必须显式引用该工作区的 `graph.json`，不能依赖当前目录的默认图谱路径。

## Consequences

- 每次运行的 metadata 和 manifest 可以完整定位其图谱证据，不污染源码状态或目标仓库的 Git diff。
- 重跑、清理和并行分析按工作区隔离；不同运行不得共享或覆盖 Graphify cache。
- 验证器必须拒绝图谱输出落在目标仓库或缺少显式关联工作区的情况。
