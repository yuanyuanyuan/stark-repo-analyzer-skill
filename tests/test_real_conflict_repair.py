"""T13: 真实跨模块冲突检测与修复测试（对应 D·#4）。

使用已提交的最小冲突仓库 fixtures/conflict-repo：
- module_a/processor.py 与 module_b/processor.py 都定义了同名公开函数 ``process()``
- orchestrator.py 同时 import 两者（别名），构成真实跨模块职责冲突

测试覆盖：
- analyze 能在冲突仓库上完整跑通并产出核心产物 + cross-ref 报告
- 独立 cross-ref 审稿若指出冲突，``cross_ref_repair_modules`` 能正确选出冲突模块
- 修复 agent 追加的修复说明被写入草稿，且不引入新的重复章节（cross-ref 仍 PASS）
"""

import json
import os
import re
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

FIXTURE = ROOT / "tests" / "fixtures" / "conflict-repo"


class RealConflictRepairTest(unittest.TestCase):
    def setUp(self):
        self._old_path = os.environ.get("PATH", "")
        self._fake_tools_tmp = tempfile.TemporaryDirectory()
        self.fake_tools = Path(self._fake_tools_tmp.name)
        install_fake_repomix(self.fake_tools)
        install_fake_agent(self.fake_tools)
        install_fake_codex(self.fake_tools)
        os.environ["PATH"] = f"{self.fake_tools}{os.pathsep}{self._old_path}"

    def tearDown(self):
        os.environ["PATH"] = self._old_path
        self._fake_tools_tmp.cleanup()

    def _prepare_repo(self, dst: Path):
        shutil.copytree(FIXTURE, dst)
        subprocess.run(["git", "init"], cwd=dst, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "add", "."], cwd=dst, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=dst, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def _run_analyze(self, repo: Path, output: Path, extra=None):
        cmd = [sys.executable, str(CLI), str(repo), "--output", str(output),
               "--no-question"]
        if extra:
            cmd.extend(extra)
        return subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True)

    def test_analyze_conflict_repo_produces_artifacts(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp) / "conflict-repo"
            output = Path(out_tmp) / "analysis"
            self._prepare_repo(repo)

            result = self._run_analyze(repo, output)
            self.assertEqual(result.returncode, 0, result.stderr)

            # 核心产物 + cross-ref 报告必须存在
            self.assertTrue((output / "data" / "meta.txt").exists())
            self.assertTrue((output / "data" / "repo-type.yaml").exists())
            self.assertTrue((output / "reports" / "ANALYSIS_REPORT.md").exists())
            self.assertTrue((output / "diagnostics" / "cross-ref-checks.md").exists())

            # 冲突符号 process 应同时出现在两份模块草稿中（真实冲突被纳入分析）
            module_drafts = list((output / "diagnostics" / "module-drafts").glob("module-*.md"))
            self.assertTrue(module_drafts)
            combined = "\n".join(d.read_text(encoding="utf-8") for d in module_drafts)
            self.assertIn("process", combined)

    def test_cross_ref_repair_selection_picks_conflicting_modules(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp) / "conflict-repo"
            output = Path(out_tmp) / "analysis"
            self._prepare_repo(repo)
            self._run_analyze(repo, output)

            module_text = (output / "data" / "module-ids.yaml").read_text(encoding="utf-8")
            module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", module_text)
            self.assertGreaterEqual(len(module_ids), 2)

            # 构造一条指出冲突的审稿意见，明确建议回退其中一个模块
            target = module_ids[1]
            review = (
                f"## 独立审稿\n"
                f"- 发现跨模块冲突：module_a 与 {target} 都定义了同名函数 process()。\n"
                f"- 建议回退模块: {target}\n"
            )
            selected = repo_analyzer.cross_ref_repair_modules(review, module_ids)
            self.assertEqual(selected, [target])

    def test_cross_ref_repair_no_op_when_review_clean(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp) / "conflict-repo"
            output = Path(out_tmp) / "analysis"
            self._prepare_repo(repo)
            self._run_analyze(repo, output)
            module_text = (output / "data" / "module-ids.yaml").read_text(encoding="utf-8")
            module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", module_text)

            clean_review = "## 独立审稿\n- 未发现跨模块矛盾。\n"
            self.assertEqual(
                repo_analyzer.cross_ref_repair_modules(clean_review, module_ids), []
            )

    def test_repair_appendix_does_not_break_cross_ref(self):
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as out_tmp:
            repo = Path(repo_tmp) / "conflict-repo"
            output = Path(out_tmp) / "analysis"
            self._prepare_repo(repo)
            self._run_analyze(repo, output)

            module_text = (output / "data" / "module-ids.yaml").read_text(encoding="utf-8")
            module_ids = re.findall(r"(?m)^\s*- id: (module_[0-9]+)", module_text)
            target = module_ids[1]

            # 模拟修复 agent 返回的修复说明
            repair_md = (
                "## Agent Cross-ref 修复\n\n"
                f"- 已将 `{target}` 的 process() 重命名为 export_process()，消除与 module_a 的职责冲突。\n"
            )
            repo_analyzer.append_agent_cross_ref_repair(output, target, repair_md, 1)

            appendix = (output / "diagnostics" / "module-drafts" / f"module-{target}.md").read_text(encoding="utf-8")
            self.assertIn("Agent Cross-ref 修复", appendix)

            # 追加修复后，确定性 cross-ref 仍应 PASS（无新增重复章节 / 断裂引用）
            issues = repo_analyzer.write_cross_ref(output)
            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
