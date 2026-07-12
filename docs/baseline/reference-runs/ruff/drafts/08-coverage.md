# Ruff standard 覆盖率汇总

## 口径

有效生产 Rust 行；排除 tests、resources、快照和明显生成文件。已读是本次分析实际请求的源码行范围；重复读取不重复计数。完整仓库约 493,612 行，以下只列入已定义的业务模块范围。

## 核心模块

| 模块 | 统计范围 | 有效行 | 已读行 | 覆盖率 | standard 目标 | 状态 |
|---|---|---:|---:|---:|---:|---|
| CLI 与执行控制 | main/lib/check/resolve | 1,218 | 1,136 | 93.3% | 60% | 通过 |
| 配置与文件发现控制面 | resolver/pyproject/settings | 2,141 | 1,360 | 63.5% | 60% | 通过 |
| Lint pipeline | linter/fix/logical_lines | 1,866 | 1,425 | 76.4% | 60% | 通过 |
| Formatter document core | formatter lib/IR/formatter | 1,844 | 1,844 | 100.0% | 60% | 通过 |
| 完整 Python parser | parser src production | 19,886 | 4,443 | 22.3% | 60% | 未通过 |

## 次要模块

| 模块 | 有效行 | 已读行 | 覆盖率 | standard 目标 | 状态 |
|---|---:|---:|---:|---:|---|
| Python semantic model | 9,687 | 约 660 | 约 6.8% | 30% | 未通过 |
| Ruff LSP/server | 10,071 | 约 760 | 约 7.5% | 30% | 未通过 |
| ty project/type semantic | 162,379 | 约 600 | 约 0.4% | 30% | 未通过 |

## 解释

“Formatter document core”是语言无关的 IR/Printer 控制面，不包含约 32,032 行 Python formatter 节点后端；“完整 Python parser”明确包含未读的 expression/statement grammar，因此不能用已读的 lexer 控制面覆盖率替代。Ruff 的主要规则实现约 199k 行，同样没有被伪装成 pipeline 已覆盖。standard 基线因此是**部分达标**，适合作为后续重实现的参考输出，而不是完整源码审计。
