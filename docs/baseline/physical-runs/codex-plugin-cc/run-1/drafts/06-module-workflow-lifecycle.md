# 模块：命令到作业、会话与审查门的生命周期

> **叙事位置。** 插件以 Claude 的 slash command 为入口，却把真正的 Codex 调用收敛在一个 Node broker 边界内。本节沿着一次人的意图追踪到可持久、可查询、可取消的 job；随后说明会话结束如何回收它，并说明为何停止动作还能被一条独立审查门阻断。下一节应转向这些公共 command/skill 契约如何把该运行时能力交付给 Claude 用户。【待主 agent 验证】

## 角色与问题

`codex-companion.mjs` 是插件的命令级编排器，而不是又一层自然语言代理：它解析 CLI，绑定工作区、模型、沙箱和状态，再把执行委托给 App Server / tracked-job 设施（导入边界见 `plugins/codex/scripts/codex-companion.mjs:9-65`）。它要解决的是 Claude 会话和长时 Codex 工作之间的错配：前者是交互轮次，后者可能在后台运行、需要跨命令查询，并且必须在 SessionEnd 被清理。

项目在这里贯彻的哲学是 **显式边界优先于隐式共享**：用户意图先变为 request/job，状态从内存提升为 workspace 派生的 JSON，结果再变为人和 JSON 都可消费的渲染输出。去掉这一层，`task --background` 没有稳定的身份、`status/result/cancel` 没有共同对象，停止钩子也无法判定还有哪些工作正在运行。

## 设计与数据结构

状态层把状态根限定为“真实路径的工作区哈希”：先 `realpath`，以目录名加 SHA-256 前 16 位隔离不同工作区，优先放入 `CLAUDE_PLUGIN_DATA/state`，否则落在系统临时目录（`lib/state.mjs:29-43`）。默认 state 是版本、`stopReviewGate` 配置和 jobs 数组（`lib/state.mjs:8-27`）；单个 job 另有 `jobs/<id>.json` 和 `.log` 文件（`lib/state.mjs:166-190`）。

从此模块实际读写字段可复原的 job 契约如下（记录创建和生命周期细节由 `tracked-jobs` 提供，故该部分是跨模块观察）：

```text
JobIndexEntry { id, kind, kindLabel, title, workspaceRoot, jobClass,
  summary, write, status, phase, pid, logFile, request?, sessionId?,
  threadId?, turnId?, completedAt?, errorMessage? }
JobFile = JobIndexEntry + { request, result?, rendered?, cancelledAt? }
```

`upsertJob` 以 id 合并并更新时间，`saveState` 按 `updatedAt` 保留最近 50 个，同时删除被淘汰 job 的 JSON 与日志（`lib/state.mjs:80-115,129-146`）。这是一个小型持久队列，而非通用数据库：它刻意买到可恢复的控制面，代价是同步覆写没有原子写入/锁，两个进程同时更新时可能出现丢失更新风险。

命令输入也保持窄边界。`parseArgs` 只识别每个子命令声明的值和布尔选项、`--` 后原样保留；未知 flag 仍作为 positional，以免通用解析器悄悄改变 prompt（`lib/args.mjs:1-74`）。单个 raw 参数会经轻量引号/反斜杠拆分（`lib/args.mjs:76-128`）。工作区优先取 Git 顶层，非 Git 则退化为 cwd（`lib/workspace.mjs:1-9`），使 task 可在普通目录执行，但 review 仍会明确拒绝非 Git 仓库（`lib/git.mjs:78-92`）。

## 主流程：从 slash command 到可见 job

```mermaid
sequenceDiagram
  participant U as Claude slash command / hook
  participant C as codex-companion
  participant S as state + job JSON/log
  participant W as foreground runner / detached worker
  participant X as Codex App Server
  participant R as status/result/cancel renderer

  U->>C: task/review + argv
  C->>C: parse options; resolve workspace; build job
  alt task --background
    C->>W: spawn detached task-worker(job id)
    C->>S: write request, queued status, PID, log
    C-->>U: job id + status hint
    W->>S: read stored request; update progress【待主 agent 验证】
  else foreground task/review
    C->>S: tracked execution + log/progress【待主 agent 验证】
  end
  W->>X: App Server turn/review
  X-->>W: status, thread/turn id, output
  W->>S: terminal result + rendered output【待主 agent 验证】
  U->>C: status/result/cancel
  C->>S: select job and persisted result
  C->>R: human Markdown or --json payload
  R-->>U: stable control-plane response
```

具体地，`task` 从 positional、`--prompt-file` 或 pipe 取 prompt，规范化 model/effort，并拒绝 `--resume` 与 `--fresh` 同用（`codex-companion.mjs:762-786`）。普通任务建立带摘要的 job；`--background` 先验证 Codex，再把 request（cwd、model、effort、prompt、write、resumeLast、jobId）写入 job，spawn 一个 `task-worker` 后立即返回（`codex-companion.mjs:788-804,604-613,671-710`）。worker 只凭 job id 重读 request，复用日志与 runner，因此父 CLI 退出不丢失工作定义（`codex-companion.mjs:838-880`）。

前台路径与后台路径在 `runForegroundCommand` / `runTrackedJob` 汇合，后者使执行结果成为 payload、rendered、exit status 的同一三元组（`codex-companion.mjs:658-669`）。task 执行默认 `read-only`，仅显式 `--write` 升为 `workspace-write`，并持久化 Codex thread；`--resume-last` 又先从本 Claude session 的终态 task 选 thread，防止续接仍在运行的任务（`codex-companion.mjs:461-529,336-355`）。这把“能修改仓库”和“能续接历史”都变成受审计的命令选择，而不是默认副作用。

review 复用同一 job 跟踪面，却有不同的业务后端：普通 Review 只允许 native 支持的 working-tree/base-branch target；Adversarial Review 采集 Git 上下文、模板化 prompt、以 `read-only` 和 schema 执行（`codex-companion.mjs:358-457,712-760`；`lib/git.mjs:135-191,300-346`）。Git 上下文会按文件数和 256 KiB diff 阈值选择 inline diff 或要求 Codex 自行只读采集，避免把大变更无界塞进 prompt（`lib/git.mjs:7-9,309-345`）。

## 结果、可见性与取消

`status` 能轮询一个 active job，也能输出当前 session 或全部作业的快照；`result` 用控制层选择 job 后读取 job 文件（`codex-companion.mjs:883-926`）。渲染层不是装饰：状态表把 job id、阶段、耗时、thread id、摘要与下一步 action 一起暴露（`lib/render.mjs:109-164,325-388`）；result 优先原始输出/结构化 review，仍附 `codex resume <thread>`，让跨 CLI 的连续性对用户可见（`lib/render.mjs:390-445`）。`--json` 则绕过 Markdown，保留同一 payload（`codex-companion.mjs:91-101`）。

取消采用两层终止：先根据存储的 thread/turn 请求 App Server interrupt，再终止本地 pid 树，最后把 job file 与索引都改成 `cancelled`（`codex-companion.mjs:963-1021`）。相较只 kill 子进程，这降低远端 Codex turn 残留概率；但两步不是事务，interrupt 成功与本地 kill/状态写入任一失败都可能留下不完全一致的控制面。

## 会话生命周期与停止审查门

SessionStart 不创建常驻服务，而是把 Claude 提供的 `session_id`、transcript path 和插件数据目录写入 Claude 环境文件（`session-lifecycle-hook.mjs:20-40,77-81`）。这让随后的命令用环境变量自动限定 jobs 与 transfer 来源；transfer 则校验 `.jsonl` 真实路径在 `~/.claude/projects` 下，拒绝任意外部文件（`lib/claude-session-transfer.mjs:20-43`），再导入成可 `codex resume` 的 thread（`codex-companion.mjs:625-640`）。

SessionEnd 是资源所有权的另一端：读取 broker session（或环境回退），先请求 broker shutdown，再找出本 session jobs，对 queued/running pid 做最佳努力 kill，移除这些 jobs，随后 teardown pid/log/session dir 并清除 broker session（`session-lifecycle-hook.mjs:42-75,83-114`）。这是“会话拥有后台工作”的明确选择；优点是不会把用户离开后的隐形进程留在机器上，代价是任务不能跨 Claude session 存活，即使其 Codex thread 已可续接。【待主 agent 验证】

Stop hook 在本 session 的 jobs 中先寻找 active 任务，作为提醒信息；配置关闭时永不阻挡退出（`stop-review-gate-hook.mjs:40-46,142-157`）。配置开启且 Codex 可用时，它同步调用 `codex-companion task --json <stop prompt>`，最多 15 分钟，把 raw 输出首行严格解析成 `ALLOW:` 或 `BLOCK:`；超时、失败、空输出、无效 JSON、未知前缀均 fail closed（`stop-review-gate-hook.mjs:48-140,159-175`）。这不是复用普通 review 命令，而是把 stop-time 审查表达为标记化 task（任务元数据由 marker 命名为 “Codex Stop Gate Review”，`codex-companion.mjs:540-554`），因此它仍纳入统一 job 可见性。注意：若 gate 未启用或 Codex 不可用，hook 仅写 stderr note 并允许结束，属于“配置时强制、不可用时可用性优先”的策略，而非绝对安全门。

## 协作、权衡与风险

| 决策 | 获得 | 代价 / 替代方案 |
| --- | --- | --- |
| 索引 state + 独立 job 文件/日志 | 查询轻、worker 可重读完整 request、结果不依赖终端 | 不如 SQLite 有事务与并发控制；同步 JSON 写入会在并行更新下脆弱。 |
| detached worker 仅接 job id | 父命令退出后仍有可追踪后台工作，参数不必重新解析 | spawn 后才写 queued record 的时间窗会使极早退出的 worker 找不到 job；源码顺序为 spawn 后写入（`codex-companion.mjs:684-698`）。 |
| 会话归属清理 + fail-closed stop parsing | 避免孤儿进程；对“审查不确定”宁可阻断，契合质量门 | 长任务不可跨 Claude session；审查可同步阻塞 15 分钟，并且 gate 未配置或 Codex 缺失时会允许退出，语义需在产品文档说清。 |

业界上，这类似 GitHub Actions 将 run id、日志与取消 API 组成控制面，也类似 IDE task runner 把工作进程和 UI session 解耦；本插件的区别是用本地 JSON 故意避免守护数据库。若要重新设计，我会先用原子 temp-rename 或 SQLite 替代 state 覆写，再在 spawn 前持久化 `queued` job，以收敛两个真实的竞态窗口。

**主要风险。** (1) `saveState` 与 `writeJobFile` 都是直接覆写，无锁/原子替换（`lib/state.mjs:92-115,166-170`）；(2) pid 复用或 kill 失败会使 SessionEnd 的“最佳努力”与实际进程偏离（`session-lifecycle-hook.mjs:59-68`）；(3) review 的 branch 上下文内部使用 Git `log` 以供产品运行时比较（`lib/git.mjs:262-289`），这只是被分析源码的行为，**本次基线分析没有执行任何 Git history 命令**。

## 覆盖率

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
| --- | ---: | ---: | ---: | --- |
| `scripts/codex-companion.mjs` | 1073 | 1073 | 100% | 无 |
| `scripts/session-lifecycle-hook.mjs` | 133 | 133 | 100% | 无 |
| `scripts/stop-review-gate-hook.mjs` | 184 | 184 | 100% | 无 |
| `scripts/lib/state.mjs` | 191 | 191 | 100% | 无 |
| `scripts/lib/render.mjs` | 465 | 465 | 100% | 无 |
| `scripts/lib/git.mjs` | 347 | 347 | 100% | 无 |
| `scripts/lib/args.mjs` | 128 | 128 | 100% | 无 |
| `scripts/lib/prompts.mjs` | 13 | 13 | 100% | 无 |
| `scripts/lib/workspace.mjs` | 9 | 9 | 100% | 无 |
| `scripts/lib/fs.mjs` | 40 | 40 | 100% | 无 |
| `scripts/lib/claude-session-transfer.mjs` | 44 | 44 | 100% | 无 |
| **合计（核心模块）** | **2627** | **2627** | **100% ✅** | **达标（standard 要求 >=60%）** |
