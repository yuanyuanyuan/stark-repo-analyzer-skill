# 阶段 8：覆盖率汇总

覆盖率按各 subagent 实际执行的源码读取行范围并集计算；每个模块草稿末尾均有文件级明细表。有效代码分母排除测试、文档、示例、构建配置和锁文件；空的 `py.typed` 标记文件不贡献有效行。

| 模块 | 类型 | 文件数 | 有效代码行 | 已读行数 | 覆盖率 | 达标 |
|---|---|---:|---:|---:|---:|---|
| command-model | 核心 | 4 | 4,795 | 4,795 | 100.0% | ✅ |
| parse-types | 核心 | 2 | 1,908 | 1,908 | 100.0% | ✅ |
| terminal-io | 核心 | 8 | 3,982 | 3,982 | 100.0% | ✅ |
| shell-completion | 核心 | 1 | 704 | 704 | 100.0% | ✅ |
| secondary | 次要 | 3 | 899 | 899 | 100.0% | ✅ |
| **合计** | - | **18** | **12,288** | **12,288** | **100.0%** | **全部达标✅** |

## 文件明细

| 文件 | 总行数 | 已读行数 | 覆盖率 |
|---|---:|---:|---:|
| `src/click/core.py` | 3,723 | 3,723 | 100% |
| `src/click/decorators.py` | 627 | 627 | 100% |
| `src/click/globals.py` | 67 | 67 | 100% |
| `src/click/exceptions.py` | 378 | 378 | 100% |
| `src/click/parser.py` | 533 | 533 | 100% |
| `src/click/types.py` | 1,375 | 1,375 | 100% |
| `src/click/termui.py` | 960 | 960 | 100% |
| `src/click/utils.py` | 646 | 646 | 100% |
| `src/click/formatting.py` | 320 | 320 | 100% |
| `src/click/_termui_impl.py` | 945 | 945 | 100% |
| `src/click/_compat.py` | 590 | 590 | 100% |
| `src/click/_textwrap.py` | 188 | 188 | 100% |
| `src/click/_winconsole.py` | 297 | 297 | 100% |
| `src/click/_utils.py` | 36 | 36 | 100% |
| `src/click/shell_completion.py` | 704 | 704 | 100% |
| `src/click/testing.py` | 772 | 772 | 100% |
| `src/click/__init__.py` | 127 | 127 | 100% |
| `src/click/py.typed` | 0 | 0 | N/A，空标记文件 |

行覆盖率不代表运行时行为覆盖率；本次没有运行 pytest、编译、真实 shell 或 Windows 实机验证。
