"""T17: ask_user 三运行时适配器 + 降级链测试（对应 T03/T04）。

覆盖：
- detect_runtime 检测顺序（env → 进程特征 → unknown）
- ask_user 在 --no-question 下返回默认值
- 未知 / 无 provider 运行时降级到默认值，不抛异常
- REPO_ANALYZER_ANSWERS_FILE provider 注入答案
- set_runtime_provider 注册自定义 provider
- ensure_defaults_file 自动生成 defaults.yaml
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys = __import__("sys")
sys.path.insert(0, str(ROOT / "scripts"))
from ask_user_adapters import (  # noqa: E402
    Answer,
    ask_user,
    build_questions,
    config_home,
    defaults_path,
    detect_runtime,
    ensure_defaults_file,
    set_runtime_provider,
)


class DetectRuntimeTest(unittest.TestCase):
    def setUp(self):
        self._saved = {}
        for key in ("REPO_ANALYZER_RUNTIME", "CLAUDECODE", "CODEX", "CODEX_CLI", "CURSOR"):
            self._saved[key] = os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_explicit_env_wins(self):
        os.environ["REPO_ANALYZER_RUNTIME"] = "codex"
        self.assertEqual(detect_runtime(), "codex")

    def test_claude_code_feature(self):
        os.environ["CLAUDECODE"] = "1"
        self.assertEqual(detect_runtime(), "claude-code")

    def test_codex_feature(self):
        os.environ["CODEX"] = "1"
        self.assertEqual(detect_runtime(), "codex")

    def test_cursor_feature(self):
        os.environ["CURSOR"] = "1"
        self.assertEqual(detect_runtime(), "cursor")

    def test_unknown(self):
        self.assertEqual(detect_runtime(), "unknown")


class AskUserDegradationTest(unittest.TestCase):
    def setUp(self):
        self._saved = {}
        for key in ("REPO_ANALYZER_RUNTIME", "CLAUDECODE", "CODEX", "CODEX_CLI", "CURSOR", "REPO_ANALYZER_ANSWERS_FILE"):
            self._saved[key] = os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_no_question_returns_defaults(self):
        answers = ask_user(build_questions(), no_question=True, mode_default="business")
        self.assertEqual(answers["priority"], ["architecture"])
        self.assertEqual(answers["audience"], ["business"])
        self.assertEqual(answers["usage_assumptions"], [])
        self.assertEqual(answers["future_extensions"], [])

    def test_unknown_runtime_degrades_to_defaults(self):
        # 无运行时、无 answers 文件 → 降级默认值，不抛异常
        answers = ask_user(build_questions(), no_question=False, mode_default="tech-lead")
        self.assertEqual(answers["priority"], ["architecture"])
        self.assertEqual(answers["audience"], ["tech-lead"])

    def test_answers_file_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            answers_file = Path(tmp) / "answers.json"
            answers_file.write_text(
                json.dumps({
                    "priority": ["product"],
                    "audience": ["learning"],
                    "usage_assumptions": ["cli", "service"],
                    "future_extensions": ["api"],
                }),
                encoding="utf-8",
            )
            # answers 文件由默认 provider 读取；需有运行时创建适配器（cursor 等）。
            os.environ["REPO_ANALYZER_RUNTIME"] = "cursor"
            os.environ["REPO_ANALYZER_ANSWERS_FILE"] = str(answers_file)
            answers = ask_user(build_questions(), no_question=False)
        self.assertEqual(answers["priority"], ["product"])
        self.assertEqual(answers["audience"], ["learning"])
        self.assertEqual(answers["usage_assumptions"], ["cli", "service"])
        self.assertEqual(answers["future_extensions"], ["api"])

    def test_set_runtime_provider_injection(self):
        calls = []

        def fake_provider(questions, timeout_sec=60):
            calls.append(questions)
            return [
                Answer(key="priority", selected=["learning"]),
                Answer(key="audience", selected=["business"]),
                Answer(key="usage_assumptions", selected=["library"]),
                Answer(key="future_extensions", selected=["plugins"]),
            ]

        set_runtime_provider("claude-code", fake_provider)
        try:
            os.environ["REPO_ANALYZER_RUNTIME"] = "claude-code"
            answers = ask_user(build_questions(), no_question=False)
        finally:
            set_runtime_provider("claude-code", None)
        self.assertTrue(calls)
        self.assertEqual(answers["priority"], ["learning"])
        self.assertEqual(answers["audience"], ["business"])
        self.assertEqual(answers["usage_assumptions"], ["library"])
        self.assertEqual(answers["future_extensions"], ["plugins"])


class DefaultsFileTest(unittest.TestCase):
    def setUp(self):
        self._home = tempfile.TemporaryDirectory()
        os.environ["REPO_ANALYZER_CONFIG_HOME"] = self._home.name

    def tearDown(self):
        self._home.cleanup()
        os.environ.pop("REPO_ANALYZER_CONFIG_HOME", None)

    def test_ensure_defaults_file_generated(self):
        path = ensure_defaults_file()
        self.assertTrue(path.exists())
        self.assertEqual(path, defaults_path())
        text = path.read_text(encoding="utf-8")
        self.assertIn("priority: architecture", text)
        self.assertIn("audience: tech-lead", text)

    def test_defaults_file_idempotent(self):
        first = ensure_defaults_file()
        second = ensure_defaults_file()
        self.assertEqual(first, second)


class BuildQuestionsTest(unittest.TestCase):
    def test_four_questions_with_keys(self):
        questions = build_questions()
        keys = [q.key for q in questions]
        self.assertEqual(
            keys,
            ["priority", "audience", "usage_assumptions", "future_extensions"],
        )
        # 多选项题应为 multi_select
        self.assertTrue(questions[2].multi_select)
        self.assertTrue(questions[3].multi_select)


if __name__ == "__main__":
    unittest.main()
