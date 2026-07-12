#!/bin/bash
set -u
ROOT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to"
OUT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
echo "CMD_START $(date -Iseconds)" >> "$OUT/runner.log"
PROMPT_TEXT=$(cat "$OUT/PROMPT.txt")
/opt/homebrew/bin/codex exec \
  -C "$ROOT" \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --add-dir /tmp/Long_screenshot_splitting_tool \
  --add-dir "$OUT" \
  "$PROMPT_TEXT" \
  >"$OUT/codex-exec.stdout.txt" 2>"$OUT/codex-exec.stderr.txt"
ec=$?
echo "$ec" > "$OUT/codex-exec.exitcode"
date -Iseconds > "$OUT/codex-exec.ended"
echo "CMD_END exit=$ec $(date -Iseconds)" >> "$OUT/runner.log"
cat "$OUT/codex-exec.stdout.txt" "$OUT/codex-exec.stderr.txt" > "$OUT/codex-exec.full.log" 2>/dev/null || true
exit $ec
