#!/bin/bash
set -u
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-regression-20260711-2133"
ROOT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to"
REPO="/tmp/Long_screenshot_splitting_tool"
PROMPT_FILE="$OUT/PROMPT.txt"
LOG="$OUT/codex-exec.full.log"
START=$(date -Iseconds)
echo "RUN_START $START" | tee -a "$OUT/runner.log"
echo "session launch" >> "$OUT/CODEX_EXEC_CMD.txt"
echo "RESTART $(date -Iseconds)" >> "$OUT/CODEX_EXEC_CMD.txt"

# Feed prompt as argument (not stdin) to avoid "Reading additional input from stdin"
PROMPT=$(cat "$PROMPT_FILE")
# Also write combined log
codex exec \
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
echo "RUN_END $END rc=$RC" | tee -a "$OUT/runner.log"
echo "$END" > "$OUT/codex-exec.ended"
# merge logs
{
  echo "===== STDOUT ====="
  cat "$OUT/codex-exec.stdout.txt"
  echo "===== STDERR ====="
  cat "$OUT/codex-exec.stderr.txt"
} > "$LOG"
exit $RC
