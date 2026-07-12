# Research Notes

## Evidence Scope

External research supports product framing and comparison only. Source-code behavior claims are grounded in the fixed local snapshot, not in web material. Retrieved on 2026-07-12.

## Core Problem

Claude Code users who want a second implementation/review agent otherwise switch terminals, repeat repository context, and manually track a separate Codex session. This plugin embeds that delegation into Claude Code's command and hook model: it exposes read-only review, targeted adversarial review, task rescue, handoff, status/result, cancellation, and an optional stop-time review gate (local `README.md:1-320`). The need is not a new coding model; it is a workflow boundary that preserves local Codex authentication/configuration and makes asynchronous work observable.

## External Sources

| Source | Retrieval mechanism | Finding used | Limit |
|---|---|---|---|
| GitHub repository metadata: `https://github.com/openai/codex-plugin-cc` | `gh repo view` | Description states the intended bridge: review code or delegate tasks; Apache-2.0; reported 27,828 stars and 1,817 forks at retrieval. | Volatile social metadata; no architecture claim inferred. |
| OpenAI Codex pricing: `https://developers.openai.com/codex/pricing` | Jina Reader | Codex has CLI/SDK/IDE surfaces and usage limits that vary by task/model/context; validates why explicit background-job state and usage-warning UX matter. | Product documentation can change; not a source-code specification. |
| Anthropic Claude Code overview: `https://docs.anthropic.com/en/docs/claude-code/overview` | Jina Reader | Claude Code operates across terminal/IDE/web and supports integrations, matching the plugin's host-environment premise. | General host product documentation. |
| GitHub search: `codex plugin claude code` | `gh search repos` | Returned a small third-party plugin result, suggesting this exact narrow bridge is distinct from broad orchestration products. | Search recall is not exhaustive. |
| GitHub search: `claude code codex integration` | `gh search repos` | Returned primarily broad AI desktops, orchestration frameworks, and experiments rather than command-native Claude plugins. | Keyword search only. |
| GitHub search: `multi agent code review plugin` | `gh search repos` | Returned multi-agent review plugins, a relevant comparison for review specialization versus cross-runtime delegation. | Functionality not independently inspected. |

### Search Limitations

- The reference workflow asks for 3-5 WebSearch queries. `agent-reach doctor --json` reported Exa web search unconfigured, so direct Exa WebSearch was **not performed**. Three available GitHub repository searches were used as a documented substitute; two initial search attempts had an invalid `--json nameWithOwner` field and returned an error before corrected retries.
- No social-platform research was attempted: it was not necessary to frame this developer tool, and the available social backends were not configured.

## Competitive Positioning

| Alternative | Design center | Difference from this plugin |
|---|---|---|
| Running Codex CLI separately | Direct Codex workflow | Lowest abstraction but no Claude slash-command, hook, or shared job-control surface. |
| Multi-agent review plugins | Specialist auditors inside Claude Code | Optimize review breadth; this project instead makes a separately installed Codex runtime a controllable collaborator. |
| AI desktops/orchestration platforms | Cross-agent workspace and governance | Broader control plane, usually with more setup and a different product boundary. |

## Why a Separate Project

The README explicitly delegates through the globally installed Codex CLI and app server rather than embedding a second model runtime. Its distinctive value is translating Claude Code conventions (commands, SessionStart/End and Stop hooks, slash-command UX) into durable Codex jobs and resumable sessions while retaining the user's existing local auth/configuration. Combining two CLIs manually can reproduce the underlying model access but not the lifecycle, review-gate, and status/result contracts.

## Organization Motive

The package is private in `package.json` but distributed as an `openai-codex` marketplace entry. From source and public metadata, the plausible organizational goal is ecosystem adoption: make Codex useful to teams standardized on Claude Code without forcing a host-environment migration. This is an inference, not an explicit business statement.
