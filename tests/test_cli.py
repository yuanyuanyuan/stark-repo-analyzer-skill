import tempfile
import unittest
import json
import subprocess
from pathlib import Path
import sys
from argparse import Namespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stark_repo_analyzer.cli import analyze, feature_questions, finalize, normalize_input, size_report
from stark_repo_analyzer.contracts import ContractError, validate_run_contract


class CliContractTests(unittest.TestCase):
    def test_local_input_records_commit_shape_without_cloning(self):
        target = Path(__file__).resolve().parents[1]
        resolved, metadata = normalize_input(str(target), target.parent / "work")
        self.assertEqual(resolved, target.resolve())
        self.assertEqual(metadata["kind"], "local-path")
        self.assertIsNotNone(metadata["source_commit"])

    def test_non_git_local_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                normalize_input(directory, Path(directory).parent / "work")

    def test_public_owner_repo_input_is_normalized_without_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"

            def fake_run(command, **kwargs):
                if command[:2] == ["git", "clone"]:
                    return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()
                if command[-2:] == ["rev-parse", "HEAD"]:
                    return type("Result", (), {"returncode": 0, "stdout": "abc1234\n", "stderr": ""})()
                return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

            with patch("stark_repo_analyzer.cli.run", side_effect=fake_run):
                target, metadata = normalize_input("https://github.com/example/project", work_dir)
            self.assertEqual(metadata["kind"], "public-url")
            self.assertEqual(metadata["clone_source"], "https://github.com/example/project.git")
            self.assertNotIn("@", metadata["clone_source"])
            self.assertEqual(metadata["source_commit"], "abc1234")

    def test_public_input_rejects_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                normalize_input("https://user:secret@example.com/org/repo", Path(directory))

    def test_analyze_rejects_nonempty_workspace(self):
        target = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "run"
            work_dir.mkdir()
            (work_dir / "stale.txt").write_text("stale\n", encoding="utf-8")
            result = analyze(Namespace(input=str(target), work_dir=str(work_dir), run_id="stale", mode="standard"))
            self.assertEqual(result, 30)
            self.assertTrue((work_dir / "stale.txt").is_file())

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

    def test_analyze_writes_agent_handoff_contract(self):
        target = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "run"

            def fake_doctor(script, phase, target_path, output_dir):
                return 0, {
                    "phase": phase,
                    "status": {"code": 0, "name": "ready"},
                    "failures": [],
                    "target": str(target_path),
                    "work_dir": str(output_dir.resolve()),
                "graphify": {
                    "version": "graphify test",
                    "backend": "test-backend",
                    "model": "test-model",
                    "health": {"nodes": 1, "edges": 1, "node_source_references": 1, "edge_source_references": 1},
                },
                }

            def fake_extract(target_path, output_dir, log):
                graph_dir = output_dir / "graphify-out"
                graph_dir.mkdir(parents=True)
                graph = {
                    "nodes": [{
                        "id": "cli",
                        "label": "CLI",
                        "source_file": "src/stark_repo_analyzer/cli.py",
                        "source_location": "L1",
                    }],
                    "links": [{
                        "source": "cli",
                        "target": "cli",
                        "relation": "self",
                        "confidence": "EXTRACTED",
                        "source_file": "src/stark_repo_analyzer/cli.py",
                        "source_location": "L1",
                    }],
                }
                (graph_dir / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
                (graph_dir / "GRAPH_REPORT.md").write_text("1 nodes · 1 edges\n", encoding="utf-8")
                (graph_dir / "manifest.json").write_text("{}\n", encoding="utf-8")
                return [{"exit_code": 0, "transient_failure": False}]

            args = Namespace(input=str(target), work_dir=str(work_dir), run_id="test-run", mode="standard")
            with patch("stark_repo_analyzer.cli.find_doctor", return_value=Path("doctor.sh")), \
                patch("stark_repo_analyzer.cli.doctor", side_effect=fake_doctor), \
                patch("stark_repo_analyzer.cli.graphify_extract", side_effect=fake_extract):
                self.assertEqual(analyze(args), 2)

            self.assertTrue((work_dir / "drafts/01-graphify-map.md").is_file())
            self.assertTrue((work_dir / "drafts/06-module-tasks.json").is_file())
            self.assertTrue((work_dir / "manifest.json").is_file())
            summary = validate_run_contract(work_dir)
            self.assertEqual(summary["analysis_mode"], "standard")
            self.assertEqual(summary["graph"]["nodes"], 1)

    def test_finalize_requires_passing_agent_module_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            (work_dir / "drafts").mkdir()
            (work_dir / "graphify-out").mkdir()
            for name in ("input.md", "execution-log.md", "ANALYSIS_REPORT.md", "checks.md"):
                (work_dir / name).write_text("placeholder\n", encoding="utf-8")
            (work_dir / "metadata.json").write_text(json.dumps({
                "analysis_mode": "standard",
                "source": {"source_commit": "abc"},
            }), encoding="utf-8")
            (work_dir / "graphify-out/graph.json").write_text('{"nodes":[1],"links":[1]}', encoding="utf-8")
            (work_dir / "graphify-out/GRAPH_REPORT.md").write_text("1 nodes · 1 edges", encoding="utf-8")
            for name in ("01-graphify-map.md", "03-research.md", "03-plan.md", "05-modules-plan.md", "07-cross-validation.md", "08-insights.md", "08-coverage.md"):
                (work_dir / "drafts" / name).write_text("pending\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                validate_run_contract(work_dir, complete=True)

    def test_complete_validation_requires_every_manifested_module_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            (work_dir / "drafts").mkdir()
            (work_dir / "graphify-out").mkdir()
            for name in ("input.md", "execution-log.md", "ANALYSIS_REPORT.md", "checks.md"):
                (work_dir / name).write_text("placeholder\n", encoding="utf-8")
            (work_dir / "metadata.json").write_text(json.dumps({
                "analysis_mode": "standard",
                "source": {"source_commit": "abc"},
            }), encoding="utf-8")
            (work_dir / "graphify-out/graph.json").write_text('{"nodes":[1],"links":[1]}', encoding="utf-8")
            (work_dir / "graphify-out/GRAPH_REPORT.md").write_text("1 nodes · 1 edges", encoding="utf-8")
            for name in ("01-graphify-map.md", "03-research.md", "03-plan.md", "05-modules-plan.md", "07-cross-validation.md", "08-insights.md", "08-coverage.md"):
                (work_dir / "drafts" / name).write_text("source coverage PASS\n", encoding="utf-8")
            (work_dir / "drafts/06-module-tasks.json").write_text(json.dumps([
                {"id": "module-01", "output": "drafts/06-module-module-01.md", "status": "completed"},
                {"id": "module-02", "output": "drafts/06-module-module-02.md", "status": "completed"},
            ]), encoding="utf-8")
            for name, phase in (("doctor-preflight.json", "preflight"), ("doctor-post-graph.json", "post-graph")):
                (work_dir / name).write_text(json.dumps({"phase": phase, "status": {"code": 0}, "graphify": {"health": {"nodes": 1, "edges": 1, "node_source_references": 1, "edge_source_references": 1}}}), encoding="utf-8")
            (work_dir / "drafts/06-module-module-01.md").write_text(
                "# Module\n\nRole and Why trade-offs.\n\n```mermaid\nflowchart LR\nA --> B\n```\n\n"
                "| File | Lines | Coverage |\n|---|---:|---|\n| src/a.py | 1 | PASS |\n| Total | 1 | PASS |\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ContractError, "module drafts missing"):
                validate_run_contract(work_dir, complete=True)

    def test_finalize_fuses_verified_modules_without_coverage_chapter(self):
        target = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "run"

            def fake_doctor(script, phase, target_path, output_dir):
                return 0, {
                    "phase": phase,
                    "status": {"code": 0, "name": "ready"},
                    "failures": [],
                    "target": str(target_path),
                    "work_dir": str(output_dir.resolve()),
                    "graphify": {"version": "test", "backend": "test", "model": "test", "health": {"nodes": 1, "edges": 1, "node_source_references": 1, "edge_source_references": 1}},
                }

            def fake_extract(target_path, output_dir, log):
                graph_dir = output_dir / "graphify-out"
                graph_dir.mkdir(parents=True)
                graph = {
                    "nodes": [{"id": "cli", "source_file": "src/stark_repo_analyzer/cli.py", "source_location": "L1"}],
                    "links": [{"source": "cli", "target": "cli", "source_file": "src/stark_repo_analyzer/cli.py", "source_location": "L1", "confidence": "EXTRACTED"}],
                }
                (graph_dir / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
                (graph_dir / "GRAPH_REPORT.md").write_text("1 nodes · 1 edges", encoding="utf-8")
                (graph_dir / "manifest.json").write_text("{}", encoding="utf-8")
                return [{"exit_code": 0, "transient_failure": False}]

            with patch("stark_repo_analyzer.cli.find_doctor", return_value=Path("doctor.sh")), \
                patch("stark_repo_analyzer.cli.doctor", side_effect=fake_doctor), \
                patch("stark_repo_analyzer.cli.graphify_extract", side_effect=fake_extract):
                self.assertEqual(analyze(Namespace(input=str(target), work_dir=str(work_dir), run_id="finalize-test", mode="standard")), 2)

            (work_dir / "drafts/06-module-tasks.json").write_text(json.dumps([
                {"id": "module-core", "output": "drafts/06-module-core.md", "status": "completed"},
            ]), encoding="utf-8")
            (work_dir / "drafts/06-module-core.md").write_text(
                "# Core Module\n\n"
                "## Role\nThis module owns the core business boundary.\n\n"
                "## Why and trade-offs\nWhy this boundary exists and why the alternative costs more.\n\n"
                "```mermaid\nflowchart LR\nA --> B\n```\n\n"
                "| File | Total lines | Read lines | Coverage |\n|---|---:|---:|---:|\n"
                "Source evidence: `src/stark_repo_analyzer/cli.py:L1`\n\n"
                "| src/stark_repo_analyzer/cli.py | 10 | 10 | 100% |\n| Total | 10 | 10 | PASS |\n",
                encoding="utf-8",
            )
            (work_dir / "drafts/07-cross-validation.md").write_text("# Cross Validation\n\n源码抽查确认核心路径。\n", encoding="utf-8")
            (work_dir / "drafts/08-insights.md").write_text("# Insights\n\nThe trade-off is explicit.\n", encoding="utf-8")
            (work_dir / "drafts/08-coverage.md").write_text("# Coverage\n\n| Total | 10 | 10 | PASS |\n", encoding="utf-8")
            result = finalize(Namespace(work_dir=str(work_dir)))
            self.assertEqual(result, 0)
            report = (work_dir / "ANALYSIS_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Core Module", report)
            self.assertNotIn("## 8. Coverage", report)
            self.assertTrue((work_dir / "manifest.json").is_file())
            manifest = json.loads((work_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["files"])
            self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["files"]))

    def test_doctor_rejects_unlocatable_graph_evidence(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory)
            graph_dir = work_dir / "graphify-out"
            graph_dir.mkdir()
            graph = {
                "nodes": [{"id": "outside", "source_file": "../outside.py", "source_location": "L1"}],
                "links": [{"source": "outside", "target": "outside", "source_file": "../outside.py", "source_location": "L1"}],
            }
            (graph_dir / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
            (graph_dir / "GRAPH_REPORT.md").write_text("1 nodes · 1 edges", encoding="utf-8")
            result = subprocess.run(
                [str(root / "acceptance/doctor.sh"), "post-graph", "--target", str(root), "--work-dir", str(work_dir), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 30)
            self.assertIn("source references", result.stdout)


if __name__ == "__main__":
    unittest.main()
