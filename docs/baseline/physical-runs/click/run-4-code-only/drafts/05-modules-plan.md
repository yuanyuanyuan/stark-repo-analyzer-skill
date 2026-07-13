# Module Analysis Plan

Graphify and size scans are navigation only. The business modules below are derived from Click's data flow and public responsibilities, not copied from the `.devcontainer`/`src` directory split.

## Narrative

Decorator declarations ->[need an executable command tree and lifecycle] -> command model and Context ->[need reliable typed values] -> parameter parsing and type conversion ->[results must be visible to humans and scripts] -> terminal/help output ->[the same metadata must be projected to automation and verification] -> completion/testing/platform support.

## Core Modules

1. `module-core-command-model` — `src/click/core.py`, `src/click/decorators.py`; command tree, Context lifecycle, callback invocation and cleanup.
2. `module-parameter-resolution` — `src/click/parser.py`, `src/click/types.py`, parameter portions of `src/click/core.py`; argv/env/default/prompt resolution and typed conversion.
3. `module-terminal-experience` — `src/click/termui.py`, `src/click/formatting.py`, `src/click/utils.py`; help, prompt, output streams, progress and platform-visible behavior.

## Secondary Modules

4. `module-secondary` — `src/click/shell_completion.py`, `src/click/testing.py`, `src/click/_compat.py`, `src/click/_termui_impl.py`, `src/click/_winconsole.py`, `src/click/_textwrap.py`, `src/click/_utils.py`, `src/click/globals.py`, `src/click/exceptions.py`, `src/click/__init__.py`.

## Analysis Requirements

- One independent sub-agent per core business module.
- One independent sub-agent handles all secondary modules.
- Every draft must include role, problem, design, core data structures, Mermaid flow, module collaboration, Why > What trade-offs, source paths/lines and a final coverage table.
- Cross-module claims are resolved in `drafts/07-cross-validation.md`; runtime-only limitations remain explicitly marked.
