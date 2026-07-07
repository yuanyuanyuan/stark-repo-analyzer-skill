---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q2)
---

# ADR-0002 Phase-2a：先识别仓库类型，再动态生成切片清单

## Context

PLAN.md §3「阶段二：12 维精细切片」写死 12 道工序（`01-frontend.xml`、`02-backend.xml`、`03-database.xml`……`12-history-hotspot.txt`），按 web 全栈隐式建模。

但在以下 repo 类型下硬套 12 维会导致严重错配或空集：

| Repo 类型 | 12 维硬套效果 |
|-----------|-------------|
| Go CLI / Python SDK / Rust crate | 8 道工序空集（无 frontend / database） |
| 单语言库 | `backend` 与 `dependencies` 互相覆盖 |
| monorepo（`vercel/turborepo`、`pnpm`） | `frontend` 命中过宽，跨子包通信是缺失的「第 13 维」 |
| 嵌入式 / 内核 | 缺「中断处理 / IPC / 启动流程」维度 |
| 多 agent 配置共存 | `05-agent-config.xml` 装不下 `.claude/**`+`.cursor/**`+`.codex/**` |

更深层问题：阶段三「项目特征识别」**在 12 维切片之后**才跑，但识别的结果**无法反馈**给切片轴线。这是流程图上**有向无环、超时 hardcoded** 的设计。

## Decision

**改为自适应切片模式**：

1. **新增 Phase-2a**（阶段二开始前的轻量级探测）：仅扫 manifest 文件 + 顶层目录树，**不读源码**，耗时 < 2 秒。
2. Phase-2a 识别出 6 种 Repo 类型之一：
   - `web-fullstack`（web 全栈）
   - `single-lang-CLI`（单语言 CLI 工具）
   - `single-lang-lib`（单语言库 / SDK）
   - `monorepo`（多包仓库）
   - `embedded-kernel`（嵌入式 / 内核 / 驱动）
   - `multi-agent-config`（多 AI agent 配置共存）

3. **类型→切片模板映射**用 YAML 表达，落地为 `config/repo-types.yaml`：
   ```yaml
   web-fullstack:
     dimensions: [frontend, backend, database, api-surface, tests,
                  agent-config, dependencies, build, error-handling,
                  i18n-a11y, performance, history-hotspot]
     dimension_count: 12
   single-lang-CLI:
     dimensions: [cli-surface, type-system, error-handling, config,
                  tests, dependencies, history-hotspot]
     dimension_count: 7
   single-lang-lib:
     dimensions: [public-api, type-system, examples, error-handling,
                  tests, dependencies, history-hotspot]
     dimension_count: 7
   monorepo:
     dimensions: [top-level-orchestrator, package-manifest,
                  inter-package-graph, shared-code, build-script,
                  tests, history-hotspot]
     dimension_count: 7
   embedded-kernel:
     dimensions: [subsystem-map, boot-flow, ipc, key-data-structures,
                  error-handling, tests, history-hotspot]
     dimension_count: 7
   multi-agent-config:
     dimensions: [claude-config, cursor-config, codex-config,
                  shared-rules, conflicts, tests, history-hotspot]
     dimension_count: 7
   ```

4. Phase-2a **同时**承担 ADR-0001 钉死的「5KB 名片」生成职责——只跑 1 次扫描，产出两份产物：
   - `analysis/02a-repo-type.yaml`（类型 + 切片清单 + dim 数）
   - `analysis/02a-manifest-card.md`（5KB 名片，纯 markdown）

5. 阶段三再以 Phase-2a 的类型声明作为输入，做**二次**特征识别（业务领域、活跃度、技术债），不重新识别 Repo 类型。

## Alternatives

- **B1. 12 维写死**——简单，但 6 类 repo 中 5 类会出 3-8 道空工序，浪费 token。
- **B2. 自适应切片（本 ADR）**——多 1 次轻量扫描，下游更准确。
- **B3. 完全 free-form**——灵活但交叉验证脚本写不出来。
- **B4. 单会话先识别再切片**——Sub-agent 上下文污染风险高，不如分两次执行。

## Consequences

- 阶段二从 1 步变 2 步，**额外加一次 Phase-2a 调用**（轻量级，仅读 manifest）。
- 阶段六交叉验证脚本需要参数化，按 `02a-repo-type.yaml` 的 `dimension_count` 字段选择不同必含字段集合。
- 报告 §9 报告骨架模板需要先读 `02a-repo-type.yaml` 选 `tech-lead.tmpl.md` / `business.tmpl.md` / `learning.tmpl.md` 各自的 dim 章节。
- §10 验收标准「12 维切片索引」改名为「N 维切片索引 + 类型 tag」。
- `config/repo-types.yaml` 需要 versioning 与 skill 版本绑定。

## Open Questions

- [ ] 单次会话内先 Phase-2a 再阶段二切片，还是必须用两次会话避免上下文污染？
- [ ] monorepo 下 ADR-0002 拟的 `inter-package-graph` 维度与 ADR-0006 三变体模板中的 `dependencies` 维度是否重叠？需要消歧。
- [ ] Phase-2a 识别错误（误判 monorepo 为单包）如何降级？需要 fallback 路径：默认按 12 维硬套并打 warning。

## Linked

- ADR-0001（5KB 名片复用 Phase-2a）
- ADR-0006（按类型选模板）
- 阶段二 §3 / 阶段三 §4 / 阶段六 §8 / 阶段七 §9
