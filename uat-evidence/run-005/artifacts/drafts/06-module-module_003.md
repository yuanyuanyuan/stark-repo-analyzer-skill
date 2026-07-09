# module_003 [root]

- 文件数: 9
- 分层: core

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`[root]` 路径组，共 9 个文件。
- 分析优先级：核心模块，必须优先核对入口、测试和对外 API。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `.gitattributes`
- `.gitignore`
- `.skillignore`
- `AGENTS.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `LICENSE`
- `README.md`
- `dev-sync.sh`

## 关键路径
- 先从模块文件清单逐个确认入口。

## 关键符号
- 未识别到公开符号

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 风险与缺口
- 缺少可见测试文件，变更该模块前应先补最小回归验证。

## 证据
- 模块 ID 来源：`05-module-ids.yaml`
- 代码切片：`slices/02-backend.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 历史热点：`slices/12-history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| [root] | 9 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：根模块是项目的产品说明、开发约束和发布协作中枢。`README.md` 面向用户解释 `/watch` 的安装、使用、限制和工作原理；`AGENTS.md` 面向 agent/维护者定义结构、宿主兼容原则和发布规则；`CLAUDE.md` 转向 `AGENTS.md` 作为 Claude 入口（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**设计思路**：根文档把产品定位明确为“slash-command-invoked skill，不是 CLI”。这会反向约束代码组织：`scripts/watch.py` 是实现细节，`skills/watch/SKILL.md` 是跨宿主 contract，`skills/watch` 必须保持自包含，不能把脚本移回 repo root（证据：`slices/05-agent-config.xml`）。README 则以用户工作流组织，从“为什么需要视频输入”到 install、first run、detail modes、limits、develop/release，形成从使用到维护的完整路径（证据：`slices/04-docs.xml`）。

**关键数据流**：根模块不处理运行时数据，但定义了安装与发布数据流：用户通过 Claude Code marketplace、Agent Skills CLI、claude.ai `.skill` bundle 或手动 symlink 安装；开发者通过 `build-skill.sh` 生成 bundle，通过 tag 触发 GitHub release（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`、`slices/07-config-scripts.xml`）。`dev-sync.sh` 的角色是把工作树同步到 Claude Code plugin cache，用于开发验证（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。

**模块协同**：根模块是所有 minor 配置模块的解释层：它说明 `.claude-plugin`、`.codex-plugin`、`.agents/plugins`、`hooks`、`.github/workflows` 各自服务的安装面和发布面（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。它也与核心 skill 模块保持版本约束：发布时需同步 `SKILL.md`、`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**架构亮点**：根文档将“跨宿主兼容性”写成硬规则，而不是隐含知识，例如禁止重引入 `${CLAUDE_SKILL_DIR}`、禁止额外 `commands/` wrapper、保持 `SKILL.md + scripts/` 同级。这类文档约束能显著降低 agent 修改时破坏安装面的概率（证据：`slices/05-agent-config.xml`）。

**主要风险**：第一，根模块承载多安装面的事实来源，版本同步依赖人工遵守；虽然文档提示同步版本，但当前证据未显示自动校验版本一致性的测试或 CI（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`、`slices/07-config-scripts.xml`）。第二，`.gitattributes`、`.gitignore`、`.skillignore` 的具体内容未在当前读取到的主要切片中展开，不能进一步判断打包排除策略是否完备（证据：`drafts/06-module-module_003.md`、`slices/04-docs.xml`）。第三，历史热点信号全部为 1 次，不能识别根文档中真正的维护热点（证据：`slices/12-history-hotspot.txt`）。

