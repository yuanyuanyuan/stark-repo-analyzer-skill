import subprocess
import sys
import tempfile
import re
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_analyzer.py"


class RepoAnalyzerCliTest(TestCase):
    def test_analyzes_local_repo_and_writes_core_artifacts(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Demo Tool\n\nA tiny command line tool.\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text(
                '[project]\nname = "demo-tool"\nversion = "0.1.0"\n',
                encoding="utf-8",
            )
            (repo / "main.py").write_text(
                "def run():\n    return 'ok'\n\n\ndef search_docs(query):\n    return query\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "00-meta.txt").exists())
            self.assertTrue((output / "02a-repo-type.yaml").exists())
            self.assertTrue((output / "02a-manifest-card.md").exists())
            self.assertTrue((output / "slices" / "04-docs.xml").exists())
            self.assertTrue((output / "ANALYSIS_REPORT.md").exists())
            self.assertTrue((output / "README.md").exists())
            self.assertIn("single-lang-CLI", (output / "02a-repo-type.yaml").read_text(encoding="utf-8"))
            report = (output / "ANALYSIS_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Demo Tool", report)
            self.assertIn("A tiny command line tool.", report)
            self.assertIn("python main.py", report)
            self.assertIn("name = \"demo-tool\"", report)
            self.assertIn("search_docs", report)
            self.assertTrue((output / "drafts" / "06-module-module_001.md").exists())

    def test_mode_all_writes_three_reports_and_acceptance_entrypoint(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Demo Tool\n", encoding="utf-8")
            (repo / "package.json").write_text(
                '{"name":"demo-tool","scripts":{"start":"node mcp_server_node.js"}}',
                encoding="utf-8",
            )
            (repo / "mcp_server_node.js").write_text(
                "const AI_TOOLS = [{ name: 'ai_search_web', description: 'Web search' }];\n"
                "async function main() { return AI_TOOLS; }\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--mode", "all", "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "ANALYSIS_REPORT.tech-lead.md").exists())
            self.assertTrue((output / "ANALYSIS_REPORT.business.md").exists())
            self.assertTrue((output / "ANALYSIS_REPORT.learning.md").exists())
            tech = (output / "ANALYSIS_REPORT.tech-lead.md").read_text(encoding="utf-8")
            business = (output / "ANALYSIS_REPORT.business.md").read_text(encoding="utf-8")
            learning = (output / "ANALYSIS_REPORT.learning.md").read_text(encoding="utf-8")
            self.assertIn("技术负责人关注", tech)
            self.assertIn("业务负责人关注", business)
            self.assertIn("学习路径", learning)
            self.assertNotEqual(tech, business)
            self.assertNotEqual(tech, learning)
            check = output / "acceptance" / "check.sh"
            self.assertTrue(check.exists())
            self.assertTrue(check.read_text(encoding="utf-8").startswith("#!/bin/sh"))
            acceptance = subprocess.run([str(check)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(acceptance.returncode, 0, acceptance.stdout + acceptance.stderr)
            (output / "ANALYSIS_REPORT.business.md").write_text(tech, encoding="utf-8")
            broken_audience = subprocess.run([str(check)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertNotEqual(broken_audience.returncode, 0, broken_audience.stdout + broken_audience.stderr)

    def test_acceptance_fails_when_report_drops_mcp_tool(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Search MCP\n", encoding="utf-8")
            (repo / "package.json").write_text('{"name":"search-mcp"}', encoding="utf-8")
            (repo / "mcp_server_node.js").write_text(
                "const AI_TOOLS = [{ name: 'ai_search_web', description: 'Web search' }];\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--mode", "all", "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            check = output / "acceptance" / "check.sh"
            passing = subprocess.run([str(check)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(passing.returncode, 0, passing.stdout + passing.stderr)
            report = output / "ANALYSIS_REPORT.md"
            report.write_text(report.read_text(encoding="utf-8").replace("ai_search_web", "removed_tool"), encoding="utf-8")
            broken_api = subprocess.run([str(check)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertNotEqual(broken_api.returncode, 0, broken_api.stdout + broken_api.stderr)

    def test_coverage_and_state_are_final_deterministic_outputs(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Demo Tool\n", encoding="utf-8")
            (repo / "main.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            coverage = (output / "08-coverage.md").read_text(encoding="utf-8")
            state = (output / "STATE_REPORT.md").read_text(encoding="utf-8")
            self.assertNotIn("待 LLM 深度分析补全", coverage)
            self.assertNotIn("PASS_WITH_DETERMINISTIC_BASELINE", state)

    def test_report_only_links_existing_artifacts_and_history_ignores_dependencies(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Demo Tool\n", encoding="utf-8")
            (repo / "main.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")
            (repo / "node_modules").mkdir()
            (repo / "node_modules" / "ignored.js").write_text("console.log('noise')\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = (output / "ANALYSIS_REPORT.md").read_text(encoding="utf-8")
            slice_refs = set(re.findall(r"slices/[A-Za-z0-9_.-]+", report))
            self.assertTrue(slice_refs)
            for ref in slice_refs:
                self.assertTrue((output / ref).exists(), ref)
            history = (output / "slices" / "12-history-hotspot.txt").read_text(encoding="utf-8")
            self.assertNotIn("node_modules", history)

    def test_reports_mcp_tool_names_from_source(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp)
            output = Path(out_tmp) / "analysis"

            (repo / "README.md").write_text("# Search MCP\n", encoding="utf-8")
            (repo / "package.json").write_text(
                '{"name":"search-mcp","main":"mcp_server_node.js","dependencies":{"@modelcontextprotocol/sdk":"1.0.0"}}',
                encoding="utf-8",
            )
            (repo / "mcp_server_node.js").write_text(
                "const AI_TOOLS = [{ name: 'ai_search_web', description: 'Web search' },"
                "{ name: 'ai_search_github', description: 'GitHub search' }];\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI), str(repo), "--output", str(output), "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = (output / "ANALYSIS_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("ai_search_web", report)
            self.assertIn("ai_search_github", report)
