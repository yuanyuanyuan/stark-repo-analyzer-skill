"""Contract checks for SKILL_ROOT resolution and Skill gate invocation docs."""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = ROOT / "skills" / "repo-analyzer" / "SKILL.md"
GATE_PATH = ROOT / "skills" / "repo-analyzer" / "scripts" / "graphify_gate.py"
SCHEMA_PATH = (
    ROOT
    / "skills"
    / "repo-analyzer"
    / "references"
    / "contracts"
    / "graphify-gate-status.schema.json"
)


def resolve_skill_root(skill_md_absolute: Path | None) -> Path:
    """Host-side resolution rule required by the Skill delivery contract."""
    if skill_md_absolute is None:
        raise RuntimeError(
            "Unable to resolve SKILL_ROOT: current loaded SKILL.md absolute path is unavailable. "
            "Refuse to start the gate subprocess; do not guess plugin root, cwd, repository root, or src/."
        )
    path = Path(skill_md_absolute)
    if not path.is_absolute():
        raise RuntimeError(
            "Unable to resolve SKILL_ROOT: SKILL.md path must be absolute before constructing the gate command."
        )
    if path.name != "SKILL.md":
        raise RuntimeError(
            f"Unable to resolve SKILL_ROOT: expected a SKILL.md path, got {path.name!r}."
        )
    return path.parent


def build_gate_command(skill_root: Path, target: Path, work_dir: Path) -> list[str]:
    return [
        "python",
        str(skill_root / "scripts" / "graphify_gate.py"),
        "--target",
        str(target),
        "--work-dir",
        str(work_dir),
    ]


class SkillRootResolutionTests(unittest.TestCase):
    def test_positive_resolution_builds_absolute_gate_command(self):
        skill_root = resolve_skill_root(SKILL_PATH.resolve())
        command = build_gate_command(skill_root, ROOT, Path("/tmp/work"))
        self.assertEqual(skill_root, SKILL_PATH.parent.resolve())
        self.assertEqual(command[1], str(GATE_PATH.resolve()))
        self.assertTrue(Path(command[1]).is_absolute())
        self.assertTrue(Path(command[1]).is_file())

    def test_missing_skill_source_fails_before_subprocess(self):
        with self.assertRaises(RuntimeError) as caught:
            resolve_skill_root(None)
        message = str(caught.exception)
        self.assertIn("SKILL_ROOT", message)
        self.assertIn("do not guess", message.lower())

    def test_relative_skill_path_is_rejected(self):
        with self.assertRaises(RuntimeError):
            resolve_skill_root(Path("skills/repo-analyzer/SKILL.md"))

    def test_skill_documents_only_bundled_gate_command(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>",
            skill,
        )
        self.assertNotIn("stark-repo-analyzer-graphify-gate --target <TARGET> --work-dir <WORK_DIR>", skill)
        self.assertNotIn("python -m stark_repo_analyzer.graphify_gate", skill)
        self.assertNotIn("PYTHONPATH=<SKILL_REPOSITORY_ROOT>/src", skill)
        self.assertIn("不得猜测 plugin 根", skill)
        self.assertIn("启动子进程前", skill)

    def test_old_schema_filename_is_gone_and_bundled_schema_exists(self):
        self.assertFalse((ROOT / "docs" / "spec" / "graphify-gate-status-schema.json").exists())
        self.assertTrue(SCHEMA_PATH.is_file())
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["code"]["enum"], [0, 10, 30])


class SkillContractLintTests(unittest.TestCase):
    def test_core_behavioral_phrases_remain(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        graphify_guide = (
            ROOT / "skills/repo-analyzer/references/graphify-integration-guide.md"
        ).read_text(encoding="utf-8")
        module_guide = (
            ROOT / "skills/repo-analyzer/references/module-analysis-guide.md"
        ).read_text(encoding="utf-8")
        self.assertIn("未指定模式时直接执行 `standard`", skill)
        self.assertIn("`deep` 只集中询问一次", skill)
        self.assertIn("`standard` 的核心/次要模块最低覆盖率为 60%/30%", skill)
        self.assertIn("`deep` 为 90%/60%", skill)
        self.assertIn("Graphify `0.9.13+`", skill)
        self.assertIn("Graphify 始终使用 code-only", skill)
        self.assertIn("安装后复检", skill)
        self.assertIn("本次使用无 Graphify 的原版兼容流程", skill)
        self.assertIn("不得代替用户安装", skill)
        self.assertIn("不得自动进入兼容流程", skill)
        self.assertTrue(all(f"`{code}`" in skill for code in (0, 10, 30)))
        self.assertIn("用户只接收这一份最终报告", skill)
        self.assertIn("不启用 semantic extraction 或 LLM provider", graphify_guide)
        self.assertIn("不能自动选择兼容流程", graphify_guide)
        self.assertIn("未获同意前不得开始顺序分析", module_guide)
        self.assertIsNone(re.search(r"stark-repo-analyzer\s+(?:analyze|finalize|validate|resume)\b", skill))
        self.assertIsNone(re.search(r"(?:`quick`|quick 模式|快速模式)", skill, re.I))

    def test_gate_source_has_no_backend_or_model_state(self):
        gate_source = GATE_PATH.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b(?:backend|model)\b", gate_source))


if __name__ == "__main__":
    unittest.main()
