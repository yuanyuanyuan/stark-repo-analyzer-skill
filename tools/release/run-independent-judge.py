#!/usr/bin/env python3
"""Run the Codex fallback for an independent, read-only Judge review.

Uses a scoped review package and fixed model/reasoning settings so fallback
does not inherit drifting user defaults.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_RELEASE_DIR = Path(__file__).resolve().parent
if str(_RELEASE_DIR) not in sys.path:
    sys.path.insert(0, str(_RELEASE_DIR))

from judge_review_package import (
    JUDGE_MODEL,
    JUDGE_REASONING_EFFORT,
    ReviewPackage,
    blocked_review_markdown,
    build_package,
    default_artifact_path,
    load_package,
    paired_progress,
    write_package,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_prompt(root: Path, package: ReviewPackage) -> str:
    package_md = package.to_markdown()
    return f"""You are the independent Judge for a repository delivery task.

Repository: {root}
Fixed model/reasoning for this review: {package.model} / {package.reasoning_effort}

You MUST review only the scoped review package below. Do not expand into
excluded paths or invent ownership from a dirty worktree. If the package is
incomplete, return blocked: insufficient review package and stop.

Read AGENTS.md and docs/dev-rules/dual-agent-review/README.md for protocol.
You are strictly read-only: do not edit files, run formatters, stage, commit,
stash, reset, or change control-plane state. Independently run at least one
relevant read-only check against the owned files.

Blocking findings are limited to the package blocking_criteria. Style
preferences, optional refactors, out-of-scope discoveries, and historical
issues outside current acceptance are non-blocking suggestions only.

## Review package
{package_md}

Return only this Markdown section, with concrete findings and commands/results:
### Judge Review
- Verdict: pass | revise | blocked
- 刚性约束违规：
- 问题（按严重级别）：
- 缺失验证：
- 建议复查范围：
- 独立执行的验证及结果：
- 实际模型 / 推理等级：`{package.model}` / `{package.reasoning_effort}`
"""


def resolve_package(
    root: Path,
    plan: Path,
    package_path: Path | None,
    *,
    owned_files: list[str] | None,
    exclude_files: list[str] | None,
    goal: str | None,
    acceptance: list[str] | None,
) -> tuple[ReviewPackage, Path]:
    path = package_path or default_artifact_path(plan)
    if package_path and package_path.is_file():
        return load_package(package_path), package_path
    if path.is_file() and not any([owned_files, exclude_files, goal, acceptance]):
        return load_package(path), path
    package = build_package(
        root,
        plan,
        user_goal=goal,
        acceptance_items=acceptance,
        owned_files=owned_files,
        excluded_user_changes=exclude_files,
    )
    write_package(package, path)
    return package, path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path, help="paired exec plan")
    parser.add_argument(
        "--package",
        type=Path,
        default=None,
        help="existing review package JSON; default artifact path is used when present",
    )
    parser.add_argument("--goal", default=None, help="override user goal when building package")
    parser.add_argument(
        "--acceptance",
        action="append",
        default=None,
        help="acceptance item when building package (repeatable)",
    )
    parser.add_argument(
        "--owned-file",
        action="append",
        default=None,
        dest="owned_files",
        help="task-owned file when building package (repeatable)",
    )
    parser.add_argument(
        "--exclude-file",
        action="append",
        default=None,
        dest="exclude_files",
        help="excluded pre-existing user change (repeatable)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print Judge prompt only")
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="print the codex exec argv that would run, then exit 0",
    )
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

    package, package_path = resolve_package(
        root,
        plan,
        args.package.resolve() if args.package else None,
        owned_files=args.owned_files,
        exclude_files=args.exclude_files,
        goal=args.goal,
        acceptance=args.acceptance,
    )
    # Fixed Judge runtime config cannot be overridden by package artifacts.
    package.model = JUDGE_MODEL
    package.reasoning_effort = JUDGE_REASONING_EFFORT
    missing = package.missing_fields()
    if missing:
        sys.stdout.write(blocked_review_markdown(missing))
        print(
            f"review package incomplete at {package_path}: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 3

    prompt = build_prompt(root, package)
    codex_cmd = [
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "-m",
        package.model or JUDGE_MODEL,
        "-c",
        f"model_reasoning_effort={package.reasoning_effort or JUDGE_REASONING_EFFORT}",
        "--output-last-message",
        "__OUTPUT__",
        "-C",
        str(root),
        prompt,
    ]

    if args.print_command:
        printable = [
            part if part != "__OUTPUT__" else "<temp-output>"
            for part in codex_cmd
        ]
        # Keep prompt compact in command dump.
        printable[-1] = "<prompt>"
        print(" ".join(shlex_quote(part) for part in printable))
        print(f"# package={package_path}")
        print(f"# model={package.model} reasoning={package.reasoning_effort}")
        return 0

    if args.dry_run:
        print(prompt)
        return 0

    codex = shutil.which("codex")
    if codex is None:
        print("codex exec fallback unavailable: `codex` is not on PATH", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="independent-judge-") as temp_dir:
        output = Path(temp_dir) / "judge-review.md"
        cmd = [codex if part == "codex" else part for part in codex_cmd]
        cmd[cmd.index("__OUTPUT__")] = str(output)
        completed = subprocess.run(
            cmd,
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


def shlex_quote(value: str) -> str:
    if not value:
        return "''"
    if all(ch.isalnum() or ch in "@%_+-=:,./" for ch in value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
