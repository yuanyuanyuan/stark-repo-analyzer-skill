#!/usr/bin/env python3
"""Run the Codex fallback for an independent, read-only Judge review."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paired_progress(plan: Path) -> Path:
    if not plan.name.endswith("-plan.md"):
        raise ValueError("--plan must name a docs/exec-plans/*-plan.md file")
    return plan.with_name(plan.name.replace("-plan.md", "-progress.md"))


def build_prompt(root: Path, plan: Path, progress: Path) -> str:
    return f"""You are the independent Judge for a repository delivery task.

Repository: {root}
Plan: {plan.relative_to(root)}
Progress: {progress.relative_to(root)}

Read AGENTS.md and docs/dev-rules/dual-agent-review/README.md. Review only the
task increment and preserve unrelated user changes. You are strictly read-only:
do not edit files, run formatters, stage, commit, stash, reset, or change
control-plane state. Independently run at least one relevant read-only check.

Return only this Markdown section, with concrete findings and commands/results:
### Judge Review
- Verdict: pass | revise | blocked
- 刚性约束违规：
- 问题（按严重级别）：
- 缺失验证：
- 建议复查范围：
- 独立执行的验证及结果：
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path, help="paired exec plan")
    parser.add_argument("--dry-run", action="store_true", help="print the generated Judge prompt")
    args = parser.parse_args(argv)

    root = repo_root().resolve()
    plan = args.plan.resolve()
    try:
        plan.relative_to(root / "docs" / "exec-plans")
        progress = paired_progress(plan)
    except ValueError as exc:
        parser.error(str(exc))
    if not plan.is_file() or not progress.is_file():
        parser.error("--plan and its paired progress file must both exist")

    prompt = build_prompt(root, plan, progress)
    if args.dry_run:
        print(prompt)
        return 0

    codex = shutil.which("codex")
    if codex is None:
        print("codex exec fallback unavailable: `codex` is not on PATH", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="independent-judge-") as temp_dir:
        output = Path(temp_dir) / "judge-review.md"
        completed = subprocess.run(
            [codex, "exec", "--sandbox", "read-only", "--ephemeral", "--output-last-message", str(output), "-C", str(root), prompt],
            cwd=root,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode
        if not output.is_file():
            print("codex exec completed without a Judge review", file=sys.stderr)
            return 2
        print(output.read_text(encoding="utf-8").strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
