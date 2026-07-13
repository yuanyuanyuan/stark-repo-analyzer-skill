# Hybrid code intelligence rollout and evaluation plan

Status: proposal only. This document defines evaluation and rollout policy; it does not authorize or describe an implementation change.

## 1. Decision to be tested

The candidate V2 architecture uses Git `SourceUniverse` as the authoritative corpus, Graphify `0.9.13 --code-only` as an always-on local static graph, deterministic hotspot ranking, Repomix for bounded directional context, and direct source-range reads for final evidence. It uses the resulting graph and hotspots to propose responsibility/data-flow clusters and coordinate shared source ownership across agents. Serena with an approved OSS language server is an optional precision resolver; Joern is available only for an explicit deep-dataflow question and is not part of the standard path.

The experiment must answer one narrow question:

> Can V2 reduce analysis cost, elapsed time, and duplicate source reading without reducing module-boundary accuracy, cross-directory flow recall, source traceability, or repeatability relative to V1?

Directory structure is inventory evidence, not a module boundary. A V2 result that merely turns top-level directories into agent tasks fails the experiment even when it is cheaper.

## 2. Non-negotiable V1 preservation

V1 remains the released and default path until every V2 gate in this document passes.

- V1 keeps its current `standard` semantics, required Graphify deep extraction, doctor preflight/post-graph gates, source adjudication, Agent-owned module analysis, coverage gate, finalization, and output contract.
- V2 artifacts must use a separate workspace and must never overwrite, repair, or supply missing evidence to a V1 run.
- V1 and V2 must analyze the same fixed source commit and must leave the target repository unchanged.
- A V2 failure, timeout, uncertainty, or missing artifact falls back to a new, clean V1 run. It must not resume from a partially trusted V2 partition.
- No V1 acceptance rule is weakened to make V2 comparable. In particular, a structurally complete directory cannot substitute for a completed Agent analysis.

The V2 experiment is not a migration. Its outputs are evaluation candidates until the canary promotion decision is recorded.

## 3. Terminology and evidence boundary

This work uses the terms **benchmark run**, **shadow run**, and **canary run**. It must not be described as a real UAT run or a real UAT pass.

Any future claim of "real UAT" remains governed by `dev-rules/real-uat-regression/README.md`. Such a claim requires the prescribed fixed inputs, source commit, Graphify version/backend/model, complete concrete commands, exit codes, timing, classified stdout/stderr, artifacts, metadata, real Agent/runtime evidence, doctor gates, and repeatability evidence. Static comparison, an interrupted run, copied output, or a directory that merely has the expected shape cannot establish a real UAT pass.

The benchmark in this document may reuse the same six fixed repositories and evidence discipline, but reuse does not promote it to UAT. Benchmark results must be labeled as experimental evaluation evidence.

## 4. Compared paths

Only two algorithm paths are compared. Rollout stages are not additional algorithm paths.

### Path A: V1 control

Run the current V1 standard workflow without modification, including mandatory Graphify and both doctor gates. Preserve all normal V1 artifacts and failure classifications.

### Path B: V2 candidate

Run the proposed hybrid workflow in an isolated workspace:

1. Fix and record source identity.
2. Build an auditable Git `SourceUniverse` manifest covering tracked and untracked-but-not-ignored files, dirty identity, and explicit inclusion/exclusion reasons.
3. Run Graphify `0.9.13 --code-only` locally for every Path B run. Record it as `graphify-code-only`, never as V1 `raw-deep` evidence, and do not configure or invoke a semantic/LLM backend.
4. Reconcile Graphify's detected code corpus against `SourceUniverse`. Any `outside_manifest` path blocks the run; every `missing_from_graph` path must be classified as unsupported language, parse failure, or another declared limitation.
5. Compute deterministic hotspot ranking from the manifest, static graph, entrypoints/public surfaces, cross-directory edges, history when available, unresolved relations, and question relevance. Freeze the raw feature values and ranking before Agent planning.
6. Build bounded Repomix packs from explicit non-empty hotspot file lists and use direct source-range reads for core implementation, disputed edges, and final citations.
7. Evaluate optional precision escalation before final Agent assignments. Serena may use only an approved OSS LSP backend; ctags or ast-grep may be used as declared fallbacks. Record unresolved relations instead of guessing.
8. Propose business/data-flow modules and a shared-file ownership matrix, then run module agents, cross-validation, coverage accounting, and final fusion.

Path B must record the graph/hotspot proposal before optional precision queries and the final proposal after them. Otherwise precision-escalation false negatives, false positives, and discarded planning work cannot be measured. Joern must not run in this standard A/B matrix; it is evaluated separately only when an explicit deep-dataflow question defines its own bounded corpus and budget.

## 5. Fixed evaluation corpus and run matrix

Use the six standard fixed repositories and commits already named by the repository's real-UAT rule:

- `click`
- `httpx`
- `ruff`
- `codex-plugin-cc`
- `claude-code`
- `codex`

For every repository, run Path A twice and Path B twice as independent runs. The minimum comparison matrix is therefore 6 repositories x 2 paths x 2 runs = **24 independent runs**.

Independence means:

- a fresh work directory;
- no reuse of generated graph, module plan, draft, summary, prompt cache, or previous adjudication;
- the same fixed source commit, analysis mode, user brief, language, model policy, tool versions, and resource limits;
- randomized path order per repository to reduce warm-cache and operator-order bias;
- separate run IDs, logs, metadata, and manifests;
- no manual correction during a run unless the correction policy was declared before the matrix started and is applied symmetrically.

OS filesystem cache and provider-side cache cannot always be controlled. Record known cache state and run order, then treat unexplained differences as variance rather than deleting them.

If Path A is blocked by its required Graphify gate, preserve the blocked result. Do not replace it with a fixture or partial graph. That repository remains unavailable for paired completion-quality comparison, while its availability, time-to-block, and failure classification remain valid operational evidence. Promotion cannot rely only on repositories where both paths happened to complete.

Any material change to V2's `SourceUniverse` policy, Graphify version or `--code-only` configuration, corpus reconciliation, hotspot features/weights, Repomix policy, precision-escalation rule, agent ownership protocol, or evaluation rubric invalidates earlier Path B results and requires the full 24-run matrix again.

## 6. Gold set and adjudication

Before viewing candidate results, freeze a versioned evaluation packet for each repository:

- accepted reference module plan and report;
- named critical end-to-end flows;
- known cross-directory or cross-package boundaries;
- shared files that legitimately participate in more than one module;
- infrastructure paths that must not be promoted as business modules without specific evidence;
- high-impact conclusions and their source locations;
- documented baseline limitations and blocked claims.

The gold set is a comparison aid, not unquestionable truth. Two independent reviewers must adjudicate disagreements against the fixed source commit. Reviewers should receive anonymized Path A/Path B outputs in randomized order and must not know which architecture produced an output until scoring is locked.

For each proposed module, reviewers classify it as matched, justified split, justified merge, unsupported, or omitted. For each flow edge, they classify source and destination responsibilities, contract/data transferred, source evidence, confidence, and whether the edge crosses a directory/package boundary.

Disagreements are resolved by source adjudication and recorded. A prose assertion without source-locatable evidence cannot win adjudication.

## 7. Required metrics

All metrics are reported per run, per repository, and in aggregate. Aggregate medians must never hide a per-repository critical failure.

### 7.1 Quality and accuracy

Record:

- business-module precision, recall, and F1 against the adjudicated gold set;
- critical flow-edge recall, with cross-directory edges reported separately;
- `SourceUniverse`/Graphify corpus reconciliation: expected code files, graph source files, classified `missing_from_graph`, and blocking `outside_manifest` paths;
- hotspot recall for gold critical entrypoints, shared files, and cross-boundary edges, plus rank correlation across repeats;
- unsupported module rate, including infrastructure-as-business false positives;
- shared-file boundary accuracy: whether every shared file has consistent producer/consumer responsibilities across agent drafts;
- source citation validity and claim-to-source traceability;
- number and severity of conclusions corrected during cross-validation;
- number of unresolved inter-agent contradictions;
- critical omissions, defined as a missed boundary or flow that changes the report's explanation of system behavior;
- runtime/test claims incorrectly inferred from static reading.

Coverage is source-reading coverage, not test coverage. Report both separately whenever runtime or test evidence exists.

### 7.2 Cost

Record:

- total model input/output tokens by phase and agent;
- V1 Graphify semantic/deep invocations, backend/model, semantic token budget, and attributable provider cost;
- V2 Graphify `0.9.13 --code-only` invocations, local compute, graph size, and confirmation that semantic backend calls and provider cost are zero;
- optional Serena/OSS-LSP, ctags, ast-grep, and explicit deep-only Joern costs, reported separately rather than blended into the standard path;
- Repomix context-packaging bytes/tokens, compression ratio, and over-budget retries;
- number of tool calls and agent turns;
- compute/storage cost where measurable;
- cost of failed or abandoned work, not only successful completion cost.

### 7.3 Time

Record:

- end-to-end wall-clock time;
- time to first usable module plan;
- `SourceUniverse` inventory and dirty-fingerprint time;
- Graphify `--code-only`, corpus-reconciliation, and deterministic hotspot-ranking time;
- Repomix packing time and optional precision-resolution time;
- agent source-reading time;
- cross-validation and reconciliation time;
- finalization time;
- human adjudication time, reported separately from automated run time.

### 7.4 Repeated reading and coordination

Instrument source reads as normalized `(commit, path, line interval, agent, phase)` records. Record:

- total lines requested and unique lines requested;
- duplicate-read ratio: `(total requested lines - unique requested lines) / total requested lines`;
- cross-agent duplicate-read ratio;
- repeated reads of shared files;
- lines read again by the main agent during cross-validation;
- ownership collisions and unowned source ranges;
- number of cross-module claims deferred to the main agent;
- number of contradictions caused by agents assigning different roles to the same shared code.

Overlapping ranges must be unioned before counting unique lines. Aggregate coverage must not sum the same line once per agent.

### 7.5 Optional precision-escalation quality

Graphify `0.9.13 --code-only` is always on in Path B and is therefore not an escalation decision. The escalation oracle evaluates whether Serena with an approved OSS LSP, ctags, or ast-grep was materially needed after the always-on graph and hotspot plan. The oracle is determined only after both the pre-precision and final artifacts are frozen. Optional precision evidence is **materially needed** when its source-adjudicated result causes at least one of these changes:

- restores a critical missing module or flow;
- corrects a materially wrong boundary;
- selects the correct definition/reference among ambiguous same-name symbols;
- resolves a dynamic registration, macro, generated-code, or missing-range ambiguity that changes agent ownership or final narrative;
- resolves a high-severity relation that Graphify plus direct source reading could not resolve within the declared standard budget.

Record:

- true positive: optional precision escalation fired and was materially needed;
- false positive: escalation fired but produced no material adjudicated change;
- true negative: escalation did not fire and no material omission was found;
- false negative: escalation did not fire but adjudication found optional precision evidence was materially needed, or a critical ambiguity remained that an approved precision adapter would have resolved;
- trigger stability across the two independent runs;
- reason code, evidence observed at decision time, selected adapter/backend, and threshold values for every escalation decision.

An escalation decision cannot be justified retrospectively with evidence unavailable when the decision was made.

Joern is not a fallback precision adapter for standard analysis. Its invocation is correct only when the user explicitly requested deep dataflow, taint, CFG, or PDG analysis and a separate bounded manifest, timeout, and deep budget were fixed. Accidental Joern use in a standard Path B run is an architecture violation, not a true-positive escalation.

### 7.6 Repeatability and operational safety

Record:

- module-membership similarity across the two runs;
- critical flow-edge similarity across the two runs;
- Graphify corpus-reconciliation agreement and hotspot-rank similarity;
- optional precision-escalation decision agreement;
- source coverage delta;
- cost and time coefficient of variation;
- source-tree cleanliness before and after each run;
- out-of-workspace writes, invalid paths, missing artifacts, and failure classification stability.

Unlike the existing physical repeatability normalization, this experiment must not exclude module names, module membership, or critical flow edges: those are primary outcome variables.

## 8. Promotion thresholds

Thresholds are frozen before the first scored run. Changing a threshold after results are visible invalidates the matrix.

### Mandatory quality gates

Path B is eligible only if all of the following hold:

- zero critical module or critical flow omissions on every completed repository run;
- 100% recall for the frozen critical cross-directory flow set;
- zero unsupported infrastructure directories classified as core business modules;
- 100% of scored material claims have locatable source evidence;
- zero static-reading claims mislabeled as runtime/test validation;
- module F1 is no worse than Path A by more than 0.02 in aggregate or 0.05 on any repository;
- no increase in unresolved high-severity inter-agent contradictions;
- zero `outside_manifest` paths and 100% classification of `missing_from_graph` paths in every Path B run;
- every frozen critical entrypoint, shared file, and cross-boundary edge appears in the adjudicated hotspot set;
- zero optional precision-escalation false negatives across all Path B runs;
- optional precision-escalation decisions agree across the two runs for every repository unless the differing decision is traced to a recorded external failure;
- zero Joern invocations in the standard A/B matrix;

Any failure above is an automatic no-go regardless of cost savings.

### Repeatability gates

- module-membership similarity of at least 0.85 Jaccard after adjudicated split/merge normalization;
- critical flow-edge similarity of at least 0.90 Jaccard and no difference on the frozen critical edge set;
- hotspot top-k rank correlation of at least 0.85 after normalizing ties, with no missing frozen critical hotspot;
- identical `outside_manifest` results and no unexplained `missing_from_graph` classification drift;
- aggregate source-reading coverage differs by no more than 5 percentage points between repeats unless both runs exceed the required threshold and the omitted ranges are identical documented exclusions;
- no unexplained failure-classification change between repeats.

### Efficiency gates

After mandatory quality and repeatability gates pass, Path B must demonstrate all of:

- at least 20% lower median total model tokens than Path A;
- at least 20% lower median end-to-end wall time than Path A;
- at least 25% lower median duplicate-read ratio;
- no repository with more than a 10% cost or elapsed-time regression unless Path B recovers a documented Path A blocker;
- V2 Graphify `--code-only` produces no semantic backend calls or provider cost on every Path B run;
- the combined median time of `SourceUniverse`, Graphify `--code-only`, reconciliation, hotspot ranking, and Repomix packing is lower than the median V1 Graphify semantic/deep stage;
- optional precision false-positive escalation rate no greater than 25%.

If quality passes but efficiency does not, the result is no-go for replacing V1. The candidate may return to research with its evidence preserved.

## 9. Rollout stages

### Stage 0: offline benchmark

Complete and adjudicate the 24-run matrix. V1 remains unchanged. No candidate result is user-facing.

Exit condition: every mandatory metric is present, reviewers have signed the adjudication packet, and the promotion decision is reproducible from stored data.

### Stage 1: V2 shadow

For eligible standard analyses, run V2 beside V1 in a separate workspace. Only V1 output is delivered. V2 receives the same fixed source identity and user brief but cannot modify V1 planning, prompts, artifacts, or final report.

Shadow sampling starts with repositories representative of the six fixed shapes: single-package library, multi-package application, and large monorepo. Continue until at least 20 completed paired analyses exist, including at least five from each shape that is available. Blocked pairs remain in the denominator for reliability reporting.

Re-run the accuracy rubric on a risk-weighted sample: every optional precision-escalation disagreement, every corpus-reconciliation failure, every blocked run, every low-confidence partition, and at least 25% of otherwise normal pairs.

Exit condition: benchmark gates remain satisfied, shadow optional precision false negatives remain zero, Graphify stays inside `SourceUniverse`, no source-boundary violation occurs, and cost/time benefits persist within 5 percentage points of benchmark results.

### Stage 2: internal canary

Route at most 5% of opted-in internal standard analyses to V2 as the primary result. Run V1 in parallel for the first 10 canaries and retain it as immediate fallback. Clearly label the result as canary output, not UAT evidence.

Increase to 15% only after 10 consecutive canaries have no critical adjudication issue, no optional precision-escalation false negative, no Graphify corpus mismatch, no source-boundary violation, and no rollback trigger. Hold each allocation level for at least one full review window; do not increase allocation while any critical comparison is pending.

Exit condition: at least 30 completed canaries, the same quality gates as the offline benchmark, stable operational metrics, and an explicit go decision by the analyzer-skill owner and acceptance-rule owner.

### Stage 3: default consideration

Default promotion is a separate decision, not an automatic consequence of canary completion. It requires updated product/acceptance documentation, an explicit compatibility decision for V1 artifacts, and a separately executed real-UAT campaign that follows `dev-rules/real-uat-regression/README.md` in full.

Until that campaign actually completes, documentation may say only that V2 passed benchmark/shadow/canary evaluation. It must not say V2 passed real UAT.

## 10. Go, no-go, and rollback

### Go

Proceed to the next stage only when all stage exit conditions and all mandatory quality gates pass. A go record must include the frozen configuration, run matrix, missing-data accounting, adjudication decisions, metric calculations, known limitations, and named approvers.

### No-go

Stop promotion when any of these occurs:

- a critical module/flow omission;
- an optional precision-escalation false negative;
- a Graphify `outside_manifest` path, an unclassified critical `missing_from_graph` path, or an incomplete always-on static graph;
- a semantic/backend call from the V2 Graphify `--code-only` stage;
- a Joern invocation in standard mode without an explicit deep-dataflow request and bounded deep contract;
- an infrastructure directory promoted as a core module without source-adjudicated business responsibility;
- invalid or fabricated source evidence;
- aggregate coverage obtained by double-counting shared reads;
- a source-tree mutation or output-boundary violation;
- a claimed pass based on fixtures, partial graphs, interrupted runs, or static artifacts alone;
- failure to reproduce the hotspot ranking, optional precision-escalation decision, or core module/flow shape;
- efficiency gains below the frozen thresholds.

A no-go is an experiment outcome, not permission to relax the gate. Preserve the evidence and revise the proposal before restarting the full matrix.

### Automatic rollback during canary

Immediately return allocation to 0% V2 and deliver/re-run V1 when any of these occurs:

- one critical accuracy failure;
- one optional precision-escalation false negative;
- one Graphify `outside_manifest` path, unclassified critical graph omission, or semantic/backend invocation;
- one undeclared Joern invocation in standard mode;
- one source-boundary or workspace-isolation violation;
- two high-severity boundary errors within any 10 canaries;
- more than 10% of canaries fail to produce a complete candidate artifact for reasons not also affecting V1;
- p95 elapsed time or total token cost exceeds V1 by more than 20% over the latest 10 comparable canaries;
- required evidence is missing or cannot be tied to the analyzed source commit.

Rollback must preserve both workspaces, logs, failure classifications, and the V1 fallback provenance. Do not merge partial V2 artifacts into V1. Resume canary only after root-cause review, a revised frozen candidate, and a fresh 24-run matrix.

## 11. Required evaluation record

Each run record must contain enough information for an independent reviewer to recompute the metrics:

- path and rollout stage;
- run ID, fixed input, source commit, source dirty state, tool/model versions, and resource limits;
- complete commands and classified exits for every invoked external tool;
- `SourceUniverse` manifest, dirty fingerprint, inclusion/exclusion reasons, and source-policy digest;
- Graphify `0.9.13 --code-only` command, graph artifacts, configuration digest, and proof that no semantic backend was called;
- corpus reconciliation with expected code files, graph source files, `missing_from_graph`, and `outside_manifest`;
- hotspot raw features, weights, ranked output, and shared-ownership proposal;
- Repomix explicit non-empty file list, configuration, token budget, pack manifest, and failure/secret-scan classification;
- pre-precision module/flow proposal;
- optional precision-escalation decision, reason code, observed features, selected OSS adapter/backend, queries, and thresholds;
- post-precision proposal when applicable;
- direct source-range reads that adjudicate core implementation and final citations;
- any explicit deep-only Joern record kept outside standard metrics, including user question, bounded manifest, budget, and evidence adjudication;
- agent ownership matrix, including shared files and allowed overlap;
- normalized source-read intervals by agent and phase;
- drafts, cross-validation corrections, coverage, final report, and limitations;
- wall time, tokens, cost, retries, and failure classification;
- target cleanliness and output-boundary check;
- reviewer scores, disagreements, adjudication, and final metric row.

Secrets and private provider configuration must not be recorded. Public backend/model identity and non-sensitive execution metadata should be recorded where a V1 tool was actually invoked. Path B must record Graphify as local `graphify-code-only`; an unexpected provider/backend identity is a failure, not normal V2 metadata. Serena records must identify the approved OSS language server and version without private configuration.

## 12. Decision report shape

The final evaluation report should lead with per-repository quality outcomes, then Graphify corpus reconciliation and hotspot quality, optional precision-escalation errors, repeatability, cost/time/repeated-reading savings, failures, and limitations. Standard results must exclude deep-only Joern cost and quality from their aggregate; any separate deep experiment is reported in its own section. The report must show both independent runs rather than only averages.

The report must distinguish:

- completed paired comparisons;
- blocked Path A or Path B runs;
- unpaired operational evidence;
- benchmark conclusions;
- shadow observations;
- canary observations;
- future real-UAT evidence, if and only if it was separately executed under the repository rule.

The final recommendation is one of: **promote to shadow**, **promote to canary**, **hold for more evidence**, **revise and rerun**, or **reject**. "Passed real UAT" is not an available conclusion from this evaluation plan.
