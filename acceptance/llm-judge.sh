#!/bin/sh
# LLM-judge 入口：调用 scripts/llm_judge.py（codex exec）。
# 输出 STATUS|name|detail 行，供 acceptance/check.sh 汇总。
set -u

ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
STRICT=""
[ "${1:-}" = "--strict" ] && STRICT=1

# 定位 skill 根目录（含 scripts/llm_judge.py）。
# __SKILL_ROOT__ 由 write_acceptance 在分析产物中替换为绝对路径；
# 仓库内已提交副本该值为空占位符，回退到 $0 相对探测。
SKILL_ROOT="__SKILL_ROOT__"
if [ "$SKILL_ROOT" = "__SKILL_ROOT__" ] || [ -z "$SKILL_ROOT" ] || [ ! -f "$SKILL_ROOT/scripts/llm_judge.py" ]; then
  SKILL_ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
  for d in "$SKILL_ROOT" "$SKILL_ROOT/.." "$SKILL_ROOT/../.." "$SKILL_ROOT/../../.."; do
    if [ -f "$d/scripts/llm_judge.py" ]; then
      SKILL_ROOT="$d"
      break
    fi
  done
fi

if [ ! -f "$SKILL_ROOT/scripts/llm_judge.py" ]; then
  echo "SKIP|llm-judge:执行|scripts/llm_judge.py 未找到"
  exit 0
fi

python3 "$SKILL_ROOT/scripts/llm_judge.py" "$ROOT" ${STRICT:+--strict}
