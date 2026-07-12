# 真实 UAT 回归测试

本规则定义 `stark-repo-analyzer-skill` 的真实 UAT 回归口径。它补充产品 skill，不替代 `skills/repo-analyzer/` 的分析责任。

## 分档

- `quick`：固定一个小型本地 Git 仓库，验证输入归一化、doctor preflight/post-graph、隔离和最小失败边界。
- `standard`：固定 `click`、`httpx`、`ruff`、`codex-plugin-cc`、`claude-code`、`codex` 六个源码 commit，要求标准分析报告、源码证据、覆盖率和限制记录。
- `deep`：不是 V1 产品分析档位；只有 Graphify 的 `--mode deep` 提取参数可以出现在 V1 执行命令中。

## 必备证据

每次真实 UAT 都必须保存固定输入、源码 commit、Graphify 版本/backend/model、完整的具体 `extract` 与 `cluster-only` 命令、退出码、运行时间、stdout/stderr 分类、产物目录和 `metadata.json`。V1 使用 `graphify extract <target> --mode deep --out <WORK_DIR> --max-concurrency 8 --token-budget 24000 --api-timeout 120`，随后可使用官方 `graphify cluster-only <WORK_DIR> --no-label --no-viz` 物化报告；raw graph/report 与 source-locatable normalized graph/report 都必须留在 `$WORK_DIR/graphify-out/`，目标仓库不得写入 Graphify 产物。

实现控制面可通过 `resume --work-dir <WORK_DIR>` 继续一次已保存的 post-graph 修复，但不得跳过 `doctor post-graph`。真实 Agent 完成的模块草稿、源码 adjudication、coverage gate 和最终 manifest 必须与 fixture/control-plane-only 结果分开记录。

P2 必须有真实 Agent/runtime 入口；P4 必须有同一固定输入的两次独立快照，并运行 `acceptance/physical-repeatability-check.sh`。规范化比较排除运行 ID、时间戳和临时 work-dir，但不排除源码 commit、图谱来源、覆盖率或失败分类。

## 禁止假通过

- doctor 非零时不得开始正式分析；空图、无来源、越界路径和无效报告必须阻断。
- `EXTRACTED` 关系也必须回到源码验证；`INFERRED` 只能待验证，`AMBIGUOUS` 只能风险/问题。
- 不得把静态源码阅读覆盖率称为测试覆盖率或运行时验证。
- 中断的物理运行、手写报告、复制参考输出和仅结构存在的目录不能证明真实 UAT 通过。
