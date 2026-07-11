# 测试证据 v2.1-human

> 正式测试名：**真实UAT回归测试**

本目录是 **真实UAT回归测试**（独立 `codex exec` 严格执行 skill）的默认落盘位置（规则 SSOT 见下）。

## 规则（必读）

- 仓库规则：[`docs/specs/v2.1-codex-exec-uat.md`](../../docs/specs/v2.1-codex-exec-uat.md)
- 入口引用：根目录 [`AGENTS.md`](../../AGENTS.md) →「真实UAT回归测试」
- 多子代理口径：[`docs/specs/v2.0-multi-agent-acceptance.md`](../../docs/specs/v2.0-multi-agent-acceptance.md)

## 标准命令

```bash
cd /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded

codex exec "严格执行 /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded/skills/repo-analyzer/SKILL.md 分析 /tmp/Long_screenshot_splitting_tool ，输出报告到 /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded/测试证据/v2.1-human"
```

## 本目录当前状态

- 是否已有工件：是（见 doctor/repo-map/units/evidence-plan/module-evidence/report/gate 等）
- 验收时仍须核对：是否来自**独立** `codex exec`（见 `RUN_LOG.md` / `UAT_EXEC_SUMMARY.md` 中的命令），而不是同会话 ticket 交付顺手写入
- 推荐补写：`UAT_EXEC_SUMMARY.md`（命令、时间、parallelism、gate、产物清单）

## 不算本 UAT 的目录

- `测试证据/v2.1/standard/`（同会话 degraded 实验）
- `测试证据/v2.1/standard-multiagent/`（同会话多进程实验）
- `测试证据/v2.0/pr-evidence/`（PR 文档/unit 证据）
