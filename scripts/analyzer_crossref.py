#!/usr/bin/env python3
"""Cross-reference validation for repo-analyzer.

Extracted from repo_analyzer.py (T04).
"""

import re
from pathlib import Path
from typing import List

from analyzer_common import read_text
from analyzer_modules import draft_outline


def write_cross_ref(output: Path) -> List[str]:
    drafts = output / "diagnostics" / "module-drafts"
    (output / "diagnostics").mkdir(parents=True, exist_ok=True)
    module_text = (output / "data" / "module-ids.yaml").read_text(encoding="utf-8", errors="replace")
    module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", module_text)
    valid_ids = set(module_ids)
    issues = []
    seen_titles = set()
    for draft in sorted(drafts.glob("module-*.md")):
        text = draft.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"^#\s+(module_[0-9]+)", text)
        module_id = title_match.group(1) if title_match else draft.stem.replace("module-", "")
        if module_id not in valid_ids:
            issues.append(f"{draft.name}: 未在 data/module-ids.yaml 中登记")
        for ref in re.findall(r"\[\[(module_[0-9]+)\]\]", text):
            if ref not in valid_ids:
                issues.append(f"{draft.name}: 断裂引用 {ref}")
        for heading in re.findall(r"(?m)^##\s+(.+)$", text):
            key = heading.strip().lower()
            if (module_id, key) in seen_titles:
                issues.append(f"{draft.name}: 重复章节 {heading}")
            seen_titles.add((module_id, key))
    lines = [
        "# Cross-ref 校验",
        "",
        f"- 状态: {'PASS' if not issues else 'FAIL'}",
        f"- 模块数: {len(module_ids)}",
        "",
        "## 检查项",
        "- 模块草稿标题必须匹配 `data/module-ids.yaml` 中的 ID。",
        "- `[[module_xxx]]` 引用必须能解析到模块清单。",
        "- 单个模块草稿不应出现重复二级章节。",
        "",
        "## 问题",
    ]
    lines.extend(f"- {issue}" for issue in issues)
    if not issues:
        lines.append("- 未发现断裂引用或重复章节。")
    (output / "diagnostics" / "cross-ref-checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return issues


def write_cross_ref_review_packet(output: Path) -> str:
    packet = "\n\n".join(
        [
            "# Cross-ref 审稿包",
            "## 模块清单\n```yaml\n" + read_text(output / "data" / "module-ids.yaml", 120_000) + "\n```",
            "## 确定性 cross-ref\n```text\n" + read_text(output / "diagnostics" / "cross-ref-checks.md", 120_000) + "\n```",
            "## 覆盖率摘要\n```text\n" + read_text(output / "data" / "coverage.md", 120_000) + "\n```",
            "## 模块草稿结构\n" + "\n\n".join(draft_outline(path) for path in sorted((output / "diagnostics" / "module-drafts").glob("module-*.md"))),
        ]
    )
    packet_path = output / "diagnostics" / "cross-ref-review-input.md"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(packet + "\n", encoding="utf-8")
    return packet
