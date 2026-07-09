#!/usr/bin/env python3
"""LLM-judge 执行体（stdlib-only）。

对应 ADR-0011 / ADR-0007：用 ``codex exec`` 对分析产物做
内容准确度 / 受众匹配度 / 受众区分度 评分，解析 JSON 后按阈值输出
``STATUS|name|detail`` 行，供 ``acceptance/check.sh`` 汇总。

模型选择：``DEFAULT_MODEL`` 默认为空字符串，表示使用 codex 自身配置的
默认模型；可通过环境变量 ``REPO_ANALYZER_LLM_JUDGE_MODEL`` 或 ``--model``
参数覆盖。仅当 model 非空时才向 codex 追加 ``--model`` 参数。

阈值（ADR-0011）：accuracy >= 7；jaccard >= 0.30。
- codex 未安装 / 调用失败 / JSON 无法解析：非 --strict 时 WARN，--strict 时 FAIL。
- 失败输出包含模型名与 stderr 摘要，便于定位问题。
- 正常解析且达标：输出 PASS 行。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_MODEL = os.environ.get("REPO_ANALYZER_LLM_JUDGE_MODEL", "")
ACCURACY_THRESHOLD = 7.0
JACCARD_THRESHOLD = 0.30


def _read_reports(root: Path) -> str:
    """Read analysis reports from the reports/ subdirectory.

    T08: reports moved from output root to output/reports/.
    Falls back to output root for backward compatibility.
    """
    reports_dir = root / "reports"
    if not reports_dir.is_dir():
        reports_dir = root
    chunks = []
    for name in (
        "ANALYSIS_REPORT.md",
        "ANALYSIS_REPORT.tech-lead.md",
        "ANALYSIS_REPORT.business.md",
        "ANALYSIS_REPORT.learning.md",
    ):
        path = reports_dir / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(chunks)[:12000]


def _build_prompt(report: str) -> str:
    return f"""你是独立的分析质量裁判。请基于下面的分析产物，对报告质量打分。

## 输入产物
{report}

## 要求
只输出一个 JSON 对象，不要包含任何 Markdown 围栏或额外解释：
{{
  "accuracy": <0-10 数字，内容事实准确度>,
  "audience_match": {{
    "tech-lead": <0-10>,
    "business": <0-10>,
    "learning": <0-10>
  }},
  "jaccard": <0-1 数字，三份受众报告两两内容差异度，越高越好>
}}
"""


def _parse_score(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("未找到 JSON 对象")
    return json.loads(text[start : end + 1])


def _emit(status: str, name: str, detail: str) -> None:
    print(f"{status}|{name}|{detail}")


def _extract_error_summary(stderr: str, max_len: int = 200) -> str:
    """从 codex stderr 中提取最后几行作为错误摘要。

    codex 报错时 stderr 通常包含多行调试信息，
    取最后非空行并截断到 *max_len* 字符。
    """
    if not stderr:
        return "(无 stderr 输出)"
    lines = [ln.strip() for ln in stderr.strip().splitlines() if ln.strip()]
    if not lines:
        return "(stderr 为空白)"
    summary = lines[-1]
    if len(summary) > max_len:
        summary = summary[:max_len] + "..."
    return summary


def judge(root: Path, strict: bool = False, model: str = DEFAULT_MODEL) -> None:
    codex = shutil.which("codex")
    if not codex:
        _emit("SKIP", "llm-judge:工具可用", "codex 未安装，跳过 LLM-judge")
        return
    prompt = _build_prompt(_read_reports(root))
    cmd = ["codex", "exec"]
    if model:
        cmd += ["--model", model]
    cmd += ["-", "--skip-git-repo-check"]
    model_label = model or "(codex 默认模型)"
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _emit("WARN" if not strict else "FAIL", "llm-judge:执行",
              f"codex 调用失败 [model={model_label}]: {exc}")
        return
    if proc.returncode != 0:
        err_summary = _extract_error_summary(proc.stderr)
        _emit("WARN" if not strict else "FAIL", "llm-judge:执行",
              f"codex 退出码 {proc.returncode} [model={model_label}]: {err_summary}")
        return
    try:
        data = _parse_score(proc.stdout)
        accuracy = float(data["accuracy"])
        jaccard = float(data["jaccard"])
        audience = data.get("audience_match", {})
    except (ValueError, KeyError, TypeError) as exc:
        _emit("WARN" if not strict else "FAIL", "llm-judge:解析", f"无法解析评分 JSON: {exc}")
        return
    if accuracy >= ACCURACY_THRESHOLD:
        _emit("PASS", "llm-judge:内容准确度", f"{accuracy:.1f}/10 ≥ {ACCURACY_THRESHOLD:.0f}")
    else:
        _emit("WARN" if not strict else "FAIL", "llm-judge:内容准确度", f"{accuracy:.1f}/10 < {ACCURACY_THRESHOLD:.0f}")
    parts = []
    for key in ("tech-lead", "business", "learning"):
        value = float(audience.get(key, 0))
        parts.append(f"{key} {value:.1f}")
    _emit("PASS", "llm-judge:受众匹配度", " / ".join(parts))
    if jaccard >= JACCARD_THRESHOLD:
        _emit("PASS", "llm-judge:受众区分度", f"Jaccard {jaccard:.2f} ≥ {JACCARD_THRESHOLD:.2f}")
    else:
        _emit("WARN" if not strict else "FAIL", "llm-judge:受众区分度", f"Jaccard {jaccard:.2f} < {JACCARD_THRESHOLD:.2f}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LLM-judge 评分（codex exec）")
    parser.add_argument("root", help="分析产物目录")
    parser.add_argument("--strict", action="store_true", help="阈值不达标时 FAIL 而非 WARN")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="codex 模型（默认空=使用 codex 自身默认模型）")
    args = parser.parse_args(argv)
    judge(Path(args.root).expanduser().resolve(), strict=args.strict, model=args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
