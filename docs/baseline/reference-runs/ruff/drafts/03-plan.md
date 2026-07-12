# Ruff standard 分析计划

## 规模评估

仓库是 Rust flat workspace，`Cargo.toml` 声明 `crates/*` workspace（`Cargo.toml:1-5`）。有效生产 Rust 源码扫描约 493,612 行，主要分布如下：

| 范围 | 有效行数 | 说明 |
|---|---:|---|
| `crates/ruff_linter/src` | 198,749 | 规则实现和 lint pipeline；规则文件数量巨大 |
| `crates/ty_python_semantic/src` | 152,213 | 类型语义与类型关系实现 |
| `crates/ruff_python_formatter/src` | 32,032 | Python AST 到 formatter IR 的后端 |
| `crates/ruff_python_ast/src` | 28,210 | Python AST 类型和遍历工具 |
| `crates/ruff_python_parser/src` | 20,435 | lexer/parser |
| 其他已扫描核心/支撑 crate | 62,000+ | CLI、配置、server、workspace、formatter core 等 |

## 模式和边界

- 模式：`standard`。
- 核心目标：至少 60%；次要目标：至少 30%。
- 覆盖单位：有效生产源码行。tests、resources、快照和明显生成文件排除。
- 本次将核心模块按业务数据流划分，而不是按 crate 目录机械罗列。
- 对大模块只读入口、控制流、核心数据结构和关键边界；规则全集、所有 AST 节点 formatter、ty 类型关系族不可能在本轮完整读完，必须在覆盖表中列出。

## 核心模块

1. CLI 与执行控制：输入命令、stdin/watch、退出状态、check/format 调度。
2. 项目配置与文件发现：配置优先级、项目根、include/exclude、解析后的 Settings。
3. Lint pipeline：文件并行处理、解析/规则调用、诊断聚合、cache/fix/noqa 边界。
4. Formatter document pipeline：格式规则生成中间文档、宽度/缩进上下文和 printer 输出。
5. Python parsing frontend：lexer、parse API、模块 AST 入口；预计由于 grammar 体量只能部分达标。

## 次要模块

- Python semantic model：binding/scope/reference/CFG；核心接口已读，规则消费面未全读。
- LSP/server：session、request loop、lint/format bridge；作为 CLI 之外的交互入口。
- ty type checker：新型类型检查 CLI、Salsa project DB、semantic checks；类型关系实现只做结构和入口抽样。
- diagnostics/source/cache/WASM/notebook/dev tooling：记录职责和关键边界，不展开所有实现。

## 计划覆盖

| 模块 | 目标 | 预期 | 备注 |
|---|---:|---:|---|
| CLI 与执行控制 | 60% | 达标 | 重点读取 `ruff/src/lib.rs`、check/resolve 入口 |
| 配置与文件发现 | 60% | 达标或接近 | 重点读取 resolver/pyproject/settings |
| Lint pipeline | 60% | 达标或接近 | 不逐条读取近千条规则 |
| Formatter document pipeline | 60% | 达标或接近 | 重点读取 core formatter API/IR/printer 边界 |
| Python parsing frontend | 60% | 未达标风险高 | grammar 文件规模超过本轮边界 |
| 次要模块合计 | 30% | 未达标 | ty 和语义系统规模过大，必须如实报告 |

## 报告叙事

先从“一个 CLI 统一多种 Python 质量反馈”进入，再解释配置/文件发现如何决定输入集合；随后沿数据流进入 parser、linter/formatter 两条消费路径，最后讨论诊断、缓存、watch、LSP 和 ty 如何复用或扩展平台边界。核心判断是统一接口背后并非一个巨型模块，而是多个 crate 通过 source/AST/settings/diagnostic 契约连接。
