import tempfile
import unittest
from pathlib import Path

from stark_repo_analyzer.cli import feature_questions, normalize_input, size_report


class CliContractTests(unittest.TestCase):
    def test_local_input_records_commit_shape_without_cloning(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            resolved, metadata = normalize_input(str(target), target / "work")
            self.assertEqual(resolved, target.resolve())
            self.assertEqual(metadata["kind"], "local-path")
            self.assertIsNone(metadata["clone_source"])

    def test_size_report_excludes_tests_and_generated_dependency_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "src").mkdir()
            (target / "tests").mkdir()
            (target / "node_modules").mkdir()
            (target / "src" / "main.py").write_text("a\nb\n", encoding="utf-8")
            (target / "tests" / "test_main.py").write_text("x\n" * 20, encoding="utf-8")
            (target / "node_modules" / "dep.js").write_text("x\n" * 20, encoding="utf-8")
            report = size_report(target)
            self.assertEqual(report["files"], 1)
            self.assertEqual(report["effective_lines"], 2)

    def test_questions_change_with_project_features(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            questions = feature_questions(
                target,
                {"effective_lines": 1},
                {"external_sources": [], "research_status": "agent-research-required"},
            )
            self.assertTrue(any("配置" in question for question in questions))
            self.assertTrue(any("外部来源" in question for question in questions))


if __name__ == "__main__":
    unittest.main()
