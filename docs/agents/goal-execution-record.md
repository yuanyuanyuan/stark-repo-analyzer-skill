# Goal Execution Record

## Scope

This record collects the problems, fixes, evidence and remaining limits encountered while executing the `stark-repo-analyzer-skill` V1 goal. It complements the domain and issue-tracker documents in this directory; those files define agent conventions and were not intended to be a run ledger.

P5 dynamic behavior validation is explicitly excluded from this goal execution. No analyzed repository is claimed to have been built, tested, network-exercised or run interactively.

## Outcome Snapshot

| Area | Result | Evidence |
|---|---|---|
| Core control plane | Complete | `b5705d4`, `tests/test_cli.py` |
| Graphify doctor and contracts | Complete | `acceptance/doctor.sh`, `acceptance/doctor-self-test.sh`, contract checks |
| Click real run | Complete | `/tmp/stark-repo-analyzer-real-click-v3` |
| Codex-plugin-cc real run | Complete | `/tmp/stark-repo-analyzer-real-codex-plugin-v1` |
| HTTPX real run | Complete | `/tmp/stark-repo-analyzer-real-httpx-v2` |
| Claude Code real run | Complete | `/tmp/stark-repo-analyzer-real-claude-code-v2` |
| Codex real run | Complete | `/tmp/stark-repo-analyzer-real-codex-v3` |
| Ruff Graphify semantic extraction | Blocked after bounded retries; code-only continuation complete | `docs/baseline/physical-runs/ruff/run-1/`, `docs/baseline/physical-runs/ruff/run-2-code-only/` |
| P5 dynamic validation | Excluded by scope | `goals.txt`, `docs/baseline/physical-runs/p5-dynamic-feasibility.md` |

## Problems And Resolutions

### 1. Graphify output could cross the source boundary

Some early physical runs showed Graphify creating output under the analyzed repository. The control plane was changed to use an isolated analysis work directory, preserve raw output separately, normalize source-locatable graph evidence, and remove/record any target-tree residue before acceptance.

Decision records: `docs/adr/0006-isolate-graphify-output-in-the-analysis-workspace.md`, `docs/adr/0015-use-doctor-as-a-non-invasive-graphify-sidecar.md`.

Lesson: source cleanliness must be checked before and after every real run; output isolation is an acceptance condition, not a cleanup detail.

### 2. A graph file alone is not evidence of a usable analysis

Early fixtures and partial outputs could contain an empty graph, missing report, invalid references, or no source locations. Doctor was made responsible for preflight/post-graph classification, requiring a parseable non-empty graph/report pair and source-bounded references. Graphify discoveries remain navigation evidence and source code remains the final authority.

Decision records: `docs/adr/0003-graphify-is-a-required-structure-evidence-gate.md`, `docs/adr/0008-require-a-healthy-graphify-graph.md`, `docs/adr/0009-source-code-adjudicates-graphify-conflicts.md`.

Lesson: never promote partial Graphify output into an analysis report just because files exist.

### 3. Resume needed to preserve raw Graphify evidence

The resume path initially risked retaining only normalized output. Commit `b5705d4` updated the control plane and tests so raw Graphify evidence is preserved when post-graph repair/resume is used.

Evidence: `b5705d4`, `acceptance/doctor-self-test.sh`, `tests/test_cli.py`.

Lesson: recovery paths must preserve the same evidence lineage as a first run; a repaired result must remain auditable.

### 4. Ruff repeatedly stalled during semantic extraction

Ruff passed Graphify preflight with `graphify 0.9.8`, backend `deepseek`, and model `deepseek-v4-flash`. Both tuned attempts ran the official command with bounded concurrency, token budget and API timeout. After about 12 minutes 54 seconds, each attempt had only `graphify-out/cache/stat-index.json`; neither produced `graph.json` nor `GRAPH_REPORT.md`.

Classification: `interrupted-after-long-running-semantic-extraction`.

Evidence: `/tmp/stark-repo-analyzer-real-ruff-v2/graphify-failure.md`, `/tmp/stark-repo-analyzer-real-ruff-v2/execution-log.md`, `/tmp/stark-repo-analyzer-real-ruff-v2/metadata.json`.

Lesson: a long-running extraction without accepted artifacts is not a successful run and must not be converted into a hand-written or fixture-backed report. The available records do not identify a specific API request, HTTP status, model error or memory failure.

The third bounded attempt (`/tmp/stark-repo-analyzer-real-ruff-v3`) captured more detail. Preflight passed, AST extraction scanned `5098/5098` files, then semantic extraction started for `722` files across `380` chunks. The process logged `AST extraction failed: PosixPath('/') has an empty name`, repeated `LLM returned invalid JSON`, markdown-fenced JSON, `max_completion_tokens` truncation, and adaptive chunk splitting. After roughly 40 minutes of extended observation, only `graphify-out/cache/stat-index.json` existed. No `graph.json`, `GRAPH_REPORT.md`, raw graph, or post-graph acceptance was available.

The source tree remained clean. The full process output is retained at `/tmp/stark-repo-analyzer-real-ruff-v3/graphify-process.log`; the work directory is an isolated failure artifact and is not promoted as a report.

### 5. Missing detailed Graphify stdout/stderr

The existing records preserve commands, timings, backend/model, artifact presence, source cleanliness and failure classification, but not a complete Graphify internal stdout/stderr or per-request trace. Therefore the cause is narrowed to the semantic extraction stage, not falsely attributed to 429, timeout, provider failure or OOM.

Lesson: future real runs should redirect process stdout/stderr to a work-directory log while redacting sensitive values, and record exit code plus process termination reason.

### 6. Official configuration tuning was investigated, then explicitly deferred

The official Graphify documentation and CLI help confirm these controls:

- `GRAPHIFY_MAX_OUTPUT_TOKENS` raises the semantic response cap. The official troubleshooting section recommends it for invalid JSON/truncated responses.
- `--token-budget` packs smaller or larger semantic input chunks. The official example uses `4000` to reduce output truncation, at the cost of many more requests.
- `--api-timeout`/`GRAPHIFY_API_TIMEOUT` controls the per-request timeout; the documented default is `600` seconds.
- `--max-concurrency` controls parallel semantic calls. The current run already used `8`, above the documented default of `4`; increasing it was not justified without evidence of rate-limit headroom.
- `.graphifyignore` can reduce the corpus, but excluding Ruff docs/resources would change the full-repository evidence scope.
- `GRAPHIFY_DISABLE_THINKING=1` is an opt-in DeepSeek setting; the installed Graphify source warns that it can reduce extraction quality and increase truncation.

Official references: `https://github.com/Graphify-Labs/graphify`, `https://www.graphify.com/`, and the installed CLI help from `graphify 0.9.8`.

A plausible tuned command would use `GRAPHIFY_MAX_OUTPUT_TOKENS=32768`, `--token-budget 12000`, `--api-timeout 600`, and keep concurrency at `8`. The user explicitly chose to skip Ruff after the bounded v3 observation, so this full-corpus tuning experiment was not run and does not change the Ruff failure classification.

### 7. Ruff code-only continuation

The user later requested that Graphify LLM chunking be removed and the unfinished Ruff run be completed with code-only extraction. Graphify `0.9.13` ran as `graphify extract <target> --code-only --no-cluster` with no semantic/provider backend. The AST pass covered 5,098 code files and produced 58,118 raw nodes and 152,791 raw edges; the normalized graph passed post-graph doctor with exit 0. A narrow runtime guard skipped only Graphify's `PosixPath('/') has an empty name` Python relative-module resolver failure; the source tree and installed package were not modified.

The follow-on `gpt-5.6-luna` / low-reasoning physical analysis completed the bounded standard report and drafts. It is a valid `graphify-code-only` static evidence run, but it is deliberately not a semantic Graphify replacement and cannot be compared as a P4 repeatability run with `run-1`.

## Execution Rules For This Continuation

1. P5 dynamic validation is not run.
2. Ruff semantic extraction remains a recorded failure; the unfinished Ruff physical analysis was completed through the explicitly separate code-only path.
3. `run-2-code-only` is not a semantic P4 repeatability pass and does not promote the old semantic run to success.
4. The other completed real runs and control-plane checks remain valid evidence.
5. No final status may claim six-project semantic Graphify completion; the residual semantic-mode and other physical isolation/repeatability gates remain explicit.

## Evidence Index

- Goal and scope: `goals.txt`, `docs/goals/stark-repo-analyzer-v1-implementation.md`
- Task state: `tasks.txt`
- Acceptance rules: `dev-rules/real-uat-regression/README.md`
- Architecture decisions: `docs/adr/`
- Reference and physical run records: `docs/baseline/`
- Current implementation: `src/stark_repo_analyzer/`, `skills/repo-analyzer/`, `acceptance/`, `tests/`

### 7. Physical baseline report depth differs from reference reports

The user compared `docs/baseline/physical-runs/codex-plugin-cc/run-2/ANALYSIS_REPORT.md` with `docs/baseline/reference-runs/codex-plugin-cc/ANALYSIS_REPORT.md`. The physical report is 98 lines with three module-draft families; the reference report is 196 lines with separate App Server, Broker, Hooks and secondary module drafts. This is expected from the actual execution boundaries: the physical snapshot was run as a fixed local baseline without external research, project tests, or Agent/subagent orchestration, while the reference report was produced by a broader earlier workflow.

Classification: `report-fidelity-mismatch`, not a source or artifact-integrity failure.

Resolution: physical reports are documented as invocation/evidence snapshots, not semantic replacements for `reference-runs`. No report text was copied across runs and no implementation run was promoted as physical evidence. A future parity pass must restore the missing module decomposition and verification stages before claiming equal report depth.

### 8. Click code-only pilot and finalization state drift

The first V1 Click pilot used the repository's own `skills/repo-analyzer/SKILL.md` and launched four
independent module subagents. Graphify `0.9.13 --code-only --no-cluster` completed in about 3.23s;
raw and normalized graphs passed both doctor gates. The completed module drafts initially disagreed
with `drafts/06-module-tasks.json`, which was still marked `pending`; `validate --complete` correctly
blocked finalization until the manifest was repaired.

The pilot also exposed an idempotence bug in `finalize`: retrying after a corrected draft appended a
second fused report because the first fused section was not stripped. The finalizer now recognizes
both the pre-finalization and already-fused section markers before rebuilding the report.

Evidence: `docs/baseline/physical-runs/click/run-4-code-only/`, `src/stark_repo_analyzer/cli.py`,
`src/stark_repo_analyzer/contracts.py`, `pytest -q` (17 passed).

Lessons:

1. Dispatch state and output state must be reconciled before synthesis; a file existing is not enough.
2. Finalization must be safe to retry after quality corrections.
3. Code-only Graphify improves deterministic structure evidence, but it does not replace source
   reading, cross-validation or Why > What analysis.
