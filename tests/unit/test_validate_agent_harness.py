"""Unit tests for validate-agent-harness.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "tools" / "release" / "validate-agent-harness.py"
    spec = importlib.util.spec_from_file_location("validate_agent_harness_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = load_module()


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


MIN_MAP = """version: 1
updated: "2026-07-15"
layers: []
features:
  - id: agent-harness-navigation
    name: Agent Harness
    status: active
    summary: demo
    task_hints:
      - harness
    layers:
      control-plane:
        entrypoints:
          - AGENTS.md
      verification:
        entrypoints:
          - tools/release/validate-agent-harness.py
    watch_paths:
      - AGENTS.md
"""


class ValidateAgentHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # minimal tree for required files
        write(self.root / "AGENTS.md", "\n".join([
            "# agents",
            "docs/code-map/",
            "docs/spec/product-map.md",
            "docs/dev-rules/workflows/",
            "docs/dev-rules/agent-boundaries/",
            "validate-agent-harness",
            "docs/dev-rules/output-style/",
            "docs/dev-rules/document-control/",
            "docs/dev-rules/dual-agent-review/",
            "绿勾 ≠ ship",
            "| Judge `pass` | 真实回归 UAT |",
            "| Harness 契约校验 | Judge pass |",
            "| 安全扫描 | 真实回归 UAT |",
            "| GitHub Release | 真实回归 UAT |",
            "Judge `pass` 不等于真实回归 UAT 通过。",
            "",
        ]))
        write(self.root / "CONTEXT.md", "# ctx\n")
        write(self.root / "docs/code-map/README.md", "# map\n## 60 秒用法\n## cheat sheet\n")
        write(self.root / "docs/code-map/map.yaml", MIN_MAP)
        write(self.root / "docs/spec/product-map.md", "# pm\n边界\n场景 1\n同步规则\n")
        write(
            self.root / "docs/dev-rules/README.md",
            "# dr\nworkflows/\nagent-boundaries/\n",
        )
        write(
            self.root / "docs/dev-rules/workflows/README.md",
            "# wf\n通用骨架\n任务类型入口\nSame-Type Failure\n",
        )
        write(
            self.root / "docs/dev-rules/agent-boundaries/README.md",
            "# ab\n硬规则\n暂停条件\nSame-Type Failure\n",
        )
        write(
            self.root
            / "docs/adr/0028-agent-harness-progressive-disclosure-without-parallel-ai-harness.md",
            "# adr\n",
        )
        write(
            self.root / "docs/adr/README.md",
            "\n".join([
                "# ADR",
                "## 当前主线决策索引",
                "| Skill | [ADR-0025](0025.md) |",
                "| Harness | [ADR-0028](0028.md) |",
                "## 已接受但尚未实施",
                "当前无条目。",
                "当前主线只采用上表中的 ADR-0016 至 ADR-0019、ADR-0021 至 ADR-0028。",
                "",
            ]),
        )
        write(
            self.root / "docs/dev-rules/version-release/README.md",
            "# vr\n绿勾 ≠ ship\nJudge\nHarness\n安全扫描\nRelease\n真实回归 UAT\n",
        )
        write(
            self.root / "tools/release/validate-agent-harness.py",
            "# placeholder\n",
        )
        write(self.root / "tools/release/validate-agent-harness.py", "# placeholder\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_ok_minimal_tree(self):
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 0)

    def test_missing_file_fails(self):
        (self.root / "docs/spec/product-map.md").unlink()
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 1)

    def test_missing_agents_keyword_fails(self):
        write(self.root / "AGENTS.md", "# no routes\n")
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 1)

    def test_missing_feature_id_fails(self):
        write(
            self.root / "docs/code-map/map.yaml",
            "version: 1\nfeatures:\n  - id: other\n    status: active\n    layers: {}\n",
        )
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 1)

    def test_stale_adr_0025_pending_fails(self):
        """Regression: 0025 back under 尚未实施 + proposed must fail (not Judge/UAT)."""
        write(
            self.root / "docs/adr/README.md",
            "\n".join([
                "# ADR",
                "## 当前主线决策索引",
                "ADR-0028 only",
                "## 已接受但尚未实施",
                "| Skill 交付与安装 | ADR-0025 | 关联 roadmap/plan 均为 `proposed`，当前代码与 spec 尚未迁移 |",
                "当前主线只采用上表中的 ADR-0016 至 ADR-0019、ADR-0021 至 ADR-0024、ADR-0026 至 ADR-0027。",
                "",
            ]),
        )
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 1)

    def test_adr_index_green_path_ok(self):
        """Current-style index with 0025/0028 baseline stays green."""
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 0)

    def test_incomplete_completion_semantics_fails(self):
        """AGENTS has 绿勾 keyword but lacks required completion topics."""
        write(
            self.root / "AGENTS.md",
            "\n".join([
                "# agents",
                "docs/code-map/",
                "docs/spec/product-map.md",
                "docs/dev-rules/workflows/",
                "docs/dev-rules/agent-boundaries/",
                "validate-agent-harness",
                "docs/dev-rules/output-style/",
                "docs/dev-rules/document-control/",
                "docs/dev-rules/dual-agent-review/",
                "绿勾",
                "Judge",
                # missing Harness / 安全扫描 / Release / 真实回归 UAT
            ]),
        )
        write(self.root / "docs/dev-rules/version-release/README.md", "# empty\n")
        code = mod.main(["--root", str(self.root)])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
