"""Install-adapter smoke tests for the Skill core package file contract."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE_LIST = ROOT / "tools" / "release" / "core-package-files.txt"
SCHEMA_REL = "skills/repo-analyzer/references/contracts/graphify-gate-status.schema.json"


def core_package_files() -> list[str]:
    items: list[str] = []
    for line in CORE_LIST.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        items.append(item)
    return items


def materialize_core_package(destination: Path) -> Path:
    for relative in core_package_files():
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination / "skills" / "repo-analyzer" / "SKILL.md"


def resolve_skill_root(skill_md: Path) -> Path:
    return skill_md.resolve().parent


class CorePackageInstallSmokeTests(unittest.TestCase):
    def _run_adapter(self, adapter_name: str, install_root: Path, skill_md: Path) -> dict:
        skill_root = resolve_skill_root(skill_md)
        gate = skill_root / "scripts" / "graphify_gate.py"
        schema = install_root / SCHEMA_REL
        target = ROOT / "tests" / "fixtures" / "graphify" / "g2-target"
        with tempfile.TemporaryDirectory() as work:
            work_dir = Path(work) / "work"
            completed = subprocess.run(
                [
                    "python",
                    str(gate),
                    "--target",
                    str(target),
                    "--work-dir",
                    str(work_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            status = None
            status_path = work_dir / "graphify-gate-status.json"
            if status_path.is_file():
                status = json.loads(status_path.read_text(encoding="utf-8"))
            elif completed.stdout.strip():
                status = json.loads(completed.stdout)
            schema_obj = json.loads(schema.read_text(encoding="utf-8"))
            evidence = {
                "adapter": adapter_name,
                "isolate_root": str(install_root),
                "skill_md": str(skill_md.resolve()),
                "skill_root": str(skill_root),
                "gate_command": [
                    "python",
                    str(gate),
                    "--target",
                    str(target),
                    "--work-dir",
                    str(work_dir),
                ],
                "exit_code": completed.returncode,
                "status_code": None if status is None else status.get("code"),
                "schema_code_enum": schema_obj["properties"]["code"]["enum"],
                "stdout_tail": completed.stdout[-500:],
                "stderr_tail": completed.stderr[-500:],
            }
            self.assertTrue(skill_md.is_file(), evidence)
            self.assertTrue(gate.is_file(), evidence)
            self.assertTrue(schema.is_file(), evidence)
            self.assertIsNotNone(status, evidence)
            self.assertIn(status["code"], (0, 10, 30), evidence)
            self.assertEqual(status["schema_version"], 1, evidence)
            self.assertEqual(status["graphify"]["extraction_mode"], "code-only", evidence)
            self.assertEqual(completed.returncode, status["code"], evidence)
            return evidence

    def test_manual_core_package_install_five_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            install_root = Path(directory) / "manual-install"
            skill_md = materialize_core_package(install_root)
            evidence = self._run_adapter("manual", install_root, skill_md)
            self.assertEqual(evidence["adapter"], "manual")

    def test_claude_plugin_layout_exposes_core_package(self):
        with tempfile.TemporaryDirectory() as directory:
            install_root = Path(directory) / "claude-plugin"
            (install_root / ".claude-plugin").mkdir(parents=True)
            shutil.copy2(
                ROOT / ".claude-plugin" / "plugin.json",
                install_root / ".claude-plugin" / "plugin.json",
            )
            skill_md = materialize_core_package(install_root)
            evidence = self._run_adapter("claude-plugin", install_root, skill_md)
            plugin = json.loads((install_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(plugin["name"], "repo-analyzer")
            self.assertEqual(evidence["adapter"], "claude-plugin")


    def test_codex_plugin_layout_exposes_core_package(self):
        with tempfile.TemporaryDirectory() as directory:
            install_root = Path(directory) / "codex-plugin"
            (install_root / ".codex-plugin").mkdir(parents=True)
            (install_root / ".agents" / "plugins").mkdir(parents=True)
            shutil.copy2(ROOT / ".codex-plugin" / "plugin.json", install_root / ".codex-plugin" / "plugin.json")
            shutil.copy2(
                ROOT / ".agents" / "plugins" / "marketplace.json",
                install_root / ".agents" / "plugins" / "marketplace.json",
            )
            skill_md = materialize_core_package(install_root)
            evidence = self._run_adapter("codex-plugin", install_root, skill_md)
            plugin = json.loads((install_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(plugin["skills"], "./skills/")
            self.assertEqual(evidence["adapter"], "codex-plugin")

    def test_npx_identity_package_still_delivers_core_package(self):
        with tempfile.TemporaryDirectory() as directory:
            install_root = Path(directory) / "npx-package"
            skill_md = materialize_core_package(install_root)
            shutil.copy2(ROOT / "package.json", install_root / "package.json")
            evidence = self._run_adapter("npx-skills-add", install_root, skill_md)
            package = json.loads((install_root / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(package["name"], "repo-analyzer")
            # Evidence: npx skills packaging currently still relies on package.json identity.
            self.assertTrue((install_root / "package.json").is_file())
            self.assertEqual(evidence["adapter"], "npx-skills-add")

    def test_core_package_list_matches_repository_files(self):
        for relative in core_package_files():
            self.assertTrue((ROOT / relative).is_file(), relative)
        # No second schema body under docs/spec.
        self.assertFalse((ROOT / "docs" / "spec" / "graphify-gate-status-schema.json").exists())


if __name__ == "__main__":
    unittest.main()
