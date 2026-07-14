# Graphify 简化执行计划

状态：`completed`

Roadmap：
[`graphify-simplification-roadmap.md`](../roadmap/graphify-simplification-roadmap.md)

进度记录：
[`graphify-simplification-progress.md`](graphify-simplification-progress.md)

## 当前主线

主目标：保留参考 repo-analyzer 的 Agent 分析能力，把程序层收缩为单一 Graphify code-only 闸门，并使产品合同、测试和仓库证据边界与活动 ADR 一致。该目标已完成。

当前阶段：`completed`，G0-G4 为 `5/5`。

下一步：没有未完成的实施刀。准备发布时为 G5 三条真实回归建立新的活动执行计划；P1/P2 条目不是本已完成计划的自动续做授权。

## 执行约束

- 当前工作树包含用户已有改动；禁止 reset、checkout 或整文件覆盖。
- 每刀开始前记录 `git status --short`，只修改该刀拥有的文件。
- 产品实现、历史证据清理和真实 UAT 不得混在同一刀。
- 删除大型运行证据前必须先按 ADR-0019 完成 Git 外归档和轻量索引。
- 聚焦 UAT 只能证明对应分支；真实回归声明必须满足 `docs/dev-rules/real-uat-regression/README.md`。
- 逐文件迁移输入见
  [`graphify-simplification-file-plan.md`](../archive/v1-control-plane/graphify-simplification-file-plan.md)；与本计划冲突时以本计划和 roadmap 为准。

## P0 必需任务

| ID | 任务 | 依赖 | 输出 | 验证 | 状态 |
|---|---|---|---|---|---|
| G0-1 | 建立目录与 AGENTS 边界 | - | `AGENTS.md`、三个目录 README | `git diff --check`、路径检查 | 完成 |
| G0-2 | 指定唯一活动 roadmap、plan、progress 并标记旧控制面 | G0-1 | 本 roadmap/plan/progress 与 superseded 横幅 | 活动状态与链接扫描 | 完成 |
| G0-3 | 物理归档旧控制面和执行记忆 | G0-2 | `docs/archive/`、`docs/README.md`、收敛后的 `docs/dev-rules/` | 目录角色与链接检查 | 完成 |
| G1-0 | 建立 output style 路由并迁移第一方维护性文档 | G0-3 | `docs/dev-rules/output-style/`、中文入口与文档正文 | 语言扫描、注释扫描、链接检查 | 完成 |
| G1-0b | 为人类与 Agent 建立四类文档的快速读取入口 | G1-0 | docs map、roadmap/plan/spec/ADR 目录索引 | 首屏字段审计、链接检查 | 完成 |
| G1-0c | 将 baseline 测试证据迁出产品文档层 | G1-0b | `tests/baseline/`、更新后的 acceptance 路径 | 文件计数、路径扫描、测试与 acceptance 检查 | 完成 |
| G1-1 | 审计活动合同与当前工作树差异 | G0-2 | progress 中的文件级差异清单 | 每项差异回挂 roadmap/ADR | 完成 |
| G1-2 | 对齐输入输出合同、README、skill 与集成指南 | G1-1 | 活动产品文档 | 静态矛盾扫描、skill 合同测试 | 完成 |
| G1-3 | 标记被 ADR-0016 至 ADR-0024 取代的旧 ADR | G1-1 | ADR 状态更新 | 活动 ADR 决定唯一 | 完成 |
| G2-1 | 建立单一 `graphify-gate` 模块与 CLI | G1-2 | 薄 CLI、gate、最小 status schema | gate 单元测试 | 完成 |
| G2-2 | 迁移路径规范化、raw 保留和源码只读保护 | G2-1 | gate 实现与负向 fixtures | 有效噪声图通过、空图/越界失败 | 完成 |
| G2-3 | 删除重复 doctor、完整分析控制面与失效 contracts | G2-2 | 收敛后的 Python/acceptance 表面 | 全量单元测试、旧命令静态扫描 | 完成 |
| G3-1 | 重建 skill 静态合同与结构检查 | G1-2、G2-3 | skill/structure tests | 测试通过 | 完成 |
| G3-2 | 执行四类聚焦 UAT | G3-1 | 模式、安装选择、健康门、subagent 分支证据 | 每类记录入口、结果和边界 | 完成 |
| G4-1 | 外置仍需保存的真实运行证据 | G3-2 | Git 外证据与轻量索引 | 路径、摘要/校验、可定位性检查 | 完成 |
| G4-2 | 清理生成状态、旧运行目录和失效过程文档 | G4-1 | 收敛后的仓库 | `git ls-files` 与引用扫描 | 完成 |
| G4-3 | 完成实施主线验收 | G4-2 | 完成记录与残余风险 | 必需测试通过，未执行 UAT 明示 | 完成 |

## P1 后续改进

- 精简仍然重复的 README 和安装说明，但不改变产品合同。
- 为 progress 和 roadmap 增加轻量静态一致性检查。
- 评估是否将 Git 外真实回归证据接入 CI artifact。

P1 不计入 G0-G4 实施完成度，除非后续被显式提升为 P0。

## P2 条件触发

- 准备发布或用户明确要求时，执行 G5 的三条真实回归 UAT。
- 新增 Graphify 版本或新的分析档位时，重新评估 gate 和 UAT 矩阵。

## 失败与人工决策

- 同一失败原因连续出现两次时停止机械重试，记录 failure class 和需要的决策。
- 产品合同与活动 ADR 冲突时先修合同，不用兼容代码掩盖冲突。
- 原始 UAT 证据无法迁移或核验时，保留历史文件或降低历史声明，不能先删除再补摘要。
- 需要改变公开输入、输出、模式或回退语义时，先新增或更新 ADR，再实施代码。
