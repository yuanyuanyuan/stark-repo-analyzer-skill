"""T06 回归（第 2 轮）：run_agent_task 将 token 字段写入 performance['agent_attempts']。

修复前（Round 1 发现的源码 Bug）：agent_attempts[] 条目不含
tokens_in/out/total，因为 append 发生在 token 解析之前。
修复后：命令模式天然记 0；命中 <!-- TOKENS: in,out --> 时记录 in/out/total。

独立复现路径：直接调用 repo_analyzer.run_agent_task，用 command 模式 fake 命令
吐出（或不吐）TOKENS 标记，再检查 performance['agent_attempts'][-1] 与落盘
metadata.json。
"""

import argparse
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import repo_analyzer  # noqa: E402


def _args(agent_command: str) -> argparse.Namespace:
    return argparse.Namespace(
        agent_mode="command",
        agent_command=agent_command,
        agent_model="test-model",
        agent_reasoning_effort="",
        agent_timeout_seconds=0,
        agent_max_attempts=1,
    )


class AgentTokenIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "analysis"
        self.output.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_command_mode_records_zero_tokens(self):
        # 命令模式（无 TOKENS 标记）应记 0，满足 PRD T06「command 模式记 0」。
        performance: dict = {}
        ok, _msg, _attempt = repo_analyzer.run_agent_task(
            self.output, _args("printf 'no tokens here'"), "module-001", "prompt", performance
        )
        self.assertTrue(ok)
        attempt = performance["agent_attempts"][-1]
        self.assertEqual(attempt["tokens_in"], 0)
        self.assertEqual(attempt["tokens_out"], 0)
        self.assertEqual(attempt["tokens_total"], 0)

    def test_token_marker_recorded_in_agent_attempts(self):
        # 命中 <!-- TOKENS: 120,45 --> 时，agent_attempts 必须含真实 token 字段
        # （这是 Round 1 Bug 的回归点）。
        performance: dict = {}
        ok, _msg, _attempt = repo_analyzer.run_agent_task(
            self.output, _args("printf '<!-- TOKENS: 120,45 -->'"), "module-002", "prompt", performance
        )
        self.assertTrue(ok)
        attempt = performance["agent_attempts"][-1]
        self.assertEqual(attempt["tokens_in"], 120)
        self.assertEqual(attempt["tokens_out"], 45)
        self.assertEqual(attempt["tokens_total"], 165)
        # 落盘 metadata.json 也应含 token 字段（不应是修复前的「定格无 token 拷贝」）。
        meta_path = self.output / "agent-runs" / "module-002" / "attempt-1" / "metadata.json"
        self.assertTrue(meta_path.exists())
        self.assertIn('"tokens_in": 120', meta_path.read_text(encoding="utf-8"))
        self.assertIn('"tokens_total": 165', meta_path.read_text(encoding="utf-8"))

    def test_multiple_attempts_each_carry_tokens(self):
        # 多次 agent 调用的 token 应分别记录到各自 agent_attempts 条目。
        performance: dict = {}
        repo_analyzer.run_agent_task(
            self.output, _args("printf '<!-- TOKENS: 10,20 -->'"), "m-a", "p", performance
        )
        repo_analyzer.run_agent_task(
            self.output, _args("printf '<!-- TOKENS: 30,40 -->'"), "m-b", "p", performance
        )
        self.assertEqual(len(performance["agent_attempts"]), 2)
        self.assertEqual(performance["agent_attempts"][0]["tokens_total"], 30)
        self.assertEqual(performance["agent_attempts"][1]["tokens_total"], 70)


if __name__ == "__main__":
    unittest.main()
