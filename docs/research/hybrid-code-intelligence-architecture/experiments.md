# 只读实验记录

日期：**2026-07-13**

这些实验用于验证工具行为和修正架构假设。它们不是 analyzer skill 的标准执行、没有完成当前 `docs/dev-rules/real-uat-regression/README.md` 要求的 V1 Agent 分析链，因此**不得称为真实 UAT 通过**。

## 1. Graphify 0.9.13 code-only

### 目标

- 固定本地仓库：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click`
- 目标源码保持只读；所有工具、缓存和产物位于 `/tmp`
- Graphify：`graphifyy==0.9.13`
- 模式：纯代码 AST/关系提取，无 LLM semantic extraction

### 安装/缓存边界

第一次直接使用 `uvx` 时，用户级 uv cache 权限导致失败。重试时把以下目录全部设置到 `/tmp` 的独立实验目录：

```bash
export XDG_CACHE_HOME=<tmp>/cache
export UV_CACHE_DIR=<tmp>/uv-cache
export UV_TOOL_DIR=<tmp>/uv-tools
export UV_TOOL_BIN_DIR=<tmp>/uv-bin
export GRAPHIFY_OUT=<tmp>/graphify-out
```

这是安装环境问题，不是 Graphify 解析失败。成功重试没有修改目标仓库。

### 命令

```bash
uvx --from graphifyy==0.9.13 graphify extract \
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click \
  --code-only \
  --out <tmp> \
  --no-cluster \
  --timing
```

随后单独聚类：

```bash
uvx --from graphifyy==0.9.13 graphify cluster-only <tmp> \
  --no-label \
  --no-viz \
  --timing
```

### 结果

| 阶段 | 结果 |
|---|---:|
| Detect | 约 `0.1s` |
| AST extraction | 约 `2.5s` |
| Semantic extraction | `0.0s` |
| `extract` 总时间 | 约 `3.0s` |
| 代码文件 | `89` |
| 明确跳过的非代码文件 | `57` |
| extract raw graph | `1910 nodes / 4347 edges` |
| `cluster-only` | 约 `0.6s` |
| clustered graph | `1910 nodes / 3916 edges` |
| communities | `170` |

目标仓库前后保持 clean，未出现 Graphify 产物。实验 work dir 当前保留的 normalized graph 为 `1907 nodes / 3916 edges`。

### 与当前 doctor 的兼容性观察

当前 V1 doctor 要求：

- `raw-deep-graph.json`
- `raw-GRAPH_REPORT.md`
- source-locatable normalized graph/report

code-only 初始产物没有天然表达“deep semantic”的契约含义。使用仓库现有 `normalize_graphify_artifacts` 在 `/tmp` 保存 raw pair 并规范化来源后，doctor 返回 0。这个结果只证明现有机械 validator 可以消费该形状，**不证明 V1 semantic/deep 口径与 V2 code-only 等价**。因此正式方案采用新的 `schema_version: 2` 和 `structure_evidence.kind: graphify-code-only`。

### 对旧耗时数据的解释

旧版 `0.9.8` 物理运行记录包含：

- Click 约 369 秒；
- HTTPX 约 407 秒，另一次约 9 分钟后中断；
- Ruff 两次约 12 分 54 秒仍无 graph/report，扩展观察约 40 分钟仍停留在 semantic extraction。

这些旧命令会处理文档/语义 chunk，并使用 LLM backend；新实验使用 `0.9.13 --code-only`。版本、输入类别和运行模式不同，不能把 3 秒与旧数字当作严格性能回归结论。它们能够证明的是：**默认只分析代码时，Graphify 不必承担旧 semantic path 的时间和费用。**

## 2. Repomix 1.16.1 hotspot pack

### 目标和文件集

在相同 Click 仓库选择 6 个核心文件：

```text
src/click/core.py
src/click/parser.py
src/click/types.py
src/click/exceptions.py
src/click/shell_completion.py
src/click/utils.py
```

使用 Repomix `1.16.1`、XML 输出、Secretlint、Tree-sitter compression、stdin 精确文件列表和 50,000 token budget。

### 实验 A：三份全文 + 三份压缩

- seed 文件：全文；
- 邻域文件：压缩；
- 输出：`77,006 tokens`；
- 结果：超过 `50,000` budget，Repomix 仍产生输出但返回 budget failure。

该行为符合预期：hard budget 可作为控制器闸门。它也说明热点中存在 `core.py` 这类大文件时，“少量全文”仍可能迅速挤爆上下文。

### 实验 B：六份全部压缩

- 输出：`40,028 tokens`；
- 结果：低于 budget，成功；
- security scan：通过。

### 结论

- Repomix 适合提供热点邻域的 import、signature、type 和结构概览；
- compression 是有损且 best-effort 的，不能保证包含某个热点实现体；
- 精确 line-level hotspot 不能依赖 Repomix compression；
- Agent 应通过 Graphify/LSP 给出的 source location 直接读取核心实现；
- 控制器必须在调用前拒绝空 stdin，否则可能退化为宽泛 repository scan；
- token budget failure 不能被当作成功 pack 继续使用。

## 3. 配置样例校验

本方案的 `repomix-hotspot.config.example.json` 已通过：

```bash
jq empty repomix-hotspot.config.example.json
```

并使用 Repomix `1.16.1` 对 Click 的 `exceptions.py`、`utils.py` 做了真实两文件 pack：Secretlint 通过，输出 `6,088 tokens`，产物写入 `/tmp`，目标仓库保持 clean。

校验还确认：Repomix `--stdin` 与 repository directory 参数互斥。正确调用是从 target 根目录运行、stdin 传 target-relative 文件清单，并用绝对 `--output` 把文件写到隔离 work dir。配置文档已按该真实行为修正。

## 4. 当前可证实与不可证实的结论

可证实：

- Graphify `0.9.13 --code-only` 在 Click 小仓库上可以完全本地、秒级地产生跨文件静态图；
- 将 semantic document extraction 移出默认路径，可以消除这部分 provider 调用；
- Repomix 能严格接收文件列表、执行安全扫描并对 token 超预算返回非零；
- compressed pack 能降低上下文，但无法替代精确源码读取。

尚不可证实：

- V2 在六个仓库上的总 wall time 和总费用一定下降；
- Graphify 0.9.13 code-only 在 Ruff/Codex 等大仓库仍保持相同比例耗时；
- Graphify 社区 + hotspot rank 产生的业务模块不劣于当前 Agent 规划；
- Serena LSP 对多语言仓库的精确度和启动成本满足默认启用条件；
- Joern deep mode 的收益足以覆盖安装、索引和查询成本。

这些问题必须按 [rollout-and-evaluation.md](rollout-and-evaluation.md) 的固定仓库 A/B 方案回答。

## 主线总结

现有实验只能证明 Graphify code-only 在 Click 上可本地秒级建图，以及 Repomix 能按明确文件列表受控打包；它还不能证明 V2 在大型仓库上的总成本、模块质量或默认 resolver 策略更优。下一步不是继续外推，而是按冻结矩阵做完整 A/B。
