#!/usr/bin/env python3
"""Codex lifecycle hook: block illegal completed upgrades and surface audit failures.

Events:
  PreToolUse (apply_patch/Edit/Write/Bash): deny attempts that mark plan completed
    without existing Judge pass / structured waiver.
  PostToolUse (apply_patch/Edit/Write): after control-plane edits, re-audit and warn.
  Stop / SubagentStop: audit current tree and surface systemMessage when invalid.

This is a guardrail, not a complete enforcement boundary (see Codex hooks docs).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


COMPLETED_MARKERS = (
    r"状态：\s*`?completed`?",
    r"状态:\s*`?completed`?",
    r"\|\s*当前状态\s*\|\s*`?completed`?",
    r"status\s*[:=]\s*`?completed`?",
)
COMPLETED_RE = re.compile("|".join(f"(?:{p})" for p in COMPLETED_MARKERS), re.I)
PLAN_PATH_RE = re.compile(r"docs/exec-plans/[\w./-]*-plan\.md")
JUDGE_PASS_RE = re.compile(
    r"(?ims)^###\s*Judge Review\b.*?^(?:\s*[-*]\s*)?Verdict\s*:\s*`?pass`?\b"
)
AWAITING_JUDGE_RE = re.compile(
    r"(?im)^状态：\s*`?awaiting-judge`?|\|\s*当前状态\s*\|\s*`?awaiting-judge`?"
)
CONTROL_PLANE_PATH_RE = re.compile(
    r"(?:docs/exec-plans/|docs/roadmap/|AGENTS\.md|docs/dev-rules/(?:dual-agent-review|document-control|task-quality-gates)/)"
)


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def emit(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def find_repo_root(cwd: Path) -> Path | None:
    cur = cwd.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / "tools" / "release" / "validate-control-plane.py").is_file():
            return candidate
        if (candidate / ".git").exists() and (candidate / "docs" / "exec-plans").is_dir():
            return candidate
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cur,
            text=True,
            capture_output=True,
            check=False,
        )
        if out.returncode == 0:
            root = Path(out.stdout.strip())
            if (root / "tools" / "release" / "validate-control-plane.py").is_file():
                return root
    except OSError:
        pass
    return None


def run_validator(root: Path, mode: str = "audit") -> tuple[int, str]:
    script = root / "tools" / "release" / "validate-control-plane.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--mode", mode, "--root", str(root)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    text = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, text.strip()


def tool_blob(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    chunks: list[str] = []
    if isinstance(tool_input, dict):
        for key in ("command", "path", "file_path", "content", "patch", "diff"):
            value = tool_input.get(key)
            if isinstance(value, str):
                chunks.append(value)
        # apply_patch may nest changes
        chunks.append(json.dumps(tool_input, ensure_ascii=False))
    elif isinstance(tool_input, str):
        chunks.append(tool_input)
    for key in ("command",):
        value = payload.get(key)
        if isinstance(value, str):
            chunks.append(value)
    return "\n".join(chunks)


def mentions_control_plane(blob: str) -> bool:
    return bool(CONTROL_PLANE_PATH_RE.search(blob) or PLAN_PATH_RE.search(blob))


def extract_plan_paths(blob: str) -> list[str]:
    found = list(PLAN_PATH_RE.findall(blob))
    for match in re.finditer(r"(?m)^\*\*\*\s*(?:Add|Update|Delete)\s+File:\s*(\S+)", blob):
        path = match.group(1).strip()
        if path.endswith("-plan.md"):
            if not path.startswith("docs/"):
                path = f"docs/exec-plans/{Path(path).name}"
            if path not in found:
                found.append(path)
    return found


def real_judge_pass(progress_text: str) -> bool:
    return bool(JUDGE_PASS_RE.search(progress_text or ""))


def awaiting_judge_plans(root: Path) -> list[str]:
    """Return full-gate plans that need an independent Judge dispatch."""
    plans: list[str] = []
    for plan in sorted((root / "docs" / "exec-plans").glob("*-plan.md")):
        text = plan.read_text(encoding="utf-8")
        if not AWAITING_JUDGE_RE.search(text):
            continue
        if not re.search(r"质量门\s*[：:=]\s*完整门|独立Judge\s*[：:=]\s*必须", text):
            continue
        progress = plan.with_name(plan.name.replace("-plan.md", "-progress.md"))
        progress_text = progress.read_text(encoding="utf-8") if progress.is_file() else ""
        if not real_judge_pass(progress_text):
            plans.append(str(plan.relative_to(root)))
    return plans


def judge_dispatch_context(root: Path) -> str:
    plans = awaiting_judge_plans(root)
    if not plans:
        return ""
    paths = ", ".join(f"`{path}`" for path in plans)
    return (
        f"Independent Judge dispatch is pending for {paths}. The orchestrating Agent must "
        "start a native read-only Judge subagent without asking the user to paste a prompt. "
        "If native subagents are unavailable, the Agent must autonomously run "
        "`python tools/release/run-independent-judge.py --plan <plan-path>` instead. "
        "The Worker may only append the returned fixed Judge Review verbatim; it must not "
        "invent a verdict or mark the plan completed."
    )


def attempts_completed_upgrade(blob: str) -> bool:
    if not COMPLETED_RE.search(blob):
        return False
    # Prefer signals that this is a plan lifecycle edit.
    if PLAN_PATH_RE.search(blob) or "exec-plans" in blob or "-plan.md" in blob:
        return True
    # Bash rewriting plan status without explicit path still risky when completed appears
    # with 状态 field.
    return bool(re.search(r"状态", blob) and re.search(r"completed", blob, re.I))


def pre_tool_use(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    blob = tool_blob(payload)
    tool_name = str(payload.get("tool_name") or "")
    interesting = tool_name in {"apply_patch", "Edit", "Write", "Bash"} or mentions_control_plane(blob)
    if not interesting:
        return {}

    if attempts_completed_upgrade(blob):
        code, text = run_validator(root, "audit")
        # If tree already valid (rare mid-edit), still require existing pass before upgrade.
        # Deny unless audit currently passes AND progress already has pass for all completed.
        # Safer default: if the patch introduces completed, require current audit pass first
        # only if no new illegal completed would remain. Since file isn't written yet, check
        # whether any existing completed is illegal; if audit fails now, deny completed upgrades.
        # If audit currently passes, still deny introducing completed without explicit
        # Judge evidence already present for that plan name.
        if code != 0:
            reason = (
                "Blocked control-plane completed upgrade: existing tree already fails "
                "validate-control-plane audit, or this edit marks a plan completed without "
                "Judge pass/waiver.\n\n"
                f"{text}\n\n"
                "Required path: awaiting-judge → independent Judge Verdict: pass "
                "(or structured user waiver) → python tools/release/validate-control-plane.py "
                "→ only then mark completed."
            )
            return {
                "systemMessage": reason,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                },
            }

        # Audit currently clean. Still block if the patch itself sets completed on a plan
        # whose progress does not already contain Verdict: pass / waiver. Heuristic scan:
        plans = extract_plan_paths(blob)
        if not plans and attempts_completed_upgrade(blob):
            # Ambiguous Bash rewrite — force re-check path by denying direct completed set.
            reason = (
                "Blocked ambiguous attempt to mark plan completed. "
                "First ensure progress has Judge Review `Verdict: pass` or structured waiver, "
                "run tools/release/validate-control-plane.py, then set completed in a clear "
                "apply_patch on the plan file."
            )
            return {
                "systemMessage": reason,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                },
            }
        for rel in plans:
            progress = root / rel.replace("-plan.md", "-progress.md")
            progress_text = progress.read_text(encoding="utf-8") if progress.is_file() else ""
            has_pass = real_judge_pass(progress_text)
            has_waiver = bool(
                re.search(r"用户(?:书面)?豁免|written\s+waiver", progress_text, re.I)
                and re.search(r"豁免人\s*[:：]", progress_text)
                and re.search(r"豁免项\s*[:：]", progress_text)
            )
            if not (has_pass or has_waiver):
                reason = (
                    f"Blocked marking `{rel}` completed: paired progress lacks "
                    "`Verdict: pass` or structured user waiver (豁免人/豁免项). "
                    "Stay on awaiting-judge until independent Judge finishes."
                )
                return {
                    "systemMessage": reason,
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    },
                }

    # Soft context for control-plane edits.
    if mentions_control_plane(blob):
        context = (
            "Control-plane edit detected. Full-gate close path is "
            "awaiting-judge → independent Judge pass/waiver → "
            "python tools/release/validate-control-plane.py → completed. "
            "Worker must not self-pass Judge."
        )
        dispatch = judge_dispatch_context(root)
        if dispatch:
            context = f"{context}\n\n{dispatch}"
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": context,
            }
        }
    return {}


def post_or_stop(payload: dict[str, Any], root: Path, event_name: str) -> dict[str, Any]:
    blob = tool_blob(payload)
    if event_name == "PostToolUse" and not mentions_control_plane(blob) and not attempts_completed_upgrade(blob):
        # Cheap filter: only re-audit when control-plane files were touched.
        tool_name = str(payload.get("tool_name") or "")
        if tool_name not in {"apply_patch", "Edit", "Write"}:
            return {}
        # Still skip unrelated patches.
        if not mentions_control_plane(blob):
            return {}

    code, text = run_validator(root, "audit")
    if code == 0:
        dispatch = judge_dispatch_context(root)
        if event_name in {"Stop", "SubagentStop"}:
            if not dispatch:
                return {}
            return {
                "systemMessage": dispatch,
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": dispatch,
                },
            }
        message = "Control-plane audit PASS after edit."
        if dispatch:
            message = f"{message}\n{dispatch}"
        return {
            "systemMessage": message,
        }

    message = (
        "Control-plane audit FAIL. Illegal completed state or missing Judge evidence.\n"
        f"{text}\n"
        "Do not treat the task as closed. Move plan to awaiting-judge, run independent Judge, "
        "or record structured user waiver before completed."
    )
    if event_name == "PostToolUse":
        # File may already be written; stop the turn so Worker cannot continue celebrating.
        return {
            "continue": False,
            "stopReason": "control-plane-audit-failed",
            "systemMessage": message,
        }
    # Stop / SubagentStop
    return {
        "continue": True,
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": message,
        },
    }


def main() -> int:
    payload = load_payload()
    event = str(payload.get("hook_event_name") or "")
    cwd_raw = payload.get("cwd")
    cwd = Path(cwd_raw) if isinstance(cwd_raw, str) and cwd_raw else Path.cwd()
    root = find_repo_root(cwd)
    if root is None:
        # Outside this repo — no-op.
        return 0

    try:
        if event == "PreToolUse":
            out = pre_tool_use(payload, root)
        elif event in {"PostToolUse", "Stop", "SubagentStop"}:
            out = post_or_stop(payload, root, event)
        else:
            out = {}
    except Exception as exc:  # pragma: no cover - hook must not crash Codex
        out = {
            "systemMessage": f"control_plane_gate hook error: {exc}",
        }

    if out:
        emit(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
