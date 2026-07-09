"""T20: 外部调研阶段（T07）单元测试。

覆盖：
- ``write_research`` 离线 / 在线均不抛异常，写入 data/research.md 并返回 research_section
- ``report_data`` 透传 ``research_section`` 到 data/report-data.json
- ``build_parser`` 提供 ``--research`` 开关
- 集成：analyze --research --no-question 产出 data/research.md 且报告含 research_section
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))
import repo_analyzer  # noqa: E402
from test_repo_analyzer_cli import (  # noqa: E402
    CLI,
    install_fake_agent,
    install_fake_codex,
    install_fake_repomix,
)


class ResearchStageTest(unittest.TestCase):
    def setUp(self):
        self._old_path = os.environ.get("PATH", "")
        self._fake_tools_tmp = tempfile.TemporaryDirectory()
        self.fake_tools = Path(self._fake_tools_tmp.name)
        install_fake_repomix(self.fake_tools)
        install_fake_agent(self.fake_tools)
        install_fake_codex(self.fake_tools)
        os.environ["PATH"] = f"{self.fake_tools}{os.pathsep}{self._old_path}"
        self._repo_tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._repo_tmp.name) / "demo"
        self.repo.mkdir(parents=True)
        (self.repo / "README.md").write_text("# Demo\n", encoding="utf-8")
        (self.repo / "main.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=self.repo, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.repo, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def tearDown(self):
        os.environ["PATH"] = self._old_path
        self._fake_tools_tmp.cleanup()
        self._repo_tmp.cleanup()

    def test_write_research_offline_skips(self):
        with tempfile.TemporaryDirectory() as out_tmp:
            output = Path(out_tmp)
            section = repo_analyzer.write_research(output, offline=True)
            self.assertIn("SKIP", section)
            research_file = output / "data" / "research.md"
            self.assertTrue(research_file.exists())
            self.assertIn("SKIP", research_file.read_text(encoding="utf-8"))

    def test_write_research_online_also_safe(self):
        with tempfile.TemporaryDirectory() as out_tmp:
            output = Path(out_tmp)
            # 在线但当前环境无联网源，同样降级 SKIP，不抛异常
            section = repo_analyzer.write_research(output, offline=False)
            self.assertIn("SKIP", section)
            self.assertTrue((output / "data" / "research.md").exists())

    def test_report_data_carries_research_section(self):
        with tempfile.TemporaryDirectory() as out_tmp:
            output = Path(out_tmp)
            data = repo_analyzer.report_data(
                project_name="demo",
                source="local",
                repo_type="single-lang-CLI",
                files=[],
                repo=self.repo,
                output=output,
                failed_modules=[],
                research_section="## 外部调研\n\n- 状态: SKIP\n",
            )
            self.assertIn("research_section", data)
            self.assertEqual(data["research_section"], "## 外部调研\n\n- 状态: SKIP\n")

    def test_parser_has_research_flag(self):
        parser = repo_analyzer.build_parser()
        namespace = parser.parse_args([str(self.repo), "--research", "--no-question"])
        self.assertTrue(namespace.research)
        self.assertTrue(namespace.no_question)

    def test_analyze_with_research_flag_writes_research_md(self):
        with tempfile.TemporaryDirectory() as out_tmp:
            output = Path(out_tmp) / "analysis"
            result = subprocess.run(
                [sys.executable, str(CLI), str(self.repo), "--output", str(output),
                 "--research", "--no-question"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "data" / "research.md").exists())
            report_data = json.loads((output / "data" / "report-data.json").read_text(encoding="utf-8"))
            self.assertIn("research_section", report_data)
            self.assertIn("SKIP", report_data["research_section"])


if __name__ == "__main__":
    unittest.main()
