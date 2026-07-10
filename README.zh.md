# Repo Analyzer v2

一个 Evidence-First 开源仓库深度架构分析 skill。它保留原有 Why > What、设计权衡、全局关联和叙事分析，同时把证据获取、关键单元覆盖率和最终质量决定变成可审计工件。

v2 是 breaking release：工作流必须运行随包提供的 CLI，并安装 Universal Ctags 或 ast-grep 至少一个。Graphify 仍是可选增强，不是硬依赖。

**[English Documentation](README.md)**

## 安装

```bash
npx skills add yzddmr6/repo-analyzer
```

也可以把仓库克隆到 Agent 的 skills 目录。确定性 CLI 需要 Node.js 20 或更高版本。

分析前至少安装一个符号枚举器：

```bash
brew install universal-ctags
# 或按当前平台安装 ast-grep
```

## v2 变化

- Doctor 成为硬预检门：必需工具、目标语言支持或输出目录权限失败时，分析阻塞并给出修复指引。
- `scan` 不执行生态命令，确定性生成 `repo-map.json`。
- `units` 生成稳定关键单元 ID、模块分级、parsed/unparsed、引用来源和覆盖率分母。
- 每个核心模块必须同时提交机器可读的 `module-evidence/*.json` Evidence Matrix 和叙事分析。
- 单元只有同时具备 analyzed 状态、源码锚点和实质设计判断才计入覆盖率。
- `gate` 生成 `quality-gate-report.json`；缺少证据、覆盖率不足或未声明 unsupported 区域时阻止最终合成。
- 快速、标准、深度模式的核心/次要关键单元阈值分别为 30/10、60/30、90/60。
- Graphify 状态会被记录，但不可用时不阻塞 Doctor。

## CLI 命令链

Agent 会在分析过程中依次运行：

```bash
repo-analyzer doctor --repo "$REPO" --out "$WORK_DIR"
repo-analyzer scan --repo "$REPO" --out "$WORK_DIR"
repo-analyzer summarize --repo "$REPO" --out "$WORK_DIR"
repo-analyzer units --repo "$REPO" --out "$WORK_DIR"
# Agent 写入 evidence-plan.md、module-evidence/*.json 和 report.md。
repo-analyzer gate --repo "$REPO" --out "$WORK_DIR" --mode standard
```

`doctor-report.json` 的 `allowed` 不为 true 时，下游命令不能运行。`quality-gate-report.json` 的 `allowed_to_synthesize` 不为 true 时，不能生成最终报告。

## 生成工件

| 工件 | 用途 |
|---|---|
| `doctor-report.json` | 预检逐项状态、修复指引和放行决定 |
| `repo-map.json` | 文件、语言、manifest、依赖、候选信号和排除范围 |
| `repo-map.md` | 面向模型的候选摘要、来源与待验证问题 |
| `coverage-units.json` | 稳定关键单元、模块分级、引用、解析率和覆盖状态 |
| `evidence-plan.md` | 架构问题、候选证据、分工与预算 |
| `module-evidence/*.json` | 每个核心模块的机器可读 Evidence Matrix |
| `report.md` | 包含开放问题和 Unsupported Area 的叙事草稿 |
| `quality-gate-report.json` | 机械质量门结果与最终合成决定 |

## 分析哲学

确定性工具只能识别候选，不能产出最终架构结论。每个重要判断仍须由源码锚点、项目文档或外部一手来源验证。最终报告继续解释设计动机、权衡、替代方案、跨模块协同、风险和可借鉴经验，不能退化成目录或符号清单。

运行时没有 subagent 时，主 Agent 串行执行，并在 Evidence Plan 中记录 `parallelism: degraded`；证据、覆盖率和质量门要求不降低。

## 使用方式

直接向编程 Agent 提问：

```text
分析项目 https://github.com/astral-sh/ruff
分析一下 ollama/ollama 这个仓库的架构
对比分析 express 和 fastify
```

支持本地路径、GitHub/GitLab/Gitee 完整 URL 和 `owner/repo` 简写。默认输出中文报告。

## 开发验证

```bash
npm test
npm run typecheck
npm pack --dry-run
```

发布包只包含 CLI 运行时、skill、用户文档、变更日志和许可证；维护者本机 hook、绝对路径、测试证据和 Graphify hook 配置不会发布。

## 许可证

[MIT](LICENSE)
