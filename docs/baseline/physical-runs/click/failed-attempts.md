# Click Physical Baseline Failed Attempts

These attempts are retained as evidence and are not counted as completed runs.

## Codex CLI c2

- Started `codex exec --json -C /tmp/stark-repo-analyzer-click-run-c2 --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check - < input.md`.
- Thread: `019f55bf-a2a5-7432-a64a-4d01487adfb9`.
- The process produced no analysis files or runtime events after approximately four minutes and was terminated. No source tree changes were observed.
- A subsequent non-PTY invocation with the same fixed input was used for completed `run-3`; its thread was `019f55c3-9cce-72e0-adcf-3f50dac340d8`.

The failed attempt is intentionally preserved rather than folded into a success record.
