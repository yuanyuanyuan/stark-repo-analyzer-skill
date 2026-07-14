# Repo Analyzer

一个 AI 编程 Agent 技能，用于对开源项目进行深度架构分析，生成专业级架构报告——包含设计洞察、权衡分析、Mermaid 架构图和可审计的 Graphify 结构导航增强。

正式读源码前，Agent 会检查本机是否存在兼容的 Graphify。可用时通过 code-only gate 生成并验证结构导航；缺失时只提供安装指引，由用户选择安装后复检或本次使用纯源码兼容流程。Graphify 只提供导航上下文，源码裁决冲突，所有产物都写在目标仓库之外。

正式支持运行时：[Claude Code](https://claude.ai/claude-code) 与 [Codex](https://github.com/openai/codex)。四种安装 adapter 共用同一 Skill 核心交付包；其他 Skills 兼容宿主不在正式支持矩阵内。

仓库维护性文档以中文为主；命令、标识符和专业术语保留其原始写法。

## 来源与致谢

本项目独立维护，参考并扩展了采用 MIT 许可证的 [yzddmr6/repo-analyzer](https://github.com/yzddmr6/repo-analyzer)，并加入可审计的 Graphify 导航增强。它不是上游镜像或官方关联项目，支持范围以本仓库为准。

## 相关文章

- [一键生成专业级分析报告：迭代20多轮的深度架构分析Skill，我决定开源了](https://mp.weixin.qq.com/s/sOPHFaNS8pIkhB4F-FysTQ)
- [Claude Code 源码深度架构分析](https://mp.weixin.qq.com/s/GjZ-tFBVwfJwK11F1lP5TQ)

## 快速安装

四种安装 adapter 共用 `skills/repo-analyzer/` 这一份 Skill 核心交付包。

**npx**

```bash
npx skills add yuanyuanyuan/stark-repo-analyzer-skill
```

**Claude Code 插件**

```
claude plugin marketplace add yuanyuanyuan/stark-repo-analyzer-skill
claude plugin install repo-analyzer@repo-analyzer
```

**Codex 插件**

使用仓库中的 `.codex-plugin/plugin.json` 与 `.agents/plugins/marketplace.json` 作为 Codex 安装入口：

```bash
codex plugin marketplace add yuanyuanyuan/stark-repo-analyzer-skill
codex plugin add repo-analyzer@repo-analyzer
```

安装后从 `skills/` 发现 Skill。

**手动安装**

```bash
# macOS / Linux
git clone https://github.com/yuanyuanyuan/stark-repo-analyzer-skill.git ~/.claude/skills/repo-analyzer

# Windows
git clone https://github.com/yuanyuanyuan/stark-repo-analyzer-skill.git %USERPROFILE%\.claude\skills\repo-analyzer
```

Skill 发现后的稳定 gate 调用：

```bash
python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>
```

`SKILL_ROOT` 是当前加载的 `SKILL.md` 所在目录。宿主无法解析该路径时，必须在启动 gate 前停止。

## 特性

- **架构级分析** — 聚焦"为什么这样设计"，而不是"这个文件里有什么函数"
- **自适应报告结构** — 没有固定模板，章节结构根据每个项目的特点动态生成
- **并行 Subagent 分析** — 为每个核心模块启动独立 Agent 并行分析，高效处理大型代码库
- **竞品定位** — 对比设计哲学和技术路线差异，而非功能清单
- **Mermaid 架构图** — 贯穿报告的系统架构图、数据流图和模块时序图
- **按需交互** — 标准分析默认一键执行；只有显式深度分析才在快速扫描后进行一轮集中对齐

## 使用方式

直接对 Claude Code 说：

```
分析项目 https://github.com/astral-sh/ruff
```

```
分析一下 ollama/ollama 这个仓库的架构
```

```
对比分析 express 和 fastify
```

支持 `owner/repo` 简写、GitHub/GitLab/Gitee 完整 URL、本地路径。

### 触发关键词

提到以下任意关键词时技能自动激活：

`分析项目` `分析仓库` `分析 GitHub` `项目分析` `源码分析` `架构分析` `代码分析` `学习这个项目` `研究这个框架` `看看这个库怎么实现的` `对比两个项目` `项目评测` `框架评测`

> **说明：** 默认输出中文报告。如果用其他语言提问，会跟随你的语言。

## 分析模式

未指定时直接使用标准分析；明确要求“深度分析”时进入深度模式。不提供快速模式。

| 模式 | 核心模块覆盖率 | 次要模块覆盖率 | 适用场景 |
|------|--------------|--------------|---------|
| **标准分析**（默认） | >= 60% | >= 30% | 常规架构分析 |
| **深度分析**（显式选择） | >= 90% | >= 60% | 快速扫描后集中确认一次范围与重点，再深入研究设计决策 |

## 工作流程

1. **克隆与扫描** — 克隆仓库（或使用本地路径），固定 commit 并选择分析模式
2. **Graphify 导航** — 可用时运行 code-only gate；缺失时由用户选择安装或兼容流程
3. **范围与调研** — 统计代码规模、搜索外部资料；深度模式只集中确认一次范围与重点
4. **动态报告结构** — 根据项目特点设计章节布局和模块边界
5. **并行深度分析** — 为核心模块启动 Subagent；能力不可用时先取得用户同意再顺序执行
6. **交叉验证** — 回到源码验证图谱和跨模块结论，检查代码阅读覆盖率
7. **多源融合** — 将调研、模块分析、洞察融合为连贯叙事
8. **最终报告** — 只向用户输出一份包含 Mermaid 图表的 Markdown 文件

## 报告输出

最终报告保存为单一 Markdown 文件：

```
~/repo-analyses/{项目名}-{日期}/ANALYSIS_REPORT.md
```

每份报告包含（根据项目特点调整）：

- **问题引入** — 用具体场景讲清楚项目解决什么问题、现有方案的不足
- **竞品定位** — 与同类项目的设计哲学和技术路线差异
- **项目全景** — 一览架构全貌
- **深度模块分析** — Why > What 的分析，包含权衡和业界对比
- **评价与启发** — 诚实的优缺点评估和可借鉴的设计经验
- **架构图表** — 系统全局图和各模块流程图（Mermaid）

## 可选依赖

技能可以使用 Agent 的基础源码工具完成纯源码兼容流程。Graphify `0.9.13+` 是结构导航增强依赖；Agent 不会自动安装或升级，缺失时会给出指引并等待用户选择。

以下 MCP 服务器为可选调研增强：

- [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) — 通过 `tavily_crawl` 遍历网站
- [Brave Search MCP](https://github.com/anthropics/anthropic-quickstarts/tree/main/brave-search-mcp) — 替代搜索引擎

## 文件结构

```
repo-analyzer/
├── .claude-plugin/                         # Claude 插件与 marketplace adapter
├── .codex-plugin/plugin.json               # Codex 插件 adapter
├── .agents/plugins/marketplace.json        # Codex marketplace adapter
├── skills/repo-analyzer/                   # Skill 核心交付包（唯一实现真源）
│   ├── SKILL.md
│   ├── scripts/graphify_gate.py
│   └── references/
│       ├── analysis-guide.md
│       ├── graphify-integration-guide.md
│       ├── module-analysis-guide.md
│       └── contracts/graphify-gate-status.schema.json
├── package.json                            # npx skills add 的最小 identity 文件
├── VERSION
├── CHANGELOG.md
├── README.md
├── README.zh.md
└── LICENSE
```

## 贡献

欢迎提交 Issue 和 Pull Request！

如果你想改进分析工作流，核心逻辑在 `skills/repo-analyzer/SKILL.md`。评价框架和 Subagent 模板在 `references/` 目录下。

## 许可证

[MIT](LICENSE)
