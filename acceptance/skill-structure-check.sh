#!/usr/bin/env bash

set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
failures=0
fail() { printf 'FAIL: %s\n' "$1"; failures=$((failures + 1)); }
pass() { printf 'PASS: %s\n' "$1"; }

for file in \
  "$ROOT/.claude-plugin/plugin.json" \
  "$ROOT/.claude-plugin/marketplace.json" \
  "$ROOT/package.json" \
  "$ROOT/skills/repo-analyzer/SKILL.md" \
  "$ROOT/skills/repo-analyzer/references/analysis-guide.md" \
  "$ROOT/skills/repo-analyzer/references/module-analysis-guide.md" \
  "$ROOT/skills/repo-analyzer/references/graphify-integration-guide.md"; do
  if [ -s "$file" ]; then pass "required skill file exists: ${file#$ROOT/}"; else fail "required skill file missing: ${file#$ROOT/}"; fi
done

for file in "$ROOT/.claude-plugin/plugin.json" "$ROOT/.claude-plugin/marketplace.json" "$ROOT/package.json"; do
  if jq empty "$file" >/dev/null 2>&1; then pass "valid JSON: ${file#$ROOT/}"; else fail "invalid JSON: ${file#$ROOT/}"; fi
done

for keyword in "分析项目" "分析仓库" "源码分析" "架构分析" "对比两个项目"; do
  if grep -Fq "$keyword" "$ROOT/skills/repo-analyzer/SKILL.md"; then pass "trigger keyword present: $keyword"; else fail "trigger keyword missing: $keyword"; fi
done

if grep -Fq 'Graphify' "$ROOT/skills/repo-analyzer/SKILL.md" && grep -Fq 'Why > What' "$ROOT/skills/repo-analyzer/SKILL.md"; then
  pass "reference workflow and Graphify enhancement are documented"
else
  fail "workflow documentation is incomplete"
fi

printf '\nSkill structure check: '
if [ "$failures" -eq 0 ]; then
  printf 'PASS\n'
  "$ROOT/acceptance/skill-contract-check.sh"
  exit $?
fi
printf 'FAIL (%s)\n' "$failures"
exit 1
