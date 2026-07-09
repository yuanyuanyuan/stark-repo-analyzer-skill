#!/usr/bin/env python3
"""Acceptance script generation for repo-analyzer.

Extracted from repo_analyzer.py (T05). Updated for T08 directory restructure.
"""

import shutil
from pathlib import Path


def write_acceptance(output: Path) -> None:
    acceptance = output / "acceptance"
    acceptance.mkdir(parents=True, exist_ok=True)
    # T12：将 3 个扩展验收执行器脚本随 check.sh 一起落地到 output/acceptance/，
    # 使 check.sh 能在 ROOT/acceptance 下找到它们（脚本自身按 $0 定位分析产物目录）。
    skill_root = Path(__file__).resolve().parents[1]
    skill_acceptance = skill_root / "acceptance"
    for name in ("04-link.sh", "05-mermaid-judge.sh", "llm-judge.sh"):
        src = skill_acceptance / name
        if src.exists():
            shutil.copyfile(src, acceptance / name)
            (acceptance / name).chmod(0o755)
            # Issue 5: Replace __SKILL_ROOT__ placeholder with the actual skill
            # root path so llm-judge.sh can locate scripts/llm_judge.py without
            # relying on $0 relative probing.
            if name == "llm-judge.sh":
                content = (acceptance / name).read_text(encoding="utf-8")
                content = content.replace('"__SKILL_ROOT__"', f'"{skill_root}"')
                (acceptance / name).write_text(content, encoding="utf-8")
                (acceptance / name).chmod(0o755)
    check = acceptance / "check.sh"
    check.write_text(
        """#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

python3 - "$ROOT" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
failures = []
_pass_count = 0


def read(relative):
    path = root / relative
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def check(name, ok, detail=""):
    global _pass_count
    status = "PASS" if ok else "FAIL"
    print(f"{status}|{name}{('|'+detail) if detail else ''}")
    if ok:
        _pass_count += 1
    else:
        failures.append(name)


def strip_fenced_code(text):
    return re.sub(r"(?ms)^```.*?^```", "", text)


required = [
    "data/meta.txt",
    "data/repo-type.yaml",
    "data/manifest-card.md",
    "data/question-answers.md",
    "data/module-ids.yaml",
    "data/coverage.md",
    "data/expected-symbols.json",
    "data/coverage-symbols.json",
    "data/mcp-tools.json",
    "reports/STATE_REPORT.md",
    "reports/SLA_REPORT.md",
    "reports/PERFORMANCE_REPORT.md",
    "data/performance-report.json",
    "data/config-effective.json",
    "data/report-data.json",
    "data/agent-summary.json",
    "reports/ANALYSIS_REPORT.md",
    "reports/README.md",
    "diagnostics/cross-ref-checks.md",
]
for item in required:
    check(f"required:{item}", (root / item).is_file())

slices = sorted((root / "diagnostics" / "slices").glob("*")) if (root / "diagnostics" / "slices").is_dir() else []
check("slices present", bool(slices))

modules_text = read("data/module-ids.yaml")
module_ids = re.findall(r"(?m)^\\s*- id: (module_[0-9]+)", modules_text)
check("module ids unique", bool(module_ids) and len(module_ids) == len(set(module_ids)))
for module_id in module_ids:
    block = modules_text.split(f"- id: {module_id}", 1)[1].split("\\n  - id:", 1)[0]
    check(f"module schema:{module_id}", "tier:" in block and "storyline_position:" in block)

state = read("reports/STATE_REPORT.md")
coverage = read("data/coverage.md")
performance_report = read("reports/PERFORMANCE_REPORT.md")
check("failed_modules tracked", "failed_modules: []" in state)
check("state final", "PASS_DETERMINISTIC_ACCEPTANCE" in state and "PASS_WITH_DETERMINISTIC_BASELINE" not in state)
check("coverage final", "状态: PASS" in coverage and "待 LLM" not in coverage)
check("coverage engine recorded", "engine:" in coverage and "tree_sitter_available:" in coverage)
check("cross-ref pass", "状态: PASS" in read("diagnostics/cross-ref-checks.md"))
check("sla pass", "status: PASS" in read("reports/SLA_REPORT.md"))
check("performance diagnostic present", "慢因结论" in performance_report and "阶段耗时 Top20" in performance_report)
check("timeout not default fix", "agent_timeout: disabled" in performance_report or "agent_timeout: enabled" in performance_report)

try:
    expected_data = json.loads(read("data/expected-symbols.json"))
    check("expected symbols json parse", isinstance(expected_data.get("symbols"), list) and "engine" in expected_data)
except json.JSONDecodeError:
    check("expected symbols json parse", False)

try:
    coverage_data = json.loads(read("data/coverage-symbols.json"))
except json.JSONDecodeError:
    coverage_data = {"modules": {}}
    check("coverage json parse", False)

try:
    agent_summary = json.loads(read("data/agent-summary.json"))
    check("agent summary json parse", isinstance(agent_summary, dict) and "mode" in agent_summary and "status" in agent_summary)
    if agent_summary.get("mode") != "deterministic":
        check("agent summary pass", agent_summary.get("status") == "PASS")
except json.JSONDecodeError:
    agent_summary = {}
    check("agent summary json parse", False)
try:
    performance = json.loads(read("data/performance-report.json"))
    check("performance json parse", isinstance(performance.get("stages"), list) and "summary" in performance)
except json.JSONDecodeError:
    performance = {}
    check("performance json parse", False)
for module_id, item in coverage_data.get("modules", {}).items():
    draft_text = read(f"diagnostics/module-drafts/module-{module_id}.md")
    threshold = float(item.get("threshold", 0))
    expected = item.get("expected_symbols", [])
    covered_now = []
    for symbol in expected:
        name = symbol.get("name", "")
        ok = bool(name) and re.search(rf"\\b{re.escape(name)}\\b", draft_text)
        check(f"coverage symbol:{module_id}:{name}", ok)
        if ok:
            covered_now.append(name)
    ratio = 1.0 if not expected else len(set(covered_now)) / max(1, len({symbol.get("name", "") for symbol in expected if symbol.get("name")}))
    check(f"coverage gate:{module_id}", ratio >= threshold, f"{ratio:.2f}/{threshold:.2f}")

failed_blocks = re.findall(r"(?m)^  - id: (module_[0-9]+)\\n((?:    .+\\n)+)", state)
for module_id, block in failed_blocks:
    check(
        f"failed module schema:{module_id}",
        all(field in block for field in ["tier:", "attempts:", "last_error:", "coverage_ratio:", "missing_symbols_count:", "suggested_recovery:"]),
    )

markdown_files = [path for path in (root / "reports").glob("*.md") if path.is_file()]
claim_files = [
    path
    for path in root.rglob("*")
    if path.is_file()
    and "acceptance" not in path.relative_to(root).parts
    and "agent-runs" not in path.relative_to(root).parts
    and (path.name.startswith("ANALYSIS_REPORT") or path.name in {"coverage.md", "STATE_REPORT.md", "SLA_REPORT.md"})
]
claim_text = "\\n".join(path.read_text(encoding="utf-8", errors="replace") for path in claim_files)
markdown_text = "\\n".join(strip_fenced_code(path.read_text(encoding="utf-8", errors="replace")) for path in markdown_files)
main_report = read("reports/ANALYSIS_REPORT.md")
check("failed section absent on pass", "§9 未完成模块明细" not in main_report)
try:
    tools = sorted(item["name"] for item in json.loads(read("data/mcp-tools.json")))
except (json.JSONDecodeError, KeyError, TypeError):
    tools = []
    check("mcp tools json parse", False)
check("api surface count", not tools or all(tool in main_report for tool in tools), f"{len(tools)} tools")

slice_refs = sorted(set(re.findall(r"diagnostics/slices/[A-Za-z0-9_.-]+", main_report)))
check("slice refs exist", bool(slice_refs) and all((root / ref).exists() for ref in slice_refs))

draft_refs = sorted(set(re.findall(r"diagnostics/module-drafts/[A-Za-z0-9_.-]+", main_report)))
check("draft refs exist", all((root / ref).exists() for ref in draft_refs))

readme_path = root / "reports" / "README.md"
readme = read("reports/README.md")
local_links = [link for link in re.findall(r"\\[[^\\]]+\\]\\(([^)#][^)]+)\\)", readme) if not link.startswith(("http://", "https://"))]
check("readme links exist", all((readme_path.parent / link).resolve().exists() for link in local_links))

wiki_refs = set(re.findall(r"\\[\\[([^\\]]+)\\]\\]", markdown_text))
valid_wiki = set(module_ids)
check("wikilinks valid", all(ref in valid_wiki for ref in wiki_refs), ",".join(sorted(wiki_refs - valid_wiki)))

for md in markdown_files:
    text = md.read_text(encoding="utf-8", errors="replace")
    structural_text = strip_fenced_code(text)
    headings = set()
    for heading in re.findall(r"(?m)^#+\\s+(.+)$", structural_text):
        slug = re.sub(r"[^a-z0-9\\u4e00-\\u9fff -]", "", heading.lower()).strip().replace(" ", "-")
        if slug:
            headings.add(slug)
    anchors = [anchor[1:] for anchor in re.findall(r"\\(#[^)]+\\)", structural_text)]
    check(f"anchors:{md.name}", all(anchor in headings for anchor in anchors))

report_names = ["tech-lead", "business", "learning"]
reports = {name: read(f"reports/ANALYSIS_REPORT.{name}.md") for name in report_names}
if all(reports.values()):
    check("main report distinct", all(main_report != report for report in reports.values()))
    check("audience marker:tech", "技术负责人关注" in reports["tech-lead"])
    check("audience marker:business", "业务负责人关注" in reports["business"])
    check("audience marker:learning", "学习路径" in reports["learning"])
    if agent_summary.get("mode") != "deterministic":
        combined_reports = main_report + "\\n" + "\\n".join(reports.values())
        check("agent insights in main report", "Agent 深度分析摘要" in main_report)
        check("agent insights in tech report", "Agent 深度分析摘要" in reports["tech-lead"])
        check("agent insights in audience reports", "Agent insight 摘要" in reports["business"] and "Agent insight 学习线索" in reports["learning"])
        check("agent insights substantive", "业务角色" in combined_reports and "attempts:" not in combined_reports)
        check("agent reports not stale", "需要后续 subagent 深化" not in combined_reports)
    pairs = [("tech-lead", "business"), ("tech-lead", "learning"), ("business", "learning")]
    for left, right in pairs:
        left_words = set(re.findall(r"[A-Za-z0-9_\\u4e00-\\u9fff]+", reports[left]))
        right_words = set(re.findall(r"[A-Za-z0-9_\\u4e00-\\u9fff]+", reports[right]))
        distance = 1 - (len(left_words & right_words) / max(1, len(left_words | right_words)))
        check(f"audience distance:{left}:{right}", reports[left] != reports[right] and distance >= 0.18, f"{distance:.2f}")
else:
    check("audience reports optional", True)

check("mermaid present", "```mermaid" in main_report and "flowchart TD" in main_report)
check("markdown fences balanced", main_report.count("```") % 2 == 0)
check("no placeholder claims", not any(term in claim_text for term in ["待 LLM 深度分析补全", "PASS_WITH_DETERMINISTIC_BASELINE", "骨架/待补全"]))

# --- 扩展验收执行器（T12）：链接可达性 / Mermaid 校验 / LLM 裁判 ---
# 解析各执行器输出的 STATUS|name|detail 行，聚合为 PASS/FAIL/WARN/SKIP 计数。
import subprocess as _subprocess

_warn_count = 0
_skip_count = 0


def run_executor(script_name):
    global _warn_count, _skip_count
    script = root / "acceptance" / script_name
    if not script.exists():
        check(f"executor:{script_name}", False, "脚本缺失")
        return
    try:
        proc = _subprocess.run(
            ["sh", str(script), str(root)],
            stdout=_subprocess.PIPE,
            stderr=_subprocess.PIPE,
            text=True,
            timeout=120,
        )
    except _subprocess.TimeoutExpired:
        check(f"executor:{script_name}", False, "执行超时")
        return
    parsed_lines = 0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|", 2)
        status = parts[0].strip()
        name = parts[1].strip() if len(parts) > 1 else script_name
        detail = parts[2].strip() if len(parts) > 2 else ""
        parsed_lines += 1
        if status == "PASS":
            check(f"{name}", True, detail)
        elif status == "SKIP":
            _skip_count += 1
            print(f"SKIP|{name}{('|'+detail) if detail else ''}")
        elif status == "WARN":
            _warn_count += 1
            print(f"WARN|{name}{('|'+detail) if detail else ''}")
        else:
            check(f"{name}", False, detail)
    # Issue 5: If the executor exited non-zero and produced no status lines,
    # it crashed silently — report as FAIL instead of ignoring.
    if proc.returncode != 0 and parsed_lines == 0:
        stderr_tail = (proc.stderr or "").strip().splitlines()[-1] if proc.stderr else ""
        check(f"executor:{script_name}", False, f"exit code {proc.returncode}{('|'+stderr_tail) if stderr_tail else ''}")


run_executor("04-link.sh")
run_executor("05-mermaid-judge.sh")
run_executor("llm-judge.sh")


_total = _pass_count + len(failures) + _warn_count + _skip_count
print(f"TOTAL:{_total} PASS:{_pass_count} FAIL:{len(failures)} WARN:{_warn_count} SKIP:{_skip_count}")

sys.exit(1 if failures else 0)
PY
""",
        encoding="utf-8",
    )
    check.chmod(0o755)
