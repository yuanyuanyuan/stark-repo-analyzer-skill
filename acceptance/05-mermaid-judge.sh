#!/bin/sh
# 真实 Mermaid 渲染校验：用 mermaid-cli 渲染全景图。
# 缺失/失败 → WARN（非 --strict）；--strict 时 FAIL。
# 离线环境无 mmdc 且无 timeout 保护时，安全降级为 WARN，避免 npx 联网挂起。
set -u

ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
STRICT=""
[ "${1:-}" = "--strict" ] && STRICT=1

# 收集报告中的 mermaid 代码块，写出全景 .mmd
PANORAMA="$ROOT/acceptance/panorama.mmd"
: > "$PANORAMA"
found=0
for md in "$ROOT"/*.md "$ROOT"/reports/*.md; do
  [ -f "$md" ] || continue
  awk '/^```mermaid$/{f=1;next} /^```$/{if(f){f=0}} f{print}' "$md" >> "$PANORAMA"
  found=1
done
if [ "$found" -eq 0 ] || [ ! -s "$PANORAMA" ]; then
  echo "SKIP|mermaid render:全景图|未找到 mermaid 代码块"
  exit 0
fi

MMDC=$(command -v mmdc 2>/dev/null || true)
if [ -n "$MMDC" ]; then
  if $MMDC -i "$PANORAMA" -o "$ROOT/acceptance/panorama.svg" >/dev/null 2>&1; then
    echo "PASS|mermaid render:全景图|exit 0"
  elif [ -n "$STRICT" ]; then
    echo "FAIL|mermaid render:全景图|渲染失败"
  else
    echo "WARN|mermaid render:全景图|渲染不可用（非 --strict 不致命）"
  fi
else
  # mmdc 未安装：尝试 npx 安装并渲染，但用 timeout 保护以免离线环境长时间挂起。
  if command -v timeout >/dev/null 2>&1; then
    if timeout 90 npx --yes @mermaid-js/mermaid-cli -i "$PANORAMA" -o "$ROOT/acceptance/panorama.svg" >/dev/null 2>&1; then
      echo "PASS|mermaid render:全景图|exit 0 (npx)"
    elif [ -n "$STRICT" ]; then
      echo "FAIL|mermaid render:全景图|渲染失败"
    else
      echo "WARN|mermaid render:全景图|渲染不可用（非 --strict 不致命）"
    fi
  else
    # mmdc 未安装且无可用的 timeout 保护（离线环境）：--strict 时判定为 FAIL，否则 WARN。
    if [ -n "$STRICT" ]; then
      echo "FAIL|mermaid render:全景图|mmdc 未安装且无可用的 timeout 保护，离线无法渲染"
    else
      echo "WARN|mermaid render:全景图|mmdc 未安装且无可用的 timeout 保护，离线跳过"
    fi
  fi
fi
