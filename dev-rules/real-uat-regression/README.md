# 真实 UAT 回归测试

本规则定义 `stark-repo-analyzer-skill` V1 的真实 UAT 回归口径。它补充
`skills/repo-analyzer/SKILL.md`，不替代该 skill 的源码阅读、模块分析和报告责任。

## 范围与通过条件

V1 控制面只支持 `standard` 模式。`quick`、`deep` 不是可传给
`stark_repo_analyzer.cli analyze` 的模式；尤其不得用 `graphify extract --mode deep`
替代产品规定的 code-only 提取。

一次真实 UAT 是对一个实际 Git 源码快照的端到端运行：输入可以是本地 Git 仓库、
公开 HTTPS Git URL 或 `owner/repo`。工作目录必须为空、可写、且在目标仓库外。控制面
负责固定 commit、Graphify 门禁和初始工件；只有在 Graphify 健康门通过后，Agent 才能
完成模块草稿并 finalise 成完整报告。

不得将以下任一状态称为真实 UAT 通过：静态 fixture、手写或复制的报告、只有目录结构
的输出、中断运行，或停在 doctor / Graphify / module / finalisation 门之前的运行。

## 唯一允许的 Graphify 路径

正式入口必须是：

```bash
PYTHONPATH=src python -m stark_repo_analyzer.cli analyze <input> \\
  --work-dir <WORK_DIR> --mode standard
```

该入口必须依次执行并记录：

```text
doctor preflight
graphify extract <target> --code-only --no-cluster --out <WORK_DIR>
graphify cluster-only <WORK_DIR> --no-label --no-viz
authoritative artifact normalization
doctor post-graph
```

Graphify 必须是 `0.9.13` 或兼容的更高版本，且提取始终是
`code-only`，`semantic_extraction=disabled`。不得调用 semantic extraction、LLM
provider 或 semantic chunking，也不得探测、读取或把 backend/model 记为 UAT 证据。
Graphify 产物只可位于 `<WORK_DIR>/graphify-out/`；目标源码仓库在整个运行中必须保持
未修改。

`raw-code-only-graph.json` 和 `raw-code-only-GRAPH_REPORT.md` 是原始旁车证据；
`graph.json` 和 `GRAPH_REPORT.md` 是 source-locatable 的规范化证据。任何空图、无来源、
越界路径、无效行号或规范化后没有节点/边，均必须阻断运行。`EXTRACTED` 关系仍须回到
源码裁决；`INFERRED` 仅为待验证，`AMBIGUOUS` 仅能作为风险或问题。

## 证据合同

每次运行均须保留输入、固定 commit、Graphify 版本、精确命令、退出码、耗时、stdout/stderr
分类、目标源码状态和失败分类。成功通过 Graphify 门之后，最低工件为：

- `input.md`、`metadata.json`、`execution-log.md`、`checks.md`
- `doctor-preflight.json`、`doctor-post-graph.json`
- `graphify-out/raw-code-only-graph.json`、`raw-code-only-GRAPH_REPORT.md`、`graph.json`、`GRAPH_REPORT.md`
- `drafts/01-graphify-map.md`、规划与调研草稿、模块任务清单，以及 `manifest.json`

门禁失败的真实运行同样有效，但它只能证明失败边界。它必须保留已产生的工件、命令和
failure class；不要求、也不得补写不存在的 post-graph、模块草稿、最终报告或成功 manifest。

完整产品分析还必须由 Agent 完成所有任务清单中的 `drafts/06-module-*.md`、交叉验证和
静态阅读覆盖率门，然后运行：

```bash
PYTHONPATH=src python -m stark_repo_analyzer.cli finalize --work-dir <WORK_DIR>
PYTHONPATH=src python -m stark_repo_analyzer.cli validate --work-dir <WORK_DIR> --complete
```

静态源码阅读覆盖率、测试覆盖率和运行时验证是三种不同的指标，必须分别记录。`resume`
只可在保存的运行目录中重做规范化和 `doctor post-graph`，不能跳过健康门。

## 2026-07-13 实际回归：browser-use/video-use

本次输入为 `https://github.com/browser-use/video-use`，工作目录为
`/Users/chuzu/repo-analyses/video-use-20260713`，固定 commit 为
`92c2b34e44c205cbc2acae7f6ca7c1c219d5dd66`。Graphify `0.9.13` 的 code-only
extract 和 `cluster-only` 都以退出码 `0` 完成，原始图包含 89 个节点和 150 条边。

但原始来源路径以 `source/` 为相对前缀；按目标仓库根目录解析时没有 source-locatable
节点或边，规范化以 `graphify-artifact: Graphify normalization produced an empty graph`
停止。因此未产生 `doctor-post-graph.json`、模块草稿、最终报告或成功 manifest。这是一次
真实的、正确阻断的 UAT 运行，不是通过结果；修复来源路径规范化后必须使用新的空工作目录
重新执行整条流程，才能声称回归通过。
