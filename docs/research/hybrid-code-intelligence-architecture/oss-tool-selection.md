# 混合代码智能的 OSS 与本地工具选型

状态：V2 提案的最终研究选型。本文与本目录的 `README.md` 和 [architecture.md](architecture.md) 对齐，但不修改已发布的 V1 合同，也不构成真实 UAT 证据。

本文先回答“选什么”，再说明“为什么”和“哪些不能选”。迁移前的完整英文矩阵保留在
[`docs/archive/research-source/hybrid-code-intelligence-architecture/oss-tool-selection.en.md`](../../archive/research-source/hybrid-code-intelligence-architecture/oss-tool-selection.en.md)，只用于追溯细节。

## 一、选型结论

第一阶段采用 Git `SourceUniverse` 加 Graphify code-only 静态图，不再建设一套由应用自行拥有的 Tree-sitter + SQLite 跨文件图。Tree-sitter 继续作为 Graphify 的 parser substrate，也就是底层解析器，并只在明确的语法精度缺口中作为扩展；除非 A/B 证据证明 Graphify 无法达标，否则不升级为完整替代品。

直觉上，这个边界是在避免同一项目同时维护“两套地图系统”。类比的边界是，Git、Graphify 和可选 resolver 各自仍有不同职责，不是简单删除冗余：Git 管语料真源，Graphify 管静态结构候选，Agent 和源码管最终语义。

所有进入 runtime 的工具必须：开源、可在禁止出网时运行、只写分析工作区、锁定审查过的版本，并能给出来源可定位的证据或明确限制。目录结构和 graph community 只能辅助导航，不能直接成为业务模块。

## 二、工具分层

| 分层 | 选择 | 作用 | 关键边界 |
|---|---|---|---|
| 默认 | Git `SourceUniverse` | 枚举 tracked 与 untracked-not-ignored 文件，记录 commit、dirty fingerprint、hash 和特殊 Git 状态 | manifest 是源码全集权威，commit 不能单独代表 dirty worktree |
| 默认 | Graphify `0.9.13 --code-only` | 生成 symbol、import、call、inheritance、community 和来源可定位的静态关系候选 | 禁止 semantic/LLM/provider；与 `SourceUniverse` 对账；重要关系回到源码裁决 |
| 推荐上下文 | Repomix `1.16.1` | 把明确文件列表压缩为受 token 预算限制的 Agent 定向上下文 | `--stdin` 不能为空；保持 Secretlint；压缩有损，不能作最终行号证据 |
| 可选精度 | Serena `1.5.3` + OSS LSP | 在 Graphify 有实质歧义时解析 definition/reference/implementation | 只允许独立审计的开源 LSP；拒绝付费 JetBrains backend |
| 可选精度 | Universal Ctags | Graphify/LSP 不支持时提供广语言 definition/scope inventory | tag 不能证明 reference、call direction 或 data flow |
| 可选精度 | ast-grep `0.44.1` | 用确定性 rule 查 decorator、registration、builder、macro 等结构 | 是语法模式证据，不是通用 name resolution 或跨文件图 |
| 窄扩展/未来替代 | Tree-sitter `0.26.x` | 补 exact byte/point range 和特殊框架语法；可能成为未来替代基础 | 第一阶段不能借此重建完整仓库图；每个 grammar/scanner/query pack 单独审计 |
| 显式 deep | Joern `4.0.579` | 回答明确的 taint、source-to-sink、CFG、DDG、PDG 或安全数据流问题 | 不属于 standard；需要用户问题、独立预算、有界 manifest 和超时 |
| 仅设计参考 | Aider repository map | 为 `HotspotRanker` 提供 symbol ranking 与 token budget 思路 | 不为获得 repo-map 而安装完整 Aider runtime |
| 未来评估 | Semgrep CE、已验证 SCIP producer、其他 OSS static graph | 只有证明增量价值后才可能进入 | 每项重新经过来源、维护、offline、正确性、license 和 rollout 门 |

license 标签是工程初筛，不是法律意见。最终准入以固定 artifact 自带的 license 和完整依赖 inventory 为准。

## 三、选定架构

```text
Git SourceUniverse
        |
        v
Graphify 0.9.13 --code-only
        |
        v
Deterministic HotspotRanker
        |
   +----+------------------+
   |                       |
   v                       v
Optional PrecisionResolver  Repomix ContextPack
   |                       |
   +-----------+-----------+
               v
      Agent direct source-range reads
               |
               v
 business modules -> subagents -> cross-validation -> report

仅显式 deep-dataflow：Joern CPG / CFG / PDG / data flow
```

controller 拥有 source manifest、证据规范化、hotspot 评分、provenance 和状态机。它可以用紧凑、确定性的存储保存自己的 metadata，但第一阶段不能再引入一套重复 Graphify 的完整 parser/index 数据库。

## 四、语料与证据规则

1. `SourceUniverse` 是分析语料权威，包含策略允许的 tracked 和 untracked-not-ignored 文件，并记录 commit 与 dirty fingerprint。
2. manifest 记录 path、content hash、size、language hint、纳入/排除理由，以及 symlink、submodule、LFS、sparse 和 deleted 状态。
3. Graphify 检测到的源码必须与 manifest 对账。`outside_manifest` 直接阻塞；`missing_from_graph` 必须分类为不支持、显式排除或 parse failure。
4. Graphify `--code-only` 是本地静态证据，不能标为 runtime validation、semantic/deep extraction，也不能证明所有跨文件 edge 正确。
5. community、目录、文本邻近和历史只用于 hotspot 排序，不能直接决定业务模块或 subagent 所有权。
6. precision tool 只解决已记录、会影响重要边界/流程/结论的 unresolved relation；失败写为 `UNRESOLVED`，不能猜测关系。
7. Repomix pack 只帮助建立方向；核心实现、争议关系和最终引用必须直接读取 source range。
8. Joern 仍是静态 data-flow 证据，不是 runtime execution。
9. 每条证据记录工具、精确版本、source identity、path/range、query/rule、置信度、耗时和裁决状态。
10. 输出、缓存、索引、pack、日志和 tool home 全部重定向到 `$WORK_DIR`，目标仓库保持只读。

## 五、准入门

| Gate | 必需证据 |
|---|---|
| Provenance | 官方 source/release、精确 version/commit、artifact hash、安装来源、维护状态和可复现安装记录 |
| License | 顶层 license 加 runtime、bundled、optional、downloaded、grammar、rule、model 和 server 的机器可读 inventory |
| Local-only | 禁止出网的代表性运行通过；关闭或不存在 telemetry、update check、hosted rule/config 和 provider call |
| Corpus control | 支持时传精确 manifest；否则确定性对账，并由 `outside_manifest` 阻塞 |
| Source traceability | 重要事实能解析到固定 source identity 中的有效 file 和 byte/line range |
| Determinism | 两次 clean run 的规范化图、事实、语料分类、失败分类和工具 metadata 在阈值内稳定 |
| Resource bounds | wall time、CPU、memory、disk、process、file、context token 和 deep budget 明确；取消后仍可审计 |
| Isolation | 目标树前后身份不变，所有写入都位于工作区 |
| Failure semantics | unsupported language、parse error、incomplete graph、LSP unavailable、over-budget 和 timeout 都是具名状态 |
| Incremental value | 可选/deep 工具必须改善冻结指标或回答明确问题，否则移出路径 |

standard 路径只强制 Git 和 Graphify code-only。Repomix 失败时可以退回有边界的 direct source read，并披露限制；Serena、Ctags、ast-grep、direct Tree-sitter 和 Joern 不能意外变成普通 standard 结果的前置依赖。

## 六、传递依赖审计

版本、lockfile、wheel、binary、grammar、rule pack、LSP server、frontend、model、build image 或 installer 变化时，都要重新审计。

- Git：检查系统构建、linked library、credential helper、LFS/submodule helper、平台路径行为和 offline trace。
- Graphify：锁 Python dependency、Tree-sitter grammar/scanner、optional semantic/LLM extra、clustering dependency 和安装期下载，并证明 code-only 无 provider call。
- Repomix：锁 npm tree、Secretlint、tokenizer、`web-tree-sitter`、Wasm grammar、install script 和压缩回退行为。
- Serena/LSP：Serena 与每个 language server 分开做 SBOM、license、offline、source range 和资源审计，backend allowlist 必须拒绝 JetBrains。
- Ctags、ast-grep、direct Tree-sitter、Joern：分别固定 binary/build、parser/grammar/rule/frontend、license、fixture、range correctness 和取消/资源行为。

顶层 permissive license 不能覆盖未经审计的 bundled grammar、server、frontend、binary、rule、model 或 runtime download。`UNKNOWN`、缺失、不可再分发、source-available-only 或 field-of-use license 默认阻塞，除非获得明确 owner/legal 批准。SBOM 只是证据输入，不能替代人工对 optional path 和 bundled asset 的核对。

## 七、明确排除

- 第一阶段自建 Tree-sitter + SQLite 完整跨文件图：重复 Graphify，并提前承担 parser、query、invalidation 和 schema 所有权。
- 默认路径中的 Graphify document/media semantic 或 LLM extraction：重新引入 latency、provider cost 和外部配置。
- CodeQL：license/distribution 边界不符合本 local-only OSS profile。
- Serena 付费 JetBrains backend、Semgrep 商业跨文件能力、closed SaaS/hosted index/remote graph API：超出 OSS 与本地信任边界。
- GitHub Stack Graphs：已归档且不维护，不作为第一阶段核心依赖。
- 未验证 SCIP indexer：能生成可解析 SCIP 文件不等于 producer 正确、维护、本地、可定位或 license 兼容。

排除的是具体能力，不是永远禁止项目名称。未来的 Semgrep CE 本地实验或已验证 SCIP producer 仍可走完整准入流程，但不能暗示具备被排除的商业能力。

## 八、决策摘要

- 默认：Git `SourceUniverse` + Graphify `0.9.13 --code-only`。
- 推荐上下文：Repomix `1.16.1`，只用于 manifest-selected、token-bounded hotspot pack。
- 可选精度：审计过的 Serena OSS LSP、Universal Ctags、ast-grep 和窄范围 Tree-sitter query。
- 显式 deep：Joern 只回答用户明确提出且有独立预算的数据流/安全问题。
- 最终语义权威：直接读取固定 source range 的 Agent，不是任何 graph、community 或 pack。

主要来源：Graphify `v0.9.13`、Tree-sitter/py-tree-sitter、Repomix `v1.16.1`、Serena `v1.5.3`、Universal Ctags、ast-grep `0.44.1`、Joern `v4.0.579`、Aider repo-map 和 SCIP protocol。逐条 URL 与 claim-to-source 映射见 [tool-research.md](tool-research.md) 及其归档英文底稿。

## 主线总结

第一阶段只保留一套默认静态图：Git 管源码全集，Graphify 管结构候选，Repomix 管上下文，precision tool 只补明确缺口，Joern 只处理显式 deep 问题。任何工具要进入路径，都必须先证明本地可运行、来源可定位、依赖可审计且确实带来增量价值。
