#!/usr/bin/env python3
"""Codex lifecycle hook: remind when watched paths change without map.yaml sync.

Events:
  PostToolUse (apply_patch|Edit|Write): inspect tool payload paths.
  Stop: fall back to git status when useful.

Reminder only: never deny edits, never continue:false for stale map.
Independent from control_plane_gate.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

MAP_REL = "docs/code-map/map.yaml"
MAP_README_REL = "docs/code-map/README.md"

PATCH_FILE_RE = re.compile(
    r"(?m)^(?:\*\*\*\s*(?:Add|Update|Delete)\s+File:\s+|diff --git a/)\s*(\S+)"
)
WATCH_KEY_RE = re.compile(r"(?m)^[ \t]*watch_paths:[ \t]*$")
LIST_ITEM_RE = re.compile(r"(?m)^[ \t]*-\s+[\"']?([^\"'#\n]+?)[\"']?\s*(?:#.*)?$")
REL_TOKEN_RE = re.compile(
    r"(?m)(?:^|[\s\"'])((?:\.\.?/)*(?:AGENTS\.md|CONTEXT\.md|README(?:\.zh)?\.md|"
    r"docs/|skills/|tools/|tests/|\.codex/)[A-Za-z0-9_./\-]+)"
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
        if (candidate / MAP_REL).is_file() and (candidate / ".codex" / "hooks").is_dir():
            return candidate
        if (candidate / ".git").exists() and (candidate / "docs" / "code-map").is_dir():
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
            if (root / MAP_REL).is_file():
                return root
    except OSError:
        pass
    return None


def parse_watch_paths(map_text: str) -> list[str]:
    """Minimal YAML list collector for watch_paths entries (stdlib only)."""
    paths: list[str] = []
    lines = map_text.splitlines()
    i = 0
    while i < len(lines):
        if WATCH_KEY_RE.match(lines[i]):
            i += 1
            while i < len(lines):
                line = lines[i]
                if not line.strip() or line.lstrip().startswith("#"):
                    i += 1
                    continue
                item = LIST_ITEM_RE.match(line)
                if not item:
                    break
                rel = item.group(1).strip().rstrip("/")
                if rel and rel not in paths:
                    paths.append(rel)
                i += 1
            continue
        i += 1
    return paths


def tool_blob(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in ("command", "path", "file_path", "patch", "diff", "content"):
            value = tool_input.get(key)
            if isinstance(value, str):
                chunks.append(value)
        slim = {
            k: tool_input.get(k)
            for k in ("path", "file_path", "command")
            if isinstance(tool_input.get(k), str)
        }
        if slim:
            try:
                chunks.append(json.dumps(slim, ensure_ascii=False))
            except (TypeError, ValueError):
                pass
    elif isinstance(tool_input, str):
        chunks.append(tool_input)
    value = payload.get("command")
    if isinstance(value, str):
        chunks.append(value)
    return "\n".join(chunks)


def normalize_rel(path: str, root: Path) -> str | None:
    raw = path.strip().strip("\"'")
    if not raw or raw == "/dev/null":
        return None
    for sep in ("\\n", "\\r", "\\t", "\n", "\r"):
        if sep in raw:
            raw = raw.split(sep, 1)[0]
    raw = raw.replace("\\", "/").rstrip("/")
    if raw.startswith("b/"):
        raw = raw[2:]
    # Keep only plausible path characters after first invalid token.
    m = re.match(r"([A-Za-z0-9_./\-]+)", raw)
    if not m:
        return None
    raw = m.group(1)
    try:
        p = Path(raw)
        root_res = root.resolve()
        if p.is_absolute():
            candidates = [p]
            try:
                candidates.append(p.resolve())
            except OSError:
                pass
            text = str(p)
            if text.startswith("/var/"):
                candidates.append(Path("/private" + text))
            if text.startswith("/private/var/"):
                candidates.append(Path(text[len("/private") :]))
            for cand in candidates:
                for base in (root_res, root):
                    try:
                        rel = cand.relative_to(base)
                        return str(rel).replace("\\", "/")
                    except ValueError:
                        continue
            return None
        while raw.startswith("./"):
            raw = raw[2:]
        return raw.lstrip("/")
    except Exception:
        return None


def paths_from_blob(blob: str, root: Path) -> set[str]:
    found: set[str] = set()
    for match in PATCH_FILE_RE.finditer(blob):
        rel = normalize_rel(match.group(1), root)
        if rel:
            found.add(rel)
    for match in REL_TOKEN_RE.finditer(blob):
        rel = normalize_rel(match.group(1), root)
        if rel:
            found.add(rel)
    blob_n = blob.replace("\\", "/")
    root_forms = {
        str(root).replace("\\", "/").rstrip("/"),
        str(root.resolve()).replace("\\", "/").rstrip("/"),
    }
    for root_s in root_forms:
        if not root_s:
            continue
        for match in re.finditer(re.escape(root_s) + r"/([A-Za-z0-9_./\-]+)", blob_n):
            rel = normalize_rel(match.group(1), root)
            if rel:
                found.add(rel)
    for match in re.finditer(r"(/[A-Za-z0-9_./\-]+)", blob_n):
        rel = normalize_rel(match.group(1), root)
        if rel:
            found.add(rel)
    return found


def paths_from_git_status(root: Path) -> set[str]:
    try:
        out = subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return set()
    if out.returncode != 0:
        return set()
    found: set[str] = set()
    for line in (out.stdout or "").splitlines():
        if len(line) < 4:
            continue
        body = line[3:].strip()
        if " -> " in body:
            body = body.split(" -> ", 1)[1]
        rel = normalize_rel(body, root)
        if rel:
            found.add(rel)
    return found


def path_is_watched(rel: str, watch_paths: list[str]) -> bool:
    rel_n = rel.rstrip("/")
    for watch in watch_paths:
        w = watch.rstrip("/")
        if rel_n == w or rel_n.startswith(w + "/"):
            return True
    return False


def map_updated(touched: set[str]) -> bool:
    return any(t == MAP_REL or t.startswith("docs/code-map/") for t in touched)


def reminder_message(hits: list[str]) -> str:
    sample = ", ".join(f"`{p}`" for p in hits[:8])
    more = "" if len(hits) <= 8 else f" (+{len(hits) - 8} more)"
    return (
        "Code-map reminder: watched paths changed without updating "
        f"`{MAP_REL}` in the same change set. Touched: {sample}{more}. "
        "Either sync feature entrypoints/watch_paths in the code map, or record "
        "`code-map 无影响：<reason>` in progress/PR/final reply. "
        f"See `{MAP_README_REL}` and `docs/dev-rules/code-map/`. "
        "This is a reminder only; edits are not blocked."
    )


def evaluate(root: Path, payload: dict[str, Any], event: str) -> dict[str, Any]:
    map_path = root / MAP_REL
    if not map_path.is_file():
        return {
            "systemMessage": (
                f"Code-map reminder: missing `{MAP_REL}`. "
                "Restore the semantic map before relying on navigation."
            )
        }

    watch_paths = parse_watch_paths(map_path.read_text(encoding="utf-8"))
    if not watch_paths:
        return {}

    blob = tool_blob(payload)
    touched = paths_from_blob(blob, root)
    if event == "Stop" or not touched:
        touched |= paths_from_git_status(root)

    if not touched or map_updated(touched):
        return {}

    hits = sorted(p for p in touched if path_is_watched(p, watch_paths))
    if not hits:
        return {}

    message = reminder_message(hits)
    if event == "PostToolUse":
        return {"systemMessage": message}
    return {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": event,
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
        return 0

    try:
        if event == "PostToolUse":
            tool_name = str(payload.get("tool_name") or "")
            if tool_name and tool_name not in {"apply_patch", "Edit", "Write"}:
                return 0
            out = evaluate(root, payload, event)
        elif event == "Stop":
            out = evaluate(root, payload, event)
        else:
            out = {}
    except Exception as exc:  # pragma: no cover - hook must not crash Codex
        out = {"systemMessage": f"code_map_gate hook error: {exc}"}

    if out:
        emit(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
