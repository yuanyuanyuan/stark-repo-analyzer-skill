# v2.1-human · UAT 状态（对照规则）

规则：`docs/specs/v2.1-codex-exec-uat.md`  
AGENTS 引用：根目录 `AGENTS.md` →「UAT / codex exec」

## 当前结论

| 项 | 状态 |
|---|---|
| 目录与工件是否存在 | 是（doctor/units/plan/matrix/report/gate 等） |
| 是否已证明来自**独立** `codex exec` | **未证明**（`RUN_LOG` 写的是同环境主 agent 串行，未见独立 `codex exec` 命令与会话 ID） |
| 是否计入规则定义的 UAT 通过 | **否** — 须补跑下方命令，或补全可复核的 exec 证据后改判 |
| 产品 gate 完整通过 | 否（见已有 `quality-gate-report.json` / `ACCEPTANCE_RESULT.md`） |

## 必须补跑（用户指定形态）

```bash
cd /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded

codex exec "严格执行 /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded/skills/repo-analyzer/SKILL.md 分析 /tmp/Long_screenshot_splitting_tool ，输出报告到 /Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded/测试证据/v2.1-human"
```

exec 结束后应新增或更新：

- `UAT_EXEC_SUMMARY.md`（完整命令、开始/结束时间、exit、parallelism、gate、产物清单）
- 必要时刷新 CLI/分析工件
- 将本文件状态改为「过程通过 / 失败」并写明依据

## 已有工件的用途

在独立 exec 补齐前，目录内工件仅可作为 **预跑/对照样例**，**不得**在 PR 中写「v2.1-human UAT 已按 codex exec 规则通过」。
