# 阶段 3：调研记录

## 执行边界

- 目标：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/ruff`
- 固定 HEAD：`c588a3f7f57461692652d339936222b4496c5953`
- 证据来源：仓库内 `README.md`、`docs/linter.md`、`docs/formatter.md`、
  `docs/configuration.md`、`CONTRIBUTING.md`、`AGENTS.md`、`Cargo.toml`。
- 外部 Web 搜索和官网抓取：**not performed**。本物理基线仅允许指定源目录，
  且本次运行未调用网络研究工具；因此下面的竞品定位只采用仓库自述，不把它
  表述为独立验证的市场事实。
- Git 历史研究：**not performed**（用户明确禁止）。

## 核心问题与场景

1. Python 团队通常要组合 Flake8 及插件、isort、pydocstyle、pyupgrade、
   autoflake 和 Black；每个工具都有独立启动、配置和修复语义。Ruff 将这类
   检查与格式化收进 Rust 实现的统一 CLI，目标是减少工具链碎片并缩短反馈回路
   （`README.md`，`docs/linter.md`）。
2. 单体仓库的不同目录可能需要不同规则和路径解释。Ruff 以“每个文件找最近配置”
   处理配置发现，而不是隐式合并父配置；显式 `extend` 承担继承职责
   （`docs/configuration.md`）。
3. 自动修改可节省机械维护，却可能改变行为或删除注释。Ruff 区分 safe 与 unsafe
   fix，默认只应用前者（`docs/linter.md`）。

## 同类工具定位（仓库自述，非外部验证）

| 工具/路线 | Ruff 文档中的关系 | 关键差异 |
|---|---|---|
| Flake8 + 插件 | linter 的替代目标 | 将多类规则原生收进同一 Rust 引擎与规则选择模型 |
| isort / pydocstyle / pyupgrade / autoflake | linter 的替代目标 | 规则、诊断与 fix 在同一命令和配置解析中交付 |
| Black | formatter 的兼容目标 | 优先近似输出兼容与性能；不是持续混用的承诺 |
| ESLint | 配置发现的参照 | Ruff 取“最近配置”而非隐式层叠合并，显式 `extend` 才继承 |

## 为什么独立做 Ruff

仅靠把既有 Python 工具串成脚本仍保留多次启动、彼此独立的配置和修复语义。
Ruff 的独特主张是共同的命令面、配置发现和底层 Rust 实现；formatter 则选择
Black 兼容来压低迁移成本，而非要求用户接受一套新风格（`README.md`、
`docs/formatter.md`）。

## 组织与生态动机

README 将 Ruff 标为 Astral 支持的开源项目；仓库同时容纳 Ruff 和 Python 类型检查器
ty，并共享 parser 与 AST（`AGENTS.md`）。本报告只分析 Ruff 主产品路径；没有使用
外部资料验证商业策略或社区规模，相关结论不作延伸。
