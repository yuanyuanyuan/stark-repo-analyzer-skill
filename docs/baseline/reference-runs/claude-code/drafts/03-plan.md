# 03 Plan

## Scale Estimate

| 指标 | 数值 | 解释 |
|---|---:|---|
| tracked files | 1,906 | 含 README、assets 和源码 |
| TypeScript/TSX files | 1,884 | 本次有效代码统计的主要对象 |
| TypeScript/TSX lines | 512,664 | 不含测试/生成代码过滤信息，因缺少配置只能作为上界 |
| largest file | `src/cli/print.ts`, 5,594 lines | 大型文件需要分段读取 |
| entry file | `src/main.tsx`, 4,683 lines | 存在大量条件 feature 和启动副作用 |

## Selected Analysis Mode

选择 `standard`。参考 skill 的目标是核心模块至少 60%、次要模块至少 30%。由于仓库没有依赖/构建元数据且规模超过 500k 行，本次把“核心用户路径”作为可审计范围，把剩余目录做外围盘点。未读部分不计入覆盖率。

## Core Modules

1. `query-loop`：请求状态、压缩、流式模型响应、tool result 回填和继续条件。
2. `tool-runtime`：Tool/ToolUseContext 契约、工具池、并发/串行执行和错误/取消。
3. `task-agent`：后台任务、子代理、coordinator 和任务输出/终止模型。
4. `command-skill`：内置命令、skill frontmatter、动态发现、条件激活和 forked skill。
5. `context-memory`：系统/用户上下文、应用状态、会话记忆和 autoDream。

## Secondary Modules

- `mcp-plugin`：MCP server 配置/连接/工具转换，插件安装/缓存/manifest。
- `permission-security`：Bash/PowerShell 解析、文件系统和 yolo/deny 规则。
- `entry-ui`：主入口、setup、REPL、Ink renderer、组件与交互界面。
- `remote-ide`：bridge、remote session、LSP、SDK entrypoint。
- `platform-services`：OAuth、API、analytics、native-ts、settings、updater、hooks 等。

## Reading Plan

核心模块优先读契约、状态转换和主流程；每个关键结论至少绑定一个源码路径和行号。次要模块只读入口和代表性实现，无法达到 30% 时在 coverage 中标记失败。

## Output Plan

- 研究和规模：`03-research.md`、`03-plan.md`。
- 业务模块与叙事：`05-modules-plan.md`。
- 逐模块证据：`06-module-*.md`。
- 交叉验证：`07-cross-validation.md`。
- 洞察与覆盖：`08-insights.md`、`08-coverage.md`。
- 单一交付报告：`ANALYSIS_REPORT.md`。
- 验收清单：`checks.md`。
