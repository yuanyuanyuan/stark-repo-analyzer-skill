#!/bin/bash
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-2133"
ROOT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to"
REPO="/tmp/Long_screenshot_splitting_tool"
cd "$ROOT" || exit 1
PROMPT=$(cat "$OUT/PROMPT.txt")
export NODE_OPTIONS=""
echo "DAEMONIZE_START $(date -Iseconds)" >> "$OUT/runner.log"
# redirect all FDs, new session
exec </dev/null
codex exec \
  -C "$ROOT" \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --add-dir "$REPO" \
  --add-dir "$OUT" \
  "$PROMPT" \
  >"$OUT/codex-exec.stdout.txt" 2>"$OUT/codex-exec.stderr.txt"
RC=$?
echo "$RC" > "$OUT/codex-exec.exitcode"
date -Iseconds > "$OUT/codex-exec.ended"
echo "DAEMONIZE_END $(date -Iseconds) rc=$RC" >> "$OUT/runner.log"
{
  echo "===== STDOUT ====="; cat "$OUT/codex-exec.stdout.txt"
  echo "===== STDERR ====="; cat "$OUT/codex-exec.stderr.txt"
} > "$OUT/codex-exec.full.log"
