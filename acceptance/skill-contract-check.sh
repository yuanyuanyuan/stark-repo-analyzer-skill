#!/usr/bin/env bash

set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)

python - "$ROOT" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
skill = (root / "skills/repo-analyzer/SKILL.md").read_text(encoding="utf-8")
graphify_guide = (root / "skills/repo-analyzer/references/graphify-integration-guide.md").read_text(encoding="utf-8")
module_guide = (root / "skills/repo-analyzer/references/module-analysis-guide.md").read_text(encoding="utf-8")
pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
gate_source = (root / "src/stark_repo_analyzer/graphify_gate.py").read_text(encoding="utf-8")
schema = json.loads((root / "docs/spec/graphify-gate-status-schema.json").read_text(encoding="utf-8"))

failures = []


def require(label, condition):
    if condition:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        failures.append(label)


require("default mode is standard", "未指定模式时直接执行 `standard`" in skill)
require("deep mode has one consolidated question round", "`deep` 只集中询问一次" in skill)
require("standard coverage is 60/30", "`standard` 的核心/次要模块最低覆盖率为 60%/30%" in skill)
require("deep coverage is 90/60", "`deep` 为 90%/60%" in skill)
require("Graphify minimum and code-only are explicit", "Graphify `0.9.13+`" in skill and "Graphify 始终使用 code-only" in skill)
require("Graphify dependency requires user choice", "安装后复检" in skill and "本次使用无 Graphify 的原版兼容流程" in skill)
require("Agent cannot install or auto-fallback", "不得代替用户安装" in skill and "不得自动进入兼容流程" in skill)
require("started gate failures block", "Graphify 已开始执行后" in skill and "必须停止" in skill)
require("single gate command is documented", "stark-repo-analyzer-graphify-gate --target <TARGET> --work-dir <WORK_DIR>" in skill)
require("source checkout module fallback is documented", "python -m stark_repo_analyzer.graphify_gate" in skill)
require("gate return boundaries are documented", all(f"`{code}`" in skill for code in (0, 10, 30)))
require("bounded scope disclosure is mandatory", all(term in skill for term in ("纳入内容", "排除内容", "选择理由", "覆盖率分母")))
require("subagent degradation needs consent", "只有用户同意后" in skill and "parallelism: degraded" in skill)
require("module guide forbids unapproved sequential fallback", "未获同意前不得开始顺序分析" in module_guide)
require("only ANALYSIS_REPORT is user-facing", "用户只接收这一份最终报告" in skill and "ANALYSIS_REPORT.md" in skill)
require("Graphify guide forbids semantic provider paths", "不启用 semantic extraction 或 LLM provider" in graphify_guide)
require("Graphify guide forbids automatic compatibility", "不能自动选择兼容流程" in graphify_guide)

scripts_section = pyproject.split("[project.scripts]", 1)[1].split("[", 1)[0]
script_rows = [line.strip() for line in scripts_section.splitlines() if "=" in line]
require("package exposes only one gate script", script_rows == [
    'stark-repo-analyzer-graphify-gate = "stark_repo_analyzer.graphify_gate:main"'
])
require("old control-plane modules are absent", not any((root / path).exists() for path in (
    "src/stark_repo_analyzer/cli.py",
    "src/stark_repo_analyzer/contracts.py",
    "src/stark_repo_analyzer/doctor.sh",
)))
require("gate source excludes backend and model state", not re.search(r"\b(?:backend|model)\b", gate_source))
require("status schema exposes 0/10/30", schema["properties"]["code"]["enum"] == [0, 10, 30])
require("status schema fixes code-only", schema["properties"]["graphify"]["properties"]["extraction_mode"]["const"] == "code-only")

forbidden_commands = re.compile(r"stark-repo-analyzer\s+(?:analyze|finalize|validate|resume)\b")
require("Skill has no old user commands", forbidden_commands.search(skill) is None)
require("Skill has no quick analysis mode", re.search(r"(?:`quick`|quick 模式|快速模式)", skill, re.I) is None)

if failures:
    print(f"\nSkill contract check: FAIL ({len(failures)})")
    raise SystemExit(1)
print("\nSkill contract check: PASS")
PY
