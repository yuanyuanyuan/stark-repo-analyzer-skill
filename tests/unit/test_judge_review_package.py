"""Unit tests for scoped Judge review packages and fallback wiring."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "tools" / "release"
TERMINAL = "completed"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


package_mod = load_module("judge_review_package", RELEASE / "judge_review_package.py")
judge_mod = load_module("run_independent_judge", RELEASE / "run-independent-judge.py")


class JudgeReviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "exec-plans").mkdir(parents=True)
        self.plan = self.root / "docs" / "exec-plans" / "sample-plan.md"
        self.progress = self.root / "docs" / "exec-plans" / "sample-progress.md"
        self.plan.write_text(
            "# sample\n\n"
            "状态：`active`\n\n"
            "质量门：完整门\n独立Judge：必须\n\n"
            "## 目标\n实现审查包。\n\n"
            "## 完成条件\n"
            "1. 可为典型任务生成完整审查包\n"
            "2. 缺字段可确定性 blocked\n",
            encoding="utf-8",
        )
        self.progress.write_text(
            "# progress\n\n"
            "文档类型：`progress-log`\n\n"
            "### Worker 验证\n"
            "- python -m unittest tests.unit.test_judge_review_package\n"
            "- exit 0 / PASS\n"
            "- 未执行真实 codex exec 网络调用\n\n"
            "### Deviations\n无\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_owned_files_is_incomplete(self):
        pkg = package_mod.build_package(
            self.root,
            self.plan,
            capture_status=False,
            startup_baseline={
                "summary": "fixture",
                "git_status_short": " M foo",
                "captured_at": "t0",
            },
        )
        self.assertIn("owned_files", pkg.missing_fields())

    def test_complete_package_and_markdown(self):
        pkg = package_mod.build_package(
            self.root,
            self.plan,
            owned_files=["tools/release/judge_review_package.py"],
            excluded_user_changes=["CONTEXT.md"],
            capture_status=False,
            startup_baseline={
                "summary": "fixture",
                "git_status_short": " M CONTEXT.md\n M tools/release/judge_review_package.py",
                "captured_at": "t0",
            },
        )
        self.assertEqual(pkg.missing_fields(), [])
        md = pkg.to_markdown()
        self.assertIn("本任务拥有的文件范围", md)
        self.assertIn("状态：complete", md)

    def test_cli_writes_artifact_and_strict_exit(self):
        out = self.root / "docs" / "exec-plans" / "artifacts" / "sample-review-package.json"
        code = package_mod.main(
            [
                "--plan",
                str(self.plan),
                "--root",
                str(self.root),
                "--output",
                str(out),
                "--no-capture-status",
                "--strict",
            ]
        )
        self.assertEqual(code, 3)
        self.assertTrue(out.is_file())
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["plan"], "docs/exec-plans/sample-plan.md")

        code_ok = package_mod.main(
            [
                "--plan",
                str(self.plan),
                "--root",
                str(self.root),
                "--output",
                str(out),
                "--owned-file",
                "tools/release/judge_review_package.py",
                "--command-run",
                "unittest",
                "--result",
                "exit 0",
                "--no-capture-status",
                "--strict",
            ]
        )
        self.assertEqual(code_ok, 0)

    def test_run_independent_judge_blocks_without_package_fields(self):
        with patch.object(judge_mod, "repo_root", return_value=self.root):
            code = judge_mod.main(["--plan", str(self.plan)])
        self.assertEqual(code, 3)

    def test_run_independent_judge_print_command_uses_fixed_model(self):
        package_mod.write_package(
            package_mod.build_package(
                self.root,
                self.plan,
                owned_files=["tools/release/run-independent-judge.py"],
                excluded_user_changes=[],
                capture_status=False,
                startup_baseline={
                    "summary": "fixture",
                    "git_status_short": "",
                    "captured_at": "t0",
                },
                worker_verification=package_mod.WorkerVerification(
                    commands_run=["unittest"],
                    results=["ok"],
                ),
            ),
            package_mod.default_artifact_path(self.plan),
        )
        with patch.object(judge_mod, "repo_root", return_value=self.root):
            from io import StringIO
            import contextlib
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                code = judge_mod.main(["--plan", str(self.plan), "--print-command"])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn("workspace-write", out)
        self.assertNotIn("--sandbox read-only", out)

    def test_prompt_contains_model_and_package(self):
        pkg = package_mod.ReviewPackage(
            user_goal="g",
            acceptance_items=["a"],
            startup_baseline={"summary": "s", "git_status_short": "", "captured_at": "t0"},
            owned_files=["x"],
            excluded_user_changes=[],
            worker_verification=package_mod.WorkerVerification(
                commands_run=["c"], results=["r"]
            ),
            blocking_criteria=list(package_mod.DEFAULT_BLOCKING_CRITERIA),
            plan="docs/exec-plans/sample-plan.md",
            progress="docs/exec-plans/sample-progress.md",
        )
        prompt = judge_mod.build_prompt(self.root, pkg)
        self.assertIn("gpt-5.6-terra", prompt)
        self.assertIn("medium", prompt)
        self.assertIn("Review package", prompt)



    def test_load_package_missing_required_keys_not_silently_filled(self):
        artifact = self.root / "docs" / "exec-plans" / "artifacts" / "incomplete.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(
                {
                    "user_goal": "g",
                    "acceptance_items": ["a"],
                    "startup_baseline": {"summary": "only-summary"},
                    "owned_files": ["x"],
                    "worker_verification": {"commands_run": ["c"], "results": ["r"]},
                    "plan": "docs/exec-plans/sample-plan.md",
                    "progress": "docs/exec-plans/sample-progress.md",
                }
            ),
            encoding="utf-8",
        )
        pkg = package_mod.load_package(artifact)
        missing = pkg.missing_fields()
        self.assertIn("excluded_user_changes", missing)
        self.assertIn("blocking_criteria", missing)
        self.assertIn("startup_baseline", missing)

    def test_load_package_forces_fixed_model_even_if_artifact_overrides(self):
        artifact = self.root / "docs" / "exec-plans" / "artifacts" / "override-model.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(
                {
                    "user_goal": "g",
                    "acceptance_items": ["a"],
                    "startup_baseline": {"git_status_short": "", "summary": "s", "captured_at": "t0"},
                    "owned_files": ["x"],
                    "excluded_user_changes": [],
                    "worker_verification": {"commands_run": ["c"], "results": ["r"]},
                    "blocking_criteria": list(package_mod.DEFAULT_BLOCKING_CRITERIA),
                    "plan": "docs/exec-plans/sample-plan.md",
                    "progress": "docs/exec-plans/sample-progress.md",
                    "model": "should-not-win",
                    "reasoning_effort": "ultra",
                }
            ),
            encoding="utf-8",
        )
        pkg = package_mod.load_package(artifact)
        self.assertEqual(pkg.model, package_mod.JUDGE_MODEL)
        self.assertEqual(pkg.reasoning_effort, package_mod.JUDGE_REASONING_EFFORT)
        self.assertEqual(pkg.missing_fields(), [])

    def test_run_independent_judge_blocks_incomplete_artifact(self):
        artifact = package_mod.default_artifact_path(self.plan)
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(
                {
                    "user_goal": "g",
                    "acceptance_items": ["a"],
                    "startup_baseline": {"summary": "s"},
                    "owned_files": ["x"],
                    "worker_verification": {"commands_run": ["c"]},
                    "plan": "docs/exec-plans/sample-plan.md",
                    "progress": "docs/exec-plans/sample-progress.md",
                }
            ),
            encoding="utf-8",
        )
        with patch.object(judge_mod, "repo_root", return_value=self.root):
            code = judge_mod.main(["--plan", str(self.plan), "--package", str(artifact)])
        self.assertEqual(code, 3)


    def test_startup_baseline_requires_captured_at(self):
        pkg = package_mod.ReviewPackage(
            user_goal="g",
            acceptance_items=["a"],
            startup_baseline={"git_status_short": " M x", "summary": "s"},
            owned_files=["x"],
            excluded_user_changes=[],
            worker_verification=package_mod.WorkerVerification(
                commands_run=["c"], results=["r"]
            ),
            blocking_criteria=list(package_mod.DEFAULT_BLOCKING_CRITERIA),
            plan="docs/exec-plans/sample-plan.md",
            progress="docs/exec-plans/sample-progress.md",
        )
        self.assertIn("startup_baseline", pkg.missing_fields())


    def test_prompt_forbids_worker_test_substitution(self):
        pkg = package_mod.ReviewPackage(
            user_goal="g",
            acceptance_items=["a"],
            startup_baseline={"summary": "s", "git_status_short": "", "captured_at": "t0"},
            owned_files=["x"],
            excluded_user_changes=[],
            worker_verification=package_mod.WorkerVerification(
                commands_run=["pytest"], results=["8 passed"]
            ),
            blocking_criteria=list(package_mod.DEFAULT_BLOCKING_CRITERIA),
            plan="docs/exec-plans/sample-plan.md",
            progress="docs/exec-plans/sample-progress.md",
        )
        prompt = judge_mod.build_prompt(self.root, pkg)
        self.assertIn("NEVER pass by citing Worker", prompt)
        self.assertIn("workspace-write", judge_mod.JUDGE_SANDBOX)


class ControlPlaneGateHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "exec-plans").mkdir(parents=True)
        (self.root / "tools" / "release").mkdir(parents=True)
        validator = self.root / "tools" / "release" / "validate-control-plane.py"
        validator.write_text(
            "#!/usr/bin/env python3\nimport sys\nprint('PASS')\nsys.exit(0)\n",
            encoding="utf-8",
        )
        validator.chmod(0o755)
        self.hook = load_module(
            "control_plane_gate_under_test",
            ROOT / ".codex" / "hooks" / "control_plane_gate.py",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _write_plan(self, status: str, with_pass: bool = False):
        plan = self.root / "docs" / "exec-plans" / "demo-plan.md"
        progress = self.root / "docs" / "exec-plans" / "demo-progress.md"
        plan.write_text(
            f"状态：`{status}`\n质量门：完整门\n独立Judge：必须\n",
            encoding="utf-8",
        )
        body = "# progress\n"
        if with_pass:
            body += (
                "### Judge Review\n"
                "- Verdict: pass\n"
                "- 刚性约束违规：无\n"
            )
        progress.write_text(body, encoding="utf-8")
        return plan

    def test_awaiting_judge_dispatch_message_once_path(self):
        self._write_plan("awaiting-judge", with_pass=False)
        plans = self.hook.awaiting_judge_plans(self.root)
        self.assertEqual(plans, ["docs/exec-plans/demo-plan.md"])
        message = self.hook.judge_dispatch_context(self.root)
        self.assertIn("Independent Judge dispatch is pending", message)
        self.assertIn("run-independent-judge.py", message)

    def test_finished_plan_not_in_dispatch_list(self):
        self._write_plan(TERMINAL, with_pass=True)
        self.assertEqual(self.hook.awaiting_judge_plans(self.root), [])
        self.assertEqual(self.hook.judge_dispatch_context(self.root), "")

    def test_pretool_blocks_terminal_upgrade_without_pass(self):
        self._write_plan("awaiting-judge", with_pass=False)
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "cwd": str(self.root),
            "tool_input": {
                "path": "docs/exec-plans/demo-plan.md",
                "content": f"状态：`{TERMINAL}`\n质量门：完整门\n独立Judge：必须\n",
            },
        }
        with patch.object(self.hook, "run_validator", return_value=(1, "FAIL")):
            out = self.hook.pre_tool_use(payload, self.root)
        self.assertIn("permissionDecision", out.get("hookSpecificOutput", {}))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
