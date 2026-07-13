# OSS and local-only tool selection for hybrid code intelligence

Status: final research selection for the proposed V2 architecture. It aligns with `README.md` and `architecture.md`; it does not modify the released V1 contract or constitute real UAT evidence.

## 1. Selection policy

The phase-one architecture uses an auditable Git source universe and a local Graphify code graph. It does **not** build a second application-owned Tree-sitter plus SQLite cross-file graph. Tree-sitter remains Graphify's parser substrate, a narrow custom-query extension point, and a possible future replacement only if comparative evidence justifies that work.

All admitted runtime tools must be open source, runnable with outbound network access denied, isolated to the analysis workspace, pinned to reviewed releases, and able to return source-locatable evidence or an explicit limitation. Directory structure and graph communities are navigation evidence, not final business-module boundaries.

The categories mean:

- **Default**: required for every V2 standard run.
- **Recommended context**: expected context-packaging component, but not an authority for final claims.
- **Optional precision**: invoked for bounded ambiguity or unsupported-language cases.
- **Explicit deep mode**: heavy analysis requiring an explicit data-flow/security question and separate budget.
- **Future/deferred**: not a phase-one dependency; requires a new admission decision.
- **Excluded**: prohibited from the architecture profile.

License labels are preliminary engineering classifications, not legal advice. Admission uses the license files and dependency inventory shipped by the exact pinned artifact.

## 2. Selection matrix

| Category | Tool/component | Reviewed version | License | Architecture role | Limits and admission rule |
|---|---|---:|---|---|---|
| Default | Git-backed `SourceUniverse` | System Git, version recorded per run | GPL-2.0 | Enumerate tracked plus untracked-not-ignored files; record commit, dirty fingerprint, content hashes, ignore state, deleted paths, symlinks, submodules, LFS pointers, and sparse checkout | Base enumeration is `git -C "$TARGET" ls-files -z --cached --others --exclude-standard`, but the controller must add missing-tracked, submodule, LFS, symlink, and sparse-state checks. Commit identity alone is not a dirty-worktree cache key. The manifest, not a directory walk or downstream tool, is the source-universe authority |
| Default | Graphify CLI `--code-only` static graph adapter | `graphifyy 0.9.13` | MIT | Use local Tree-sitter extraction to produce symbols, imports, calls, inheritance, communities, path/impact evidence, and source-locatable static graph candidates before hotspot ranking | Run only `--code-only`; default V2 must not invoke document/media semantic extraction, an LLM backend, or provider APIs. Pin command/config and deny outbound network. Graphify has no confirmed exact positive file-list interface, so reconcile its effective corpus against `SourceUniverse`: `outside_manifest` blocks; `missing_from_graph` is classified by unsupported language or parse failure. Source code adjudicates material graph relations |
| Recommended context | Repomix context-pack adapter | `1.16.1` | MIT | Pack manifest-selected hotspot neighborhoods into compressed, token-bounded orientation context for agents | Invoke with a non-empty target-relative file list through `--stdin`; reject empty stdin before launch. Keep Secretlint enabled; disable file processors, Git diff, and Git log injection. Enforce hard token/file-size budgets. Compression is lossy and may fall back to full content, so packs cannot serve as final line-accurate evidence |
| Optional precision | Serena MCP with OSS LSP backends only | `1.5.3` | MIT for Serena; each language server audited separately | Resolve definitions, references, declarations, implementations, and symbol overviews when Graphify evidence is ambiguous or materially incomplete | LSP-only admission. Each configured language server must be maintained, OSS, pinned, offline-capable, source-locatable, and separately licensed/audited. Record adapter, server/version, request, response summary, ranges, timing, and failure. The paid JetBrains backend is rejected in configuration and acceptance |
| Optional precision | Universal Ctags | Exact release pinned before implementation | GPL-2.0 | Broad-language fallback inventory for definitions and scopes when Graphify/LSP coverage is unavailable | Separate-process use only. Tags do not establish references, call direction, or data flow. Admit after parser fixtures, binary provenance, license review, deterministic JSON output checks, and demonstrated incremental value |
| Optional precision | ast-grep | `0.44.1` | MIT | Deterministic structural queries for decorators, registrations, builders, macros, and framework-specific syntax patterns | Rule-driven syntax evidence, not general name resolution or a cross-file architecture graph. Admit reviewed rule packs one at a time; pin binary and rules; require golden-query fixtures and source ranges. Findings remain `STRUCTURAL_QUERY` evidence pending source interpretation |
| Optional extension / future replacement | Tree-sitter core and bindings | `0.26.x` family, exact binding/grammar versions pinned per use | MIT for core/bindings; grammar licenses vary | Existing parser substrate inside Graphify; caller-owned query extension for exact byte/point ranges or unsupported framework syntax; possible future static-graph replacement | Phase one must not rebuild a full repository graph with Tree-sitter. Add a direct query only for a named coverage/precision gap and audit every grammar, external scanner, ABI, and query pack. A replacement adapter requires A/B evidence that Graphify cannot meet quality or operational gates and triggers full architecture reevaluation |
| Explicit deep mode | Joern local code-property-graph/data-flow adapter | `4.0.579` | Apache-2.0 | Answer explicit taint, source-to-sink, CFG, CDG, DDG, PDG, lifecycle, or security/data-flow questions | Not a standard-run dependency. Require an explicit user question, bounded language/directory/file manifest, independent install/disk budget, timeout, process/resource limits, and source adjudication. Unsupported frontend/build failures and budget exhaustion are named outcomes; deep failure must not invalidate already accepted standard static evidence |
| Design reference, not runtime | Aider repository map | Reviewed as an algorithm reference | Apache-2.0 | Its symbol-graph ranking and token-budgeted repository map inform the `HotspotRanker` design | Do not install the full Aider application only to obtain repo-map behavior. Reuse only small deterministic ranking ideas justified by V2 tests, with required attribution |
| Future/deferred | Semgrep Community Edition local evaluation | Exact component/version not selected | Component/license set must be re-audited | Possible local rule and intra-file data-flow evidence if it adds measurable value beyond Graphify and ast-grep | No phase-one dependency. A trial must isolate exact OSS components, run offline with telemetry/remote services disabled, use reviewed local rules, and never imply access to commercial cross-file/interfile capabilities |
| Future/deferred | Verified SCIP producer and ingestion adapter | Not selected | Protocol and producer licenses vary | Potential normalized symbol/reference interchange for a specifically admitted ecosystem | SCIP syntax support alone is insufficient. Every producer must independently pass provenance, maintenance, offline, correctness, source-range, license, and transitive dependency gates before its output is accepted |
| Future/deferred | Alternative OSS static-graph adapter | Not selected | Varies | Possible replacement if Graphify code-only fails frozen coverage, precision, repeatability, or maintenance gates | Must implement the `StaticGraph` contract, reconcile against `SourceUniverse`, produce source-locatable normalized evidence, and pass the complete benchmark/shadow/canary evaluation. Convenience or language count alone is not sufficient |

## 3. Selected architecture

```text
Git SourceUniverse
  tracked + untracked-not-ignored + dirty fingerprint
                    |
                    v
Graphify 0.9.13 --code-only
  local Tree-sitter AST + static cross-file graph + communities
                    |
                    v
Deterministic HotspotRanker
  graph centrality + cross-boundary edges + entrypoints
  + change/test/question relevance + unresolved relations
                    |
          +---------+----------+
          |                    |
          v                    v
Optional PrecisionResolver   Repomix ContextPack
Serena LSP / ctags /         compressed orientation,
ast-grep / narrow            strict token budget
Tree-sitter query
          |                    |
          +---------+----------+
                    v
Agent direct source-range reads
                    |
                    v
business modules -> subagents -> cross-validation -> report

Explicit deep-dataflow only:
Joern CPG / CFG / PDG / data flow
```

The controller owns the source manifest, evidence normalization, hotspot scoring, provenance, and state machine. It may use compact deterministic storage for its own metadata, but phase one does not introduce a second full parser/index database that duplicates Graphify.

## 4. Corpus and evidence rules

1. `SourceUniverse` is authoritative for the analyzed corpus. It includes tracked files and untracked-not-ignored files under the declared policy and records a commit plus dirty-worktree fingerprint.
2. The manifest records path, content hash, size, language hint, inclusion/exclusion reason, and symlink/submodule/LFS/sparse/deleted state.
3. Graphify's detected source files are compared with the expected code-file manifest. `outside_manifest` is a hard failure. `missing_from_graph` must be classified as unsupported, excluded by explicit policy, or parse failure; it cannot silently disappear.
4. Graphify `--code-only` produces local static evidence. It must not be labeled runtime validation, semantic/deep extraction, or proof that every cross-file edge is correct.
5. Graphify communities, Git directories, text proximity, and change history may rank hotspots but cannot directly become business modules or subagent ownership.
6. Precision tools are invoked only for a recorded unresolved relation that affects a material boundary, flow, or conclusion. Failure becomes `UNRESOLVED`, not a guessed edge.
7. Repomix output is orientation context. Core implementations, disputed relations, and final citations come from direct source-range reads.
8. Joern evidence is deep static data-flow evidence, not runtime execution. Material findings return to source and configuration adjudication.
9. Every evidence item records tool, exact version, source identity, source path/range, query/rule, confidence, timing, and adjudication state.
10. All outputs, caches, indexes, packs, logs, and tool homes are redirected to `$WORK_DIR`; the target repository remains read-only.

## 5. Admission gates

| Gate | Required evidence |
|---|---|
| Provenance | Official source/release, exact version or commit, artifact hash, installation source, maintenance status, and reproducible install record |
| License | Direct license file plus machine-readable inventory of runtime, bundled, optional, downloaded, grammar, rule, model, and server dependencies; unknown/custom/field-of-use terms block admission absent explicit approval |
| Local-only | Representative run succeeds with outbound network denied; telemetry, update checks, hosted configuration/rules, provider calls, and remote model execution are disabled or absent |
| Corpus control | Exact manifest input where supported; otherwise a deterministic effective-corpus reconciliation with blocking `outside_manifest` behavior |
| Source traceability | Material facts resolve to valid files and byte/line ranges in the fixed source identity |
| Determinism | Two clean runs produce stable normalized graph/facts, corpus classifications, failure classes, and tool metadata within declared thresholds |
| Resource bounds | Wall time, CPU, memory, disk, process count, file count, context tokens, and deep-analysis budgets are explicit; cancellation leaves auditable state |
| Isolation | Target-tree before/after identity is unchanged and all writes stay inside the run workspace |
| Failure semantics | Unsupported language, parse error, incomplete graph, unavailable LSP, pack over-budget, timeout, and deep-budget exhaustion are named states, never empty success |
| Incremental value | Optional/deep tools improve a frozen quality metric or answer an explicit question; otherwise they are removed from the path |

The V2 standard path requires Git and Graphify code-only. Repomix is the recommended packer, but a pack failure may fall back to bounded direct source reads with an explicit limitation. Serena, Ctags, ast-grep, direct Tree-sitter queries, and Joern cannot become accidental prerequisites for an ordinary standard result.

## 6. Transitive dependency audit

The audit is repeated whenever a version, lockfile, wheel, binary, grammar, query/rule pack, language server, frontend, model, build image, or installer changes.

| Component | Dependency risks | Required audit artifact |
|---|---|---|
| Git / `SourceUniverse` | System build, crypto/network libraries, credential helpers, LFS, submodule helpers, platform-specific path behavior | Package provenance, `git --version --build-options`, license notice, command allowlist, offline trace, LFS/submodule policy, and platform fixtures for NUL paths, symlinks, sparse checkout, dirty/untracked/deleted files |
| Graphify `0.9.13 --code-only` | Python dependency graph, Tree-sitter bindings/grammars/external scanners, optional document/media/LLM packages, clustering/graph dependencies, install-time downloads, local-vs-upstream version drift | Hash-locked environment, CycloneDX/SPDX or equivalent SBOM, full license report, optional-extra inventory, grammar/source mapping, artifact hashes, exact command/config, network-deny trace proving no semantic/provider call, corpus reconciliation, source-location fixtures, and target-isolation check |
| Repomix `1.16.1` | Node runtime, npm dependency tree, Secretlint and rules, tokenizer, `web-tree-sitter`, bundled Wasm grammars, install scripts, fallback from compressed to full content | Frozen lockfile, npm/CycloneDX/SPDX SBOM, license report, bundled-asset hashes/licenses, install-script review, offline trace, security/config snapshot, empty-stdin test, token-budget test, and compression-fallback accounting |
| Serena `1.5.3` plus OSS LSP | Python/runtime dependencies, MCP transport, project configuration, telemetry/update behavior, language-server binaries/plugins/runtime downloads, and server-specific licenses | Serena lock/SBOM/license report, backend allowlist that rejects JetBrains, one complete audit per language server, offline trace, deterministic workspace config, request/response fixtures, source-range validation, resource profile, and uninstall/rollback instructions |
| Universal Ctags | Binary provenance, compiled parsers, JSON support, linked libraries, copyleft obligations | Exact release/build hash, build options, license notices, package provenance, parser fixtures, deterministic JSON output, and distribution/legal review |
| ast-grep `0.44.1` | Rust crates, parser packages, bundled assets, rule packs, install scripts | Binary hash, Cargo SBOM/license report for the exact build, parser/rule hashes and licenses, offline trace, golden-query fixtures, and source-range validation |
| Direct Tree-sitter extension | Native binding, ABI range, grammar wheels/generated parsers, external scanners, query packs, concurrency behavior | Hash-locked binding/grammar packages, license file for every grammar and scanner, ABI report, query-pack hashes, parse-error fixtures, range correctness tests, and evidence-delta comparison against Graphify |
| Joern `4.0.579` | JVM/runtime, launchers, language frontends, CPG libraries, native tools, build-system integrations, downloaded components, large caches | Exact distribution hash, Apache and third-party notices, complete SBOM/license report, frontend inventory, installer/download review, network-deny trace, bounded-language fixtures, resource/disk profile, timeout/cancellation test, and source-to-result provenance checks |

Audit failures are blocking:

- A permissive top-level license does not admit unaudited bundled grammars, language servers, frontends, binaries, rules, models, or runtime downloads.
- `UNKNOWN`, missing, non-redistributable, source-available-only, or field-of-use licenses require explicit owner/legal approval and are not treated as OSS by default.
- Development dependencies may be excluded only when the shipped/runtime artifact proves they are absent.
- Separate-process use does not remove notice, redistribution, or operational audit obligations.
- SBOM generation is an evidence input, not a substitute for reconciling optional paths, bundled assets, and runtime downloads.

## 7. Explicit exclusions

| Excluded tool/capability | Reason |
|---|---|
| Phase-one application-owned Tree-sitter plus SQLite full cross-file graph | Duplicates Graphify's admitted code graph, creates parser/query/invalidation/schema ownership before evidence shows it is necessary, and conflicts with the final phase-one architecture |
| Graphify document/media semantic or LLM-backed extraction in the default V2 path | Reintroduces the latency, provider cost, and external configuration that `--code-only` is intended to remove. Any future semantic mode needs a separate product decision and evidence contract |
| CodeQL | Not an OSS dependency suitable for this local-only profile; licensing/distribution restrictions conflict with the admission policy |
| Serena paid JetBrains backend | Paid/proprietary backend and dependency boundary. V2 permits Serena only through independently audited OSS language servers |
| Semgrep commercial cross-file/interfile capabilities | Paid/proprietary capability and service boundary; it cannot be represented as Community Edition or as a local OSS cross-file graph |
| Closed SaaS code intelligence, hosted indexing, hosted rule/model execution, and proprietary remote graph APIs | Source leaves the local trust boundary, operation is externally controlled, and reproducible offline acceptance is impossible |
| GitHub Stack Graphs | Archived/unmaintained for this selection; phase one does not add an archived core dependency |
| Unverified SCIP indexers | A parseable SCIP file does not prove that its producer is correct, maintained, local-only, source-locatable, or license-compatible |

The exclusions are capability-specific. A future Semgrep Community Edition local experiment or verified SCIP producer may be evaluated through the full admission process, but neither is part of phase one and neither may imply access to excluded commercial/unknown capabilities.

## 8. Final decision summary

- **Default:** Git-backed `SourceUniverse` plus Graphify `0.9.13 --code-only` as the local static graph adapter.
- **Recommended context:** Repomix `1.16.1` for manifest-selected, compressed, token-bounded hotspot packs; agents still read exact source ranges for adjudication.
- **Optional precision:** Serena `1.5.3` with audited OSS LSP backends only, Universal Ctags, ast-grep `0.44.1`, and narrowly scoped direct Tree-sitter queries.
- **Tree-sitter boundary:** Graphify's parser substrate and a custom-query/future-replacement foundation, not a new phase-one application-owned full graph.
- **Explicit deep mode:** Joern `4.0.579` for bounded, user-requested data-flow/security questions only.
- **Design reference only:** Aider's repository-map ranking and token-budget approach; no Aider runtime dependency.
- **Future/deferred:** Semgrep Community Edition local evaluation, verified SCIP producers, and alternative OSS static-graph adapters that pass the full evidence and rollout gates.
- **Excluded:** a duplicate phase-one Tree-sitter/SQLite graph, default Graphify semantic/LLM extraction, CodeQL, Serena's paid JetBrains backend, Semgrep commercial cross-file capabilities, closed SaaS, archived Stack Graphs, and unverified SCIP indexers.

The governing split is: Git defines the source universe, Graphify code-only supplies default static structure, Repomix packages orientation context, optional resolvers sharpen bounded ambiguities, Joern answers explicit deep-dataflow questions, and source-reading Agents remain the semantic authority.

## 9. Primary sources reviewed

- Graphify official repository and `v0.9.13`: https://github.com/Graphify-Labs/graphify and https://github.com/Graphify-Labs/graphify/releases/tag/v0.9.13
- Tree-sitter and py-tree-sitter: https://github.com/tree-sitter/tree-sitter and https://github.com/tree-sitter/py-tree-sitter
- Repomix repository and `v1.16.1`: https://github.com/yamadashy/repomix and https://github.com/yamadashy/repomix/releases/tag/v1.16.1
- Serena repository, LSP/JetBrains backend distinction, and `v1.5.3`: https://github.com/oraios/serena and https://github.com/oraios/serena/releases/tag/v1.5.3
- Universal Ctags: https://github.com/universal-ctags/ctags
- ast-grep and `0.44.1`: https://github.com/ast-grep/ast-grep and https://github.com/ast-grep/ast-grep/releases/tag/0.44.1
- Joern and `v4.0.579`: https://github.com/joernio/joern and https://github.com/joernio/joern/releases/tag/v4.0.579
- Aider repository-map design: https://github.com/Aider-AI/aider and https://aider.chat/docs/repomap.html
- SCIP protocol: https://github.com/sourcegraph/scip

The detailed Graphify, Tree-sitter, and Repomix claim-to-source mapping is preserved in [tool-research.md](tool-research.md). Before implementation, every selected release must also pass the direct license-file and transitive dependency audit defined above.
