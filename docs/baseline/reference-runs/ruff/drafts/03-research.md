# Ruff 项目研究

## 研究边界

源码事实只引用固定 commit `c588a3f7f57461692652d339936222b4496c5953`。公开资料用于产品定位和同类语境，不能覆盖本地代码证据。Exa 未配置，以下外部资料来自 Jina Reader 和 GitHub API。

## 项目解决的核心问题

Ruff 面向 Python 工程团队的三个连续痛点：

1. 单个项目需要组合 Flake8、插件、isort、Black、pyupgrade 等工具，配置、进程启动和结果格式彼此割裂。仓库 README 将其定位为在一个共同接口后整合 linter、formatter 及未来工具（`README.md:40-47`）。
2. 传统 Python 工具以解释器执行，面对大型 monorepo 或保存时检查时延过高。公开文档把性能作为产品主张，并把 Rust 实现与缓存、批量文件处理放在同一价值链中（官网首页；源码层面可验证其 Rust workspace 和并行路径）。
3. 自动修复存在语义风险。Ruff 需要同时输出诊断、区分安全/不安全修复，并让 CLI 决定生成、应用、diff 或仅修复；`crates/ruff/src/lib.rs:296-319` 和 `crates/ruff_linter/src/fix/mod.rs:54-165` 直接体现这一边界。

## 定位与价值主张

- 本地 README 的直接定位是“用 Rust 编写的极快 Python linter 和 code formatter”（`README.md:12-14`）。
- 能力面不仅是单一 linter：包括 `ruff check`、`ruff format`、缓存、自动修复、层级配置、编辑器集成和 WASM/Playground 方向（`README.md:28-41,164-190`）。
- 配置层使用 `pyproject.toml`、`ruff.toml` 等生态入口；`pyproject.toml` 把 Python 包元数据与 Maturin/Rust binary 绑定到同一发布面（`pyproject.toml:1-38`）。
- 该 commit 的 workspace 仍包含 `ty`、LSP、WASM、server 等相邻能力；不能把它们简单等同为 linter 的内部实现。

## 同类对比

| 同类项目 | 主要路线 | Ruff 的差异（基于公开定位，不把未读代码写成事实） |
|---|---|---|
| Flake8 | linter 核心加插件生态 | Ruff 试图以原生规则和统一 CLI 替代多进程/多插件组合；规则兼容性是迁移资产，统一执行是架构约束。 |
| isort | Python import sorting | Ruff 将 import sorting 纳入 lint rule/修复系统，并与同一配置、诊断和缓存链协同。具体每条规则实现未逐一覆盖。 |
| Black | Python formatter | Ruff formatter 公开文档强调 Black 风格兼容和性能优先；源码拆为 Python AST formatter 与语言无关的 document/printer IR。 |
| Pylint | 更宽泛的静态检查 | Ruff 的公开目标更偏高吞吐、规则兼容和统一接口；无法仅凭当前 commit 声称两者完整功能等价。 |
| pyupgrade/autoflake | 单一变换/修复工具 | Ruff 把修复作为 linter pipeline 的一种输出模式，统一安全级别与诊断生命周期。 |

## 为什么需要单独做这个项目

如果只用现有工具组合，可以覆盖大部分功能，但每个工具都有独立配置、解析成本、进程调度和输出契约。Ruff 的独特价值不是“发明每条规则”，而是把兼容生态规则、格式化、修复、缓存、文件发现和编辑器反馈压缩进一个 Rust workspace 及共同的 source/diagnostic 抽象中。代价是维护一套大型原生实现、兼容行为和规则元数据；`CONTRIBUTING.md:133-170` 也说明了这种 monorepo 的组织成本和 crate 边界。

## 组织动机

- 当前 README 明确说 Ruff 由 Astral 支持，并与 uv、ty 同属其工具链（`README.md:60-66`）。
- GitHub API 在本次执行中返回仓库描述为 “An extremely fast Python linter and code formatter, written in Rust”，默认分支为 `main`，语言统计为 Rust；这些是仓库元数据，不是代码行为证明。
- 官网公开资料将统一工具链、性能和生态兼容作为主线。没有从当前 commit 找到足够材料证明具体商业收入、团队决策会议或历史因果，因此这些内容标为“待验证”。

## 研究结论

Ruff 的分析主线应是“高吞吐 Python 质量工具链如何把输入发现、配置解析、Python frontend、规则/修复、formatter document IR 和诊断输出串成一个可组合 CLI”。`ty` 和 LSP 是重要边界：它们体现平台化扩张，但不能为了完整性把 150k 行类型系统虚报为已覆盖。
