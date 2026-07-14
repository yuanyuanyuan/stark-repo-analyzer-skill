"""Unit tests for code_map_gate reminder hook."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / ".codex" / "hooks" / "code_map_gate.py"
    spec = importlib.util.spec_from_file_location("code_map_gate_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = load_module()


MIN_MAP = """version: 1
features:
  - id: sample
    name: Sample
    status: active
    summary: demo
    task_hints:
      - demo
    layers:
      runtime:
        entrypoints:
          - skills/repo-analyzer/SKILL.md
    watch_paths:
      - skills/repo-analyzer/
      - docs/spec/
"""


class CodeMapGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "code-map").mkdir(parents=True)
        (self.root / ".codex" / "hooks").mkdir(parents=True)
        (self.root / "docs" / "code-map" / "map.yaml").write_text(MIN_MAP, encoding="utf-8")
        (self.root / "skills" / "repo-analyzer").mkdir(parents=True)
        (self.root / "skills" / "repo-analyzer" / "SKILL.md").write_text("# skill\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_watch_paths(self):
        paths = mod.parse_watch_paths(MIN_MAP)
        self.assertEqual(paths, ["skills/repo-analyzer", "docs/spec"])

    def test_post_tool_use_reminds_without_deny(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "cwd": str(self.root),
            "tool_input": {
                "patch": "*** Update File: skills/repo-analyzer/SKILL.md\n@@\n-a\n+b\n"
            },
        }
        out = mod.evaluate(self.root, payload, "PostToolUse")
        self.assertIn("systemMessage", out)
        self.assertIn("Code-map reminder", out["systemMessage"])
        self.assertNotIn("continue", out)
        hook_out = out.get("hookSpecificOutput") or {}
        self.assertNotEqual(hook_out.get("permissionDecision"), "deny")

    def test_no_reminder_when_map_updated(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "cwd": str(self.root),
            "tool_input": {
                "patch": (
                    "*** Update File: skills/repo-analyzer/SKILL.md\n@@\n-a\n+b\n"
                    "*** Update File: docs/code-map/map.yaml\n@@\n-a\n+b\n"
                )
            },
        }
        out = mod.evaluate(self.root, payload, "PostToolUse")
        self.assertEqual(out, {})

    def test_unwatched_path_silent(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "cwd": str(self.root),
            "tool_input": {"path": "README.md", "content": "x"},
        }
        out = mod.evaluate(self.root, payload, "PostToolUse")
        self.assertEqual(out, {})

    def test_stop_uses_git_status(self):
        def fake_run(cmd, cwd=None, text=None, capture_output=None, check=None):
            class R:
                returncode = 0
                stdout = " M skills/repo-analyzer/SKILL.md\n"
                stderr = ""

            return R()

        with patch.object(mod.subprocess, "run", side_effect=fake_run):
            out = mod.evaluate(self.root, {"hook_event_name": "Stop", "cwd": str(self.root)}, "Stop")
        self.assertIn("systemMessage", out)
        self.assertIn("additionalContext", out.get("hookSpecificOutput", {}))

    def test_repo_map_yaml_entrypoints_exist(self):
        """Sanity: active map entrypoints in this repo should exist (sample check)."""
        map_text = (ROOT / "docs" / "code-map" / "map.yaml").read_text(encoding="utf-8")
        # Collect simple entrypoint list items under entrypoints blocks.
        entrypoints: list[str] = []
        lines = map_text.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].strip() == "entrypoints:":
                i += 1
                while i < len(lines):
                    m = mod.LIST_ITEM_RE.match(lines[i])
                    if not m:
                        break
                    entrypoints.append(m.group(1).strip().rstrip("/"))
                    i += 1
                continue
            i += 1
        self.assertGreaterEqual(len(entrypoints), 20)
        missing = [p for p in entrypoints if not (ROOT / p).exists()]
        self.assertEqual(missing, [], f"missing entrypoints: {missing}")

    def test_feature_count_band_b(self):
        text = (ROOT / "docs" / "code-map" / "map.yaml").read_text(encoding="utf-8")
        active = text.count("status: active")
        self.assertGreaterEqual(active, 8)
        self.assertLessEqual(active, 15)

    def test_main_emits_json(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "cwd": str(self.root),
            "tool_input": {"path": str(self.root / "docs" / "spec" / "x.md"), "content": "z"},
        }
        (self.root / "docs" / "spec").mkdir(parents=True, exist_ok=True)
        stdin = json.dumps(payload)
        with patch.object(sys, "stdin", __import__("io").StringIO(stdin)):
            with patch.object(sys, "stdout", new_callable=__import__("io").StringIO) as out:
                code = mod.main()
        self.assertEqual(code, 0)
        emitted = out.getvalue().strip()
        self.assertTrue(emitted)
        data = json.loads(emitted)
        self.assertIn("systemMessage", data)


if __name__ == "__main__":
    unittest.main()
