"""T19: 扩展验收执行器测试（对应 T09/T10/T11/T12）。

覆盖 3 个执行器脚本在正常 / 缺失依赖下的行为：
- 04-link.sh：离线探测失败 → SKIP，不抛异常
- 05-mermaid-judge.sh：mmdc 缺失 → WARN（非 --strict）；mmdc 可用 → PASS
- llm-judge.sh → llm_judge.py：codex 缺失 → SKIP；codex 可用且达标 → PASS

执行器输出格式统一为 ``STATUS|name|detail``，供 check.sh 汇总。
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_DIR = ROOT / "acceptance"
SCRIPTS_DIR = ROOT / "scripts"


def _write_fake_mmdc(bin_dir: Path) -> Path:
    fake = bin_dir / "mmdc"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "if '-o' in args:\n"
        "    out = args[args.index('-o') + 1]\n"
        "    Path(out).write_text('<svg></svg>', encoding='utf-8')\n"
        "sys.exit(0)\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


def _write_fake_codex(bin_dir: Path, accuracy: float = 9.0, jaccard: float = 0.5) -> Path:
    fake = bin_dir / "codex"
    body = (
        "#!/usr/bin/env python3\n"
        "import sys, json\n"
        "sys.stdin.read()\n"
        "print(json.dumps({\n"
        f"  'accuracy': {accuracy},\n"
        "  'audience_match': {'tech-lead': 9, 'business': 8, 'learning': 8},\n"
        f"  'jaccard': {jaccard}\n"
        "}))\n"
    )
    fake.write_text(body, encoding="utf-8")
    fake.chmod(0o755)
    return fake


class AcceptanceExecutorsTest(unittest.TestCase):
    def setUp(self):
        self.case = Path(tempfile.mkdtemp(prefix="acceptance-test-"))
        # 复制 3 个执行器脚本到 case/acceptance
        acc = self.case / "acceptance"
        acc.mkdir()
        for name in ("04-link.sh", "05-mermaid-judge.sh", "llm-judge.sh"):
            shutil.copyfile(ACCEPTANCE_DIR / name, acc / name)
        # 复制 llm_judge.py 到 case/scripts（供 llm-judge.sh 探测）
        scripts = self.case / "scripts"
        scripts.mkdir()
        shutil.copyfile(SCRIPTS_DIR / "llm_judge.py", scripts / "llm_judge.py")
        # 报告样本：含 mermaid 块与一个外链
        reports_dir = self.case / "reports"
        reports_dir.mkdir()
        (reports_dir / "ANALYSIS_REPORT.md").write_text(
            "# 报告\n\n```mermaid\nflowchart TD\n  A-->B\n```\n\n"
            "参考 [repo](https://github.com/example/repo)\n",
            encoding="utf-8",
        )
        for name in ("tech-lead", "business", "learning"):
            (reports_dir / f"ANALYSIS_REPORT.{name}.md").write_text(
                f"# {name} 报告\n", encoding="utf-8"
            )
        self.bin = Path(tempfile.mkdtemp(prefix="fake-bin-"))
        self._saved_path = os.environ.get("PATH")

    def tearDown(self):
        shutil.rmtree(self.case, ignore_errors=True)
        shutil.rmtree(self.bin, ignore_errors=True)
        if self._saved_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = self._saved_path

    @staticmethod
    def _strip_bin(path: str, name: str) -> str:
        """从 PATH 字符串中剔除包含真实 ``name`` 二进制文件的目录，便于测试构造确定性的「依赖缺失」场景。

        仅剔除该二进制自身所在目录，不影响 python3/sh/curl 等其它工具。
        """
        real = shutil.which(name, path=path)
        if not real:
            return path
        real_dir = os.path.dirname(real)
        parts = path.split(os.pathsep)
        kept = [
            p for p in parts
            if os.path.realpath(p or "/") != os.path.realpath(real_dir)
        ]
        return os.pathsep.join(kept)

    def _env(self, with_mmdc: bool = False, with_codex: bool = False):
        if with_mmdc:
            _write_fake_mmdc(self.bin)
        if with_codex:
            _write_fake_codex(self.bin)
        env = dict(os.environ)
        path = f"{self.bin}:{os.environ.get('PATH', '')}"
        # with_codex=False 时，开发机可能自带真实 codex；剔除它以保证 llm_judge 真正走入 SKIP 分支。
        if not with_codex:
            path = self._strip_bin(path, "codex")
        env["PATH"] = path
        return env

    def _run(self, script_name, env, extra_args=None):
        cmd = ["sh", str(self.case / "acceptance" / script_name)]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    # --- 04-link.sh ---
    def test_link_offline_skips(self):
        # 离线探测失败 → SKIP；在线可达 → PASS。两种情况下脚本都不抛异常、exit 0，
        # 且输出 STATUS| 行供 check.sh 汇总。这里只断言「优雅降级 + 有 STATUS 行」。
        proc = self._run("04-link.sh", self._env())
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(
            any(line.split("|", 1)[0] in ("PASS", "SKIP") for line in proc.stdout.splitlines()),
            proc.stdout,
        )

    # --- 05-mermaid-judge.sh ---
    def test_mermaid_warn_when_mmdc_missing(self):
        proc = self._run("05-mermaid-judge.sh", self._env())
        self.assertEqual(proc.returncode, 0)
        lines = proc.stdout.splitlines()
        self.assertTrue(any(line.startswith("WARN|mermaid") for line in lines), proc.stdout)

    def test_mermaid_pass_when_mmdc_present(self):
        proc = self._run("05-mermaid-judge.sh", self._env(with_mmdc=True))
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(any(line.startswith("PASS|mermaid") for line in proc.stdout.splitlines()),
                        proc.stdout)
        self.assertTrue((self.case / "acceptance" / "panorama.svg").exists())

    def test_mermaid_strict_fails_when_mmdc_missing(self):
        proc = self._run("05-mermaid-judge.sh", self._env(), extra_args=["--strict"])
        self.assertEqual(proc.returncode, 0)  # 脚本自身 exit 0，FAIL 由 check.sh 汇总
        self.assertTrue(any(line.startswith("FAIL|mermaid") for line in proc.stdout.splitlines()),
                        proc.stdout)

    # --- llm-judge.sh ---
    def test_llm_judge_skips_when_codex_missing(self):
        proc = self._run("llm-judge.sh", self._env())
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(any(line.startswith("SKIP|llm-judge") for line in proc.stdout.splitlines()),
                        proc.stdout)

    def test_llm_judge_pass_when_codex_present(self):
        proc = self._run("llm-judge.sh", self._env(with_codex=True))
        self.assertEqual(proc.returncode, 0)
        lines = proc.stdout.splitlines()
        self.assertTrue(any(line.startswith("PASS|llm-judge:内容准确度") for line in lines), proc.stdout)
        self.assertTrue(any(line.startswith("PASS|llm-judge:受众匹配度") for line in lines), proc.stdout)
        self.assertTrue(any(line.startswith("PASS|llm-judge:受众区分度") for line in lines), proc.stdout)

    def test_llm_judge_warn_when_below_threshold(self):
        # 放置一个评分不达标的 fake codex，验证非 --strict 时 WARN 分支。
        _write_fake_codex(self.bin, accuracy=3.0, jaccard=0.1)
        env = dict(os.environ)
        env["PATH"] = f"{self.bin}:{self._strip_bin(os.environ.get('PATH', ''), 'codex')}"
        proc = self._run("llm-judge.sh", env)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(any(line.startswith("WARN|llm-judge") for line in proc.stdout.splitlines()),
                        proc.stdout)


if __name__ == "__main__":
    unittest.main()
