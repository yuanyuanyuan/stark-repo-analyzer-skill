# Secondary Module: Remote, IDE and Platform Services

## Role

Remote/IDE/platform services adapt the same agent/session core to remote control, SDK, LSP, OAuth, API, analytics and operating-system-specific facilities.

## Evidence

The entry import graph includes remote session management, bridge-safe commands, MCP, API bootstrap, OAuth, settings, LSP and analytics (`src/main.tsx:36-168`). The command registry explicitly maintains `REMOTE_SAFE_COMMANDS` and `BRIDGE_SAFE_COMMANDS`, and rejects local JSX commands over the bridge (`src/commands.ts:610-686`). This is evidence of an explicit surface-specific safety boundary.

## Design Assessment

The likely design philosophy is “one core, multiple surfaces,” with allowlists at the command boundary. That reduces duplicated product logic but makes surface capability policy a cross-cutting concern. Exact remote transport behavior, SDK event contracts and platform adapters remain unverified because only representative files were inspected and no build/dependency metadata exists.

## Coverage

| Scope | Total lines | Read | Coverage |
|---|---:|---:|---:|
| `bridge`, `remote`, `server`, `entrypoints/sdk`, `services/lsp`, platform services | not fully enumerated | representative imports only | not computable |
| **Status** | — | — | **secondary target not assessed; do not treat as pass** |
