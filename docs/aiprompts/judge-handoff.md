# Judge 调度协议（独立只读会话）

本文件是 **Agent 调度 Judge 的内部输入协议**，不是要求用户复制或粘贴命令的模板。进入 `awaiting-judge` 后，Orchestrator 必须自行选择以下路径：

1. 优先启动当前运行时提供的独立只读 Judge 子代理；
2. 子代理能力不可用时，自动运行 `python tools/release/run-independent-judge.py --plan <plan-path>`，由它以 `codex exec --sandbox read-only` 创建临时 Judge；
3. Worker 只可将返回的固定区块原样追加到 progress，再运行控制面校验。Judge 或 Worker 都不能在这一步直接改为 `completed`。

只有 fallback 不可用、Judge 返回 `blocked`，或需要用户书面豁免时才向用户说明原因；不要把 prompt 或命令交给用户手动执行。

## 已确认的调度边界

- 除纯讨论、只读查询和不留正式交付物的临时探索外，Delivery Task 默认必须经过独立 Judge。
- 只有用户在**当前任务**中明确书面豁免时才能省略；记录豁免人、豁免范围和剩余风险。Agent 不得因为改动小自行豁免。
- Judge 只在 Worker 完成自验、准备收口时启动一次。hook 可以提醒 `awaiting-judge`，但不得在每次编辑或停止时重复创建 Judge。
- Judge 固定使用 `gpt-5.6-terra` 与 `medium` 推理等级；Judge Review 必须记录实际使用的模型和推理等级。
- `revise` 最多重审三轮。同一 major 连续两轮未解、Judge `blocked` 或第三轮仍未通过时，停止自动迭代并交由用户决定。

本文件是操作协议；默认 Judge 的权威定义、角色边界和完成门禁仍以 `CONTEXT.md` 与 `docs/dev-rules/` 为准。

## Judge 审查包（必需输入）

- 用户目标：
- 验收项：
- 启动基线：base ref / `git status --short` 摘要
- 本任务拥有的文件范围：
- 明确排除的用户已有改动：
- 配对 plan：`docs/exec-plans/…-plan.md`
- 配对 progress：`docs/exec-plans/…-progress.md`

Orchestrator 自动捕获基线和文件边界；Worker 只补充目标、验收项和实际验证。用户不承担字段填写责任。缺少任一字段时，Judge 只返回 `blocked: insufficient review package`，不得通过遍历整棵脏工作树猜测任务范围。

## Worker 自验证据

- 已跑命令：
- 退出码 / 关键结果：
- 未执行项：
- Deviations：

## Judge 必做

1. 只读审查相对基线的任务增量和本任务拥有的文件范围。
2. 至少独立执行一项与核心风险相关的验证（优先重跑针对性测试）。
3. 按 `docs/dev-rules/dual-agent-review/README.md` 输出：

```markdown
### Judge Review
- Verdict: pass | revise | blocked
- 刚性约束违规：
- 问题（按严重级别）：
- 缺失验证：
- 建议复查范围：
- 独立执行的验证及结果：
- 实际模型 / 推理等级：`gpt-5.6-terra` / `medium`
```

4. 不要把静态工件或未跑矩阵抬成真实 UAT 通过。

## 阻塞判定

只有以下情况可返回 `revise` 或 `blocked`：违反用户目标、验收项或审查包范围；可复现功能错误、数据/安全风险、控制面状态错误；任务要求但缺少验证；或审查包字段/边界无法确认。

风格偏好、可选重构、范围外发现和不影响当前验收的历史问题只能写为非阻塞建议，不能阻止 `pass`。

## 回传与收口

Judge 仅回传上面的 `### Judge Review` 区块，不写正式文件。Orchestrator/Worker 对照返回内容后原样追加至配对 progress：这是机械转录，不得改写 verdict 或补造验证。只有 `Verdict: pass`（或合格书面豁免）存在时，Worker 才能运行 `python tools/release/validate-control-plane.py --mode audit` 并考虑修改为 `completed`。
