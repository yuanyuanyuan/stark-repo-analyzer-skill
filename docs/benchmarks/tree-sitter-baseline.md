# tree-sitter 多语言 benchmark 基线

> 对应 ADR-0014。用 `scripts/benchmark_treesitter.py` 复用 `tree_sitter_scan`
> 串行扫描真实仓库，记录各语言 parse / query 性能基线。
>
> ⚠️ 当前文件为**结构完整的占位 / 部分实测基线**：默认参考仓库
> （pydantic / kubernetes / turborepo）需联网克隆才能填充真实数据；
> 本机无网络时对应行标记为「待联网补真实数据」。本地实测行由 `--repo` 传入填充。

## 方法论

- 串行遍历仓库非二进制源码文件（`iter_files`），对 `SYMBOL_SUFFIXES` 后缀文件调用 `tree-sitter parse`。
- ≥5MiB 文件按 ADR-0014 跳过（chunked），计入 `skipped_large_files`。
- 每个语言用对应 grammar query 抽取符号，记录 `parsed_files` / `queried_files` / `query_symbols`。
- 无 `tree-sitter` CLI 时自动回退 `regex-fallback`（基线会如实标注 engine）。
- 内存峰值为进程 `ru_maxrss`（macOS 字节 / Linux KB，此处统一折算 MB，近似）。

## 参考仓库基线（ADR-0014 目标集）

| 仓库 | 语言 | 总耗时(s) | 内存峰值(MB) | 跳过≥5MiB | 扫描文件 | 解析文件 | query符号 | engine | 状态 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| [pydantic](https://github.com/pydantic/pydantic) | Python | - | - | - | - | - | - | - | 待联网补真实数据 |
| [kubernetes](https://github.com/kubernetes/kubernetes) | Go | - | - | - | - | - | - | - | 待联网补真实数据 |
| [turborepo](https://github.com/vercel/turborepo) | TS-JS | - | - | - | - | - | - | - | 待联网补真实数据 |

## 本地实测（--repo 传入）

| 仓库 | 语言 | 总耗时(s) | 内存峰值(MB) | 跳过≥5MiB | 扫描文件 | 解析文件 | query符号 | engine |
|---|---|---:|---:|---:|---:|---:|---:|---|
| stark-repo-analyzer-skill | 本地 | 0.016 | 29.2 | 0 | 0 | 0 | 0 | regex-fallback |

## 复跑命令

```bash
python scripts/benchmark_treesitter.py \
  --repo /path/to/pydantic \
  --repo /path/to/kubernetes \
  --repo /path/to/turborepo
```

生成的基线将回写本文件，作为 tree-sitter 行为变动的回归阈值参考。

