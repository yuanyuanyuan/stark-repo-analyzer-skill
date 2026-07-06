---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q8)
---

# ADR-0008 阶段十二开关分类：5 真开关（透传运行时）+ 5 内部变量（读 `defaults.yaml`）

## Context

PLAN.md §12 列出 ~10 个开关：

| # | Flag | 默认值 | 说明 |
|---|------|--------|------|
| 1 | `--max-context` | 90k | 阶段一 sub-agent 上下文上限 |
| 2 | `--max-history` | 30k | 阶段一 history 注入上限 |
| 3 | `--offline` | false | 离线模式（跳过外部工具调用） |
| 4 | `--max-discovery-rounds` | 5 | 阶段三最大发现轮次 |
| 5 | `--target-coverage-core` | 80% | 核心模块覆盖率阈值 |
| 6 | `--target-coverage-important` | 50% | 重要模块覆盖率阈值 |
| 7 | `--target-coverage-minor` | 20% | 次要模块覆盖率阈值 |
| 8 | `--no-question` | false | 跳过阶段三提问 |
| 9 | `--mode` | tech-lead | 报告受众 |
| 10 | `--workspace` | cwd | 工作目录 |

但以下契约缺位：

1. 这些 flag 是真传到 `repomix` / `git` / `tree-sitter` CLI，还是 skill 自己读 config 决定？
2. Claude Code / Codex CLI / Cursor 三种 runtime 的 flag 表达层（env var / argv / `.claude/settings.json` / skill YAML）支持一致吗？

而且 ADR-0001 已经砍掉阶段一 → flag 1 / flag 2 应该删掉 / 重定向到 ADR-0002 的 Phase-2a。

## Decision

**二分法落地**：

### 5 个「真开关」（透传 runtime argv）

这些 flag 真正影响运行时行为，skill 启动时读取并传给对应子系统：

| Flag | 默认值 | 传给谁 |
|------|--------|--------|
| `--offline` | `false` | 阶段三外部工具调用层 |
| `--mode` | `tech-lead` | 阶段七 renderer（从 `tech-lead` / `business` / `learning` 三选一） |
| `--no-question` | `false` | 阶段三 `ask_user()` 抽象（详见 ADR-0003） |
| `--max-discovery-rounds` | `5` | 阶段三项目特征识别循环 |
| `--workspace` | `cwd` | 全局 skill 工作目录 |

### 5 个「内部变量」（写到 `~/.config/repo-analyzer/defaults.yaml`）

这些是 skill 内部约束，**不暴露为 CLI flag**：

| 变量名 | 默认值 | 影响 |
|--------|--------|------|
| `target_coverage.core` | `0.80` | 阶段六覆盖率门控 |
| `target_coverage.important` | `0.50` | 同上 |
| `target_coverage.minor` | `0.20` | 同上 |
| `sla_budget.minutes` | `30` | 阶段八 SLA 报告（详见 ADR-0007） |
| `sla_budget.tokens` | `500000` | 同上 |

5 个内部变量在 `~/.config/repo-analyzer/defaults.yaml` 中表示：

```yaml
# repo-analyzer 内置默认值
target_coverage:
  core: 0.80
  important: 0.50
  minor: 0.20

sla_budget:
  minutes: 30
  tokens: 500000

# 用户自定义会覆盖以上默认值
```

### 砍掉的 flag

- `--max-context 90k` —— 原属阶段一，ADR-0001 砍掉阶段一后作废。Phase-2a 名片 ≤ 5KB 硬约束改写为 `analysis/02a-manifest-card.md` 文件级常量。
- `--max-history 30k` —— 同上作废。

### 命名规约

- 真开关用 kebab-case（如 `--no-question`）
- 内部变量用 snake_case + dot path（如 `target_coverage.core`）
- 真开关只读一次（启动时），运行时改不生效
- 内部变量可热更新（重启 skill 后生效）

## Alternatives

- **H1. 全部 10 个 flag 透传 argv**——表达层最简单，但运行时不支持的 flag 报错。
- **H2. 全部降到内部变量**——配置统一，但缺运行时灵活性。
- **H3. 二分（本 ADR）**——runtime 影响为 CLI，常量为文件。
- **H4. 只留 3 个核心开关**——过简化。

## Consequences

- `~/.config/repo-analyzer/defaults.yaml` 成为必须配置项，首次运行自动生成模板。
- 真开关透传需要 skill 入口解析 argv → 注入到 Phase-2a / `ask_user()` / 渲染器。
- 内部变量集中在 `defaults.yaml` 一处改，无需每次启动重传。
- §12 开关表从 ~10 行压缩为 5 真 + 5 内部 + 2 删除。
- 与 ADR-0003 的 `ask_user()` 抽象联动：`--no-question` 触发 `--no-question=true` → `ask_user()` 走默认路径。
- 与 ADR-0006 的三受众模板联动：`--mode` 触发 renderer 选 `tech-lead.tmpl.md` / `business.tmpl.md` / `learning.tmpl.md`。

## Open Questions

- [ ] 真开关与内部变量是否需要支持 `REPO_ANALYZER_*` 环境变量覆盖？（如 `REPO_ANALYZER_SLA_BUDGET_MINUTES=60`）便于 CI 中自动覆盖。
- [ ] `--max-discovery-rounds 5` 与阶段三的提问轮次（4 道题）是否冲突？前者是「特征发现」轮次，后者是「用户提问」轮次，需明确区分。
- [ ] `defaults.yaml` 是否需要支持 `extends:` 字段继承团队共享配置？

## Linked

- ADR-0001（砍 `--max-context`、`--max-history`）
- ADR-0003（`--no-question` 归属）
- ADR-0007（`sla_budget.*` 内部变量）
- 阶段十二 §12（开关表重写）
