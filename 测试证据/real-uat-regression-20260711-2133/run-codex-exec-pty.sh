#!/bin/bash
set -u
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-2133"
ROOT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to"
REPO="/tmp/Long_screenshot_splitting_tool"
PROMPT=$(cat "$OUT/PROMPT.txt")
START=$(date -Iseconds)
echo "PTY_RUN_START $START" | tee -a "$OUT/runner.log"

# script provides a pseudo-TTY which some CLIs require
script -q /dev/null codex exec \
  -C "$ROOT" \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --add-dir "$REPO" \
  --add-dir "$OUT" \
  "$PROMPT" \
  >"$OUT/codex-exec.stdout.txt" 2>"$OUT/codex-exec.stderr.txt"
RC=$?
END=$(date -Iseconds)
echo "$RC" > "$OUT/codex-exec.exitcode"
echo "PTY_RUN_END $END rc=$RC" | tee -a "$OUT/runner.log"
echo "$END" > "$OUT/codex-exec.ended"
{
  echo "===== STDOUT ====="
  cat "$OUT/codex-exec.stdout.txt"
  echo "===== STDERR ====="
  cat "$OUT/codex-exec.stderr.txt"
} > "$OUT/codex-exec.full.log"
exit $RC
