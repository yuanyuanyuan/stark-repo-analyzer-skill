# Verification Report · Ticket 12 / PR #15

> 给人类 reviewer 的**可读证据主文档**。原始全量日志见同目录 `npm-test.full.txt` / `typecheck.full.txt`。

| 项 | 值 |
|---|---|
| 时间 | 2026-07-11 17:12 CST |
| 仓库 | stark-repo-analyzer-skill |
| 分支 | `yuanyuanyuan/v2.0-parallelism-degraded` |
| PR | https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/pull/15 |
| Issue | https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/12 |
| Node | v24.18.0 |
| npm | 11.16.0 |

---

## 1. 要证明什么（对应 AC）

| AC | 要证明的事 | 本包结论 |
|---|---|---|
| AC1 | ACCEPTANCE 从「通过」改为「部分通过」类结论 | **满足**（见 §4.1） |
| AC2 | RUN_LOG / COMPARISON 写明三模式 degraded、无多子代理 | **满足**（见 §4.2） |
| AC3 | 有验收规则：active + 分工 + 产物 + 融合才完整通过 | **满足**（SSOT 文档） |
| AC4 | 可选：重跑 multi-agent 恢复完整通过 | **未执行**（诚实 N/A） |
| AC5 | gate 不能只检查 parallelism 字段存在；degraded ≠ 通过 | **满足**（单测 + 真实工件） |

---

## 2. 命令与自动化结果

### 2.1 执行的命令

```bash
npm test
npm run typecheck
```

工作目录：业务仓库根（本 PR 分支）。

### 2.2 汇总

| 检查 | 退出码 | 结果 |
|---|---:|---|
| `npm test` | 0 | **35 pass / 0 fail** |
| `npm run typecheck` | 0 | **pass**（`node --check` bin + src） |

### 2.3 与本票直接相关的单测（必须绿）

| 用例名 | 结果 | 证明点 |
|---|---|---|
| `standard/deep gate 不把 parallelism degraded 视为多子代理执行通过` | ✔ pass | degraded → exit 3、`parallelism-execution` fail、`allowed_to_synthesize` false |
| `standard/deep gate 要求显式记录 active parallelism` | ✔ pass | 有分工/产物/融合但仍缺 `parallelism: active` → fail |
| `quick gate 允许 parallelism degraded 且不因缺少 active 而失败` | ✔ pass（本 PR 新增） | quick + degraded → parallelism pass |

### 2.4 完整 `npm test` 用例清单（35）

```text
✔ doctor 成功时生成逐项报告并允许进入分析
✔ doctor 缺少符号枚举器时阻塞并给出修复指引
✔ doctor 记录 graphify 缺失但不因此阻塞
✔ doctor 在 ctags 不支持主要语言时选择可用的 ast-grep
✔ 代表性仓库完成 v2 全链路并生成最小新旧流程对比
✔ gate 以双硬条件计算覆盖率，并按预算档决定是否放行
✔ gate 不把缺少实质判断的 analyzed 单元计入分子
✔ gate 不把非法锚点计入分子，并拒绝无行号的风险证据
✔ gate 要求 core 未覆盖单元记录 skip_reason
✔ gate 对未解析 core 文件要求报告显式声明 unsupported area
✔ gate 拒绝缺少 Why、源码锚点和 Mermaid 的空洞报告
✔ gate 在主语言实际解析质量过低时阻止 synthesis
✔ gate 不让次要语言的解析结果掩盖主语言 parse health
✔ gate 在 core 单元引用不完整比例过高时阻止 synthesis
✔ gate 拒绝缺少项目叙事、模块协作和改进建议的浅报告
✔ gate 拒绝只有模板句的完整标题报告
✔ standard gate 要求每个 core 模块至少一个有效 semantic review
✔ standard/deep gate 不把 parallelism degraded 视为多子代理执行通过
✔ quick gate 允许 parallelism degraded 且不因缺少 active 而失败
✔ standard/deep gate 要求显式记录 active parallelism
✔ quick gate 要求全局 2-3 条 semantic review，可用 analyzed unit 不足时要求全抽
✔ deep gate 要求每个 core 模块抽查全部不足 3 条的 analyzed unit
✔ standard gate 拒绝缺失、未知、非 analyzed 和重复的 semantic review
✔ standard gate 拒绝过期 anchor、过期 judgment、空 observation 和非 supported verdict
✔ test/helpers.js
✔ 发布包包含 v2 运行时且排除本机配置和测试证据
✔ scan 在 Doctor 未放行时拒绝扫描
✔ scan 不接受为其他仓库生成的 Doctor 报告
✔ scan 生成可审计的候选仓库地图
✔ summarize 稳定生成只含候选信号和待验证问题的 Markdown
✔ scan 直接从 Cargo 和 Python manifest 派生依赖
✔ units 由符号枚举器生成稳定、可审计的关键单元分母
✔ units 在 Doctor 之后枚举器失效时阻塞且不降级到正则分母
✔ units 使用 Doctor 选中的 ast-grep 枚举 JavaScript 单元
✔ units 在仅有 grep 时使用 Doctor 选中的文本搜索工具补充引用
ℹ tests 35
ℹ pass 35
ℹ fail 0
```

### 2.5 日志尾部原文

**npm test（末 20 行）**

```text
✔ test/helpers.js (95.911792ms)
✔ 发布包包含 v2 运行时且排除本机配置和测试证据 (374.100375ms)
✔ scan 在 Doctor 未放行时拒绝扫描 (278.253375ms)
✔ scan 不接受为其他仓库生成的 Doctor 报告 (2100.527666ms)
✔ scan 生成可审计的候选仓库地图 (966.026375ms)
✔ summarize 稳定生成只含候选信号和待验证问题的 Markdown (1267.155416ms)
✔ scan 直接从 Cargo 和 Python manifest 派生依赖 (944.508125ms)
✔ units 由符号枚举器生成稳定、可审计的关键单元分母 (2408.057625ms)
✔ units 在 Doctor 之后枚举器失效时阻塞且不降级到正则分母 (1245.281416ms)
✔ units 使用 Doctor 选中的 ast-grep 枚举 JavaScript 单元 (1620.569208ms)
✔ units 在仅有 grep 时使用 Doctor 选中的文本搜索工具补充引用 (1292.39ms)
ℹ tests 35
ℹ suites 0
ℹ pass 35
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 27163.432083
EXIT:0
```

**typecheck（全文）**

```text

> repo-analyzer@2.0.0 typecheck
> node --check bin/repo-analyzer.js && node --check src/*.js

EXIT:0

```

---

## 3. e2e

- **判定**: N/A
- **理由**: ticket 默认范围是验收文档 + 规则 + gate 口径收口；**不强制** AC4 完整 multi-agent 重跑。
- **替代证据**:
  1. unit 中 gate/parallelism 行为；
  2. 既有 `测试证据/v2.0/**` 真实工件 + §5；
  3. 「代表性仓库完成 v2 全链路…」用例已绿。

---

## 4. UAT（docs-only）— 文件级证据

完整勾选见 [uat-checklist.md](./uat-checklist.md)。

### 4.1 ACCEPTANCE_RESULT 总判定

路径: `测试证据/v2.0/ACCEPTANCE_RESULT.md`

```text
**部分通过：CLI/gate 工件链可运行，但报告质量与多子代理验收均未通过。**
```

限制说明中明确：

```text
- quick / standard / deep 的 Evidence Plan 均记录为 `parallelism: degraded`...
- 因此 standard/deep 不能按 v2.0 多子代理验收口径算完整通过
```

### 4.2 Evidence Plan 原文（三模式分工节）

**quick** — 允许 degraded：

```text
- parallelism: degraded，当前由主 agent 串行生成 quick 模式证据。
```

**standard** — 不得完整通过：

```text
- parallelism: degraded，当前由主 agent 串行生成 standard 模式证据。
```

**deep** — 不得完整通过：

```text
- parallelism: degraded，当前由主 agent 串行生成 deep 模式证据。
```

### 4.3 规则 SSOT

路径: `docs/specs/v2.0-multi-agent-acceptance.md`

| 模式 | degraded | 多子代理验收 |
|---|---|---|
| quick | 允许 | 不要求 |
| standard/deep | 只能部分通过/机械链路 | 必须 active + 分工 + 产物 + 融合 |

### 4.4 本地 ISSUE checkbox 状态

路径: `测试证据/v2.0/ISSUE_subagents_required_for_v2_acceptance.md`

- [x] AC1 ACCEPTANCE 修正
- [x] AC2 RUN_LOG / COMPARISON
- [x] AC3 验收规则
- [ ] AC4 可选 multi-agent 重跑（**本 PR 不做**）
- [x] AC5 gate 不只检查字段存在

---

## 5. 真实 v2.0 工件上的 gate 行为（已提交 JSON）

机器可读摘要: [gate-recheck-summary.json](./gate-recheck-summary.json)

说明：为避免「为了取证而改写」历史 `quality-gate-report.json`，摘要**读取已提交工件**，不在本步骤覆盖它们。

| 模式 | allowed_to_synthesize | parallelism-execution | 其它主要失败（工件内） |
|---|---|---|---|
| quick | false | **pass** | parse-quality / reference-quality / report-depth |
| standard | false | **fail**（degraded 等） | 同上 + parallelism |
| deep | false | **fail**（degraded 等） | 同上 + parallelism |

**解读（给 review）**:

1. 若只看「parallelism 字段在不在」——不够；standard/deep 在 degraded 时会被**显式拒绝**。
2. quick 的 parallelism pass **不等于** 整份验收完整通过（其它质量门仍可 block）。
3. 这与 ACCEPTANCE「部分通过」叙述一致。

---

## 6. 本 PR 改动与证据的关系

| 改动 | 证据角色 |
|---|---|
| `docs/specs/v2.0-multi-agent-acceptance.md` | AC3/AC5 人类可读规则 SSOT |
| README / evidence-first spec 措辞修正 | 消除「缺并行不影响通过标准」与 gate 冲突 |
| `test/gate.test.js` 新增 quick degraded 用例 | 锁定 quick vs standard/deep 差异 |
| `测试证据/v2.0/ISSUE_*.md` checkbox | 完成度可扫 |
| 历史 `src/gate.js` `parallelismExecutionCheck` | unit + 真实工件双重验证 |

---

## 7. 明确不在本证据包内的内容（避免假完成）

- **未**执行 AC4：真实 multi-agent 并行分析重跑
- **未**声称 v2.0 standard/deep「完整通过」
- **未**把 unit/typecheck 绿解释成多子代理验收通过
- **未**改写 `测试证据/v2.0/{mode}/quality-gate-report.json` 来美化数据

---

## 8. Reviewer 建议阅读顺序（约 5 分钟）

1. 本文 §1 表格 + §2.2 汇总
2. §4.2 Evidence Plan 三行 degraded
3. §5 gate 表（standard/deep fail）
4. 需要深挖时打开 `npm-test.full.txt` 与 `docs/specs/v2.0-multi-agent-acceptance.md`
5. 对照 Issue #12 AC 勾选状态（§4.4）

---

## 9. 原始日志指针

- 全量 unit: [`npm-test.full.txt`](./npm-test.full.txt)
- 全量 typecheck: [`typecheck.full.txt`](./typecheck.full.txt)
- gate 摘要 JSON: [`gate-recheck-summary.json`](./gate-recheck-summary.json)
- UAT 勾选: [`uat-checklist.md`](./uat-checklist.md)
