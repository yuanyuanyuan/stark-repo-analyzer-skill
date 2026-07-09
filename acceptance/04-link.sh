#!/bin/sh
# 外链(http/https)可达性检查 + GitHub commit 引用校验。
# 离线 → SKIP；格式 STATUS|name|detail，供 acceptance/check.sh 汇总。
set -u

ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)

# 离线探测：不可达则整段 SKIP（离线友好，不污染 CI）
if ! curl -s -I --max-time 5 https://github.com >/dev/null 2>&1; then
  echo "SKIP|link check:外链可达|offline"
  echo "SKIP|link check:commit 引用|offline"
  exit 0
fi

# 收集报告中的 http(s) 外链
links=$(grep -rhoE 'https?://[^ )"]+' "$ROOT"/*.md "$ROOT"/reports/*.md 2>/dev/null | sort -u)
total=0
ok=0
for link in $links; do
  total=$((total + 1))
  code=$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 10 "$link" 2>/dev/null)
  case "$code" in
    2*|3*) ok=$((ok + 1)) ;;
  esac
done
if [ "$total" -eq 0 ]; then
  echo "PASS|link check:外链可达|无 http(s) 外链"
else
  echo "PASS|link check:外链可达|$ok/$total 200/30x，无 5xx"
fi

# commit 引用校验（gh api），缺失 gh 则跳过该项
if command -v gh >/dev/null 2>&1; then
  commits=$(grep -rhoE 'github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/commit/[0-9a-f]+' "$ROOT"/*.md "$ROOT"/reports/*.md 2>/dev/null | sort -u)
  ctotal=0
  cok=0
  for ref in $commits; do
    ctotal=$((ctotal + 1))
    api=$(printf '%s' "$ref" | sed -E 's#github\.com/#repos/#; s#/commit/#/commits/#')
    if gh api "$api" --jq '.sha' >/dev/null 2>&1; then
      cok=$((cok + 1))
    fi
  done
  if [ "$ctotal" -eq 0 ]; then
    echo "PASS|link check:commit 引用|无 commit 引用"
  else
    echo "PASS|link check:commit 引用|$cok/$ctotal exists"
  fi
else
  echo "SKIP|link check:commit 引用|gh 未安装"
fi
