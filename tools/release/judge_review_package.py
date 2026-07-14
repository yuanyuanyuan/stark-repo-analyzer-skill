#!/usr/bin/env python3
"""Build and validate scoped Judge review packages.

The review package is the only Judge input boundary. Missing required fields
must produce a deterministic blocked verdict; Judges must not invent scope from
a dirty worktree.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JUDGE_MODEL = "gpt-5.6-terra"
JUDGE_REASONING_EFFORT = "medium"
INSUFFICIENT_PACKAGE = "blocked: insufficient review package"

REQUIRED_FIELDS = (
    "user_goal",
    "acceptance_items",
    "startup_baseline",
    "owned_files",
    "excluded_user_changes",
    "worker_verification",
    "blocking_criteria",
    "plan",
    "progress",
)

DEFAULT_BLOCKING_CRITERIA = [
    "违反用户明确目标、验收项或审查包范围",
    "可复现功能错误、数据/安全风险、控制面状态错误",
    "任务要求但缺失的验证证据",
    "审查包缺字段或边界无法确认",
]

NON_BLOCKING_HINTS = [
    "风格偏好",
    "可选重构",
    "范围外发现",
    "不影响当前验收的历史问题",
]


@dataclass
class WorkerVerification:
    commands_run: list[str] = field(default_factory=list)
    results: list[str] = field(default_factory=list)
    not_run: list[str] = field(default_factory=list)
    deviations: str = "无"

    def is_populated(self) -> bool:
        return bool(self.commands_run or self.results or self.not_run)


@dataclass
class ReviewPackage:
    user_goal: str
    acceptance_items: list[str]
    startup_baseline: dict[str, Any]
    owned_files: list[str]
    excluded_user_changes: list[str] | None
    worker_verification: WorkerVerification
    blocking_criteria: list[str]
    plan: str
    progress: str
    model: str = JUDGE_MODEL
    reasoning_effort: str = JUDGE_REASONING_EFFORT
    non_blocking_hints: list[str] = field(default_factory=lambda: list(NON_BLOCKING_HINTS))
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def missing_fields(self) -> list[str]:
        missing: list[str] = []
        if not str(self.user_goal or "").strip():
            missing.append("user_goal")
        if not self.acceptance_items:
            missing.append("acceptance_items")
        baseline = self.startup_baseline or {}
        # Require explicit baseline capture fields; summary alone is insufficient.
        if "git_status_short" not in baseline or not str(baseline.get("captured_at") or "").strip():
            missing.append("startup_baseline")
        if not self.owned_files:
            missing.append("owned_files")
        # Empty list is valid (no excluded files), but the field must be present.
        if self.excluded_user_changes is None:
            missing.append("excluded_user_changes")
        if not self.worker_verification or not self.worker_verification.is_populated():
            missing.append("worker_verification")
        if not self.blocking_criteria:
            missing.append("blocking_criteria")
        if not str(self.plan or "").strip():
            missing.append("plan")
        if not str(self.progress or "").strip():
            missing.append("progress")
        return missing

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload

    def to_markdown(self) -> str:
        missing = self.missing_fields()
        lines = [
            "# Judge 审查包",
            "",
            f"- 模型 / 推理等级：`{self.model}` / `{self.reasoning_effort}`",
            f"- plan：`{self.plan}`",
            f"- progress：`{self.progress}`",
            f"- generated_at：{self.generated_at}",
            "",
            "## 用户目标",
            self.user_goal.strip() or "（缺失）",
            "",
            "## 验收项",
        ]
        if self.acceptance_items:
            lines.extend(f"- {item}" for item in self.acceptance_items)
        else:
            lines.append("- （缺失）")
        lines.extend(
            [
                "",
                "## 启动基线",
                f"- summary：{self.startup_baseline.get('summary', '')}",
                f"- captured_at：{self.startup_baseline.get('captured_at', '')}",
                "```",
                str(self.startup_baseline.get("git_status_short", "")).rstrip() or "（空）",
                "```",
                "",
                "## 本任务拥有的文件范围",
            ]
        )
        if self.owned_files:
            lines.extend(f"- `{path}`" for path in self.owned_files)
        else:
            lines.append("- （缺失）")
        lines.extend(["", "## 明确排除的用户已有改动"])
        if self.excluded_user_changes is None:
            lines.append("- （缺失）")
        elif self.excluded_user_changes:
            lines.extend(f"- `{path}`" for path in self.excluded_user_changes)
        else:
            lines.append("- （无）")
        verification = self.worker_verification
        lines.extend(
            [
                "",
                "## Worker 自验证据",
                "### 已跑命令",
            ]
        )
        lines.extend(f"- {item}" for item in (verification.commands_run or ["（缺失）"]))
        lines.append("### 退出码 / 关键结果")
        lines.extend(f"- {item}" for item in (verification.results or ["（缺失）"]))
        lines.append("### 未执行项")
        lines.extend(f"- {item}" for item in (verification.not_run or ["（无）"]))
        lines.append(f"### Deviations\n{verification.deviations or '无'}")
        lines.extend(["", "## 阻塞标准"])
        lines.extend(f"- {item}" for item in (self.blocking_criteria or ["（缺失）"]))
        lines.extend(["", "## 非阻塞建议类别"])
        lines.extend(f"- {item}" for item in self.non_blocking_hints)
        if missing:
            lines.extend(
                [
                    "",
                    "## 包完整性",
                    f"- 状态：`{INSUFFICIENT_PACKAGE}`",
                    f"- 缺失字段：{', '.join(missing)}",
                ]
            )
        else:
            lines.extend(["", "## 包完整性", "- 状态：complete"])
        return "\n".join(lines) + "\n"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paired_progress(plan: Path) -> Path:
    if not plan.name.endswith("-plan.md"):
        raise ValueError("--plan must name a docs/exec-plans/*-plan.md file")
    return plan.with_name(plan.name.replace("-plan.md", "-progress.md"))


def default_artifact_path(plan: Path) -> Path:
    artifacts = plan.parent / "artifacts"
    stem = plan.name.replace("-plan.md", "")
    return artifacts / f"{stem}-review-package.json"


def capture_git_status(root: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout


def parse_section_bullets(text: str, heading: str) -> list[str]:
    pattern = re.compile(
        rf"(?ims)^##+\s*{re.escape(heading)}\s*$([\s\S]*?)(?=^##+\s|\Z)"
    )
    match = pattern.search(text)
    if not match:
        return []
    body = match.group(1)
    items: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            items.append(re.sub(r"^\d+\.\s+", "", stripped).strip())
    return [item for item in items if item]


def extract_goal(plan_text: str) -> str:
    for heading in ("目标", "当前主线", "北极星目标"):
        items = parse_section_bullets(plan_text, heading)
        if items:
            return "\n".join(items)
        pattern = re.compile(
            rf"(?ims)^###?\s*{heading}\s*$([\s\S]*?)(?=^##|\Z)"
        )
        match = pattern.search(plan_text)
        if match:
            body = match.group(1).strip()
            if body:
                # Keep first non-empty paragraph-ish block.
                paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
                if paragraphs:
                    return paragraphs[0][:2000]
    return ""


def extract_acceptance(plan_text: str) -> list[str]:
    for heading in ("完成条件", "验收项", "完成口径"):
        items = parse_section_bullets(plan_text, heading)
        if items:
            return items
    return []


def extract_worker_verification(progress_text: str) -> WorkerVerification:
    commands: list[str] = []
    results: list[str] = []
    not_run: list[str] = []
    deviations = "无"

    # Prefer the latest Worker 验证 section.
    sections = list(
        re.finditer(r"(?ims)^###\s*Worker 验证\s*$([\s\S]*?)(?=^###\s|^##\s|\Z)", progress_text)
    )
    body = sections[-1].group(1) if sections else progress_text
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ")):
            item = stripped[2:].strip()
            lower = item.lower()
            if "未执行" in item or "not run" in lower:
                not_run.append(item)
            elif "exit" in lower or "通过" in item or "fail" in lower or "pass" in lower:
                results.append(item)
            else:
                commands.append(item)
        if stripped.startswith("### Deviations") or stripped.startswith("Deviations"):
            continue
    dev_match = re.search(
        r"(?ims)^###\s*Deviations\s*$([\s\S]*?)(?=^###\s|^##\s|\Z)", progress_text
    )
    if dev_match:
        deviations = dev_match.group(1).strip() or "无"
    return WorkerVerification(
        commands_run=commands,
        results=results,
        not_run=not_run,
        deviations=deviations,
    )


def build_package(
    root: Path,
    plan: Path,
    *,
    user_goal: str | None = None,
    acceptance_items: list[str] | None = None,
    owned_files: list[str] | None = None,
    excluded_user_changes: list[str] | None = None,
    startup_baseline: dict[str, Any] | None = None,
    worker_verification: WorkerVerification | None = None,
    blocking_criteria: list[str] | None = None,
    capture_status: bool = True,
) -> ReviewPackage:
    plan = plan.resolve()
    progress = paired_progress(plan)
    plan_text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    progress_text = progress.read_text(encoding="utf-8") if progress.is_file() else ""

    if startup_baseline is None:
        status = capture_git_status(root) if capture_status else ""
        startup_baseline = {
            "summary": "git status --short at package build time",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "git_status_short": status,
        }

    if worker_verification is None:
        worker_verification = extract_worker_verification(progress_text)

    rel_plan = str(plan.relative_to(root)) if plan.is_relative_to(root) else str(plan)
    rel_progress = (
        str(progress.relative_to(root)) if progress.is_relative_to(root) else str(progress)
    )

    return ReviewPackage(
        user_goal=(user_goal if user_goal is not None else extract_goal(plan_text)).strip(),
        acceptance_items=list(
            acceptance_items if acceptance_items is not None else extract_acceptance(plan_text)
        ),
        startup_baseline=startup_baseline,
        owned_files=list(owned_files or []),
        excluded_user_changes=list(
            excluded_user_changes if excluded_user_changes is not None else []
        ),
        worker_verification=worker_verification,
        blocking_criteria=list(blocking_criteria or DEFAULT_BLOCKING_CRITERIA),
        plan=rel_plan,
        progress=rel_progress,
    )


def load_package(path: Path) -> ReviewPackage:
    """Load a package without inventing required fields.

    Missing required keys stay missing so missing_fields() can fail closed.
    Model/reasoning are always forced to the fixed Judge config.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if "worker_verification" in data and isinstance(data.get("worker_verification"), dict):
        verification_raw = data["worker_verification"]
        verification = WorkerVerification(
            commands_run=list(verification_raw.get("commands_run") or []),
            results=list(verification_raw.get("results") or []),
            not_run=list(verification_raw.get("not_run") or []),
            deviations=str(verification_raw.get("deviations") or "无"),
        )
    else:
        verification = WorkerVerification()

    excluded: list[str] | None
    if "excluded_user_changes" in data:
        excluded = list(data.get("excluded_user_changes") or [])
    else:
        excluded = None

    blocking: list[str]
    if "blocking_criteria" in data:
        blocking = list(data.get("blocking_criteria") or [])
    else:
        blocking = []

    baseline = data.get("startup_baseline")
    if not isinstance(baseline, dict):
        baseline = {}

    return ReviewPackage(
        user_goal=str(data.get("user_goal") or ""),
        acceptance_items=list(data.get("acceptance_items") or []),
        startup_baseline=dict(baseline),
        owned_files=list(data.get("owned_files") or []),
        excluded_user_changes=excluded,  # type: ignore[arg-type]
        worker_verification=verification,
        blocking_criteria=blocking,
        plan=str(data.get("plan") or ""),
        progress=str(data.get("progress") or ""),
        # Fixed runtime config is not overridable from artifacts.
        model=JUDGE_MODEL,
        reasoning_effort=JUDGE_REASONING_EFFORT,
        non_blocking_hints=list(data.get("non_blocking_hints") or NON_BLOCKING_HINTS),
        generated_at=str(data.get("generated_at") or datetime.now(timezone.utc).isoformat()),
    )


def write_package(package: ReviewPackage, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(package.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def blocked_review_markdown(missing: list[str]) -> str:
    return (
        "### Judge Review\n"
        f"- Verdict: blocked\n"
        f"- 刚性约束违规：{INSUFFICIENT_PACKAGE}\n"
        f"- 问题（按严重级别）：\n"
        f"  - [blocker] missing review package fields: {', '.join(missing)}\n"
        "- 缺失验证：审查包不完整，未启动范围外扫描\n"
        "- 建议复查范围：补齐审查包后重审本任务增量\n"
        "- 独立执行的验证及结果：package field validation only\n"
        f"- 实际模型 / 推理等级：`{JUDGE_MODEL}` / `{JUDGE_REASONING_EFFORT}`\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path, help="paired exec plan")
    parser.add_argument("--root", type=Path, default=None, help="repository root")
    parser.add_argument("--goal", default=None, help="override user goal")
    parser.add_argument(
        "--acceptance",
        action="append",
        default=None,
        help="acceptance item (repeatable)",
    )
    parser.add_argument(
        "--owned-file",
        action="append",
        default=None,
        dest="owned_files",
        help="task-owned file path (repeatable)",
    )
    parser.add_argument(
        "--exclude-file",
        action="append",
        default=None,
        dest="exclude_files",
        help="excluded pre-existing user change (repeatable)",
    )
    parser.add_argument(
        "--command-run",
        action="append",
        default=None,
        dest="commands_run",
        help="worker command evidence (repeatable)",
    )
    parser.add_argument(
        "--result",
        action="append",
        default=None,
        dest="results",
        help="worker result evidence (repeatable)",
    )
    parser.add_argument(
        "--not-run",
        action="append",
        default=None,
        dest="not_run",
        help="worker not-run evidence (repeatable)",
    )
    parser.add_argument("--deviations", default=None, help="deviations summary")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write JSON package (default: docs/exec-plans/artifacts/<task>-review-package.json)",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="print markdown package to stdout",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 3 when required fields are missing",
    )
    parser.add_argument(
        "--no-capture-status",
        action="store_true",
        help="do not shell out to git status",
    )
    args = parser.parse_args(argv)

    root = (args.root or repo_root()).resolve()
    plan = args.plan.resolve()
    try:
        plan.relative_to(root / "docs" / "exec-plans")
    except ValueError:
        parser.error("--plan must live under docs/exec-plans/")

    verification = None
    if args.commands_run or args.results or args.not_run or args.deviations is not None:
        verification = WorkerVerification(
            commands_run=list(args.commands_run or []),
            results=list(args.results or []),
            not_run=list(args.not_run or []),
            deviations=args.deviations if args.deviations is not None else "无",
        )

    package = build_package(
        root,
        plan,
        user_goal=args.goal,
        acceptance_items=args.acceptance,
        owned_files=args.owned_files,
        excluded_user_changes=args.exclude_files,
        worker_verification=verification,
        capture_status=not args.no_capture_status,
    )
    output = args.output or default_artifact_path(plan)
    write_package(package, output)

    missing = package.missing_fields()
    if args.markdown:
        sys.stdout.write(package.to_markdown())
    else:
        print(json.dumps({"path": str(output), "missing_fields": missing}, ensure_ascii=False))
    if args.strict and missing:
        print(f"{INSUFFICIENT_PACKAGE}: {', '.join(missing)}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
