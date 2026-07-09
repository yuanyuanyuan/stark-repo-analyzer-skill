---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q1)
---

# ADR-0001 砍掉阶段一压缩 repomix，改在 Phase-2a 顺手产 5KB 名片

## Context

PLAN.md §2「阶段一：宏观认知建模」用 `repomix --ignore` 压缩仓库并丢弃以下 3 类关键信号：

- `*.lock` —— 锁文件，记录依赖锁定范围与版本基线
- `.claude/**`、`.codex/**`、`.cursor/**` —— AI agent 内部配置
- `AGENTS.md`、`CLAUDE.md` —— Agent 操作守则

阶段二 §3 又以 `--include` 例外放行，把这 3 类捞回来。这意味着阶段一 sub-agent 拿到的「宏观 overview」**信号残缺**，而下游 §3 / §4 / §7 又**强依赖**这些被阶段一过滤掉的信号。

直接砍阶段一的成本是主 sub-agent 在协调 12 维精切时**心里没底**：「这家公司大概是做什么的？」

## Decision

**砍掉阶段一的 repomix 压缩 + 4+1 sub-agent 宏观调用**，**复用 ADR-0002 已拟的 Phase-2a** 顺手产出一份**5KB 名片级项目 manifest**，定位为元信息快查锚点而非压缩摘要。

具体规则：

1. Phase-2a 在阶段二开始前执行一次**轻量级、不压缩**的 manifest 扫描，源文件直读，耗时 < 2 秒：
   - `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` 等 manifest 关键字段
   - 顶层目录树 ≤ 3 层
   - `AGENTS.md` / `CLAUDE.md` / `README.md` 任选其一的**头 30 行原文**（不压缩）
   - `git log --shortstat -n 50` 提交节奏
2. 产物体积硬性 ≤ 5KB，纯 markdown，无附件。
3. **不再喂给 sub-agent 作 prompt 锚点**——主 sub-agent 拿到 12 维精切输出后，自行吸收 manifest 即可，不再需要「5KB 摘要注入」。
4. 阶段零 §1 工作根目录约定 + 阶段十二 §12 开关表中删除 `--max-context 90k` 与 `--max-history 30k`（属于阶段一的遗留 flag）。
5. Phase-2a 同时承担 ADR-0002 的「Repo 类型识别」职责，**只跑 1 次扫描**。

## Alternatives

- **A1. 保留阶段一 + 贴 low-confidence 标签** —— 心智模型连续，token 预算照样花，标签易被人脑忽略。
- **A2. 砍掉阶段一，不补任何锚点** —— 省 token，但主 sub-agent 协调缺乏广角，第一阶段切片 fail 时无 fallback。
- **A3. 砍掉阶段一 + 5KB 名片（本 ADR）** —— 单源真相，元信息不丢，关键信号保留。
- **A4. 阶段一也加 include 把锁文件加回** —— 压缩率上升、信号被噪音淹没，不解决 hallucination。

## Consequences

- 整体 token 预算预计下降 30-40%（少一次 repomix 压缩 + 5 个 sub-agent 调用）。
- 主 sub-agent 第一次读 12 维精切输出时，**额外多吸收 5KB 元信息**，上下文增量忽略不计。
- 阶段一在 PLAN 中整章删除，相关章节号顺移（§2 → §1，依此类推）。
- §0 TL;DR 不再需要「信号源 = 阶段二 12 维」声明，因为已经没有第二源。
- 阶段十二 §12 开关表与 §0 工作目录约定的删除需要同步修改 PLAN.md。

## Open Questions

- [ ] Phase-2a 扫描超时上限是 2 秒——如果目标仓库 > 100MB（大型 monorepo），5KB 名片能否在 2 秒内产完？需要 PoC 测试。
- [ ] 5KB 名片是否需要再加 1 个清单字段：last 30 days 的 GitHub issue 数（活跃度代理）？
- [ ] 阶段零 §0 中「目标仓库元数据（GitHub URL / commit ref / clone 协议）」这一节是否归并到 Phase-2a 一起做？

## Linked

- ADR-0002（Phase-2a 同时承担类型识别 + 名片生成）
- ADR-0003（ask_user 阶段会引用名片上的「已知事实」）
- 阶段二 §3 / 阶段零 §1 / 阶段十二 §12
