#!/usr/bin/env python3
"""Runtime preflight checks and stage counting for repo-analyzer.

Extracted from repo_analyzer.py (T09).
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from analyzer_common import REPOMIX_BINARY, degrade_agent_mode


def _codex_health_check() -> tuple:
    """Run a lightweight ``codex exec`` to verify codex is functional.

    Returns (ok: bool, reason: str). A successful run means codex exists,
    can authenticate, and can execute without crashing.
    """
    try:
        with tempfile.TemporaryDirectory(prefix="codex-health-") as tmp:
            result = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-"],
                input="Reply with: OK",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
                cwd=tmp,
            )
        if result.returncode == 0:
            return True, ""
        return False, f"codex exec 退出码 {result.returncode}: {(result.stderr or result.stdout).strip()[:200]}"
    except subprocess.TimeoutExpired:
        return False, "codex exec 健康检查超时（30s）"
    except OSError as exc:
        return False, f"codex 不可用: {exc}"
    except Exception as exc:  # noqa: BLE001
        return False, f"codex 健康检查异常: {exc}"


def preflight_check(args: argparse.Namespace) -> dict:
    """T09: Runtime preflight checks — 5 checks before analysis starts.

    Checks:
    1. git available in PATH
    2. repomix (npx) available in PATH
    3. target path exists or is a valid git URL
    4. codex available AND functional (if agent_mode == codex) -> auto-degrade to deterministic
    5. agent_command set (if agent_mode == command)

    Mutates *args* in place when degrading codex -> deterministic.
    Returns a dict with ``checks`` (list of {name, ok}) and ``degraded`` (bool).
    """
    args._agent_mode_degraded = False
    checks: list = []
    degraded = False

    # Check 1: git
    git_ok = shutil.which("git") is not None
    checks.append({"name": "git", "ok": git_ok})
    if not git_ok:
        raise SystemExit("preflight: git not found in PATH — cannot analyze git repositories")

    # Check 2: repomix (npx)
    repomix_ok = shutil.which(REPOMIX_BINARY) is not None
    checks.append({"name": "repomix", "ok": repomix_ok})
    if not repomix_ok:
        raise SystemExit(f"preflight: {REPOMIX_BINARY} not found in PATH — cannot generate slices")

    # Check 3: target valid
    target_str = str(args.target)
    is_url = target_str.startswith(("http://", "https://", "git@", "ssh://"))
    target_ok = is_url or Path(target_str).exists()
    checks.append({"name": "target", "ok": target_ok})
    if not target_ok:
        raise SystemExit(f"preflight: target not found or not a valid git URL: {target_str}")

    # Check 4: codex available AND functional (if agent_mode == codex) -> auto-degrade
    if args.agent_mode == "codex":
        codex_binary_ok = shutil.which("codex") is not None
        checks.append({"name": "codex", "ok": codex_binary_ok})
        if not codex_binary_ok:
            print("preflight: codex not found in PATH — auto-degrading agent_mode codex -> deterministic", file=sys.stderr)
            args.agent_mode = "deterministic"
            args._agent_mode_degraded = True
            degraded = True
        else:
            # Binary exists; verify it actually works (auth, config, no crash).
            codex_healthy, reason = _codex_health_check()
            checks.append({"name": "codex_health", "ok": codex_healthy})
            if not codex_healthy:
                degrade_agent_mode(args, f"preflight 健康检查失败: {reason}")
                degraded = True
    else:
        checks.append({"name": "codex", "ok": True})

    # Check 5: agent_command set (if agent_mode == command)
    if args.agent_mode == "command":
        cmd_ok = bool(args.agent_command)
        checks.append({"name": "agent_command", "ok": cmd_ok})
        if not cmd_ok:
            raise SystemExit("preflight: --agent-command is required when --agent-mode is command")
    else:
        checks.append({"name": "agent_command", "ok": True})

    # Print summary
    for item in checks:
        status = "OK" if item["ok"] else "FAIL"
        print(f"  preflight: {item['name']:16s} {status}", file=sys.stderr)
    if degraded:
        print("  preflight: agent_mode degraded codex -> deterministic", file=sys.stderr)

    return {"checks": checks, "degraded": degraded}


def count_stages(args: argparse.Namespace) -> int:
    """Pre-compute total stage count for progress display.

    Counts only stages that will definitely execute. Conditional stages
    (coverage-repair, cross-ref-repair-final) are NOT counted here; they
    are added dynamically via ``ProgressReporter.add_stages()`` when the
    orchestrator determines they will run.

    Guaranteed stages:
    - 19 base stages: checkout, prepare, scan, classify, meta, slices,
      drafts, cross-ref-initial, agent-init, agent-batch,
      cross-ref-after-agent, coverage-initial, agent-cross-ref-review,
      state-report, render-reports, write-index, sla, performance, acceptance
    - +1 agent-cross-ref-repair (always runs when agent_mode != deterministic)
    - +1 external-research (if --research)
    - +1 save-last-session (if --save-pref)
    """
    base = 19
    if args.agent_mode != "deterministic":
        base += 1  # agent-cross-ref-repair always runs (even if no-op)
    if args.research:
        base += 1
    if args.save_pref:
        base += 1
    return base
