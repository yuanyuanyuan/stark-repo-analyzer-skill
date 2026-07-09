# 覆盖率门控

- 状态: PASS
- 核心阈值: 0.80
- 次要阈值: 0.20
- engine: regex-fallback
- tree_sitter_available: false
- tree_sitter_parsed_files: 0
- tree_sitter_queried_files: 0
- tree_sitter_query_symbols: 0
- skipped_large_files: 0

| 模块 ID | tier | 文件数 | 符号覆盖率 | 覆盖状态 |
|---|---|---:|---:|---|
| module_001 | core | 10 | 1.00 | PASS |
| module_002 | core | 10 | 1.00 | PASS |
| module_003 | core | 9 | 1.00 | PASS |
| module_004 | minor | 2 | 1.00 | PASS |
| module_005 | minor | 2 | 1.00 | PASS |
| module_006 | minor | 1 | 1.00 | PASS |
| module_007 | minor | 1 | 1.00 | PASS |
| module_008 | minor | 1 | 1.00 | PASS |

> 覆盖率门控已用确定性符号提取核对模块草稿；tree-sitter 可用时先做串行 parse 与大文件保护记录，业务语义评价可由后续 subagent 复核。
