# Ruff standard 基线执行日志

## 边界

- 目标项目：`ruff`。
- 源码：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/ruff`。
- 输出：仅写入当前目录，不修改参考源码、其他基线项目或当前仓库共享文档。
- 证据基准：commit `c588a3f7f57461692652d339936222b4496c5953`，工作树在开始时为 clean。
- 不使用 Git log、diff 或历史版本推断当前实现。

## 实际过程

1. 检查源码目录存在，读取 `git rev-parse HEAD` 和 `git status --short --branch`。
2. 读取参考 `repo-analyzer` skill、`analysis-guide.md` 和 `module-analysis-guide.md`，采用 standard 的 60% 核心、30% 次要目标。
3. 扫描 README、`AGENTS.md`、`CLAUDE.md`、`CONTRIBUTING.md`、`pyproject.toml`、`Cargo.toml`、`docs/` 和 crates 目录。
4. 统计排除 tests/resources 的生产 Rust 代码：选定核心/次要范围合计约 493,612 行；完整仓库文件约 10,848 个。
5. 读取 CLI、配置发现、解析前端、语义模型、linter、formatter、LSP 和 ty 入口/核心实现；用 `nl -ba` 保留行号证据。
6. 使用 `agent-reach doctor --json` 检查互联网后端。GitHub CLI 和 Jina 可用，Exa 未配置。
7. 通过 Jina Reader 读取 Ruff 官网、linter、formatter、integrations 页面；通过 GitHub CLI 读取仓库元数据和 README。
8. 分块生成本目录的草稿、覆盖率和报告文件。

## 失败与限制

- Exa 搜索不可用：`mcporter` 返回 `Unknown MCP server 'exa'`。因此没有声称完成 Exa 的 3-5 次语义搜索，也没有把搜索结果伪装成证据。
- 运行时没有可用的 Agent/subagent 工具；参考 skill 要求每个核心模块并行 subagent，本次改为单 agent 顺序分析，并在 metadata 和本日志中记录。
- Ruff 是超大型 workspace。扫描结果中 `ruff_linter` 约 198,749 行、`ty_python_semantic` 约 152,213 行，无法在一次 standard 基线中逐行覆盖全部规则和类型系统实现。
- 外部页面是当前可访问的公开文档，可能反映站点最新内容，不等于固定 commit 的源码事实。报告只把它们用于定位/组织动机，具体实现结论以本地源码行号为准。
- 未运行完整 `cargo test`、`cargo clippy` 或构建流程：依赖、构建时间和本任务只读分析目标不适合把它们当作架构证据。未验证编译结果不能写成事实。
- 规则实现、Python formatter 的大量语法节点、AST 生成文件、ty 类型关系族和测试快照只做结构扫描或局部抽样，覆盖率表按实际读取记录，不作推断。

## 主要读取证据

| 主题 | 证据 |
|---|---|
| 产品定位与 CLI | `README.md:3-47,116-190`; `crates/ruff/src/main.rs:1-54`; `crates/ruff/src/lib.rs:1-241` |
| lint/format 调度 | `crates/ruff/src/lib.rs:243-533`; `crates/ruff/src/commands/check.rs:1-214`; `crates/ruff/src/commands/format.rs:1-760` |
| 配置与文件发现 | `crates/ruff_workspace/src/pyproject.rs:1-300`; `crates/ruff_workspace/src/resolver.rs:1-960` |
| Python 前端 | `crates/ruff_python_parser/src/lib.rs:1-624`; `parser/mod.rs` 和 `lexer.rs` 的入口、状态机及局部范围 |
| linter pipeline | `crates/ruff_linter/src/linter.rs:1-820`; `fix/mod.rs:1-420`; `checkers/logical_lines.rs:1-220` |
| formatter | `crates/ruff_formatter/src/lib.rs:1-974`; `format_element.rs:1-620`; `crates/ruff_python_formatter/src/lib.rs:1-240` |
| editor integration | `crates/ruff_server/src/server/main_loop.rs:1-300`; `session.rs:1-260`; `lint.rs:1-180`; `format.rs:1-160` |
| ty | `crates/ty/src/main.rs:1-260`; `crates/ty_project/src/db.rs:1-340`; `crates/ty_python_semantic/src/lib.rs:1-270`; `crates/ty/docs/cli.md:1-220` |

## 写入记录

所有文件按独立补丁分块写入；单个写入块控制在 300 行以内。

## 结束验证

- 结束时间：`2026-07-12T15:04:48+08:00`。
- 必需文件：全部存在，共 16 个输出文件（含 9 个 drafts 文件）。
- `metadata.json`：`jq empty` 通过。
- 文件限制：所有输出文件均不超过 300 行和 15KB。
- Mermaid：最终报告包含核心全景图，核心模块草稿也各自包含流程图。
- 源码边界：ruff HEAD 仍为 `c588a3f7f57461692652d339936222b4496c5953`，工作树仍为 clean。
- 本次变更：当前仓库仅新增 `docs/baseline/reference-runs/ruff/` 这一独立输出目录；未修改共享文档。
