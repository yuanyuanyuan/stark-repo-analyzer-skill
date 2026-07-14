#!/usr/bin/env python3
"""Validate exec-plan lifecycle gates for dual-agent review.

Modes:
  audit     (default)  completed plans must have Judge pass or user waiver
  bootstrap            active full-gate plans must declare required startup fields

Exit codes:
  0 success
  1 validation failure
  2 usage/runtime error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


STATUS_RE = re.compile(
    r"^(?:状态|状态：)\s*[：:]?\s*`?(proposed|active|blocked|completed|superseded|awaiting-judge)`?",
    re.MULTILINE | re.IGNORECASE,
)
# Also match table rows like | 当前状态 | `completed`...
STATUS_TABLE_RE = re.compile(
    r"\|\s*当前状态\s*\|\s*`?(proposed|active|blocked|completed|superseded|awaiting-judge)`?",
    re.IGNORECASE,
)
VERDICT_PASS_RE = re.compile(
    r"(?ims)^###\s*Judge Review\b.*?^(?:\s*[-*]\s*)?Verdict\s*:\s*`?pass`?\b",
)
WAIVER_RE = re.compile(
    r"(?is)用户(?:书面)?豁免|written\s+waiver|Judge\s*豁免"
)
WAIVER_WHO_RE = re.compile(r"(?im)豁免人\s*[:：]")
WAIVER_WHAT_RE = re.compile(r"(?im)豁免项\s*[:：]")
OMIT_JUDGE_RE = re.compile(
    r"(?is)独立Judge\s*[：:=]\s*可省略|本层可省略\s*Judge|可省略独立\s*Judge|Judge\s*=\s*可省略"
)
FULL_GATE_RE = re.compile(
    r"(?is)质量门\s*[：:=]\s*完整门|完整门|独立Judge\s*[：:=]\s*必须|必须独立\s*Judge|CLOSE-J1|CLOSE-J2"
)
BOOTSTRAP_FIELDS = (
    ("质量门", re.compile(r"(?im)质量门\s*[：:=]\s*(完整门|轻量门)")),
    ("独立Judge", re.compile(r"(?im)独立Judge\s*[：:=]\s*(必须|可省略)")),
)


@dataclass
class Finding:
    level: str
    plan: str
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def plan_files(root: Path) -> list[Path]:
    plans = sorted((root / "docs" / "exec-plans").glob("*-plan.md"))
    return [p for p in plans if p.name != "README.md"]


def progress_for(plan: Path) -> Path | None:
    candidate = plan.with_name(plan.name.replace("-plan.md", "-progress.md"))
    return candidate if candidate.is_file() else None


def extract_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    if match:
        return match.group(1).lower()
    match = STATUS_TABLE_RE.search(text)
    if match:
        return match.group(1).lower()
    # front-matter style: 状态：`completed`
    match = re.search(r"(?im)^状态：\s*`([^`]+)`", text)
    if match:
        return match.group(1).lower()
    return None


def is_full_gate(plan_text: str, progress_text: str) -> bool:
    blob = plan_text + "\n" + progress_text
    if OMIT_JUDGE_RE.search(blob) and not re.search(r"(?im)独立Judge\s*[：:=]\s*必须", blob):
        # explicit omit without mandatory wins only when full-gate markers absent
        if not re.search(r"(?im)质量门\s*[：:=]\s*完整门", blob):
            return False
    return bool(FULL_GATE_RE.search(blob))


def has_omit_judge(plan_text: str, progress_text: str) -> bool:
    return bool(OMIT_JUDGE_RE.search(plan_text + "\n" + progress_text))


def has_judge_pass(progress_text: str) -> bool:
    """Accept only a real Judge Review section, not narrative mentions."""
    if not progress_text:
        return False
    return bool(VERDICT_PASS_RE.search(progress_text))
def has_user_waiver(progress_text: str) -> bool:
    if not progress_text or not WAIVER_RE.search(progress_text):
        return False
    # Require minimal structured waiver fields when claiming waiver.
    return bool(WAIVER_WHO_RE.search(progress_text) and WAIVER_WHAT_RE.search(progress_text))


def audit(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for plan in plan_files(root):
        plan_text = read_text(plan)
        status = extract_status(plan_text)
        if status != "completed":
            continue
        progress_path = progress_for(plan)
        progress_text = read_text(progress_path) if progress_path else ""
        rel = str(plan.relative_to(root))
        # Only enforce for plans that explicitly opted into full-gate / mandatory Judge.
        # Historical completed plans without those declarations are out of scope for this gate.
        if has_omit_judge(plan_text, progress_text):
            continue
        if not is_full_gate(plan_text, progress_text):
            continue
        if has_judge_pass(progress_text):
            continue
        if has_user_waiver(progress_text):
            continue
        if progress_path is None:
            findings.append(
                Finding(
                    "error",
                    rel,
                    "status is completed but paired progress file is missing; cannot prove Judge pass/waiver",
                )
            )
            continue
        findings.append(
            Finding(
                "error",
                rel,
                "status is completed without progress Judge Review `Verdict: pass` or structured user waiver "
                "(豁免人/豁免项). Mark awaiting-judge, obtain independent Judge, or record waiver.",
            )
        )
    return findings


def bootstrap(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for plan in plan_files(root):
        plan_text = read_text(plan)
        status = extract_status(plan_text)
        if status not in {"active", "awaiting-judge", "blocked"}:
            continue
        progress_path = progress_for(plan)
        progress_text = read_text(progress_path) if progress_path else ""
        blob = plan_text + "\n" + progress_text
        rel = str(plan.relative_to(root))
        if not is_full_gate(plan_text, progress_text):
            continue
        for label, pattern in BOOTSTRAP_FIELDS:
            if not pattern.search(blob):
                findings.append(
                    Finding(
                        "error",
                        rel,
                        f"full-gate plan missing required startup field: {label}=...",
                    )
                )
        if "CLOSE-J1" not in blob and "独立 Judge" not in blob and "独立Judge" not in blob:
            findings.append(
                Finding(
                    "error",
                    rel,
                    "full-gate plan should declare CLOSE-J1/CLOSE-J2 or explicit 独立Judge close path",
                )
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("audit", "bootstrap", "all"),
        default="audit",
        help="audit completed gates, bootstrap active full-gate fields, or both",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: auto)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    root = (args.root or repo_root()).resolve()
    if not (root / "docs" / "exec-plans").is_dir():
        print(f"control-plane validation: cannot find docs/exec-plans under {root}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    if args.mode in {"audit", "all"}:
        findings.extend(audit(root))
    if args.mode in {"bootstrap", "all"}:
        findings.extend(bootstrap(root))

    payload = {
        "ok": not findings,
        "mode": args.mode,
        "root": str(root),
        "findings": [asdict(item) for item in findings],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print(f"Control-plane validation: PASS (mode={args.mode})")
        else:
            print(f"Control-plane validation: FAIL (mode={args.mode}, findings={len(findings)})")
            for item in findings:
                print(f"  - [{item.level}] {item.plan}: {item.message}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
