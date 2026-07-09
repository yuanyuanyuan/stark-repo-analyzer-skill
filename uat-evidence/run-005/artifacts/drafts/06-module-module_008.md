# module_008 .github

- 文件数: 1
- 分层: minor

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`.github` 路径组，共 1 个文件。
- 分析优先级：次要模块，先轻量确认依赖和辅助职责。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `.github/workflows/release.yml`

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
| .github | 1 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`.github` 模块承担发布自动化职责：当推送 `v*` tag 时，构建 claude.ai 可上传的 `dist/watch.skill`，并将其附加到 GitHub Release（证据：`slices/07-config-scripts.xml`、`slices/04-docs.xml`、`drafts/06-module-module_008.md`）。

**设计思路**：workflow 很窄，只做 release build，不跑完整测试。它 checkout 仓库，执行 `bash skills/watch/scripts/build-skill.sh`，确认 `dist/watch.skill` 存在，再用 `softprops/action-gh-release@v2` 创建 release 并上传文件（证据：`slices/07-config-scripts.xml`）。这与 `build-skill.sh` 的“只归档 `skills/watch`、限制 200 文件、确保唯一 SKILL.md”形成发布闭环（证据：`slices/07-config-scripts.xml`）。

**关键数据流**：开发者 tag push → GitHub Actions 触发 → `build-skill.sh` 从 `HEAD:skills/watch` 生成 zip → workflow 校验 artifact → GitHub Release 附件发布 → claude.ai 用户下载 `watch.skill` 安装（证据：`slices/07-config-scripts.xml`、`slices/04-docs.xml`）。

**模块协同**：它与 module_001 的 `build-skill.sh` 紧密协同，发布产物只包含 `skills/watch`；与 root 文档协同，README/AGENTS 均说明 tag 发布流程和版本同步要求（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`、`slices/07-config-scripts.xml`）。

**架构亮点**：发布动作保持可审计和可复现：同一个本地 build 脚本既供开发者手动构建，也供 CI release 调用，避免 CI 与本地打包逻辑分叉（证据：`slices/07-config-scripts.xml`）。

**主要风险**：第一，workflow 当前证据显示只构建并上传 release artifact，未在发布前运行 pytest，因此 release tag 可能绕过测试质量门（证据：`slices/07-config-scripts.xml`、`slices/06-tests.xml`）。第二，`build-skill.sh` 要求工作树干净，但在 GitHub Actions checkout 后通常满足；本地手动发布时该约束能防止脏构建，但不能替代版本一致性检查（证据：`slices/07-config-scripts.xml`、`slices/04-docs.xml`）。第三，历史热点只有一次修改，不能判断 release workflow 是否经历过真实发布压力测试（证据：`slices/12-history-hotspot.txt`）。

