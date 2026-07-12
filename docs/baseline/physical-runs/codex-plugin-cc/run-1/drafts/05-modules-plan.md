# Module and Narrative Plan

## Project View

`codex-plugin-cc` is a Node.js marketplace plugin that converts Claude Code command and hook events into Codex app-server operations. Its consistent philosophy is to make external-agent work explicit: command intent is normalized into protocol requests, asynchronous work is persisted as jobs, and rendering/hook decisions are expressed through declared contracts rather than hidden host state.

## Modules

| Module | Type | Ownership | Purpose |
|---|---|---|---|
| Runtime broker and app-server protocol | Core | `06-module-runtime-broker.md` | Create, discover, and supervise an app-server control plane and the protocol-facing work units. |
| Command orchestration and lifecycle | Core | `06-module-workflow-lifecycle.md` | Transform slash-command/hook intent into review/task/session/job state, user output, and cancellation. |
| Plugin public contract | Secondary | `06-module-plugin-surface.md` | Define marketplace, commands, skills, prompts, hooks, schemas, and release/version boundary. |

## Narrative Line

Public contract -> [declared commands and hooks need a reliable execution boundary] -> runtime broker -> [a broker can execute but needs user-facing intent, durable progress, and lifecycle policy] -> command orchestration and lifecycle -> [the integrated view exposes the extension's strengths and failure modes] -> evaluation.

This order intentionally begins at the user-visible boundary, descends into the broker that makes cross-runtime control possible, and returns to the command/state layer where the operational tradeoffs become tangible.
