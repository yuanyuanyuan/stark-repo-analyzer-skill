#!/usr/bin/env python3
"""tree-sitter 多语言 benchmark（stdlib-only，复用 repo_analyzer.tree_sitter_scan）。

对应 ADR-0014：用现有 ``tree_sitter_scan`` 串行扫描真实仓库，记录各语言的
parse / query 行为与性能基线（总耗时 / 内存峰值 / chunked 跳过文件数）。

用法：
    python scripts/benchmark_treesitter.py                 # 生成参考仓库基线骨架（占位）
    python scripts/benchmark_treesitter.py --repo /path/to/py --repo /path/to/go ...

注意：默认参考仓库（pydantic / kubernetes / turborepo）需联网克隆；本沙箱
网络受限时仅生成结构完整的占位基线，并标注「需联网补真实数据」。可用
``--repo`` 传入本地仓库填充真实基线。
"""

import argparse
import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_analyzer as ra  # noqa: E402


# 默认参考仓库（ADR-0014）：Python / Go / TS-JS
DEFAULT_TARGETS = [
    ("pydantic", "Python", "https://github.com/pydantic/pydantic"),
    ("kubernetes", "Go", "https://github.com/kubernetes/kubernetes"),
    ("turborepo", "TS-JS", "https://github.com/vercel/turborepo"),
]


def _peak_rss_mb() -> float:
    try:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except Exception:
        return 0.0
    # macOS 返回字节，Linux 返回 KB
    return rss / (1024.0 * 1024.0) if sys.platform == "darwin" else rss / 1024.0


def benchmark_repo(repo_path: str) -> dict:
    repo = Path(repo_path).expanduser().resolve()
    files = sorted(ra.iter_files(repo), key=lambda p: ra.rel(p, repo))
    before = _peak_rss_mb()
    started = time.monotonic()
    _symbols, meta = ra.tree_sitter_scan(repo, files, 100_000)
    elapsed = time.monotonic() - started
    after = _peak_rss_mb()
    return {
        "path": str(repo),
        "file_count": len(files),
        "elapsed_seconds": round(elapsed, 3),
        "peak_rss_mb": round(max(after, before), 1),
        "scanned_files": meta.get("scanned_files", 0),
        "parsed_files": meta.get("parsed_files", 0),
        "queried_files": meta.get("queried_files", 0),
        "query_symbols": meta.get("query_symbols", 0),
        "skipped_large_files": len(meta.get("skipped_large_files", [])),
        "engine": meta.get("engine", ""),
        "tree_sitter_available": meta.get("tree_sitter_available", False),
        "tree_sitter_version": meta.get("tree_sitter_version", ""),
        "parse_failures": len(meta.get("parse_failures", [])),
        "query_failures": len(meta.get("query_failures", [])),
    }


def _render_doc(targets, local_results) -> str:
    lines = [
        "# tree-sitter 多语言 benchmark 基线",
        "",
        "> 对应 ADR-0014。用 `scripts/benchmark_treesitter.py` 复用 `tree_sitter_scan`",
        "> 串行扫描真实仓库，记录各语言 parse / query 性能基线。",
        ">",
        "> ⚠️ 当前文件为**结构完整的占位 / 部分实测基线**：默认参考仓库",
        "> （pydantic / kubernetes / turborepo）需联网克隆才能填充真实数据；",
        "> 本机无网络时对应行标记为「待联网补真实数据」。本地实测行由 `--repo` 传入填充。",
        "",
        "## 方法论",
        "",
        "- 串行遍历仓库非二进制源码文件（`iter_files`），对 `SYMBOL_SUFFIXES` 后缀文件调用 `tree-sitter parse`。",
        "- ≥5MiB 文件按 ADR-0014 跳过（chunked），计入 `skipped_large_files`。",
        "- 每个语言用对应 grammar query 抽取符号，记录 `parsed_files` / `queried_files` / `query_symbols`。",
        "- 无 `tree-sitter` CLI 时自动回退 `regex-fallback`（基线会如实标注 engine）。",
        "- 内存峰值为进程 `ru_maxrss`（macOS 字节 / Linux KB，此处统一折算 MB，近似）。",
        "",
        "## 参考仓库基线（ADR-0014 目标集）",
        "",
        "| 仓库 | 语言 | 总耗时(s) | 内存峰值(MB) | 跳过≥5MiB | 扫描文件 | 解析文件 | query符号 | engine | 状态 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for name, lang, url in targets:
        if name in local_results:
            r = local_results[name]
            lines.append(
                f"| [{name}]({url}) | {lang} | {r['elapsed_seconds']} | {r['peak_rss_mb']} | "
                f"{r['skipped_large_files']} | {r['scanned_files']} | {r['parsed_files']} | "
                f"{r['query_symbols']} | {r['engine']} | 实测 |"
            )
        else:
            lines.append(
                f"| [{name}]({url}) | {lang} | - | - | - | - | - | - | - | 待联网补真实数据 |"
            )
    if local_results:
        lines.extend(["", "## 本地实测（--repo 传入）", ""])
        lines.append("| 仓库 | 语言 | 总耗时(s) | 内存峰值(MB) | 跳过≥5MiB | 扫描文件 | 解析文件 | query符号 | engine |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
        for name, r in local_results.items():
            lang = "本地"
            lines.append(
                f"| {name} | {lang} | {r['elapsed_seconds']} | {r['peak_rss_mb']} | "
                f"{r['skipped_large_files']} | {r['scanned_files']} | {r['parsed_files']} | "
                f"{r['query_symbols']} | {r['engine']} |"
            )
    lines.extend([
        "",
        "## 复跑命令",
        "",
        "```bash",
        "python scripts/benchmark_treesitter.py \\",
        "  --repo /path/to/pydantic \\",
        "  --repo /path/to/kubernetes \\",
        "  --repo /path/to/turborepo",
        "```",
        "",
        "生成的基线将回写本文件，作为 tree-sitter 行为变动的回归阈值参考。",
        "",
    ])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="tree-sitter 多语言 benchmark")
    parser.add_argument("--repo", action="append", default=[], help="本地仓库路径（可多次）")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent.parent / "docs" / "benchmarks" / "tree-sitter-baseline.md"),
        help="基线文档输出路径",
    )
    args = parser.parse_args(argv)

    local_results: dict = {}
    for repo in args.repo:
        if not Path(repo).expanduser().exists():
            print(f"跳过（不存在）: {repo}", file=sys.stderr)
            continue
        name = Path(repo).expanduser().resolve().name
        print(f"benchmarking {name} ...", file=sys.stderr)
        local_results[name] = benchmark_repo(repo)
        print(json.dumps(local_results[name], ensure_ascii=False), file=sys.stderr)

    doc = _render_doc(DEFAULT_TARGETS, local_results)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc + "\n", encoding="utf-8")
    print(f"baseline written: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
