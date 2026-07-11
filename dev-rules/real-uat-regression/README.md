# 真实UAT回归测试规则（dev-rules）

- **正式名称**：**真实UAT回归测试**
- **标签**：`real-uat-regression` · `codex-exec-skill-uat`
- **更新时间**：2026-07-11
- **本目录角色**：dev 可执行回归矩阵（按模式分档）的 **SSOT 入口**
- **关联产品规则**：[`docs/specs/v2.1-codex-exec-uat.md`](../../docs/specs/v2.1-codex-exec-uat.md)（独立 `codex exec` 定义与过程/产品分层）
- **关联多子代理口径**：[`docs/specs/v2.0-multi-agent-acceptance.md`](../../docs/specs/v2.0-multi-agent-acceptance.md)
- **Skill**：[`skills/repo-analyzer/SKILL.md`](../../skills/repo-analyzer/SKILL.md)

## 0. 什么是真实UAT回归测试

**默认定义**（与 `AGENTS.md` 一致）：

> **新开独立 `codex exec` 进程**，提示词要求 **严格执行** 仓库内 `skills/repo-analyzer/SKILL.md`，对 **真实目标仓** 做分析，并把工件输出到本仓 `测试证据/` 下 **新建** 目录。

下列 **不等于** 真实UAT回归测试：

- 同会话 docs-only 勾选 / 手写 report
- 仅 `node bin/repo-analyzer.js …` 机械链路而无 agent 按 skill 完整跑
- 仅 `npm test` / typecheck
- 同会话 multi-agent 实验（有价值，但不计入本正式名称）

## 1. 三档回归（必须按模式分开跑、分开记）

| 档位 | 规则文件 | 推荐输出目录 | 覆盖率/预算语义（skill） | 多子代理期望 |
|------|----------|--------------|-------------------------|--------------|
| **quick** | [quick.md](quick.md) | `测试证据/real-uat-quick-<YYYYMMDD>/` | 核心 30% / 次要 10%；unparsed 补读全局约 3–5 高影响 | 允许 `parallelism: degraded` |
| **standard** | [standard.md](standard.md) | `测试证据/real-uat-standard-<YYYYMMDD>/` | 核心 60% / 次要 30%；unparsed 主路径相关子集 | **目标** `active`；不支持则 `degraded` 且不得称 multi-agent 完整通过 |
| **deep** | [deep.md](deep.md) | `测试证据/real-uat-deep-<YYYYMMDD>/` | 核心 90% / 次要 60%；unparsed 更高比例 | 同 standard，要求更严的证据深度 |

**禁止**用一次 quick 结果声称 standard/deep 已回归；**禁止**三档共用同一输出目录互相覆盖。

## 2. 公共强制形态

### 2.1 命令骨架

```bash
# 在业务仓库根目录
SKILL="$(pwd)/skills/repo-analyzer/SKILL.md"
REPO="${REPO:-/tmp/Long_screenshot_splitting_tool}"   # 或用户指定真实仓
OUT="$(pwd)/测试证据/real-uat-<mode>-$(date +%Y%m%d)" # mode=quick|standard|deep
mkdir -p "$OUT"

codex exec --skip-git-repo-check \
  "严格执行 $SKILL 分析 $REPO ，输出报告到 $OUT

模式：必须按 <mode> 执行（quick|standard|deep），不得静默降档。
约束见 dev-rules/real-uat-regression/<mode>.md 与 docs/specs/v2.1-codex-exec-uat.md。"
```

各档完整提示词与检查清单见对应 `quick.md` / `standard.md` / `deep.md`。

### 2.2 公共硬性要求

1. **独立进程** `codex exec`（或等价非交互 exec）。
2. 提示词含 **「严格执行」** + skill **绝对路径**。
3. **真实目标仓**（默认 `/tmp/Long_screenshot_splitting_tool`）；禁止只对 fixture 冒充真实UAT。
4. **新建** `$OUT`，不覆盖历史 `测试证据/` 轮次。
5. **诚实并行**：支持 subagent 则 standard/deep 应力争 `parallelism: active` + 分工/产物/融合；不支持则写 `degraded`，**不得**标 multi-agent 完整通过。
6. **不绕过 gate**：`allowed_to_synthesize: false` 时禁止伪造成品 `ANALYSIS_REPORT.md`。
7. **core unparsed 非空** 时必须 **Unparsed File Read Pass**，落盘 `unparsed-file-reviews*` 和/或 `module-evidence.unparsed_manual_reads`；报告对高影响 unparsed 写 **manual-read** 锚点；**禁止**只列 Unsupported 路径；**禁止**把补读写成 parse_rate 提升或 analyzed unit。
8. 结束后在 `$OUT/UAT_EXEC_SUMMARY.md` 用中文写：命令、时间、**模式**、parallelism、gate、产物、unparsed 补读、结论分层。

### 2.3 两层结论（必须分开写）

| 层级 | 含义 | 可否单独成立 |
|------|------|----------------|
| **过程有效** | 独立 exec + 走 skill + 关键工件 + 诚实 parallelism/补读记录 | 可以（例如 gate 因目标仓 parse_rate 失败） |
| **产品分析完整通过** | `allowed_to_synthesize: true` + 最终报告（及该模式完整验收条件） | 更严；失败时不得对外写「分析完整通过」 |
| **多子代理完整通过**（standard/deep） | `parallelism: active` + 分工/产物/融合（见 v2.0 规则） | 与上两者独立；degraded 时明确「未通过」 |

允许写法：

> 真实UAT回归测试（standard）**过程有效**；产品分析未完整通过（原因：…）；多子代理验收未通过（degraded）。

## 3. 变更联动（强制）

当下列任一变化时，**必须**同步审阅并更新本目录规则（含三档 md 中的预算、检查项、命令、期望结论）：

- `skills/repo-analyzer/**` 工作流、模式预算、Unparsed File Read Pass、禁止事项
- `src/gate.js` 及测试所表达的质量门语义
- `docs/specs/v2.1-codex-exec-uat.md` / `v2.0-multi-agent-acceptance.md`
- 影响验收的需求、Issue、ticket、PR 范围说明
- 默认样例目标仓或证据目录约定变更

PR 检查清单（建议勾选）：

- [ ] 实现变更是否改变 UAT 可观察行为？
- [ ] 若是：已更新 `dev-rules/real-uat-regression/` 对应档
- [ ] `AGENTS.md` 链接仍指向本目录
- [ ] 若跑了真实UAT：证据目录与 `UAT_EXEC_SUMMARY.md` 已按新规则记录

## 4. 与历史证据目录的关系

| 目录 | 角色 |
|------|------|
| `测试证据/v2.1-human/` 等 | 历史/人工轮次 |
| `测试证据/v2.1-unparsed-read/` | ticket 16 等专项真实UAT |
| `测试证据/real-uat-{quick,standard,deep}-*` | **本规则推荐的新分档落盘** |

历史目录仍有效作对照，但新回归优先使用本规则命名。
