#!/bin/bash
set -u
export PATH="/opt/homebrew/bin:/usr/bin:/bin:$PATH"
OUT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-wired-20260711-220005"
ROOT="/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to"
cd "$ROOT" || exit 97
echo "CMD_START $(date -Iseconds)" >> "$OUT/runner.log"
echo "$$" > "$OUT/daemon.pid"
/opt/homebrew/bin/codex exec \
  -C "$ROOT" \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  --add-dir /tmp/Long_screenshot_splitting_tool \
  --add-dir "$OUT" \
  "$(cat "$OUT/PROMPT.txt")" \
  >"$OUT/codex-exec.stdout.txt" 2>"$OUT/codex-exec.stderr.txt"
ec=$?
echo "$ec" > "$OUT/codex-exec.exitcode"
date -Iseconds > "$OUT/codex-exec.ended"
echo "CMD_END exit=$ec $(date -Iseconds)" >> "$OUT/runner.log"
cat "$OUT/codex-exec.stdout.txt" "$OUT/codex-exec.stderr.txt" > "$OUT/codex-exec.full.log" 2>/dev/null || true
