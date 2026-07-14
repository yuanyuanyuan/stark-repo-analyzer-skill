# Graphify 集成指南

Graphify 是参考 `repo-analyzer` 工作流中唯一新增的结构证据层。可以把它理解为分析前的“结构导航图”：帮助 Agent 找到候选模块和关系，但不能代替源码裁决。这个类比的边界是，导航图本身也必须经过健康验证，不能使用手写或 fixture 图冒充真实证据。

Graphify 增强流程只使用静态 code-only 证据，不启用 semantic extraction 或 LLM provider。`standard` 与 `deep` 共享同一提取路径，模式差异只发生在 Agent 的源码阅读和验证阶段。

## 可用性与用户选择

增强流程要求 Graphify `0.9.13+` 并支持 `--code-only`。Agent 只负责检查和解释结果，不得安装或升级 Graphify，也不得创建、读取、打印或绕过 API key、企业代理和私有 provider 配置。

Graphify 缺失或不兼容时，展示官方安装/升级指引并暂停。用户只能明确选择以下一种路径：

- 安装或升级完成后复检，再进入增强流程；
- 本次进入无 Graphify 的原版兼容流程，并在运行记录和最终报告中披露。

Agent 不能自动选择兼容流程。兼容流程也不能创建 Graphify 占位文件或声称使用了图谱增强。

## 单一 Gate 边界

从当前 Skill 核心交付包中的 bundled Graphify gate 入口执行增强流程：`python <SKILL_ROOT>/scripts/graphify_gate.py --target <TARGET> --work-dir <WORK_DIR>`。Skill 不复制底层 doctor、`extract` 或 `cluster-only` 的编排；gate 负责版本检查、code-only 建图、原始工件保留、来源规范化、健康检查和导航 map。

底层 extract 不能接收 `--backend`、模型、provider 配置或 semantic extraction 标志。记录 `extraction_mode: code-only`、`semantic_extraction: disabled` 和 Graphify 版本；不探测或记录 backend/model。code-only 健康门失败时，不得降级为手写图、fixture 图或兼容流程。

## 失败边界

依赖缺失或版本不兼容返回可选择边界，由用户决定安装后复检或兼容流程。Graphify 已开始执行后，无效配置、权限错误、执行器错误、空图、规范化后无可定位节点/关系和不完整工件都必须立即失败；失败运行保留已有诊断摘要，但不能通过重跑兼容流程掩盖。

## 使用结构 Map

post-graph 成功后，把精简导航 map 保存为 `drafts/01-graphify-map.md`，其中包含图谱计数、community、候选模块路径和源码引用。map 不能单独作为报告事实来源：

| Graphify 置信类型 | 允许用途 |
|---|---|
| `EXTRACTED` | 导航候选；写成事实前必须回到源码验证 |
| `INFERRED` | 只能保持待验证 |
| `AMBIGUOUS` | 只能作为风险或问题 |

项目调研、提问、模块分析、覆盖率、交叉验证和最终报告融合仍由参考流程负责。目标仓库保持只读，所有生成文件都必须位于 `$WORK_DIR` 下。

## 主线总结

Graphify 负责提供经过验证的 code-only 结构导航，不负责给出最终结论。缺失依赖时由用户选择安装或兼容流程；增强流程开始后失败必须停止。Agent 最终仍要回到源码验证关系。
