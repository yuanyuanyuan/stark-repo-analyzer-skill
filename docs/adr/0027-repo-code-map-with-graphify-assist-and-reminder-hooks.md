# ADR-0027：本仓库代码地图采用 YAML 语义真源 + Graphify 只读协助 + 提醒型 hook

状态：`accepted`

## 决策

为本仓库维护者与 Agent 建立「产品功能 → 职责分层 → 源码/合同入口」的代码地图，采用以下组合：

1. **语义真源**：`docs/code-map/map.yaml` 手写维护功能语义、职责层与入口路径；`docs/code-map/README.md` 只解释如何阅读与何时更新。
2. **结构协助**：Graphify 产物（如 `graphify-out/`）仅用于发现或核对路径/依赖结构，不自动生成或覆盖 `map.yaml` 的功能语义。
3. **维护规则**：`docs/dev-rules/code-map/` 规定更新触发、无影响声明与 Graphify 边界。
4. **提醒而非拦截**：Codex hooks 在 `PostToolUse`（edit 类）与 `Stop` 上运行 `code_map_gate.py`；当监控路径变更且未同步 `map.yaml` 时只发 `systemMessage`，**不得** `permissionDecision: deny` 或 `continue: false` 仅因地图过期。
5. **不进 Skill 包**：代码地图与其 hook 属于本仓库协作基建，不写入 Skill 核心交付清单。

## 原因

Agent 接到任务后若直接全仓搜索，成本高且易改错层。需要稳定、任务导向的入口索引。若用 Graphify 图当语义真源，会把结构边误当产品功能边界；若用 PreToolUse 硬拦截过期地图，会把协作摩擦抬到阻塞编辑。手写 YAML + 提醒 hook 在「可导航」与「可维护」之间更平衡：语义由人/Agent 在变更边界时显式更新，结构证据仍归 Graphify。

## 备选方案

- **仅 Graphify / 自动生成 map**：结构更新快，但功能语义噪声大，且易把导航图误当产品合同。
- **仅长 Markdown 路径表**：可读，但难被 hook 机械读取，且易与另一份清单双真源。
- **PreToolUse deny 直到 map 同步**：强制力强，但误报会阻断无关编辑；与「提醒型」目标冲突。
- **把 map 打进 Skill 交付包**：会污染用户安装面，且与「本仓库协作导航」职责不符。

## 影响

- 新增 `docs/code-map/`、`docs/dev-rules/code-map/`、`.codex/hooks/code_map_gate.py` 与 `AGENTS.md` 导航行。
- 边界变更（新增/移动功能入口、改职责归属）必须同步 `map.yaml`，或在 progress/PR 声明「code-map 无影响」。
- hook 需用户在 Codex `/hooks` 信任后才会执行；未信任时地图与规则仍有效，提醒能力降级。
- 不改变 analyzer 产品行为、真实 UAT 证据等级或 Graphify gate 合同。

## 取代关系

不取代现有 ADR。与 ADR-0016/0018（Graphify 结构证据）、ADR-0017（程序控制面边界）、ADR-0026（默认 Judge）正交：本决策只约束本仓库协作导航，不扩展产品分析控制面。
