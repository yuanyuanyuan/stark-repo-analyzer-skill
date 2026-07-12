# 跨项目基线验证

## 验证范围

本文件是参考 skill `standard` 基线的阶段 7/8 汇总。6 个项目均使用固定 commit 的本地源码，分别写入独立目录；父流程在所有项目完成后统一检查产物、覆盖率和报告结构。

## 产物完整性

| 项目 | 产物文件数 | 最终报告 | 覆盖率文件 | 检查表 | 状态 |
|---|---:|---|---|---|---|
| `click` | 14 | 有 | 有 | 有 | 完成 |
| `httpx` | 16 | 有 | 有 | 有 | 完成 |
| `ruff` | 16 | 有 | 有 | 有 | 完成 |
| `codex-plugin-cc` | 16 | 有 | 有 | 有 | 完成 |
| `claude-code` | 21 | 有 | 有 | 有 | 完成 |
| `codex` | 16 | 有 | 有 | 有 | 完成 |

所有产物文件均未超过参考 skill 要求的 15KB；每个项目都包含研究、计划、模块、交叉验证、洞察、覆盖率、最终报告和检查表。

## 覆盖率门控

| 项目 | 核心模块结果 | 次要模块结果 | 基线判定 |
|---|---|---|---|
| `click` | 100% | 77.7% | 达标 |
| `httpx` | 100% | 100% | 达标 |
| `ruff` | CLI/config/lint/formatter 达标；parser 22.3% | semantic/LSP/ty 未达标 | 部分达标 |
| `codex-plugin-cc` | 100% | 100% | 达标 |
| `claude-code` | 加权 85.5%；task-agent 59.1% | entry/UI 23.6%；remote 未评估 | 部分达标 |
| `codex` | 31.3% | 24.3% | bounded，未达标 |

覆盖率是源码阅读覆盖率，不是测试覆盖率。大型项目采用 bounded scope 时，报告明确列出分母、已读范围和未读原因，不能将局部达标推广为全仓库达标。

## 跨项目设计模式

### 1. 领域对象是多条能力表面的共同协议

Click 用 `Command`、`Parameter`、`Context` 同时支撑解析、help、completion 和测试；HTTPX 用 `Request`、`Response`、`Transport` 连接 API、流生命周期和执行环境。两者共同说明：高质量分析应寻找“被多个功能表面共同消费的领域对象”，而不是只罗列目录。

证据：`reference-runs/click/ANALYSIS_REPORT.md` 第 4-9 节；`reference-runs/httpx/ANALYSIS_REPORT.md` 第 2-8 节。

### 2. Agent 系统围绕状态、事件、安全和扩展形成四边界

`codex` 把 Session/turn、Protocol/Event、Execution safety 和扩展注入分开；`claude-code` 把 Query loop、Tool runtime、Task/agent、Context/memory 和 Command/skill/MCP/plugin 分开；`codex-plugin-cc` 则以 Job、Broker、App Server 和 hook 生命周期把外部宿主接入 Codex。

证据：对应三个项目的最终报告第 3-8 节及 `drafts/07-cross-validation.md`。

### 3. 复杂度主要集中在边界和生命周期，不在入口数量

HTTPX 的流式 Response、Click 的 Context 资源栈、Codex 的 turn/compact/approval、Claude Code 的工具并发与任务取消，都把生命周期建模为显式状态。后续重实现应优先验证状态边界、取消、恢复和权限，而不是先追求报告文字数量。

### 4. 大型仓库必须允许有边界的诚实结果

Ruff、Claude Code 和 Codex 的结果均显示：标准模式可以形成有用的主线报告，但不必假装覆盖所有语义、平台和外围模块。参考输出基线的有效性来自“结论 + 证据 + 未读范围”三者同时存在。

## 执行编排差异

父流程实际并行启动了 6 个项目 agent；部分项目内部日志仍记录“无 Agent/subagent 工具”，这是 agent-local 运行限制，与父流程事实冲突。该差异已写入 [`reference-run-manifest.json`](./reference-run-manifest.json)，后续重实现应把“是否并行调度”作为独立元数据记录，不能仅依赖项目报告自述。

## 运行时验证缺口

- `click`：未验证 Windows、真实 Bash/Zsh/Fish、pager。
- `httpx`：未验证真实网络、HTTP/2、SOCKS、压缩 optional extras 和完整测试。
- `ruff`：未执行完整构建、测试和性能基准。
- `codex-plugin-cc`：测试通过，但未执行真实 Codex 生产任务。
- `claude-code`：缺少构建/依赖/测试配置，动态行为无法完整复现。
- `codex`：未运行 build/test，平台 sandbox、app-server 和扩展外围覆盖不足。

这些缺口不取消报告的静态参考价值，但后续比较必须区分静态架构报告与动态运行验证。
