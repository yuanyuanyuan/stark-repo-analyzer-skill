# 混合代码智能工具的一手资料调研

调研日期：**2026-07-13**

本文回答一个核心问题：Graphify、Tree-sitter 和 Repomix 各自应该负责哪一层，才能避免重复造轮子。直觉上，可以把三者分别看成“仓库结构导航”“语法显微镜”和“上下文打包器”；类比的边界是，三者都不能单独给出可靠的业务结论，最终事实仍要回到固定版本的源码裁决。

本版本是可维护的中文决策入口。迁移前的逐条英文记录保留在
[`docs/archive/research-source/hybrid-code-intelligence-architecture/tool-research.en.md`](../../archive/research-source/hybrid-code-intelligence-architecture/tool-research.en.md)，用于核对更细的命令、API 和来源映射。该英文底稿不是活动合同。

## 一、结论先行

1. **Graphify 适合做默认静态结构图，不适合定义源码全集。** 它的 CLI 负责文件发现、AST 提取、建图、聚类和查询，但公开 `extract` 接口没有经过确认的精确正向文件列表能力。
2. **Tree-sitter 适合解决精确语法和增量解析问题。** 它能给出 byte/point 范围、增量 reparse 和结构查询，但仓库枚举、跨文件解析、持久化和业务语义都要由上层负责。
3. **Repomix 适合把确定的文件集合打包成受 token 预算约束的 Agent 上下文。** 它支持明确选择、ignore、安全扫描和压缩，但压缩是有损的，不能作为最终源码证据。
4. **第一阶段不建设第二套完整 Tree-sitter 跨文件图。** Git 定义 `SourceUniverse`，Graphify `0.9.13 --code-only` 提供默认静态图；只有出现已记录的精度缺口时，才调用 Tree-sitter 或其他 precision resolver。

后续只读实验已经在固定 Click 仓库上运行 Graphify `0.9.13 --code-only`：约 3.0 秒完成提取，semantic extraction 为 0.0 秒。实验细节见 [experiments.md](experiments.md)，架构决策见 [architecture.md](architecture.md)。

## 二、Graphify CLI

### 身份与版本

- 本机调研时的可执行文件为 `/Users/chuzu/anaconda3/bin/graphify`，PyPI distribution 是 `graphifyy 0.9.8`。[L1]
- 上游检查的是 `Graphify-Labs/graphify` 的 `v0.9.13`；本机 `0.9.8` 与上游 `0.9.13` 不能假定行为完全一致。[G1][G2]
- PyPI 包名是双 `y` 的 `graphifyy`，命令仍是 `graphify`；其他相似包名不应视为同一项目。[G1]

### `extract` 的已确认边界

```text
graphify extract <path>
  --backend B
  --model M
  --mode deep
  --max-workers N
  --token-budget N
  --max-concurrency N
  --api-timeout S
  --out DIR
  --no-cluster
  --code-only
  --exclude PATTERN
```

- `--code-only` 跳过文档、论文和图片的 semantic 输入；它在 `0.9.13` 上游存在，但本机 `0.9.8` 顶层帮助中未出现，因此必须做版本检查。[L1][G3]
- `--mode deep` 增强的是 semantic/inferred-edge 提取，不能解释成 AST 分析深度。
- 目录或子目录输入、`.gitignore`、`.graphifyignore` 和重复 `--exclude` 已确认可用。[G3][G4]
- 没有确认公开的 `--include` 或任意文件列表合同。`.graphifyinclude` 的 helper 虽然存在，但被检查的 `detect()` 没有在枚举中实际使用，因此不能依赖它做 allowlist。[G3][G4]
- 内部 Python extractor 接受 `list[Path]` 不等于公开 CLI 合同；直接依赖它会把集成绑定到非公开实现。

### 其他命令

- `update` 可以在不调用 LLM 的情况下重建代码图，处理变更/删除文件并带 shrink guard；它不是通用 semantic refresh。[G3][G5]
- `watch` 在安装 `watchdog` 后监听路径，并按文件级增量重建；这不证明 Graphify 会跨按键保留 Tree-sitter parse tree。[G2][G5]
- `query` 在已有 `graph.json` 上执行 BFS/DFS 图遍历并受 token budget 限制；它不是源码按需解析或形式化语义查询。[G3][G6]
- `tree` 把已有图导出为 D3 HTML，可用于观察路径和边；它不是源码枚举或 Tree-sitter AST dump。[G3][G7]
- `benchmark` 使用估算词数和固定问题计算上下文压缩比；它不是延迟、检索质量或答案准确率基准。[G3][G8]

**边界结论：** Graphify 可以承担广域跨文件导航，但 `SourceUniverse` 必须由 Git manifest 定义。所有重要关系都要验证来源位置，再回到源码裁决。

## 三、Tree-sitter 与 py-tree-sitter

Tree-sitter 是 parser generator 和增量解析库。它生成 concrete syntax tree，也就是保留语法细节的解析树；named-node API 可以给出接近 AST 的视图，但不会自动生成仓库级符号图。[T1]

### 增量解析

官方流程是：

1. 用 byte 和 point 范围对旧树执行 `ts_tree_edit` / `Tree.edit`。
2. 把编辑后的旧树传给 `ts_parser_parse` / `Parser.parse`，解析新源码。
3. 使用 changed-range API 比较新旧树。[T2][P1]

未变化结构可以复用，但 Tree-sitter 只报告语法变化范围。如何把变化映射为稳定 symbol、跨文件依赖、缓存失效或数据库 transaction，仍是应用层责任。单个 tree instance 也不是线程安全的，并发使用前需要复制或重新获取节点。[T2]

### 范围与 Query

- `included_ranges` 可以限制同一文档中的 byte/point 区间，适合嵌套语言；它不是仓库 include glob。[T2][P2]
- Query 使用 S-expression pattern，支持 field、capture、alternation、predicate 和 byte/point 范围。[T3][T4]
- `TSQuery` 可在线程间共享，`TSQueryCursor` 带执行状态，不应在线程间共享。[T3]
- py-tree-sitter `0.26.0` 支持 ABI 13 到 15；当前推荐通过各语言的预编译 wheel 加载 grammar。[P1][P2]
- 当前文档没有推荐旧的 `Language.build_library(...)` 流程；依赖旧 API 的设计必须锁版本或增加独立 build step。[P2]

**边界结论：** Tree-sitter 擅长来源精确的语法事实和增量失效，不负责仓库 crawling、ignore、持久化、跨文件 name resolution、community、秘密扫描或 LLM context packaging。

## 四、Repomix

Repomix `1.16.1` 可以把仓库或明确文件集打包为 AI-friendly 输出，并计算 token、应用 ignore、运行 Secretlint、选择性压缩。[R1]

### 文件选择与配置

- `--include` 和 `--ignore` 接受 glob；`--stdin` 每行读取一个路径，适合由 `git ls-files` 或 `rg --files` 提供精确集合。[R1][R2]
- 配置支持 TypeScript、JavaScript、JSON5、JSONC 和 JSON；CLI option 覆盖配置文件。[R3]
- `output.tokenBudget` 超限时仍会生成输出，但进程返回非零，调用方必须按失败处理。[R3][R4]
- file processor 可以执行任意命令，只能在受信任的本地配置中启用；远程仓库配置默认不可信。[R2][R3]

### 安全与压缩

- Secretlint 默认开启；发现敏感信息的文件会被报告并从 pack 排除，但这不能证明输出绝对不含秘密，分享前仍需人工或策略复核。[R5]
- `--compress` 使用 `web-tree-sitter` 和 bundled Wasm grammar 保留签名、类型、结构和 import/export，删除实现细节。[R6][R7]
- 不支持的语言或解析失败会回退到完整内容，可能意外增加 token，因此必须设置硬预算。[R7][R8]
- 压缩是 best-effort、有损的结构摘要，不能证明调用关系，也不能提供稳定的最终行号证据。

**边界结论：** Repomix 适合确定性语料组装和受限上下文导出，不提供增量语法数据库、跨文件 symbol resolution 或 Graphify 风格图遍历。

## 五、职责对比

| 能力 | Graphify | Tree-sitter / py-tree-sitter | Repomix |
|---|---|---|---|
| 仓库枚举 | 内置路径与 ignore/exclude | 不提供 | 路径、glob、stdin 和 ignore 较完整 |
| 精确正向文件集 | 公开 `extract` 未确认 | 调用方直接提供 bytes/files | `--stdin` 已确认 |
| 单文件语法树 | 内部拥有 | 核心能力，调用方拥有 | 仅压缩内部使用 |
| 文件内增量编辑 | 未确认保留旧 parse tree | 原生 edit/reparse/changed ranges | 无持久增量语法索引 |
| 跨文件图 | 内置 | 应用层负责 | 不提供 |
| 受预算的 LLM 上下文 | query 有 token budget | 应用层负责 | 核心用途 |
| 来源精确性 | 节点/边需源码裁决 | byte/node range 精确 | full 模式可用，compress 模式有损 |

因此，推荐的责任划分是：

1. Git manifest 定义确定性的源码边界和 dirty-worktree 身份。
2. Graphify `0.9.13 --code-only` 提供默认静态图，并与 manifest 对账。
3. Tree-sitter 只补精确范围、特殊框架语法或已量化的 Graphify 缺口。
4. Repomix 只打包已选上下文，安全检查保持开启，压缩只用于建立方向感。

这是基于工具合同得出的架构推论，不是三个上游项目的官方联合建议。

## 六、未决问题与限制

- 尚未证明 Graphify `0.9.8` 与 `0.9.13` 的图 schema 和 query 行为兼容。
- `.graphifyinclude` 的设计意图和实际状态不一致，不能依赖；隐藏的 `--exclude` 是否属于稳定 API 也未确认。
- Tree-sitter grammar 质量和 node/query schema 随语言和版本变化，生产系统必须锁 grammar、检查 ABI 并建立按语言 fixture。
- 增量 parsing 不自动等于增量跨文件 resolution；import、inheritance、generated code 和条件编译仍需上层 invalidation 规则。
- Repomix 压缩失败可能回退完整内容，Secretlint 也不能保证零泄漏。
- 三个工具都不能单独证明检索质量；真实评估仍要测 source recall、relation precision、编辑后 freshness、token、latency 和代表性问题的答案正确性。

## 七、来源索引

### Graphify

- [L1] 2026-07-13 本机只读检查：`command -v graphify`、`graphify --version`、`graphify --help`、`pip show graphifyy` 和已安装源码；无外部 URL。
- [G1] https://pypi.org/project/graphifyy/
- [G2] https://github.com/Graphify-Labs/graphify
- [G3] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/cli.py
- [G4] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/detect.py
- [G5] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/watch.py
- [G6] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/serve.py
- [G7] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/tree_html.py
- [G8] https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/benchmark.py

### Tree-sitter 与 py-tree-sitter

- [T1] https://tree-sitter.github.io/tree-sitter/using-parsers/2-basic-parsing.html
- [T2] https://tree-sitter.github.io/tree-sitter/using-parsers/3-advanced-parsing.html
- [T3] https://tree-sitter.github.io/tree-sitter/using-parsers/queries/4-api.html
- [T4] https://tree-sitter.github.io/tree-sitter/using-parsers/queries/3-predicates-and-directives.html
- [P1] https://github.com/tree-sitter/py-tree-sitter/blob/4fb9f66172ac6d4239b0d8c79092aacc57d93bbe/README.md
- [P2] https://tree-sitter.github.io/py-tree-sitter/

### Repomix

- [R1] https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/README.md
- [R2] https://repomix.com/guide/command-line-options
- [R3] https://repomix.com/guide/configuration
- [R4] https://repomix.com/schemas/latest/schema.json
- [R5] https://repomix.com/guide/security
- [R6] https://repomix.com/guide/code-compress
- [R7] https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/core/treeSitter/parseFile.ts
- [R8] https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/core/treeSitter/languageConfig.ts

## 主线总结

Git 决定“哪些源码属于本次分析”，Graphify code-only 决定“结构上可能如何连接”，Tree-sitter 解决少量精确语法缺口，Repomix 把选定内容装进受控上下文。最终结论不能直接相信任何工具输出，必须回到固定 commit 的源码范围验证。
