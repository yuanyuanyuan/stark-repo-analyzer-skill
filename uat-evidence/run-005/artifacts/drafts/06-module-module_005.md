# module_005 hooks

- 文件数: 2
- 分层: minor

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`hooks` 路径组，共 2 个文件。
- 分析优先级：次要模块，先轻量确认依赖和辅助职责。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `hooks/hooks.json`
- `hooks/scripts/check-setup.sh`

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
| hooks | 2 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`hooks` 是 Claude Code 专属的运行前状态提示模块，用于 SessionStart 时检测 `/watch` 的依赖、API key 与配置权限，并在未就绪时给用户一行可执行提示（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`、`drafts/06-module-module_005.md`）。

**设计思路**：hook 的设计重点是“ready 时静默，异常时提示”。`check-setup.sh` 检查 `~/.config/watch/.env` 权限、读取 `GROQ_API_KEY`/`OPENAI_API_KEY`/`SETUP_COMPLETE`、检查 `ffmpeg` 和 `yt-dlp`，完全配置时直接 `exit 0`，否则输出安装或 key 提示（证据：`slices/07-config-scripts.xml`）。这与 `setup.py --check` 的 silent-on-success 设计保持一致（证据：`slices/07-config-scripts.xml`）。

**关键数据流**：SessionStart → hook 读取本机配置文件和 PATH → 判定二进制、API key、setup marker → 输出“需要 ffmpeg + yt-dlp”“ready for videos with native captions”“ready”等状态；真正安装仍交给 `skills/watch/scripts/setup.py`（证据：`slices/07-config-scripts.xml`）。

**模块协同**：hook 与 `setup.py/config.py` 共享同一个运行状态模型：`~/.config/watch/.env`、`SETUP_COMPLETE`、Groq/OpenAI key、ffmpeg/yt-dlp。它服务 Claude Code 安装面，但不影响 Codex/其他宿主的核心执行路径（证据：`slices/07-config-scripts.xml`、`slices/05-agent-config.xml`）。

**架构亮点**：hook 把用户体验问题前置解决：缺依赖、缺 key、权限过宽不会等到 `/watch` 执行中才失败。并且 ready 时静默，避免每次会话噪音（证据：`slices/07-config-scripts.xml`）。

**主要风险**：第一，hook 是 shell 脚本，存在平台命令差异；它用 GNU/BSD `stat` 双路径处理权限，但仍主要服务 Claude Code 本地环境（证据：`slices/07-config-scripts.xml`）。第二，hook 与 Python `setup.py` 各自实现读取 env/key 的逻辑，若未来状态字段变化，可能出现判断分叉；当前证据显示二者都读取同一 `.env` 和 key，但没有看到共享库机制（证据：`slices/07-config-scripts.xml`）。第三，当前底稿未显示 hook 的独立测试文件，测试覆盖主要集中在 Python `setup.py`（证据：`drafts/06-module-module_005.md`、`slices/06-tests.xml`）。

