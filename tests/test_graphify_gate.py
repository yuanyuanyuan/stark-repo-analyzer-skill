import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stark_repo_analyzer.graphify_gate import (
    NAVIGATION_MAP,
    RAW_GRAPH,
    RAW_REPORT,
    RunFailure,
    STATUS_FILENAME,
    doctor,
    main,
    normalize_graphify_artifacts,
    run_gate,
    source_tree_signature,
    write_graph_map,
    graphify_extract,
)


class GraphifyGateTests(unittest.TestCase):
    def setUp(self):
        self.target = Path(__file__).resolve().parents[1]
        self.fixtures = self.target / "tests" / "fixtures" / "graphify"

    def _copy_graph_fixture(self, name, work_dir):
        graph_dir = work_dir / "graphify-out"
        graph_dir.mkdir(parents=True)
        fixture = self.fixtures / name
        shutil.copy2(fixture / "graph.json", graph_dir / "graph.json")
        shutil.copy2(fixture / "GRAPH_REPORT.md", graph_dir / "GRAPH_REPORT.md")
        return graph_dir

    def test_dependency_unavailable_returns_10_without_extracting(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            preflight = {
                "graphify": {"version": None},
                "failures": ["Graphify CLI is unavailable"],
            }
            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(10, preflight)), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract") as extract:
                status = run_gate(self.target, work_dir)

            self.assertEqual(status["code"], 10)
            self.assertEqual(status["outcome"], "dependency-unavailable")
            self.assertEqual(status["stage"], "preflight")
            self.assertEqual(status["failure"]["class"], "graphify-dependency")
            extract.assert_not_called()

    def test_preflight_accepts_code_only_graphify_without_backend_or_model(self):
        results = [
            subprocess.CompletedProcess([], 0, "graphify 0.9.13\n", ""),
            subprocess.CompletedProcess([], 0, "extract --code-only --no-cluster\n", ""),
            subprocess.CompletedProcess([], 0, "extract --code-only\n", ""),
        ]
        with tempfile.TemporaryDirectory() as directory, \
            patch("stark_repo_analyzer.graphify_gate.shutil.which", return_value="/usr/bin/graphify"), \
            patch("stark_repo_analyzer.graphify_gate.run", side_effect=results):
            code, payload = doctor("preflight", self.target, Path(directory))

        self.assertEqual(code, 0)
        self.assertEqual(payload["graphify"], {
            "version": "graphify 0.9.13",
            "extraction_mode": "code-only",
        })
        self.assertNotIn("backend", json.dumps(payload))
        self.assertNotIn("model", json.dumps(payload))

    def test_graphify_extract_uses_workspace_and_code_only_output(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            work_dir.mkdir()
            calls = []

            def fake_run(command, **kwargs):
                calls.append((command, kwargs))
                return subprocess.CompletedProcess(command, 0, "", "")

            with patch("stark_repo_analyzer.graphify_gate.run", side_effect=fake_run):
                attempts = graphify_extract(self.target, work_dir, [])

            self.assertEqual(attempts[0]["exit_code"], 0)
            command, kwargs = calls[0]
            self.assertEqual(kwargs["cwd"], work_dir)
            self.assertEqual(kwargs["env"]["GRAPHIFY_OUT"], str((work_dir / "graphify-out").resolve()))
            self.assertEqual(command[-4:], ["--code-only", "--no-cluster", "--out", str(work_dir)])

    def test_graphify_extract_timeout_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "stark_repo_analyzer.graphify_gate.run",
            return_value=subprocess.CompletedProcess([], 124, "", "process timeout"),
        ) as execute:
            with self.assertRaises(RunFailure) as caught:
                graphify_extract(self.target, Path(directory), [])

        self.assertEqual(caught.exception.failure_class, "graphify-execution")
        execute.assert_called_once()

    def test_preflight_failure_is_mapped_to_30(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            preflight = {"graphify": {}, "failures": ["work_dir must be outside target repository"]}
            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(20, preflight)), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract") as extract:
                status = run_gate(self.target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["outcome"], "blocked")
            self.assertEqual(status["failure"]["class"], "doctor-preflight")
            extract.assert_not_called()

    def test_workspace_inside_target_is_rejected_before_creation(self):
        work_dir = self.target / ".graphify-gate-test-work"
        self.assertFalse(work_dir.exists())
        with patch("stark_repo_analyzer.graphify_gate.doctor") as gate_doctor:
            status = run_gate(self.target, work_dir)

        self.assertEqual(status["code"], 30)
        self.assertEqual(status["stage"], "preflight")
        self.assertIn("outside target", status["failure"]["message"])
        self.assertFalse(work_dir.exists())
        gate_doctor.assert_not_called()

    def test_success_runs_each_gate_stage_and_writes_minimal_status(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            calls = []
            preflight = {
                "graphify": {
                    "version": "graphify 0.9.13",
                    "backend": "must-not-leak",
                    "model": "must-not-leak",
                }
            }

            def fake_doctor(phase, target, output):
                calls.append(phase)
                return (0, preflight if phase == "preflight" else {"graphify": {"health": {"nodes": 1}}})

            def fake_extract(target, output, log):
                calls.append("extract")
                return []

            def fake_postprocess(target, output, log):
                calls.append("postprocess")
                return {
                    "raw_artifacts": ["graphify-out/raw-code-only-graph.json"],
                    "normalized_artifacts": ["graphify-out/graph.json"],
                }

            def fake_map(output, target):
                calls.append("navigation-map")
                return NAVIGATION_MAP

            with patch("stark_repo_analyzer.graphify_gate.doctor", side_effect=fake_doctor), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", side_effect=fake_extract), \
                patch("stark_repo_analyzer.graphify_gate.graphify_postprocess", side_effect=fake_postprocess), \
                patch("stark_repo_analyzer.graphify_gate.write_graph_map", side_effect=fake_map):
                status = run_gate(self.target, work_dir)

            self.assertEqual(calls, ["preflight", "extract", "postprocess", "post-graph", "navigation-map"])
            self.assertEqual(status["code"], 0)
            self.assertEqual(status["outcome"], "ready")
            self.assertEqual(status["stage"], "complete")
            self.assertEqual(status["graphify"], {"version": "graphify 0.9.13", "extraction_mode": "code-only"})
            self.assertEqual(status["artifacts"], [
                "graphify-out/raw-code-only-graph.json",
                "graphify-out/graph.json",
                NAVIGATION_MAP,
            ])
            self.assertIsNone(status["failure"])
            persisted = json.loads((work_dir / STATUS_FILENAME).read_text(encoding="utf-8"))
            self.assertEqual(persisted, status)

    def test_extract_failure_is_mapped_to_30(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(0, {"graphify": {}})), \
                patch(
                    "stark_repo_analyzer.graphify_gate.graphify_extract",
                    side_effect=RunFailure("extract failed", failure_class="graphify-execution"),
                ):
                status = run_gate(self.target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["stage"], "extract")
            self.assertEqual(status["failure"], {"class": "graphify-execution", "message": "extract failed"})

    def test_postprocess_failure_is_mapped_to_30(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(0, {"graphify": {}})), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", return_value=[]), \
                patch("stark_repo_analyzer.graphify_gate.graphify_postprocess", side_effect=ValueError("bad graph")):
                status = run_gate(self.target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["stage"], "postprocess")
            self.assertEqual(status["failure"]["class"], "graphify-gate")

    def test_post_graph_failure_is_mapped_to_30(self):
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            responses = [
                (0, {"graphify": {"version": "graphify 0.9.13"}}),
                (30, {"failures": ["graph has zero edges"]}),
            ]
            with patch("stark_repo_analyzer.graphify_gate.doctor", side_effect=responses), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", return_value=[]), \
                patch("stark_repo_analyzer.graphify_gate.graphify_postprocess", return_value={}):
                status = run_gate(self.target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["stage"], "post-graph")
            self.assertEqual(status["failure"]["class"], "doctor-post-graph")

    def test_usable_noise_fixture_retains_raw_and_normalizes_workspace_paths(self):
        target = self.fixtures / "g2-target"
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            graph_dir = self._copy_graph_fixture("g2-usable-noise", work_dir)
            original_graph = (graph_dir / "graph.json").read_bytes()
            original_report = (graph_dir / "GRAPH_REPORT.md").read_bytes()

            summary = normalize_graphify_artifacts(target, work_dir)
            normalized = json.loads((graph_dir / "graph.json").read_text(encoding="utf-8"))

            self.assertEqual((graph_dir / RAW_GRAPH).read_bytes(), original_graph)
            self.assertEqual((graph_dir / RAW_REPORT).read_bytes(), original_report)
            self.assertEqual(summary["raw_graph"], {"nodes": 3, "edges": 2})
            self.assertEqual(summary["normalized_graph"], {"nodes": 2, "edges": 1})
            self.assertEqual(summary["normalization"]["dropped_nodes"], 1)
            self.assertEqual(summary["normalization"]["dropped_edges"], 1)
            self.assertEqual(normalized["nodes"][0]["source_file"], "src/module.py")
            self.assertEqual(normalized["links"][0]["source_file"], "src/module.py")

            map_path = write_graph_map(work_dir, target)
            navigation = (work_dir / map_path).read_text(encoding="utf-8")
            self.assertEqual(map_path, NAVIGATION_MAP)
            self.assertIn("节点：2", navigation)
            self.assertIn("关系：1", navigation)
            self.assertIn("src/module.py:L1-L2", navigation)
            post_graph_code, _ = doctor("post-graph", target, work_dir)
            self.assertEqual(post_graph_code, 0)

    def test_empty_after_normalization_fixture_is_blocked(self):
        target = self.fixtures / "g2-target"
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"
            graph_dir = self._copy_graph_fixture("g2-empty-after-normalization", work_dir)
            original_graph = (graph_dir / "graph.json").read_bytes()

            with self.assertRaises(RunFailure) as caught:
                normalize_graphify_artifacts(target, work_dir)

            self.assertEqual(caught.exception.failure_class, "graphify-artifact")
            self.assertEqual((graph_dir / RAW_GRAPH).read_bytes(), original_graph)

    def test_gate_empty_graph_failure_reports_only_retained_raw_artifacts(self):
        target = self.fixtures / "g2-target"
        with tempfile.TemporaryDirectory() as directory:
            work_dir = Path(directory) / "work"

            def fake_extract(target_path, output, log):
                self._copy_graph_fixture("g2-empty-after-normalization", output)
                return []

            completed = type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(0, {"graphify": {}})), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", side_effect=fake_extract), \
                patch("stark_repo_analyzer.graphify_gate.run", return_value=completed):
                status = run_gate(target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["stage"], "postprocess")
            self.assertEqual(status["failure"]["class"], "graphify-artifact")
            self.assertEqual(status["artifacts"], [
                f"graphify-out/{RAW_GRAPH}",
                f"graphify-out/{RAW_REPORT}",
            ])

    def test_source_mutation_during_extract_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            (target / "source.py").write_text("value = 1\n", encoding="utf-8")
            work_dir = root / "work"

            def mutate_source(target_path, output, log):
                (target_path / "source.py").write_text("value = 2\n", encoding="utf-8")
                return []

            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(0, {"graphify": {}})), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", side_effect=mutate_source), \
                patch("stark_repo_analyzer.graphify_gate.graphify_postprocess") as postprocess:
                status = run_gate(target, work_dir)

            self.assertEqual(status["code"], 30)
            self.assertEqual(status["stage"], "extract")
            self.assertEqual(status["failure"]["class"], "source-boundary-violation")
            postprocess.assert_not_called()

    def test_unexpected_target_graphify_output_is_removed_and_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            (target / "source.py").write_text("value = 1\n", encoding="utf-8")
            before = source_tree_signature(target)
            work_dir = root / "work"

            def write_inside_target(target_path, output, log):
                graph_dir = target_path / "graphify-out"
                graph_dir.mkdir()
                (graph_dir / "graph.json").write_text("{}\n", encoding="utf-8")
                return []

            with patch("stark_repo_analyzer.graphify_gate.doctor", return_value=(0, {"graphify": {}})), \
                patch("stark_repo_analyzer.graphify_gate.graphify_extract", side_effect=write_inside_target):
                status = run_gate(target, work_dir)

            self.assertEqual(status["failure"]["class"], "source-boundary-violation")
            self.assertFalse((target / "graphify-out").exists())
            self.assertEqual(source_tree_signature(target), before)

    def test_cli_stdout_and_return_code_match_status(self):
        expected = {
            "schema_version": 1,
            "code": 10,
            "outcome": "dependency-unavailable",
            "stage": "preflight",
            "target": str(self.target),
            "work_dir": "/tmp/work",
            "graphify": {"version": None, "extraction_mode": "code-only"},
            "artifacts": [],
            "failure": {"class": "graphify-dependency", "message": "missing"},
        }
        stdout = io.StringIO()
        with patch("stark_repo_analyzer.graphify_gate.run_gate", return_value=expected), redirect_stdout(stdout):
            code = main(["--target", str(self.target), "--work-dir", "/tmp/work"])

        self.assertEqual(code, 10)
        self.assertEqual(json.loads(stdout.getvalue()), expected)

    def test_status_schema_declares_the_implementation_contract(self):
        schema_path = Path(__file__).resolve().parents[1] / "docs" / "spec" / "graphify-gate-status-schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["code"]["enum"], [0, 10, 30])
        self.assertEqual(schema["properties"]["outcome"]["enum"], ["ready", "dependency-unavailable", "blocked"])
        self.assertEqual(schema["properties"]["graphify"]["properties"]["extraction_mode"]["const"], "code-only")
        self.assertEqual(len(schema["allOf"]), 3)
        self.assertEqual(set(schema["required"]), {
            "schema_version", "code", "outcome", "stage", "target", "work_dir", "graphify", "artifacts", "failure"
        })


if __name__ == "__main__":
    unittest.main()
