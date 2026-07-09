"""T18: TokenCollector 与 token 汇报测试（对应 T05/T06）。

覆盖：
- ``<!-- TOKENS: in,out -->`` 标记解析
- 无标记返回 None / 不累计
- 多次 collect_from 聚合 in/out/total
- reset 清空累计
- token_status 绿/黄/红阈值（预算 500K）
- TOKEN_BUDGET / TOKEN_BUDGET_MODE 常量
"""

import unittest

from token_reporter import (  # noqa: E402
    TOKEN_BUDGET,
    TOKEN_BUDGET_MODE,
    TokenCollector,
    token_status,
)


class TokenCollectorTest(unittest.TestCase):
    def test_parse_marker_extracts_in_out(self):
        text = "分析完成。<!-- TOKENS: 1234, 567 -->\n谢谢。"
        usage = TokenCollector().collect_from(text)
        self.assertIsNotNone(usage)
        self.assertEqual(usage.tokens_in, 1234)
        self.assertEqual(usage.tokens_out, 567)

    def test_no_marker_returns_none(self):
        collector = TokenCollector()
        self.assertIsNone(collector.collect_from("没有任何标记的文本"))
        self.assertEqual(collector.total, 0)

    def test_aggregation_across_runs(self):
        collector = TokenCollector()
        collector.collect_from("a <!-- TOKENS: 100, 20 --> b")
        collector.collect_from("c <!-- TOKENS: 300, 80 --> d")
        self.assertEqual(collector.total_in, 400)
        self.assertEqual(collector.total_out, 100)
        self.assertEqual(collector.total, 500)
        self.assertEqual(len(collector.entries), 2)
        self.assertEqual(
            collector.as_dict(),
            {"tokens_in": 400, "tokens_out": 100, "tokens_total": 500},
        )

    def test_reset_clears(self):
        collector = TokenCollector()
        collector.collect_from("<!-- TOKENS: 10, 5 -->")
        collector.reset()
        self.assertEqual(collector.total, 0)
        self.assertEqual(len(collector.entries), 0)

    def test_marker_with_whitespace(self):
        text = "<!--   TOKENS:   42 , 7   -->"
        usage = TokenCollector.parse_marker(text)
        self.assertEqual(usage, (42, 7))

    def test_marker_not_confused_with_other_comments(self):
        text = "<!-- MODULE_RESULT: module_001 --><!-- TOKENS: 1, 2 --><!-- END_MODULE_RESULT -->"
        usage = TokenCollector.parse_marker(text)
        self.assertEqual(usage, (1, 2))


class TokenBudgetTest(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(TOKEN_BUDGET, 500_000)
        self.assertEqual(TOKEN_BUDGET_MODE, 0)

    def test_status_green(self):
        self.assertEqual(token_status(0), "green")
        self.assertEqual(token_status(int(TOKEN_BUDGET * 0.5)), "green")

    def test_status_yellow(self):
        # > 80% 进入 yellow
        self.assertEqual(token_status(int(TOKEN_BUDGET * 0.81)), "yellow")
        self.assertEqual(token_status(TOKEN_BUDGET), "yellow")

    def test_status_red(self):
        self.assertEqual(token_status(TOKEN_BUDGET + 1), "red")
        self.assertEqual(token_status(TOKEN_BUDGET * 2), "red")

    def test_status_custom_budget(self):
        self.assertEqual(token_status(50, budget=100), "green")
        self.assertEqual(token_status(90, budget=100), "yellow")
        self.assertEqual(token_status(101, budget=100), "red")


if __name__ == "__main__":
    unittest.main()
