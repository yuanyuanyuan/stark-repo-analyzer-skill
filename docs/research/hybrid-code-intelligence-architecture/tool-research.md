# Primary-source tool research for hybrid code intelligence

Access date: **2026-07-13**

This note records confirmed capabilities and boundaries relevant to a hybrid architecture that may combine repository enumeration, syntax-level indexing, graph construction, and context packaging. It is based on official repositories, official documentation, the official PyPI package page, and read-only inspection of the locally installed Graphify CLI. No Graphify extraction was run.

> Follow-up correction: after this primary-source pass, a separate read-only experiment ran Graphify `0.9.13 --code-only` on the fixed Click repository. It completed extraction in about 3.0 seconds with 0.0 seconds of semantic extraction. The final proposal therefore recommends Graphify code-only as the first always-on static graph adapter, while keeping caller-owned Tree-sitter queries as an extension/future replacement rather than building a second complete graph engine immediately. See [experiments.md](experiments.md) and [architecture.md](architecture.md). The source research below is retained as originally scoped.

## Executive findings

1. **Graphify is an opinionated repository-to-knowledge-graph product, not a general Tree-sitter API.** Its public CLI owns discovery, AST extraction, semantic extraction, graph construction, clustering, querying, reports, and watch/update workflows. The locally installed command is the official `graphifyy` package, version `0.9.8`; the official repository inspected on 2026-07-13 was at tag `v0.9.13`, so current upstream behavior must not be assumed to exist identically in the installed build.[L1][G1][G2]
2. **Graphify has exclusion controls but no confirmed positive file-list extraction contract.** `extract` takes one path (defaulting to `.` when options come first), supports repeated `--exclude` patterns in source, and respects `.gitignore` plus `.graphifyignore`. There is no `--include` option in the current CLI parser. Although `.graphifyinclude` parsing helpers exist, the inspected current `detect()` implementation loads those patterns but does not use them during enumeration; therefore functional include/allowlist scoping is not confirmed.[G3][G4]
3. **Tree-sitter is the correct primitive for fine-grained, incremental syntax intelligence.** It supports editing an old tree, reparsing with the old tree, computing changed ranges, parsing selected ranges of mixed-language documents, and executing structural queries over byte/point ranges. These are per-document syntax APIs; repository discovery, persistence, dependency resolution, and cross-file semantics remain application responsibilities.[T1][T2][T3]
4. **Current py-tree-sitter favors prebuilt language wheels.** The official example installs `tree-sitter` plus a language package such as `tree-sitter-python`, then constructs `Language(tspython.language())`. The current binding exposes parsers, trees, queries, query cursors, included ranges, callbacks, and incremental parsing. It does not document the older `Language.build_library(...)` workflow in its current README/API.[P1][P2]
5. **Repomix is the strongest of the three for deterministic repository/file selection and LLM context packaging.** It supports include globs, ignore globs/files, stdin file lists, remote repositories, multiple output formats, token budgets, security scanning, and optional Tree-sitter compression. Its compression is lossy structure extraction, not a dependency graph or symbol index.[R1][R2][R3]

## 1. Graphify CLI

### Identity and version provenance

- Local executable: `/Users/chuzu/anaconda3/bin/graphify`.[L1]
- Local package metadata: official PyPI distribution `graphifyy`, version `0.9.8`; console script `graphify` imports `graphify.__main__:main`.[L1]
- The official package explicitly warns that the PyPI package name is `graphifyy` (double `y`) while the CLI command is `graphify`; similarly named PyPI packages are not affiliated.[G1]
- The official source repository identified by GitHub search and package branding is `Graphify-Labs/graphify`. Its current `pyproject.toml` declares package `graphifyy`, console script `graphify`, Tree-sitter dependencies, and version `0.9.13` at the inspected commit/tag.[G2]
- Limitation: local metadata still names `https://github.com/safishamsi/graphify` as the homepage, while current branding/source is `Graphify-Labs/graphify`. The package page and repository content establish continuity, but the redirect/history was not independently audited.

### `extract`

Confirmed current upstream contract:[G3]

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
  --google-workspace
  --no-cluster
  --code-only
  --postgres DSN
  --cargo
  --global
  --as TAG
  --exclude PATTERN        # accepted by the parser; repeatable
```

- The headless pipeline is described in source as detect -> local AST extraction for code -> semantic extraction for documents/media -> merge -> build -> cluster -> outputs.[G3]
- Code parsing is local Tree-sitter work. Official product documentation says code mapping needs no LLM and does not leave the machine; non-code semantic passes can call a configured backend.[G1]
- `--mode deep` increases semantic/inferred-edge extraction. It should not be conflated with AST extraction depth.
- `--max-workers` controls AST extraction subprocesses; `--token-budget`, `--max-concurrency`, and `--api-timeout` tune semantic calls.[G3]
- `--out DIR` separates the target path from the output root. `GRAPHIFY_OUT` is also an output-directory override in source, but it is an environment-level integration detail rather than an `extract` file-selection option.[G3]
- `--code-only` skips document/paper/image semantic inputs in current upstream. It is present in current source help but was absent from the local `0.9.8` top-level help observed on 2026-07-13; treat it as version-sensitive.[L1][G3]
- `--exclude` is accepted by both the current upstream parser and the installed `0.9.8` parser source, although it is omitted from their printed top-level help/usage strings. It appends root-anchored gitignore-style rules after ignore-file rules, so it has highest precedence among Graphify exclusions.[G3][G4]

#### File/include scoping conclusion

- **Directory/subdirectory scope: confirmed.** `extract <path>` can target a repository or a subfolder; the official README itself recommends running on a subfolder for a large corpus.[G1][G3]
- **Negative file scoping: confirmed.** `.gitignore` and `.graphifyignore` are merged, and repeated `--exclude` patterns are applied after them.[G4]
- **Positive `--include` scope: not found.** No `--include` argument exists in the current CLI parser or top-level command help.[G3]
- **`.graphifyinclude`: not operationally confirmed.** Current source defines and loads `.graphifyinclude` patterns, describing them as a way to opt hidden files/directories into traversal, but the inspected `detect()` function does not consult the loaded `include_patterns` while walking or classifying files.[G4] This is not evidence of a general allowlist and may be incomplete/dead implementation.
- **Explicit list of arbitrary files: not confirmed for `graphify extract`.** The internal Python extractor accepts a list of `Path` objects, and update/watch can re-extract changed files, but the public `extract` CLI accepts one path and performs its own detection. Depending on internal Python APIs would couple an integration to non-public implementation.

### `update`

- `graphify update <path>` rebuilds code-derived graph data without an LLM. It accepts `--force` (or `GRAPHIFY_FORCE=1`) to allow graph shrinkage and `--no-cluster` to emit the raw extraction without clustering.[G3][G5]
- On an explicit changed-path set, the internal rebuild path extracts only changed files that still exist, evicts stale nodes for changed/deleted paths, and preserves semantic nodes/edges from the prior full run where appropriate.[G5]
- Without a changed-path set it enumerates the detected code corpus and performs a full AST rebuild.[G5]
- It can include document files for which Graphify has an AST extractor (for example Markdown-family inputs), but it is not a general semantic refresh: semantic nodes from a prior full run are preserved, and changed non-code inputs can mark semantic re-extraction as pending.[G5]
- A shrink guard can refuse to overwrite an existing graph with fewer nodes unless the loss is attributable to explicitly rebuilt/deleted sources or `--force` is used.[G5]

### `watch`

- `graphify watch <path>` requires the optional `watchdog` dependency and watches supported code/document/paper/image extensions.[G2][G5]
- The watch implementation debounces filesystem changes, queues pending paths, serializes rebuilds with a per-output advisory lock on supported Unix platforms, and reuses the update/rebuild path.[G5]
- Changed code files are incrementally re-extracted at the file level. This is Graphify-level incremental graph maintenance, not proof that Graphify retains and edits Tree-sitter parse trees between keystrokes.
- Limitations: watch scope is a path, not a supplied file manifest; platform behavior differs where `fcntl` is unavailable; non-code semantic changes are not equivalent to a paid/full semantic extraction.

### `query`

Confirmed CLI options:[G3][G6]

```text
graphify query "<question>"
  --dfs
  --context C       # repeatable edge-context filter
  --budget N        # default 2000 tokens
  --graph PATH
```

- The default is breadth-first traversal; `--dfs` chooses depth-first traversal. The CLI uses a fixed traversal depth of 2.[G6]
- Query terms seed matching graph nodes, optional/derived context filters restrict edge families, and output is truncated to an approximate token budget.[G6]
- The query engine operates on an existing `graph.json`; it does not parse source files on demand.
- Query output is a scoped textual subgraph. It is useful as retrieval context, but relevance is based on Graphify's node scoring and graph topology rather than a formal semantic-query language.

### `tree`

Confirmed current options:[G3][G7]

```text
graphify tree
  --graph PATH
  --output HTML
  --root PATH
  --max-children N      # default 200
  --top-k-edges N       # default 12
  --label NAME
```

- The command emits a standalone D3 v7 collapsible-tree HTML view derived from `graph.json` and source paths.[G7]
- `--root` controls filesystem hierarchy interpretation; `--max-children` bounds fan-out; `--top-k-edges` bounds the per-symbol edge inspector.[G7]
- Limitation: this is a visualization/export of an existing graph, not repository enumeration or a Tree-sitter syntax tree dump.

### `benchmark`

- `graphify benchmark [graph.json]` measures estimated context reduction versus a naive whole-corpus baseline.[G3][G8]
- If `.graphify_detect.json` supplies `total_words`, it is used; otherwise corpus words are estimated as `node_count * 50`. Tokens are estimated from words, and query cost is measured over a fixed sample-question list.[G8]
- The reported ratio is therefore a tool-specific heuristic, not a latency benchmark, parser throughput benchmark, retrieval-quality benchmark, or model-evaluated answer-accuracy result.
- Unknown: whether this heuristic is suitable as an acceptance metric for the proposed architecture. It should be independently validated against real questions and actual serialized context sizes.

### Graphify architectural boundary

Graphify can supply a ready-made graph and retrieval layer, especially for broad cross-file navigation. It cannot be the source-universe authority because its public extraction interface lacks an exact positive file list, and it does not replace custom byte-range queries or edit-level parse-tree caching. The follow-up code-only experiment showed that these gaps do not justify building a second complete Tree-sitter cross-file graph in phase one: use Git for corpus identity, Graphify code-only for the default static graph, and direct Tree-sitter only for named precision/coverage gaps.

## 2. Tree-sitter core and py-tree-sitter

### Core model and parsing API

- Tree-sitter describes itself as a parser generator and incremental parsing library that produces concrete syntax trees and can efficiently update them as source changes.[T1]
- The core C objects are `TSLanguage`, `TSParser`, `TSTree`, and `TSNode`. A language defines a grammar; a stateful parser produces a tree; nodes expose byte and row/column ranges, parent/child/sibling relationships, named-node views, and grammar field names.[T1]
- Input can be a string or a callback over a custom text structure such as a rope/piece table. The core callback receives byte offset and point and can return UTF-8/UTF-16 chunks (or use a custom decoder).[T1]
- Tree-sitter builds concrete syntax trees. Named-node APIs can provide an AST-like view, but Tree-sitter does not itself construct a repository-wide symbol/dependency graph.[T1]

### Incremental parsing

The official sequence is:[T2][P1]

1. Apply an edit to the old tree with start/old-end/new-end bytes and points (`ts_tree_edit` / Python `Tree.edit`).
2. Parse the new source while passing the edited old tree (`ts_parser_parse(..., old_tree, ...)` / Python `Parser.parse(new_source, old_tree)`).
3. Compare old and new trees with changed-range APIs (`ts_tree_get_changed_ranges` in core; Python `Tree.changed_ranges(new_tree)`).

Confirmed properties and limits:

- Reparse can reuse unchanged structure and is faster than parsing from scratch.[T2][P1]
- Nodes retained outside an edited tree need their cached positions edited too, or callers should reacquire nodes from the new tree.[T2]
- Trees are cheap to copy through reference counting, but one individual tree instance is not thread-safe; copy before using a tree concurrently.[T2]
- Tree-sitter reports syntactic changed ranges. Mapping those ranges to durable symbols, dependencies, invalidation sets, or database transactions is application logic.

### Included ranges and mixed-language documents

- Core `ts_parser_set_included_ranges` and Python `Parser.included_ranges` restrict a parser to specified byte/point ranges of a document.[T2][P2]
- This supports layered parsing of embedded languages (for example an ERB document parsed as ERB plus selected HTML and Ruby ranges).[T2]
- The application must discover the ranges and coordinate the languages. Tree-sitter explicitly does not mediate language interactions.[T2]
- Included ranges are within a source document; they are not repository include globs.

### Query language

- Queries are S-expression patterns over node types. They support fields, negated fields, anonymous tokens, wildcards, `ERROR`/`MISSING` nodes, supertypes, captures, repetitions (`+`, `*`, `?`), sibling groups, alternations, anchors, predicates, and directives.[T3][T4]
- Standard predicates include equality and regex matching families such as `#eq?`, `#not-eq?`, `#match?`, `#not-match?`, and membership predicates; directives can attach metadata such as `#set!` and transform captured text such as `#strip!`/`#select-adjacent!`.[T4]
- Core `TSQuery` values are immutable and shareable between threads; `TSQueryCursor` carries execution state, is reusable, and should not be shared between threads.[T3]
- Query cursors can restrict execution by byte or point range. Intersecting-range methods may return a match that only partly overlaps the range; containing-range variants require captured nodes to be fully inside it.[T3]

### py-tree-sitter API

- Official documentation accessed on 2026-07-13 identifies py-tree-sitter `0.26.0`, supporting language ABI versions 13 through 15.[P2]
- Installation: `pip install tree-sitter`; official language packages such as `tree-sitter-python` provide precompiled wheels. Loading is currently shown as `Language(tspython.language())`, followed by `Parser(PY_LANGUAGE)`.[P1]
- `Parser.parse` accepts a bytes-like source or a read callback, an optional old tree, UTF-8/UTF-16 encoding choices, and for callback input a progress callback.[P1][P2]
- `QueryCursor.captures()` returns captures grouped by capture name; `matches()` preserves match grouping and is more useful when captures within one pattern relate to each other.[P1]
- Current `QueryCursor` APIs include match limits, byte/point ranges, containing ranges, maximum start depth, custom predicate callbacks, and progress callbacks.[P2]
- `TreeCursor` is the efficient traversal primitive for large trees; a cursor can descend only within the subtree where it started.[P1]

### Supported build/load approaches

- **Core library:** build with `make` to obtain static/dynamic libraries, or compile `lib/src/lib.c` directly into a host project with the documented include directories.[T1]
- **Generated grammar in a native host:** compile the grammar's generated `src/parser.c` (and external scanner when present) into the application or a shared library.[T1]
- **Tree-sitter CLI:** `tree-sitter build [PATH]` emits a platform shared library by default; `--wasm` emits a Wasm module; `--output` controls the destination.[T5]
- **Python preferred path:** install per-language binary wheels and construct `Language` from the language package's exported pointer/capsule.[P1]
- **Custom Python grammar:** official grammar scaffolding includes Python binding files and `setup.py`, allowing a grammar repository to publish/install its own language wheel.[T6]
- Limitation/unknown: the current py-tree-sitter README and API do not present `Language.build_library`, so designs based on that older convenience API need version pinning or a separate build step. ABI compatibility must also be checked: current bindings are backward-compatible only within their stated minimum/maximum language ABI range.[P2]

### Tree-sitter architectural boundary

Tree-sitter is an excellent local engine for source-accurate syntax facts and incremental invalidation. It does not provide repository crawling, ignore semantics, durable storage, cross-file name resolution, community detection, prose/media semantics, security scanning, or LLM-ready packaging. A hybrid system must own those layers or delegate them to Graphify/Repomix.

## 3. Repomix (`yamadashy/repomix`)

### Identity and purpose

- The official repository describes Repomix as a tool that packs a repository into one AI-friendly output with token counting, configurable selection, Git-aware ignores, Secretlint security checks, and optional Tree-sitter compression.[R1]
- The inspected repository package version was `1.16.1` at commit `0f2e7954f8f2973405391728b27b6c12fcfdf165` on 2026-07-13.
- Basic local usage is `repomix [path]`; remote repositories can be passed with `--remote` (or supported shorthand), and branch/tag/commit can be selected with `--remote-branch`.[R1][R2]

### Explicit file selection

- `--include "src/**/*.ts,**/*.md"` selects comma-separated fast-glob patterns; config uses an `include` string array.[R1][R2][R3]
- `--ignore "**/*.log,tmp/"` adds comma-separated exclusions; config uses `ignore.customPatterns`.[R1][R2][R3]
- `--stdin` reads one file path per line, enabling an external selector such as `git ls-files`, `rg --files`, `find`, or `fzf` to define an exact file set.[R1][R2]
- `--include-full-directory-structure` can retain the full filtered directory tree while including contents only for the selected files.[R2][R3]
- Ignore inputs include built-in defaults, `.gitignore` and `.git/info/exclude`, `.ignore`, `.repomixignore`, and custom patterns. Controls exist to disable Git ignores, `.ignore`, or defaults.[R2][R3]
- CLI options override configuration-file settings.[R3]

### Configuration contract

Repomix supports local/global TypeScript, JavaScript, JSON5, JSONC, and JSON configuration files, with a documented priority order. `repomix --init` creates a JSON config; `$schema: "https://repomix.com/schemas/latest/schema.json"` enables editor validation.[R3]

Important `repomix.config.json` fields:[R3][R4]

| Area | Confirmed options |
|---|---|
| Input | `input.maxFileSize` (default 50 MB); ordered `input.processors` with `pattern`, `command`, optional timeout/error policy |
| Output format | `output.filePath`, `style` (`xml`, `markdown`, `json`, `plain`), path style, parsable escaping, stdout/clipboard via CLI |
| Output content | file summary, directory structure, files on/off, header/instruction text, line numbers, base64 truncation, empty dirs, full directory structure |
| Size control | split output, top-file count, token-count tree, `output.tokenBudget` (output is generated but exit is non-zero when over budget) |
| Normalization | remove comments, remove empty lines, global compression |
| Per-file level | ordered `output.patterns`: `{pattern, compress?, directoryStructureOnly?}`; first match wins; directory-only takes precedence |
| Git context | sort by change frequency, include diffs, include logs, log count |
| Selection | `include`, Git/dot/default ignore toggles, custom ignore patterns |
| Security | `security.enableSecurityCheck` (default true) |
| Tokenization | `tokenCount.encoding` (default `o200k_base`) |

- File processors execute arbitrary commands and are intentionally limited to trusted local CLI runs; remote repository configuration is not trusted unless `--remote-trust-config` is supplied.[R2][R3]
- Per-file output patterns can force full content, compressed content, or directory-structure-only output. This is detail-level selection after repository selection, not a symbol-level query.[R3][R4]

### Security behavior

- Security scanning is enabled by default and uses Secretlint to detect items such as API keys, access tokens, credentials, private keys, environment variables, database strings, and other common secrets.[R5]
- Files with findings are reported and excluded from packed output. `--no-security-check` or `security.enableSecurityCheck: false` disables this behavior.[R5]
- Binary contents are omitted, although paths can remain visible in the directory structure.[R3][R5]
- Security limitations: ignore rules and Secretlint reduce risk but are not proof that output contains no sensitive data. Official guidance says to review output before sharing and use `.repomixignore` for sensitive paths.[R5]

### Tree-sitter compression

- `--compress` / `output.compress: true` is explicitly experimental and uses Tree-sitter to preserve signatures, interfaces/types, class structures/properties, imports/exports, and other structural elements while removing bodies and implementation details.[R1][R6]
- Repomix uses `web-tree-sitter` with bundled Wasm grammars, chosen for cross-platform installation and reliability rather than native Node bindings. On unsupported languages or parse/runtime failure, current source falls back to uncompressed content.[R7]
- Current source lists 16 compression language families: C, C#, C++, CSS, Dart, Go, Java, JavaScript, PHP, Python, Ruby, Rust, Solidity, Swift, TypeScript, and Vue, with explicit extension mappings.[R8]
- Compression runs Tree-sitter queries and language-specific capture strategies; it is not a generic minifier and not a repository dependency analyzer.[R7][R8]
- `output.patterns` permits compression for selected globs even when global compression is off, or full content for selected globs when global compression is on.[R3][R4]
- Limitation: compression is deliberately lossy and best-effort. It should not be used as the authoritative source for exact implementations, call graphs, or line-stable evidence.

### Repomix architectural boundary

Repomix is well suited to deterministic corpus assembly and bounded LLM context export. It can complement an index by packaging exact file subsets or compressed high-level views. It does not maintain an incremental syntax database, resolve cross-file symbols, or expose Graphify-style graph traversal.

## 4. Comparative implications for a hybrid architecture

| Requirement | Graphify | Tree-sitter / py-tree-sitter | Repomix |
|---|---|---|---|
| Repository enumeration | Built in; path + ignore/exclude rules | Not provided | Strong; paths, globs, stdin lists, ignores |
| Exact positive file list | No confirmed public `extract` contract | Caller supplies bytes/files | Confirmed via `--stdin` and include globs |
| Per-file syntax tree | Internal, product-owned | Core capability, caller-owned | Internal only for compression |
| Incremental edits within a file | Not confirmed as retained parse-tree editing | First-class edit/reparse/changed-ranges API | No persistent incremental syntax index |
| File-level incremental rebuild | Confirmed in update/watch internals | Caller implements | Watch repacks output; not a syntax DB |
| Structural query language | Graph traversal over built graph | S-expression syntax queries + predicates/ranges | No public structural query interface |
| Cross-file graph | Built in | Application responsibility | Not provided |
| LLM-ready bounded context | Graph query token budget | Application responsibility | Core purpose; token budget/splitting/formats |
| Security scan | Sensitive-file controls exist, exact guarantees not audited here | Not provided | Secretlint enabled by default |
| Lossless source evidence | Graph nodes/edges need source adjudication | Yes at parse/node-range level | Full mode yes; compression mode no |

Practical division of responsibility supported by the confirmed contracts and the follow-up experiment:

1. Use a caller-owned Git repository manifest plus explicit ignore/dirty-worktree policy as the deterministic source boundary.
2. Use Graphify `0.9.13 --code-only` as the first default static graph adapter, version-pin it, reconcile its effective corpus against the Git manifest, and validate source locations before treating relations as evidence.
3. Use direct Tree-sitter/py-tree-sitter queries only for exact byte/point ranges, unsupported framework syntax, or a measured Graphify gap; defer a full caller-owned cross-file graph until A/B evidence justifies its implementation and grammar-maintenance cost.
4. Use Repomix to serialize selected source/context for Agent work, with security checks on and compression enabled only for high-level orientation rather than adjudication.

This division is an architectural inference from the tool contracts, not an official recommendation from any of the projects.

## 5. Open questions and limitations

- Does the locally installed Graphify `0.9.8` produce byte-for-byte compatible graph schema and query behavior with current `0.9.13`? Not established. The source-research phase did not run extraction; the later experiment ran only `0.9.13 --code-only` and did not establish cross-version compatibility.
- Is `.graphifyinclude` intended to become an allowlist, only a hidden-path opt-in, or is its currently unused state a regression? Official current source is internally inconsistent; do not depend on it without an upstream clarification/test.
- Is hidden `--exclude` considered stable public API despite being accepted in source but omitted from printed help? Not established.
- Graphify's internal Python `extract(list[Path])` could enable explicit file extraction, but it is not the public `graphify extract` CLI contract and its stability is unknown.
- Tree-sitter grammar quality and node/query schemas vary by language and grammar version. A production index needs pinned grammar versions, ABI checks, per-language query tests, and error/recovery handling.
- Incremental parsing does not automatically imply incremental cross-file resolution. The application must define invalidation rules for imports, inheritance, generated code, conditional compilation, and ambiguous names.
- Repomix's documented compression language set can change with bundled Wasm packages. Unsupported/failing files fall back to full content, which can unexpectedly increase token volume unless a token budget is enforced.
- Secret scanning cannot guarantee absence of confidential material; generated output still requires review and policy controls.
- None of the three tools alone establishes retrieval accuracy. A real evaluation should measure source recall, relation precision, freshness after edits/deletes, context tokens, latency, and answer correctness on representative repository questions.

## Sources

### Graphify

- [L1] Read-only local inspection on 2026-07-13: `command -v graphify`, `graphify --version`, `graphify --help`, `pip show graphifyy`, the console-script header, and searches of the installed package source. This is machine-local evidence and has no external URL.
- [G1] Graphify official PyPI package page, `graphifyy`: https://pypi.org/project/graphifyy/
- [G2] Official repository and package metadata (`v0.9.13` inspected): https://github.com/Graphify-Labs/graphify and https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/pyproject.toml
- [G3] Current CLI command parser/help: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/cli.py and https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/__main__.py
- [G4] Detection, ignore, exclude, and `.graphifyinclude` implementation: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/detect.py
- [G5] Update/watch rebuild implementation: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/watch.py
- [G6] Graph query implementation: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/serve.py
- [G7] Tree HTML implementation: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/tree_html.py
- [G8] Benchmark implementation: https://github.com/Graphify-Labs/graphify/blob/eec7a0183847cbdc8a87d92b233759a5204b89fe/graphify/benchmark.py

### Tree-sitter and py-tree-sitter

- [T1] Tree-sitter introduction and basic parsing: https://tree-sitter.github.io/tree-sitter/ and https://tree-sitter.github.io/tree-sitter/using-parsers/1-getting-started.html and https://tree-sitter.github.io/tree-sitter/using-parsers/2-basic-parsing.html
- [T2] Editing, included ranges, and concurrency: https://tree-sitter.github.io/tree-sitter/using-parsers/3-advanced-parsing.html
- [T3] Query API and range restrictions: https://tree-sitter.github.io/tree-sitter/using-parsers/queries/4-api.html
- [T4] Query syntax, operators, predicates, and directives: https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html and https://tree-sitter.github.io/tree-sitter/using-parsers/queries/2-operators.html and https://tree-sitter.github.io/tree-sitter/using-parsers/queries/3-predicates-and-directives.html
- [T5] Tree-sitter CLI build documentation: https://tree-sitter.github.io/tree-sitter/cli/build.html
- [T6] Generated parser/binding layout: https://tree-sitter.github.io/tree-sitter/cli/init.html
- [P1] py-tree-sitter official README and examples: https://github.com/tree-sitter/py-tree-sitter/blob/4fb9f66172ac6d4239b0d8c79092aacc57d93bbe/README.md
- [P2] py-tree-sitter `0.26.0` API documentation: https://tree-sitter.github.io/py-tree-sitter/

### Repomix

- [R1] Official repository README: https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/README.md
- [R2] Official CLI options: https://repomix.com/guide/command-line-options
- [R3] Official configuration guide: https://repomix.com/guide/configuration
- [R4] Configuration schema source: https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/config/configSchema.ts and https://repomix.com/schemas/latest/schema.json
- [R5] Official security guide: https://repomix.com/guide/security
- [R6] Official code-compression guide: https://repomix.com/guide/code-compress
- [R7] Tree-sitter compression implementation/fallback: https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/core/treeSitter/parseFile.ts and https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/core/treeSitter/loadLanguage.ts
- [R8] Compression language registry: https://github.com/yamadashy/repomix/blob/0f2e7954f8f2973405391728b27b6c12fcfdf165/src/core/treeSitter/languageConfig.ts
