# 默认 Judge 审查机制执行计划

状态：`completed`

Roadmap：[默认 Judge 审查机制 Roadmap](../roadmap/default-judge-review-roadmap.md)

进度记录：[default-judge-review-progress.md](default-judge-review-progress.md)

关键决策：[ADR-0026](../adr/0026-default-judge-with-scoped-review-package.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 定义默认 Judge 机制的实施顺序、所有权、验证与风险；不定义最终产品合同 |
| 当前状态 | `completed`；独立 Judge `Verdict: pass`（第 3 轮）；真实 UAT 未执行且非本任务前提 |
| 当前结论/入口 | 先执行 J0 合同冻结，再实现审查包与调度；不得跳过范围夹具 |
| 何时读取 | 准备修改 `docs/dev-rules/`、`.codex/hooks/` 或 Judge fallback 时 |
| 何时更新 | 任务顺序、依赖、验证方式或阻塞改变时 |
| 关联真源 | 方向见 roadmap，术语见 `CONTEXT.md`，原因见 ADR-0026，实际事实见 progress |

## 目标关

### 目标

实现默认 Judge、当前任务书面豁免、自动审查包、范围受限 verdict、固定模型/推理、一次收口调度与三轮上限。

### 非目标

- 不把用户变成 prompt 或元数据填写者。
- 不给 hook 写入 Judge 结论或状态升级权限。
- 不改变真实 UAT 的证据等级。

### 完成条件

1. 任何正式 Delivery Task 默认要求 Judge；只有当前任务的结构化用户豁免可省略。
2. Judge 缺少审查包字段时返回 `blocked: insufficient review package`，不扩大扫描。
3. 仅指定的阻塞类别可阻止收口；范围外问题是非阻塞建议。
4. 子代理或 fallback 都使用 `gpt-5.6-terra` / `medium` 并在 Review 留证。
5. 自动化与文档验证通过，独立 Judge 给出 verdict。

## 启动关

### Blindspot Pass

- 默认 Judge 可能让简单文档修改成本过高；用户书面豁免必须明确且可审计。
- 脏工作区可能导致 Judge 把无关改动作为问题；审查包必须有排除清单和启动基线。
- 子代理快照可能不是实时工作区；Judge 只读且返回后必须复核审查对象版本。
- fallback 继承用户默认模型会漂移；命令必须显式传入固定模型与推理配置。
- hook 频繁触发可能产生重复 Judge；只在 Worker 自验完成且准备收口时调度一次。

### 关键假设

| 假设 | 置信度 | 验证方式 |
|---|---|---|
| Codex 可用 `-m` 与 `-c model_reasoning_effort` 固定 fallback 配置 | 中 | 执行 `codex exec --help` 与只读 smoke |
| 当前运行时可从任务上下文得到可靠基线与拥有文件 | 中 | 以 dirty-worktree 夹具测试生成结果 |
| hook 可以注入提醒但不能安全管理异步 Judge 生命周期 | 高 | hook 事件模拟与不重复调度夹具 |

### 工作区基线

- 启动时必须记录 `git status --short`、任务拥有文件和已知用户改动。
- 本计划创建前已有的 `CONTEXT.md`、`docs/aiprompts/` 与控制面改动必须作为用户/前序改动核对，不得覆盖。
- **2026-07-14 激活基线（实施授权时）**：已有 staged/unstaged 控制面草案（roadmap/plan/progress/ADR-0026、`CONTEXT.md`、`docs/aiprompts/` 术语同步）全部纳入本任务拥有范围；无额外无关用户改动需要排除。
- **本任务拥有范围（声明）**：`docs/roadmap/default-judge-review-*`、`docs/exec-plans/default-judge-review-*`、`docs/adr/0026-*`、相关 README 索引、`CONTEXT.md`、`docs/aiprompts/judge-handoff.md`、`docs/dev-rules/{task-quality-gates,dual-agent-review,document-control}/`、`tools/release/judge_review_package.py`、`tools/release/run-independent-judge.py`、`.codex/hooks/control_plane_gate.py`（如改）、`tests/unit/test_judge_review_package.py`、审查包 artifact。

## 执行计划

### P0：冻结权威合同

- 将默认触发、豁免、审查包、阻塞标准、模型与迭代上限写入 `task-quality-gates`、`dual-agent-review` 与必要的 `document-control` 交叉引用。
- 同步 `CONTEXT.md` 与 `docs/aiprompts/judge-handoff.md`；Prompt 只能执行规则，不能成为权威规则。
- 输出：无冲突的术语、规则和操作协议。
- 验证：链接检查、规则冲突检查、文档 diff 审查。

### P1：实现审查包与调度边界

- 新增或扩展审查包生成器：捕获目标/验收、启动基线、拥有文件、排除文件、Worker 验证与阻塞标准。
- 修改 native 子代理与 `codex exec` fallback 调用，使它们接收同一审查包，并显式固定 `gpt-5.6-terra` / `medium`。
- 缺字段直接返回 `blocked: insufficient review package`；Judge 不得扫描范围外路径作为阻塞证据。
- 输出：机器可读或可验证的审查包及固定 Judge prompt。
- 验证：clean/dirty 工作区夹具、缺字段夹具、范围外发现夹具、prompt/CLI 参数断言。

### P2：更新 hook、验证和收口

- hook 仅在 Worker 标记准备收口后提示调度；继续拦截无 pass/豁免的 `completed`，不发起无限 Judge。
- 建立一次调度、三轮上限、豁免记录和已完成 plan 不误报的测试。
- 运行只读 fallback smoke、控制面校验与针对性测试；独立 Judge 审查任务增量。
- 输出：可复现证据与准确的未验证项。

## 验证合同

- Python/脚本语法与针对性测试。
- 审查包生成的 happy path、缺字段、dirty workspace、范围外路径和用户豁免用例。
- Hook 的 `PreToolUse`、`PostToolUse`、`Stop`/`SubagentStop` 模拟。
- `codex exec --sandbox read-only` fallback 的模型/推理参数和固定输出结构。
- `python tools/release/validate-control-plane.py --mode all` 与 `git diff --check`。
- 最终独立 Judge；真实 UAT 仅在产品行为受影响时按 `real-uat-regression` 另行执行。

## 失败与人工决策

- 无法可靠获得任务基线或拥有文件：停止并返回 `blocked`，不让 Judge 猜测。
- 原生子代理的运行时无法固定模型：记录实际配置并改用可固定的 fallback，或请求用户决定。
- `codex exec` 不可用：报告明确阻塞，不要求用户复制 prompt。
- 出现超出本计划的跨仓库规则改造：仅记录通用经验，另建控制面。

## 主线总结

本计划先把默认 Judge 变成可验证的范围合同，再实施调度。当前 `active`，授权修改 dev-rules、hooks 与 Judge 运行脚本。

## 收口说明

独立 Judge 第 3 轮 `Verdict: pass`。P0-P2 与验证合同已完成；真实 UAT 不在本任务范围。
