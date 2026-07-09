# Tickets: v1.2 Evidence Plan

为 repo-analyzer 的 v1.2 Evidence Plan 计划层增强拆分工单。来源规格：`docs/specs/evidence-first-v1-roadmap/v1.2-evidence-plan.to-spec.md`。

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

## 确立 Evidence Plan 的最小行为契约

**What to build:** repo-analyzer 明确知道 Evidence Plan 是模块深读前的轻量 Markdown 计划，字段包含模块、架构问题、候选证据范围、必需证据类型、风险路径和预期判断范围；同时保留 v1.1 源码锚点要求，并明确不引入 CLI、JSON schema、自动生成或 Evidence Matrix。

**Blocked by:** None — can start immediately.

- [x] Evidence Plan 被描述为模块深读前的计划层产物，而不是新的工具链产物。
- [x] 最小字段包含模块、架构问题、候选文件或入口、必需证据类型、风险路径和预期判断范围。
- [x] 明确继承源码锚点要求，并排除 CLI、JSON schema、自动生成和 Evidence Matrix。

## 把 Evidence Plan 嵌入模块规划阶段

**What to build:** 主 agent 在启动 subagent 前，能在现有模块规划草稿里为每个核心模块产出 Evidence Plan；用户可以先看到每个模块要回答什么问题、准备查哪些候选入口、边界在哪里，而不是只看到模块清单或文件列表。

**Blocked by:** 确立 Evidence Plan 的最小行为契约.

- [x] 模块规划阶段要求为每个核心模块先写 Evidence Plan。
- [x] Evidence Plan 可以嵌入现有模块规划草稿，不新增复杂产物链。
- [x] Evidence Plan 必须包含架构问题，不能退化成文件列表。

## 让 subagent 按模块 Evidence Plan 深读源码

**What to build:** 每个 subagent 的任务输入都包含对应模块的 Evidence Plan，使 subagent 围绕架构问题、候选证据、风险路径和预期判断范围阅读源码；不同模块的阅读范围更清楚，减少重复盲读。

**Blocked by:** 把 Evidence Plan 嵌入模块规划阶段.

- [x] 核心模块 subagent prompt 引用对应模块的 Evidence Plan。
- [x] subagent prompt 使用 Evidence Plan 限定阅读目标、候选证据和风险路径。
- [x] 分工说明强调减少重复盲读，而不是要求扩大阅读范围。

## 让模块草稿回应 Evidence Plan

**What to build:** subagent 草稿不只是补源码锚点，而是要明确回应 Evidence Plan 中的问题；如果候选文件不足、风险路径未验证或判断范围需要收窄，草稿需要标出限制或开放问题。

**Blocked by:** 让 subagent 按模块 Evidence Plan 深读源码.

- [x] 模块草稿必须回应 Evidence Plan 中的架构问题。
- [x] 候选证据不足时，草稿将相关内容降级为限制、假设或开放问题。
- [x] 草稿保留 v1.1 的源码锚点要求，不把无锚点内容写成确定性结论。

## 补齐 v1.2 人工验收清单

**What to build:** 维护者可以用代表性仓库手工验收 v1.2：检查核心模块启动前是否都有 Evidence Plan、计划是否包含架构问题而不只是文件列表、subagent 草稿是否回应计划、候选范围是否降低无目的阅读，并且不要求 Markdown 格式逐字一致。

**Blocked by:** 让模块草稿回应 Evidence Plan.

- [x] 验收清单覆盖核心模块启动前是否存在 Evidence Plan。
- [x] 验收清单检查 Evidence Plan 是否包含架构问题，而不仅是候选文件。
- [x] 验收清单检查 subagent 草稿是否回应 Evidence Plan。
- [x] 验收标准只要求字段语义完整，不要求 Markdown 格式逐字一致。

## 同步用户文档中的 v1.2 工作流说明

**What to build:** README/中文 README 或同类用户入口能说明 v1.2 的新增行为：分析会先形成模块 Evidence Plan，再分配 subagent 深读；用户理解这是计划层增强，不是新工具链或质量门。

**Blocked by:** 补齐 v1.2 人工验收清单.

- [x] 用户文档说明模块 Evidence Plan 会出现在 subagent 深读之前。
- [x] 用户文档说明 Evidence Plan 是轻量 Markdown 计划层增强。
- [x] 用户文档不暗示已引入新 CLI、JSON schema、Evidence Matrix 或硬质量门。
