#!/usr/bin/env python3
"""Token 用量收集与汇报（stdlib-only，无第三方依赖）。

对应 ADR-0004：agent 返回文本中以 ``<!-- TOKENS: in,out -->`` 标记声明 token 用量，
:class:`TokenCollector` 解析该标记并聚合到 SLA / PERFORMANCE / CONFIG_EFFECTIVE 报告。

预算：500K（ADR-0004 Q2）；命令模式 (mode) = 0 表示由命令显式声明，不做自动估算。
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


TOKEN_MARKER_RE = re.compile(r"<!--\s*TOKENS:\s*(\d+)\s*,\s*(\d+)\s*-->")

# ADR-0004 Q2：token 预算 500K；命令模式 (mode) = 0（显式声明，不自动估算）。
TOKEN_BUDGET = 500_000
TOKEN_BUDGET_MODE = 0


@dataclass
class TokenUsage:
    """单次 agent 运行的 token 用量。"""

    tokens_in: int = 0
    tokens_out: int = 0


class TokenCollector:
    """从 agent 返回文本中解析 ``<!-- TOKENS: in,out -->`` 标记并聚合用量。"""

    def __init__(self) -> None:
        self.entries: List[TokenUsage] = []

    @staticmethod
    def parse_marker(text: str) -> Optional[Tuple[int, int]]:
        """解析 ``<!-- TOKENS: in,out -->``，返回 (in, out) 或 None。"""
        match = TOKEN_MARKER_RE.search(text or "")
        if not match:
            return None
        return int(match.group(1)), int(match.group(2))

    def collect_from(self, text: str) -> Optional[TokenUsage]:
        """从一段 agent 返回文本收集 token 用量；无标记返回 None。"""
        parsed = self.parse_marker(text)
        if parsed is None:
            return None
        usage = TokenUsage(tokens_in=parsed[0], tokens_out=parsed[1])
        self.entries.append(usage)
        return usage

    @property
    def total_in(self) -> int:
        return sum(entry.tokens_in for entry in self.entries)

    @property
    def total_out(self) -> int:
        return sum(entry.tokens_out for entry in self.entries)

    @property
    def total(self) -> int:
        return self.total_in + self.total_out

    def as_dict(self) -> dict:
        return {
            "tokens_in": self.total_in,
            "tokens_out": self.total_out,
            "tokens_total": self.total,
        }

    def reset(self) -> None:
        """清空累计用量（每次 analyze 开始时调用，避免跨进程误累计）。"""
        self.entries.clear()


def token_status(used: int, budget: int = TOKEN_BUDGET) -> str:
    """根据用量返回 green / yellow / red。"""
    if used > budget:
        return "red"
    if used > budget * 0.8:
        return "yellow"
    return "green"
