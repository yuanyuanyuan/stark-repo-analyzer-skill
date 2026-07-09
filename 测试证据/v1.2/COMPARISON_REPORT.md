# v1.0 重跑结果 / v1.2 测试证据对比报告

> 更新时间：2026-07-09
> 对比对象：`v1.0没改造前` 最新测试结果 vs `v1.2` 测试结果
> 输出文件：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.2/COMPARISON_REPORT.md`

## 0. 为什么之前没有 token 和时间消耗对比

之前的 v1.2 对比报告没有写 token 消耗和时间消耗，原因不是这些指标不重要，而是当时两个目录里的落盘证据没有可靠的原始计量数据：

- 没有模型 API usage 明细。
- 没有输入 token / 输出 token / cache token 分项。
- 没有统一的阶段开始和结束时间戳。
- 没有每个 subagent 的运行耗时。
- 没有可机器复算的运行日志。

在这种情况下，不能用“报告行数”“文件数量”“源码阅读行数”反推 token/time。那些只能作为工作量侧面指标，不能作为真实成本指标。

本次 v1.0 更新后，`v1.0没改造前/ANALYSIS_REPORT.md` 和 `v1.0没改造前/ACCEPTANCE_RESULT.md` 增加了运行成本章节：v1.0 有时间估算和 token 粗估。但它仍然明确说明“精确 token 不可得”。v1.2 仍未记录同等级别的成本数据，所以本报告只能做：

- v1.0：引用已落盘的估算值。
- v1.2：标注“未记录，无法精确比较”。
- 两者：不编造精确 token 和精确耗时。

## 1. 对比对象

| 版本 | 实际目录 | 说明 |
|---|---|---|
| v1.0 重跑结果 | `/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.0没改造前` | 该目录已更新，不再只是原始“没改造前”单报告结果，而是补齐了 drafts、验收、版本对比和 graphify 输出 |
| v1.2 | `/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.2` | v1.2 的完整测试证据目录，包含最终报告、验收、对比报告和 drafts |

## 2. 文件与产物完整性

| 维度 | v1.0 重跑结果 | v1.2 | 判断 |
|---|---:|---:|---|
| 总文件数 | 59 | 13 | v1.0 更多，但包含 `.claude`、`.codex`、`.meta-kim`、`graphify-out` 等运行环境产物 |
| Markdown 文件数 | 16 | 13 | 两者都具备可读报告主体 |
| drafts Markdown 数 | 9 | 9 | 两者都补齐阶段草稿 |
| 目录体积 | 572K | 164K | v1.0 因 graphify 输出和运行环境文件更大 |
| 最终分析报告 | `ANALYSIS_REPORT.md`，135 行 | `ANALYSIS_REPORT.md`，163 行 | v1.2 最终报告更长，v1.0 新增成本章节 |
| 验收报告 | `ACCEPTANCE_RESULT.md`，25 行 | `ACCEPTANCE_RESULT.md`，43 行 | 两者都有 |
| 版本/对比报告 | `VERSION_COMPARISON.md`，65 行 | `COMPARISON_REPORT.md`，本文件 | 两者都有 |
| graphify 输出 | 有，目录内自带 `graphify-out` | 无独立拷贝，但本仓库已更新 graphify | v1.0 证据目录更重，v1.2 更聚焦报告产物 |

## 3. 草稿链路对比

| 阶段 | v1.0 重跑结果 | v1.2 | 对比 |
|---|---|---|---|
| 阶段 3 调研 | `drafts/03-research.md` | `drafts/03-research.md` | 都有 |
| 阶段 3 计划 | `drafts/03-plan.md` | `drafts/03-plan.md` | 都有 |
| 阶段 5 模块计划 | `drafts/05-modules-plan.md` | `drafts/05-modules-plan.md` | 都有 |
| 阶段 6 模块草稿 | 4 个：SEO/i18n/工程化、切割流水线、状态管理、工作台导出 | 4 个：路由、切割流水线、状态管理、导出/次要模块 | 模块切分不同 |
| 阶段 7 交叉验证 | `drafts/07-cross-validation.md` | `drafts/07-cross-validation.md` | 都有 |
| 阶段 8 洞察 | `drafts/08-insights.md` | `drafts/08-insights.md` | 都有 |

关键差异：

- v1.0 重跑把“工作台/上传预览导出”和“SEO/i18n/工程化”拆成独立模块。
- v1.2 把“路由与导航守卫”单独拆出，并把导出与次要模块合并分析。
- v1.0 和 v1.2 都已满足 repo-analyzer 技能要求的过程证据链，不再是单报告输出。

## 4. 架构结论对比

| 维度 | v1.0 重跑结果 | v1.2 | 结论 |
|---|---|---|---|
| 项目定位 | React + TypeScript + Vite 的长截图分割工具 | 纯前端长截图分割与交付工具 | 一致 |
| 主链路 | FileUploader → useImageProcessor → Worker → splitAnalyzer → AppState → Preview/Export | 上传 → Worker → splitAnalyzer → AppState → Preview → PDF/ZIP | 一致 |
| 核心亮点 | 算法/I/O 分离、Worker 隔离、安全回退、导出闭环 | Worker + 纯函数算法 + 状态守卫 + `slice.index` 页序契约 | 一致，v1.2 更强调跨模块顺序契约 |
| 主要风险 | Worker ready 缺失、done 竞态、导航规则重复、导出选项脱节、SEO 分叉 | `setTimeout(200)`、sparse array、Worker 所有权不清、导出配置链路未闭合、外围复杂度 | 高度一致 |
| 改进方向 | Worker 协议、导航条件收敛、选择语义统一、导出选项生效、SEO 收敛 | Worker handshake、Map 表示切片、sessionId、Worker 所有权、normalizeSelectedSlices、SEO/shared 收敛 | 高度一致 |

判断：v1.0 重跑结果和 v1.2 在架构结论上没有根本冲突。两者差异主要在叙事结构和证据组织，而不是对目标仓库的技术判断。

## 5. 证据质量对比

### v1.0 重跑结果

优势：

- 已补齐完整 drafts，过程可复查。
- 最终报告有源码锚点。
- 新增运行成本章节，至少给出了时间与 token 粗估。
- 自带 graphify 输出，便于复查图谱状态。

限制：

- v1.0 目录名仍叫“没改造前”，但内容已经是重跑后结果，不能再代表原始 v1.0 单报告能力。
- token 为粗估，不是 API 账单。
- 目录包含运行环境文件和 graphify 输出，文件数/体积不能直接视为报告质量。

### v1.2

优势：

- 报告产物更聚焦，目录结构更干净。
- 最终报告、验收、对比、阶段草稿齐全。
- 明确保留 Evidence Plan、交叉验证和锚点抽查。
- 单独拆出路由与导航守卫，更好解释状态驱动导航。

限制：

- v1.2 没有记录 token 消耗。
- v1.2 没有记录完整开始/结束时间和阶段耗时。
- v1.2 的 `ACCEPTANCE_RESULT.md` 曾写“graphify 更新通过”，但没有把 graphify 输出复制进 v1.2 目录，因此目录自身不包含 graphify 结果快照。

## 6. Token 与时间消耗对比

| 维度 | v1.0 重跑结果 | v1.2 | 是否可精确比较 |
|---|---|---|---|
| 精确 API token 账单 | 不可得 | 未记录 | 不可精确比较 |
| token 估算 | 约 95k-150k tokens | 未记录 | 不可精确比较 |
| 可观测开始时间 | 2026-07-09 18:31:19 CST | 未记录 | 不可精确比较 |
| 成本统计写入时间 | 2026-07-09 18:40:53 CST | 未记录 | 不可精确比较 |
| 总耗时估算 | 约 9 分 34 秒 | 未记录 | 不可精确比较 |
| 并行子代理 | 4 个 | 4 个 | 可做结构对比，不可做耗时对比 |
| 成本说明质量 | 有专门章节，明确估算限制 | 无成本章节 | v1.0 更完整 |

结论：

- v1.0 现在有成本记录，但仍是估算。
- v1.2 没有可引用的成本记录。
- 因此不能说“v1.0 比 v1.2 更省/更贵”，只能说“v1.0 重跑结果记录了成本估算，v1.2 未记录成本指标”。

后续如果要让 v1.0/v1.2/v1.3 可比较，必须在每次运行开始前写入统一成本日志，例如：

```markdown
# RUN_COST.md

- run_started_at:
- run_finished_at:
- elapsed_seconds:
- model:
- main_agent_input_tokens:
- main_agent_output_tokens:
- subagent_count:
- subagent_input_tokens:
- subagent_output_tokens:
- tool_call_count:
- notes:
```

如果工具链拿不到精确 token，就必须明确记录“不可得”，并只保留耗时、文件数、草稿数等可观测指标。

## 7. 结果判断

如果评估“当前目录里的测试证据是否完整”，v1.0 重跑结果和 v1.2 都通过。

如果评估“架构分析结论是否可信”，两者都通过，且核心结论基本一致。

如果评估“成本可比性”，v1.0 重跑结果优于 v1.2，因为 v1.0 至少记录了估算 token 和估算耗时；但由于两者都没有精确 API token 账单，不能做严格成本优劣判断。

如果评估“作为后续基准是否干净”，v1.2 更适合，因为它只保留分析证据本身；v1.0 重跑目录混入了 graphify、meta-kim、Codex/Claude 配置等运行环境产物。

## 8. 最终结论

更新后的 v1.0 已经不是原始“没改造前”的轻量结果，而是一次完整重跑后的证据目录。它和 v1.2 在 repo-analyzer 流程完整性上已经接近，甚至在成本记录上比 v1.2 更完整。

v1.2 的优势在于目录干净、证据结构稳定、路由/状态/切割/导出分层清楚。v1.0 重跑结果的优势在于补充了 token/time 成本估算和 graphify 证据快照。

本次对比的核心修正是：**不能再把 v1.0 描述为“只有单报告、过程证据不足”；应描述为“v1.0 目录已被重跑补齐，当前与 v1.2 的差异主要是成本记录、模块切分和目录洁净度”。**
