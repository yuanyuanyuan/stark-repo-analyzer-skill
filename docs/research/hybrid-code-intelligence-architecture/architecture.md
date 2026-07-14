# V2 混合代码智能架构

## 1. 设计目标

该架构优化的是分析前置阶段的可预测性和 Agent 上下文效率，同时保持当前 skill 的核心逻辑：项目理解、Why > What、业务模块划分、源码阅读、并行子代理、交叉验证、覆盖率和最终报告仍由 Agent 完成。

目标：

- 源码全集可重复、可审计，正确处理 `.gitignore` 和 dirty worktree；
- 默认结构阶段完全本地，不调用 LLM，不产生 provider 费用；
- 跨目录关系在分配子代理前可见；
- 压缩上下文与精确源码证据分离；
- 每个结论可追溯到工具、版本、源文件和范围；
- 重型工具仅按显式问题升级，不成为所有仓库的固定成本。

非目标：

- 不在本阶段修改 V1 实现、doctor 或真实 UAT 规则；
- 不把静态关系图称为运行时行为验证；
- 不让目录索引、Graphify、LSP、Repomix 或 Joern 取代源码裁决；
- 不支持闭源或商业分析后端。

## 2. 模块与接口

### 2.1 `SourceUniverse`

接口：

```text
build(target, policy) -> SourceManifest
diff(previous_manifest, current_manifest) -> ChangeSet
```

职责：

- 使用 Git 确定 tracked 与 untracked-but-not-ignored 文件；
- 标记 tracked-modified、deleted、submodule、symlink、LFS pointer 和 sparse-checkout 状态；
- 对实际存在且进入分析的每个文件记录相对路径、size、language hint、content hash；
- 生成 commit + dirty worktree 指纹，作为所有下游缓存键的根。

推荐枚举基础：

```bash
git -C "$TARGET" ls-files -z --cached --others --exclude-standard
```

控制器必须额外检查缺失的 tracked 文件、Git submodule、LFS pointer 和符号链接。`git ls-files` 不是完整策略本身。

默认源码政策：

- 已跟踪且存在的文件：包含；
- 未跟踪且未被 ignore 的文件：包含并在 dirty identity 中记录；
- ignored 文件：排除，除非用户显式 allowlist；
- 已删除 tracked 文件：不解析，但进入 `deleted_paths`；
- submodule：默认只记录 commit pointer，不递归，用户显式启用后单独建 manifest；
- LFS pointer：标记为 pointer，不能声称已读到真实内容；
- 生成目录：遵循 Git/用户策略，不以目录名猜测其价值。

### 2.2 `StaticGraph`

接口：

```text
build(source_manifest, graph_policy) -> StructureEvidence
update(change_set, previous_evidence) -> StructureEvidence
query(question_or_seed, budget) -> GraphSlice
```

第一适配器：Graphify `0.9.13 --code-only`。

职责：

- 从代码文件提取 AST、symbol、import、call、inheritance 等静态关系；
- 输出 source-locatable nodes/edges；
- 生成社区与图指标；
- 支持 path、affected、query 等局部检索；
- 不做文档/图片的 LLM 语义提取。

Graphify 没有稳定的正向文件清单接口，因此 `SourceUniverse` 与 Graphify 检测结果必须做 corpus reconciliation：

```text
expected_code_files - graph_source_files = missing_from_graph
graph_source_files - expected_code_files = outside_manifest
```

`outside_manifest` 必须阻断；`missing_from_graph` 按支持语言和 parse failure 分类，不能静默消失。

Tree-sitter 适配器暂不承担完整仓库图。只有以下情况才添加 caller-owned Tree-sitter query：

- Graphify 不支持某种语言或框架结构；
- 需要精确 byte/point range 或自定义语法模式；
- A/B 证明 Graphify 关系精度无法达标；
- 未来需要编辑级增量 parse tree，而不是文件级更新。

### 2.3 `HotspotRanker`

接口：

```text
rank(source_manifest, structure_evidence, question, history) -> HotspotPlan
```

输出不是最终业务模块，而是：热点 symbol/file、邻域、共享文件、入口点、未解析关系和建议读取范围。

建议初始分数：

```text
score =
  0.25 * normalized_graph_centrality
  + 0.20 * cross_directory_edge_ratio
  + 0.15 * entrypoint_or_public_surface
  + 0.10 * change_frequency
  + 0.10 * test_linkage
  + 0.10 * unresolved_or_ambiguous_relation
  + 0.10 * question_relevance
```

约束：

- 所有特征必须可重算，并记录原始值；
- Git 历史不可用时 `change_frequency=0`，权重重新归一化；
- 目录层级只能帮助解释 cross-boundary，不直接产生模块；
- 共享核心文件进入 coordinator/shared ownership，不强塞给单一目录代理；
- 社区聚类是候选，不是业务边界结论。

### 2.4 `PrecisionResolver`

接口：

```text
resolve(query, source_identity, budget) -> PrecisionEvidence
```

按优先级选择适配器：

1. Serena + 经审核的 OSS language server：定义、引用、声明、实现和 symbol overview；
2. Universal Ctags：广语言定义/作用域兜底；
3. ast-grep：装饰器、注册、构造模式等语法结构查询；
4. `UNRESOLVED`：不要用猜测填补。

触发条件至少满足一个：

- Graphify 边缺少可定位 source range；
- 同名 symbol 存在多个候选；
- 动态注册/宏/生成代码导致关系不完整；
- 该关系决定模块边界或核心数据流；
- Agent 对一个核心结论提出冲突证据。

每次调用必须记录 adapter、工具版本、请求、响应摘要、路径/range、耗时和失败分类。Serena 只能使用开源 LSP 后端，付费 JetBrains 后端在配置和验收中都必须拒绝。

### 2.5 `ContextPack`

接口：

```text
pack(file_manifest, detail_policy, token_budget) -> ContextPackEvidence
```

Repomix 适配器负责：

- 接收控制器提供的非空、target-relative 文件清单；
- 使用压缩模式生成邻域方向性上下文；
- 保留目录树、import/signature/type 等结构；
- 开启 Secretlint 并施加 hard token budget；
- 禁用 file processors、Git diff 和 Git log 注入。

重要不变量：

- 空 stdin 必须在调用 Repomix 前由控制器拒绝，防止回退为宽泛扫描；
- compressed pack 不是 line-accurate 证据；
- 核心实现、争议边和最终引用必须由 Agent 直接读取源文件范围；
- pack 超预算是一个可分类失败，不能悄悄截断后继续声称覆盖完整。

### 2.6 `DeepDataflow`

接口：

```text
analyze(explicit_question, bounded_manifest, deep_budget) -> DeepEvidence
```

Joern 适配器只服务显式 `deep-dataflow` 模式，用于污点传播、source-to-sink、CFG/CDG/DDG/PDG 或复杂生命周期问题。它不是 standard 分析的依赖，且必须有：

- 用户明确问题；
- 有界语言/目录/文件清单；
- 独立安装与磁盘预算；
- 明确超时；
- 结果回到源码验证。

### 2.7 `AgentAnalysis`

接口保持当前 skill 的行为语义：

```text
analyze(project_context, hotspot_plan, evidence_bundle) -> ModuleDrafts
adjudicate(module_drafts, source_reads) -> FinalReport
```

Agent 负责：

- 根据责任、能力和数据流把热点候选改写为业务模块；
- 在共享文件和跨社区边上协调子代理所有权；
- 阅读精确源码，验证 `AST_RESOLVED`/`LSP_EXACT`/`DEEP_DATAFLOW` 结论；
- 记录覆盖率、未读范围、冲突和限制；
- 保持 Why > What 与最终报告融合流程。

## 3. V2 统一证据契约

V2 不再把所有结构证据命名为 `raw-deep`。建议根对象：

```json
{
  "schema_version": 2,
  "source_identity": {
    "commit": "<git-oid>",
    "dirty_fingerprint": "sha256:<digest>",
    "manifest_digest": "sha256:<digest>"
  },
  "structure_evidence": {
    "kind": "graphify-code-only",
    "tool_version": "0.9.13",
    "config_digest": "sha256:<digest>",
    "nodes": 1907,
    "edges": 3916,
    "missing_from_graph": [],
    "outside_manifest": []
  },
  "precision_queries": [],
  "hotspots": [],
  "context_packs": [],
  "deep_evidence": null,
  "limitations": []
}
```

证据等级：

| 等级 | 含义 | 可否直接进入结论 |
|---|---|---|
| `GIT_FACT` | Git/source manifest 的文件和身份事实 | 可以 |
| `AST_EXACT` | 精确语法节点与范围 | 可以，但不代表跨文件解析正确 |
| `AST_RESOLVED` | Graphify 已解析的跨文件静态关系 | 核心路径需源码复核 |
| `LSP_EXACT` | OSS LSP 返回的定义/引用/声明 | 核心路径需源码复核 |
| `STRUCTURAL_QUERY` | ast-grep/Tree-sitter 模式命中 | 需结合源码语义 |
| `DEEP_DATAFLOW` | Joern 深度图查询结果 | 需结合源码与配置语义 |
| `AGENT_HYPOTHESIS` | Agent 基于证据提出的解释 | 必须裁决 |
| `UNRESOLVED` | 工具冲突、缺失或无法解析 | 只能作为风险/问题 |

任何 evidence item 至少包含：

```json
{
  "evidence_id": "ev-...",
  "level": "AST_RESOLVED",
  "tool": "graphify",
  "tool_version": "0.9.13",
  "source_identity": "sha256:...",
  "source_file": "src/example.py",
  "range": {"start_line": 10, "end_line": 25},
  "claim": "A calls B",
  "confidence": "candidate",
  "adjudication": "pending"
}
```

## 4. 产物布局

```text
$WORK_DIR/
  v2-evidence.json
  source/
    manifest.json
    file-list.txt
    dirty.patch-metadata.json
  structure/
    graphify/
      graph.json
      GRAPH_REPORT.md
      manifest.json
    normalized-graph.json
    corpus-reconciliation.json
  hotspots/
    ranked.json
    shared-ownership.json
  precision/
    queries.jsonl
    ctags.jsonl
    ast-grep.jsonl
  context/
    pack-manifest.json
    repomix-hotspot.xml
  deep/
    joern-metadata.json
  drafts/
  report/
```

所有路径都在 `$WORK_DIR`，目标仓库保持只读。工具产生的缓存也必须通过绝对路径指向 work dir。

## 5. 状态机与失败语义

```text
DISCOVERED
  -> INDEXED
  -> GRAPH_READY
  -> RANKED
  -> PACKED
  -> PLANNED
  -> ANALYZING
  -> ADJUDICATED
  -> COMPLETE
```

| 失败状态 | 行为 |
|---|---|
| `SOURCE_IDENTITY_CHANGED` | 立即停止；旧证据不得混入新 worktree |
| `OUTSIDE_MANIFEST` | 立即停止；Graphify 读取了未授权路径 |
| `STATIC_GRAPH_FAILED` | shadow 阶段记录并回到 V1；canary 阶段自动回滚 |
| `GRAPH_COVERAGE_INCOMPLETE` | 按 unsupported/parse-error 分类；核心语言缺失时停止 |
| `PRECISION_UNAVAILABLE` | 可记录为 `UNRESOLVED`，除非它阻断核心结论 |
| `CONTEXT_OVER_BUDGET` | 缩小邻域后最多重试一次，不能静默截断 |
| `DEEP_BUDGET_EXCEEDED` | 停止 deep 分支，不影响已完成的 standard 证据 |
| `AGENT_CONFLICT` | 进入交叉验证，不由目录所有权强行裁决 |

升级必须发生在 `PLANNED` 之前。若分析中发现需要新的图或 LSP 证据，状态回到 `RANKED`，已有草稿标记 `stale` 并记录是否复用，避免隐藏 sunk cost。

## 6. 缓存和增量更新

缓存键至少包括：

```text
source manifest digest
+ tool name/version
+ language grammar versions
+ graph/config digest
+ query/pattern digest
```

更新策略：

- manifest 不变：可复用结构图和 pack；
- 仅少量代码文件改变：Graphify `update`，随后重新 reconciliation、hotspot rank 和受影响 pack；
- ignore/config/tool version 改变：完整重建；
- 文件删除/重命名：必须验证旧 node/edge 已驱逐；
- Repomix pack 以 file content hash 集合和配置 hash 为键；
- Serena/LSP 查询结果绑定 source identity，不跨 dirty fingerprint 复用；
- Joern deep artifact 不默认增量复用。

Graphify 的文件级 `update` 不等同于 Tree-sitter 编辑级 incremental parse。若未来需要 IDE 级实时更新，再评估 caller-owned parse-tree cache。

## 7. 安全、隐私和许可证闸门

- 默认路径完全本地，不配置 Graphify LLM backend；
- Graphify 必须使用 `--code-only`，query logging 保持 opt-in；
- Repomix Secretlint 开启，processors 禁用；
- 任何 pack 在离开本机前仍需人工/策略检查；
- Serena 只允许 LSP backend，language server 必须在 allowlist 中且许可证已核验；
- Joern、ctags 等以独立进程运行，分发时另做 copyleft/NOTICE 审核；
- 禁止 CodeQL、Serena JetBrains、商业 Semgrep 跨文件能力、闭源 SaaS 和未核验 license 的 indexer；
- 每次版本升级重新锁定源码 commit、许可证、依赖清单和行为基线。

## 8. 关键不变量

1. Git manifest 是源码全集权威，Graphify 是结构事实提供者，源码是语义裁决权威。
2. 目录结构不能直接决定业务模块。
3. 压缩上下文不能成为最终 source citation。
4. Graphify/LSP/Joern 关系不能被描述成运行时验证。
5. 任何工具都不能越过 manifest 或写入目标仓库。
6. V1 与 V2 产物、验收口径和状态必须明确分版本。
7. “更快/更省/更准确”只能由总运行 A/B 数据证明，不能由单个前置阶段推断。

## 主线总结

V2 的核心不是增加更多工具，而是明确证据分工：Git manifest 定义语料，Graphify code-only 提供静态关系候选，hotspot rank 决定阅读优先级，可选 resolver 只解决具名歧义，Agent 直接读取源码并裁决。任何缓存、增量更新或深度数据流能力都不能绕过来源边界、工作区隔离和版本化证据合同。
