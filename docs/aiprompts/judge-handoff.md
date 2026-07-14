# Judge 调度协议（独立只读会话）

本文件是 **Agent 调度 Judge 的内部输入协议**，不是要求用户复制或粘贴命令的模板。进入 `awaiting-judge` 后，Orchestrator 必须自行选择以下路径：

1. 优先启动当前运行时提供的独立只读 Judge 子代理；
2. 子代理能力不可用时，自动运行 `python tools/release/run-independent-judge.py --plan <plan-path>`，由它以 `codex exec --sandbox read-only` 创建临时 Judge；
3. Worker 只可将返回的固定区块原样追加到 progress，再运行控制面校验。Judge 或 Worker 都不能在这一步直接改为 `completed`。

只有 fallback 不可用、Judge 返回 `blocked`，或需要用户书面豁免时才向用户说明原因；不要把 prompt 或命令交给用户手动执行。

## 子代理 / fallback 输入

- 用户目标：
- 质量门：完整门 | 轻量门
- 独立Judge：必须 | 可省略
- 工作区基线（`git status --short` 摘要）：
- 本轮文件范围：
- 配对 plan：`docs/exec-plans/…-plan.md`
- 配对 progress：`docs/exec-plans/…-progress.md`

## Worker 自验证据

- 已跑命令：
- 退出码 / 关键结果：
- 未执行项：
- Deviations：

## Judge 必做

1. 只读审查相对基线的任务增量。
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
```

4. 不要把静态工件或未跑矩阵抬成真实 UAT 通过。

## 回传与收口

Judge 仅回传上面的 `### Judge Review` 区块，不写正式文件。Orchestrator/Worker 对照返回内容后原样追加至配对 progress：这是机械转录，不得改写 verdict 或补造验证。只有 `Verdict: pass`（或合格书面豁免）存在时，Worker 才能运行 `python tools/release/validate-control-plane.py --mode audit` 并考虑修改为 `completed`。
