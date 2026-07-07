#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

python3 - "$ROOT" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
failures = []


def read(relative):
    path = root / relative
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}|{name}{('|'+detail) if detail else ''}")
    if not ok:
        failures.append(name)


def strip_fenced_code(text):
    return re.sub(r"(?ms)^```.*?^```", "", text)


required = [
    "00-meta.txt",
    "02a-repo-type.yaml",
    "02a-manifest-card.md",
    "03-question-answers.md",
    "05-module-ids.yaml",
    "08-coverage.md",
    "STATE_REPORT.md",
    "ANALYSIS_REPORT.md",
    "README.md",
]
for item in required:
    check(f"required:{item}", (root / item).is_file())

slices = sorted((root / "slices").glob("*")) if (root / "slices").is_dir() else []
check("slices present", bool(slices))

modules_text = read("05-module-ids.yaml")
module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", modules_text)
check("module ids unique", bool(module_ids) and len(module_ids) == len(set(module_ids)))
for module_id in module_ids:
    block = modules_text.split(f"- id: {module_id}", 1)[1].split("\n  - id:", 1)[0]
    check(f"module schema:{module_id}", "tier:" in block and "storyline_position:" in block)

state = read("STATE_REPORT.md")
coverage = read("08-coverage.md")
check("failed_modules tracked", "failed_modules: []" in state)
check("state final", "PASS_DETERMINISTIC_ACCEPTANCE" in state and "PASS_WITH_DETERMINISTIC_BASELINE" not in state)
check("coverage final", "已完成确定性门控" in coverage and "待 LLM" not in coverage)

markdown_files = [path for path in root.glob("*.md") if path.is_file()]
artifact_files = [path for path in root.rglob("*") if path.is_file() and "acceptance" not in path.relative_to(root).parts]
all_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in artifact_files)
markdown_text = "\n".join(strip_fenced_code(path.read_text(encoding="utf-8", errors="replace")) for path in markdown_files)
main_report = read("ANALYSIS_REPORT.md")
code_slices = [path for path in slices if path.name.startswith(("01-", "02-", "05-"))]
tools = sorted(set(re.findall(r"\bai_[A-Za-z0-9_$-]+\b", "\n".join(read(f"slices/{path.name}") for path in code_slices))))
check("api surface count", not tools or all(tool in main_report for tool in tools), f"{len(tools)} tools")

slice_refs = sorted(set(re.findall(r"slices/[A-Za-z0-9_.-]+", main_report)))
check("slice refs exist", bool(slice_refs) and all((root / ref).exists() for ref in slice_refs))

draft_refs = sorted(set(re.findall(r"drafts/[A-Za-z0-9_.-]+", main_report)))
check("draft refs exist", all((root / ref).exists() for ref in draft_refs))

readme = read("README.md")
local_links = [link for link in re.findall(r"\[[^\]]+\]\(([^)#][^)]+)\)", readme) if not link.startswith(("http://", "https://"))]
check("readme links exist", all((root / link).exists() for link in local_links))

wiki_refs = set(re.findall(r"\[\[([^\]]+)\]\]", markdown_text))
valid_wiki = set(module_ids)
check("wikilinks valid", all(ref in valid_wiki for ref in wiki_refs), ",".join(sorted(wiki_refs - valid_wiki)))

for md in markdown_files:
    text = md.read_text(encoding="utf-8", errors="replace")
    structural_text = strip_fenced_code(text)
    headings = set()
    for heading in re.findall(r"(?m)^#+\s+(.+)$", structural_text):
        slug = re.sub(r"[^a-z0-9\u4e00-\u9fff -]", "", heading.lower()).strip().replace(" ", "-")
        if slug:
            headings.add(slug)
    anchors = [anchor[1:] for anchor in re.findall(r"\(#[^)]+\)", structural_text)]
    check(f"anchors:{md.name}", all(anchor in headings for anchor in anchors))

report_names = ["tech-lead", "business", "learning"]
reports = {name: read(f"ANALYSIS_REPORT.{name}.md") for name in report_names}
if all(reports.values()):
    check("audience marker:tech", "技术负责人关注" in reports["tech-lead"])
    check("audience marker:business", "业务负责人关注" in reports["business"])
    check("audience marker:learning", "学习路径" in reports["learning"])
    pairs = [("tech-lead", "business"), ("tech-lead", "learning"), ("business", "learning")]
    for left, right in pairs:
        left_words = set(re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", reports[left]))
        right_words = set(re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", reports[right]))
        distance = 1 - (len(left_words & right_words) / max(1, len(left_words | right_words)))
        check(f"audience distance:{left}:{right}", reports[left] != reports[right] and distance >= 0.18, f"{distance:.2f}")
else:
    check("audience reports optional", True)

check("mermaid present", "```mermaid" in main_report and "flowchart TD" in main_report)
check("markdown fences balanced", main_report.count("```") % 2 == 0)
check("no placeholder claims", not any(term in all_text for term in ["待 LLM 深度分析补全", "PASS_WITH_DETERMINISTIC_BASELINE", "骨架/待补全"]))

sys.exit(1 if failures else 0)
PY
