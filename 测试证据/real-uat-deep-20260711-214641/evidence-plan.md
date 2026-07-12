# Evidence Plan

## 元数据
- **mode**: deep
- **tooling_level**: enhanced（目标）
- **parallelism**: degraded（deep 在 Phase 0 Doctor 被能力门禁拦截，未进入可分工的证据阶段；无真实子代理执行）
- **doctor_allowed / allowed_deep**: False / False
- **missing_capabilities.deep**: ["reference-edges"]
- **target_repo**: `/tmp/Long_screenshot_splitting_tool`
- **target_commit**: `bdee20b8c4e4985c690a255ed09f64a3e335fd20`
- **out**: `/Users/chuzu/projests/stark-repo-analyzer-skill/spec-v2.2-standard-deep-modes-and-rules-based-to/测试证据/real-uat-deep-20260711-214641`
- **rules_version**: 2.2.0
- **UAT 标签**: 真实UAT回归测试·deep（real-uat-regression）

## 架构问题（若 deep 放行本应回答）
1. Worker 协议与时序：切片/导出路径上主线程与 Web Worker 的消息契约、错误回传与取消语义如何保证一致性？
2. 导航规则一致性：路由配置、菜单、守卫与 SEO/canonical 是否单源，还是多处规则漂移？
3. 切片索引语义：长图切片的 index/offset/overlap 如何定义，边界 case 如何处理？
4. 导出选项贯通：UI 可感知导出选项是否贯通到运行时导出链路（含 worker）？
5. SEO 多源：SEOContext / 路由 meta / 静态配置是否多源冲突？

> 以上问题**未能进入源码证据阶段**：Doctor 拒绝 deep，按合同不得降级 standard 后伪称 deep Full。

## 候选证据（规划态，未取样分析）
| 问题 | 候选路径（规划） |
|---|---|
| Worker 协议/时序 | `src/workers/**`, worker postMessage 调用点 |
| 导航规则 | `config/app/routing.config.ts`, `src/router/**` |
| 切片索引 | `src/**` 中 slice/split 相关 utils 与 components |
| 导出选项贯通 | `src/components/**` 导出 UI + export pipeline |
| SEO 多源 | `src/context/SEOContext.tsx`, routing/meta 配置 |

## 模块分级（规划态，未执行 units 回填）
因 deep 未放行，**未**运行 `scan/summarize/units`，无机器模块分母。对照目标仓目录结构的**规划**分级（不得当作 coverage 硬分母）：

| 模块 | 分级 | 理由（规划） | source |
|---|---|---|---|
| src | core | 业务与 UI 主体 | planned-from-tree |
| config | secondary | 应用/路由/环境配置 | planned-from-tree |
| shared-components | secondary | 共享组件 | planned-from-tree |
| scripts / tools | secondary | 工具链 | planned-from-tree |
| tests / test-setup | excluded | 测试夹具 | planned-from-tree |

## 分工与 parallelism
- **parallelism: degraded**
- 原因：`doctor.allowed_deep=false`，`scan/summarize/units` 均以「Doctor 未放行 deep：缺失能力合同，拒绝执行且不降级」退出。
- 子代理：无实际启动（无 `subagent-artifacts` 有效业务产物）。
- 主 Agent 职责：落盘 doctor/install-prompt/诊断、记录拒绝证据、写阻塞态 report 与 UAT 摘要；**不**伪造 module-evidence 覆盖率。

## 预算（deep 合同，未消耗分析预算）
- time_minutes 目标 240 / token 目标 240000 / max_agents 8
- 本轮实际：仅 CLI doctor + 拒绝探针 + 审计工件；未进入模块证据预算。

## 风险抽样计划（未执行）
每个 core 模块多路径风险抽样（Worker 时序、导出贯通、SEO 多源等）— **blocked by doctor**。

## 预期 Unsupported Area
- **deep reference-edges 能力**：对本仓 TS/JS，ctags 无 reference roles；Graphify→units 未接线 → deep 模式整体 **Unsupported for Full Delivery**。
- 在能力补齐前，任何「deep Full」声明均为违规。

## 报告章节结构（若放行）
场景 → 全景 → 设计哲学 → 核心模块（pipeline / worker / export / SEO）→ 批判性评价 → 业界对比 → 可借鉴经验。

## 诚实边界
- 本 Evidence Plan 记录的是 **deep 被拒绝后的执行事实**，不是伪装已完成的深度分析计划执行记录。
- `parallelism: degraded` 在此表示「未进入可并行证据阶段」，**不能**判多子代理验收通过，也**不能**判 deep Full。
