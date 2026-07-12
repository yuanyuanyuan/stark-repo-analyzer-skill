# 阶段 3：项目调研

## 项目解决的核心问题

官方 README 将项目定位为：让 Claude Code 用户在已有工作流内调用 Codex 进行代码审查或任务委派（`README.md:1-6`）。具体痛点不是“再提供一个命令行客户端”，而是把两个本来独立的 agent 工作流接到同一台机器、同一份仓库和同一份本地认证状态上：

1. 用户需要只读的普通审查，以及可以质疑设计取舍的 adversarial review；项目将两者都暴露为 Claude slash command（`README.md:10-14`）。
2. 长任务不能阻塞当前交互，因此需要后台任务、状态查询、结果读取和取消；README 的第一次运行示例直接串起 `review --background`、`status`、`result`（`README.md:62-73`）。
3. Claude 会话和 Codex 会话之间存在上下文断裂，项目增加了 transfer/rescue/resume 能力，将 Claude session 导入 Codex 或继续最近的持久线程（`README.md:126-178`、`README.md:288-292`）。

从源码看，解决方案依赖本地 `codex app-server`，而不是自行实现模型调用：App Server 客户端在 `app-server.mjs:183-353` 负责直接子进程或共享 Broker 的 JSONL/Unix socket 通信；上层编排在 `codex.mjs:1002-1219` 负责 review、task、resume 和结构化输出。

## 定位与组织动机

README 的组织动机是“把 Codex 放进 Claude Code 已有工作流”，而不是替换 Claude Code 或重新包装 Codex CLI。证据包括：

- 安装方式是先把 `openai/codex-plugin-cc` 加入 Claude marketplace，再安装 `codex@openai-codex`（`README.md:22-48`）。
- FAQ 明确说插件复用本机 Codex CLI、认证状态、仓库 checkout 和环境，而不是创建独立运行时（`README.md:294-318`）。
- 项目通过 `.claude-plugin/plugin.json`、commands、hooks、agents 和 skills 组成 Claude 插件包；主运行时集中在 `plugins/codex/scripts/codex-companion.mjs`。

## 同类对比

以下只作定位层面的公开资料对比，不把外部项目的实现细节写成事实：

| 同类/替代 | 可核验定位 | 与本项目的差异 |
|---|---|---|
| 直接使用 Codex CLI/App Server | README 明确把它作为底层依赖（`README.md:267-286`） | 不提供 Claude slash command、Claude hooks、任务状态和会话导入的组合层 |
| 直接使用 Claude Code 自带命令/agent | 本项目 README 将 Claude Code 作为宿主工作流 | 宿主负责交互，Codex 负责第二审查者或被委派执行者，形成显式的跨 agent 边界 |
| `openai/codex` | 本项目 README 链接并复用 Codex app server | Codex 是执行引擎，本仓库是 Claude Code 适配层；本仓库不拥有模型/会话核心 |
| 其他 Claude/Codex 插件 | `gh search repos` 找到若干公开插件，但未逐一读取其源码 | 本次基线不做未经读取的功能或架构比较，避免把搜索结果当成事实 |

## 外部调研边界

- 已使用 `agent-reach` 的 GitHub CLI 核验公开仓库元数据：仓库为 `openai/codex-plugin-cc`，默认分支 `main`，公开描述与 README 一致；访问日期为 2026-07-12。
- 已使用 Jina Reader 读取 GitHub 页面中的官方 README 渲染内容。
- Exa 未配置，因此没有完成语义搜索；没有发现项目内 `docs/`、`CONTRIBUTING.md`、`AGENTS.md` 或架构 RFC。README 引用的 Codex 官方文档链接未在本轮独立抓取，关于底层协议的结论以当前 commit 的实现为准。
- 组织动机的更深层原因、维护者决策和历史演进在不使用 Git 历史的约束下为“待验证”。
