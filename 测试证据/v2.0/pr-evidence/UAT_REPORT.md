# UAT 报告 · Ticket 12 / PR #15

> **先读这三行，避免和别的文件搞混**
>
> 1. 本文件才是 **本轮 UAT 报告**。  
> 2. `测试证据/v2.0/standard/ANALYSIS_REPORT.md`、`deep/ANALYSIS_REPORT.md` **不是** UAT 报告（那是更早的架构分析草稿/历史样例）。  
> 3. 本轮 **没有**「重跑 multi-agent 分析」；本轮 UAT = **验收口径核对（docs-only）**，不是重新生成 ANALYSIS_REPORT。

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 报告类型 | **UAT（User Acceptance 核对）** · docs-only |
| 是否「重跑分析」 | **否** |
| 是否「重跑 multi-agent」 | **否**（对应 AC4，本 PR 未做） |
| 执行时间 | 2026-07-11 17:21 CST（本报告重写校正版） |
| 首次核对时间 | 2026-07-11 约 17:05–17:14 CST |
| 执行人 | agent（`uat_runner: agent`） |
| 授权 | `uat_authorized_by: session-user`（本会话用户授权 agent 代 UAT） |
| 环境 | `acceptance_env: local-cli + docs-only` |
| 物理位置 | 本机目录 `/Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded` |
| 远程 UAT 环境 | **无**（无 staging URL / 无独立 UAT 服务器） |
| 分支 / commit（写报告时） | `yuanyuanyuan/v2.0-parallelism-degraded` · 以推送后 HEAD 为准 |
| 关联 | Issue #12 · PR #15 · ticket `docs/agents/tickets/issue-12.md` |

---

## 1. UAT 测了什么（白话）

本票 UAT **只回答一个产品问题**：

> 仓库里的 v2.0 验收材料，会不会在 `parallelism: degraded`（主 agent 串行、没有多子代理）时，仍被写成或被当成「完整通过」？

因此实际动作是：

1. **打开并阅读**既有验收文档与规则文档  
2. **打开并阅读**既有三模式 Evidence Plan / quality-gate 工件  
3. **对照** Issue #12 / ticket 的 AC1–5 与 test_plan.uat 五条  
4. **记录** pass/fail 与文件锚点  

**没有**做的事：

- 没有对目标仓库再跑 `doctor → scan → … → gate → 合成 ANALYSIS_REPORT`
- 没有启动多个 subagent 做 standard/deep 模块分析（AC4）
- 没有在浏览器 / 生产 / 远程环境操作
- 没有把 `npm test` 本身叫做 UAT（那是 unit 基线，见 `VERIFICATION_REPORT.md` §2）

---

## 2. 总判定

| 维度 | 判定 |
|---|---|
| **本轮 UAT（docs-only 五条）** | **通过** |
| **v2.0 产品「完整通过」** | **未声称、也未达成**（仍为「部分通过」；且 AC4 未跑） |
| **与 unit 的关系** | unit 35/35 绿仅作基线；**不能**单独等于 UAT 通过 |

一句话：**UAT 通过 =「验收口径改对了、degraded 不会被装成完整通过」；≠「v2.0 分析已完整通过」。**

---

## 3. 逐步结果（对应 ticket test_plan.uat）

### UAT-1 · 验收文案不得把 degraded 记为多子代理完整通过

| 项 | 内容 |
|---|---|
| 操作 | 阅读 `测试证据/v2.0/ACCEPTANCE_RESULT.md` |
| 期望 | 总判定为「部分通过」或等价；明确 degraded / 无多子代理 |
| 观察到的原文 | `**部分通过：CLI/gate 工件链可运行，但报告质量与多子代理验收均未通过。**` |
| 另见 | 限制说明含「三模式 parallelism: degraded…没有实际开启多个子代理」 |
| 结果 | **PASS** |

### UAT-2 · RUN_LOG / COMPARISON 写明三模式 degraded、无多子代理

| 项 | 内容 |
|---|---|
| 操作 | 阅读 `RUN_LOG.md` §21；`COMPARISON_REPORT.md` §3/§6 |
| 期望 | 明确 quick/standard/deep 均为 degraded；无多子代理参与 |
| 观察 | RUN_LOG §21 写明三模式 degraded、串行、无多子代理；COMPARISON 总结「部分通过」 |
| 结果 | **PASS** |

### UAT-3 · 验收规则存在且覆盖分工/产物/融合与 degraded≠通过

| 项 | 内容 |
|---|---|
| 操作 | 阅读规则 SSOT 与 skill 模板 |
| 主文件 | `docs/specs/v2.0-multi-agent-acceptance.md` |
| 辅文件 | `skills/repo-analyzer/SKILL.md`、`references/evidence-first-v2.md`、ACCEPTANCE「多子代理验收规则」节 |
| 期望 | standard/deep 完整通过需 active + 分工 + 产物 + 融合；degraded 不得等价通过 |
| 结果 | **PASS** |

### UAT-4 · 既有 degraded 工件不会被标完整通过 / 允许合成

| 项 | 内容 |
|---|---|
| 操作 | 读取**已提交**的 `测试证据/v2.0/{quick,standard,deep}/quality-gate-report.json` 与对应 `evidence-plan.md`（不改写工件） |
| 期望 | standard/deep 在 degraded 下 parallelism 失败或整体不得完整通过；不得仅因字段存在就放行 |

| 模式 | Evidence Plan | parallelism-execution | allowed_to_synthesize | 其它失败（工件内） |
|---|---|---|---|---|
| quick | 含 `parallelism: degraded` | **pass**（quick 允许） | **false** | parse-quality, reference-quality, report-depth |
| standard | 含 `parallelism: degraded` | **fail** | **false** | parallelism-execution + 同上质量门 |
| deep | 含 `parallelism: degraded` | **fail** | **false** | 同上 |

standard 失败原因（工件原文）：

```text
standard 模式记录为 parallelism: degraded，不能作为多子代理执行通过。
standard 模式 Evidence Plan 必须记录 parallelism: active。
standard 模式 Evidence Plan 缺少实际子代理分工记录。
standard 模式 Evidence Plan 缺少每个子代理产物记录。
standard 模式 Evidence Plan 缺少主 agent 融合过程记录。
```

| 结果 | **PASS**（机器证据证明：degraded 不会被当成 multi-agent 通过） |

机器摘要 JSON：[`gate-recheck-summary.json`](./gate-recheck-summary.json)

### UAT-5 · 若声称完整通过必须有 multi-agent 证据；否则不得声称

| 项 | 内容 |
|---|---|
| 操作 | 检查 PR #15 正文、ACCEPTANCE 总判定、本地 ISSUE checkbox |
| 观察 | 全部维持「部分通过」；AC4 checkbox 仍为 `[ ]`；PR 声明未跑 multi-agent |
| 结果 | **PASS** |

### 基线（ticket uat 第 5 点 · 非 UAT 本体）

| 命令 | 结果 | 日志 |
|---|---|---|
| `npm test` | EXIT 0 · 35 pass | [`npm-test.full.txt`](./npm-test.full.txt) |
| `npm run typecheck` | EXIT 0 | [`typecheck.full.txt`](./typecheck.full.txt) |

> 基线绿只证明自动化未红；**产品完整通过仍依赖 AC4 等，本轮未做。**

---

## 4. 和这些文件的关系（纠错表）

| 文件 | 是不是本轮 UAT 报告 | 正确用途 |
|---|---|---|
| **本文件 `UAT_REPORT.md`** | **是** | 本轮 UAT 正式报告 |
| `uat-checklist.md` | 配套勾选底稿 | 与本报告同结论的 checklist |
| `VERIFICATION_REPORT.md` | **否（总验证包）** | unit + UAT 摘要 + AC 对照；内含 unit 细节 |
| `测试证据/v2.0/standard/ANALYSIS_REPORT.md` | **否** | 历史 standard 架构分析草稿 |
| `测试证据/v2.0/deep/ANALYSIS_REPORT.md` | **否** | 历史 deep 架构分析草稿 |
| `测试证据/v2.0/ACCEPTANCE_RESULT.md` | **否** | v2.0 总验收结论（UAT 的**输入材料**） |

---

## 5. AC 覆盖（UAT 视角）

| AC | UAT 是否覆盖 | 结论 |
|---|---|---|
| AC1 改 ACCEPTANCE 口径 | 是（UAT-1） | 已是部分通过 |
| AC2 改 RUN_LOG/COMPARISON | 是（UAT-2） | 已写 degraded |
| AC3 验收规则 | 是（UAT-3） | SSOT 存在 |
| AC4 重跑 multi-agent 恢复完整通过 | **本轮 UAT 不执行** | 诚实 N/A；checkbox 未勾 |
| AC5 gate degraded≠通过 | 是（UAT-4 + unit 辅助） | standard/deep fail parallelism |

---

## 6. 缺陷 / 风险（诚实）

1. **命名风险（已在本报告纠正）**：此前证据包主入口叫 `VERIFICATION_REPORT`，容易被理解成「重跑 UAT/重跑分析」。现以 `UAT_REPORT.md` 为 UAT 唯一主报告。  
2. **ANALYSIS_REPORT 易误读**：目录里仍有 standard/deep 分析草稿，**切勿**当 UAT 结果。  
3. **UAT 形态边界**：docs-only 不能代替「真人在完整 multi-agent 流程上点一遍」；若产品定义要求后者，需另开 AC4 会话。  

---

## 7. 签名式结论

```text
UAT 类型: docs-only 验收口径核对（agent 代跑，已授权）
UAT 结果: PASS（5/5 核对项 + 基线绿）
产品完整通过: 否（未声称；仍为部分通过；AC4 未跑）
重跑分析 / 重跑 multi-agent: 否
错误文件对照: standard|deep/ANALYSIS_REPORT.md ≠ UAT 报告
```
