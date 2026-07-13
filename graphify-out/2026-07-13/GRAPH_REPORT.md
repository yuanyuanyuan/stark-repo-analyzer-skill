# Graph Report - stark-repo-analyzer-skill  (2026-07-13)

## Corpus Check
- 566 files · ~151,911 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2122 nodes · 2069 edges · 290 communities (202 shown, 88 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dc0d7a9d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 参考输出基线
- codex-plugin-cc 架构基线报告
- Click：可组合命令行运行时的架构基线
- Claude Code 源码架构基线
- OpenAI Codex 架构分析基线
- HTTPX 架构分析基线
- stark-repo-analyzer-skill 保真移植与 Graphify 增强任务分解
- Ruff 架构分析基线
- 08 Insights
- Session/turn orchestration
- 03 Research
- 核心模块：命令模型与上下文执行
- 核心模块：参数解析与类型转换
- 06 Module: Authentication, Decoding and Error Propagation
- 06 Module: Request Entry and Client Orchestration
- HTTPX Standard Baseline Execution Log
- Ruff 项目研究
- 模块：CLI 与执行控制
- 模块：项目配置与文件发现
- 模块：Formatter document pipeline
- 模块：Lint pipeline 与规则/修复
- Execution Log: Click Baseline Run
- 03 Plan
- Core Module: Query Loop
- Core Module: Tool Runtime
- Execution Log
- 研究与定位
- 模块计划与报告叙事
- 核心模块：终端交互与帮助输出
- 03 Research：Codex 的问题、定位与组织动机
- 05 Modules Plan：按业务功能组织报告
- CLI/TUI user loop
- 08 Insights：架构洞察
- 阶段 3：分析计划
- 核心模块：Codex App Server 会话运行时
- 核心模块：命令与任务编排
- 03 Research: HTTPX
- 06 Module: Request, Response, Content and Multipart Models
- 06 Module: Transport Contract and Execution Adapters
- 06 Module: URL, Query Parameters and Runtime Configuration
- Ruff standard 分析计划
- 模块：Python parsing frontend
- Ruff standard 基线执行日志
- Stark Repo Analyzer V1 Implementation Goal
- 物理基线状态
- 分析计划: Click CLI Framework
- 调研笔记: Click CLI Framework
- ADR 0001: Bounded Standard Scope for a Leaked Source Mirror
- Core Module: Command and Skill Extension
- Core Module: Context and Memory
- Core Module: Task and Agent Runtime
- 08 Insights
- 洞察与评价
- 执行日志
- Execution safety boundary
- Codex standard 基线执行日志
- 核心模块：Claude 生命周期与 Stop review gate
- 核心模块：Job 状态、日志与后台生命周期
- 阶段 8：架构洞察
- 执行日志：codex-plugin-cc standard baseline
- 05 Modules Plan: HTTPX
- 06 Module: CLI and Public API Contract
- 次要模块：语义、LSP 与 ty
- 05 Modules Plan
- Secondary Module: Entry and Terminal UI
- Secondary Module: MCP and Plugins
- Secondary Module: Remote, IDE and Platform Services
- 07 Cross Validation
- 08 Coverage
- 分析计划
- 次要模块：completion、测试与平台基础设施
- 交叉验证
- 03 Plan：standard 分析计划
- MCP、skills 与 plugins
- Protocol/event contract
- 07 Cross-validation：交叉验证
- 08 Coverage：覆盖率汇总
- 阶段 3：项目调研
- 阶段 5：模块计划与报告叙事线
- 核心模块：共享 App Server Broker
- 阶段 7：交叉验证
- 阶段 8：覆盖率汇总
- 03 Plan: HTTPX Standard Analysis
- 07 Cross-Validation
- 08 Coverage
- Ruff 模块规划与报告大纲
- 交叉验证
- Ruff standard 覆盖率汇总
- Ruff 架构洞察
- 本地参考源码语料
- Secondary Module: Permission and Shell Security
- App-server integration
- physical-baseline-check.sh
- Graphify 自动探测必需的 LLM 引擎
- 覆盖率汇总
- Stark Repo Analyzer Skill Context
- 基线从当前工作树开始
- 先建立参考输出基线
- Graphify 是强制结构证据闸门
- 使用 Graphify headless CLI 进行自动分析
- Graphify 产物隔离在分析工作区
- 按失败类别限制 Graphify 重试
- 要求健康的 Graphify 图谱
- 源码裁决 Graphify 冲突
- 区分 Graphify 深度提取和分析档位
- 保真参考流程并加入 Graphify
- 复制参考文件并限制 Graphify 修改范围
- Agent 主导 Graphify Bootstrap 并保留密钥边界
- 为 V1 增加 doctor 预检脚本
- 用 doctor 作为低侵入的 Graphify 侧车
- Quality Checks
- Domain Glossary
- Codex standard 基线质量检查
- 次要模块：支撑能力与插件声明
- input.md
- STATUS.md
- checks.md
- checks.md
- checks.md
- checks.md
- 分析哲学与思维框架
- cli.py
- Stark Repo Analyzer
- 分析工作流
- doctor.sh
- package.json
- Input and Output Contract
- Graphify Integration Guide
- doctor-self-test.sh
- analysis-run-input.md
- stark-repo-analyzer
- doctor.sh
- 真实 UAT 回归测试
- physical-repeatability-check.sh
- __init__.py
- properties
- properties
- 模块分析指南
- Reference And Implementation Comparison
- implementation-fixture-check.sh
- Path
- run-contract-check.sh
- skill-structure-check.sh
- Graphify Sidecar Failure Record
- Click 次要模块批量分析
- Graphify Sidecar Failure Record
- Graphify Sidecar Failure Record
- Stark Repo Analyzer V1 Release Report
- output
- 1. Graphify CLI
- Hybrid code intelligence rollout and evaluation plan
- ANALYSIS_REPORT.md
- Analysis Plan
- 模块：参数解析与类型转换
- 终端交互与帮助输出
- Problems And Resolutions
- Graph Report - /private/tmp/stark-click-code-only-pilot  (2026-07-13)
- Ruff 架构分析报告
- click
- 命令模型与上下文执行
- 本地开源工具配置
- Codex CLI 架构分析（Physical Baseline）
- Codex CLI 架构分析（Physical Baseline）
- HTTPX 架构分析报告
- HTTPX 架构分析报告
- projects
- claude-code
- codex
- codex-plugin-cc
- httpx
- ruff
- OSS and local-only tool selection for hybrid code intelligence
- 可复用经验
- manifest.json
- Research Draft
- 核心模块分析
- 1. Shell Completion：把核心参数模型投影到 shell
- 2. Testing：在可恢复隔离中重演真实 CLI
- V2 混合代码智能架构
- 2. 模块与接口
- 2. Repomix 1.16.1 hotspot pack
- 开源混合代码智能架构方案
- Claude Code 源码架构分析
- 执行日志
- Claude Code 源码架构分析
- 交叉验证与质量门控
- 架构洞察与评价
- structure_evidence
- 1. Graphify 0.9.13 code-only
- V1 固定 Graphify code-only
- Meta_Kim 采集清单
- 结构证据与验收经验
- 失败、恢复与未完成事项
- 协作与执行方法经验
- 研究草稿
- 执行日志
- 3. Platform Compatibility：把宿主不一致压缩到 I/O 边界
- 6. Exceptions：把解析失败转成一致的用户反馈
- Analysis Plan
- Module Analysis Plan
- CLI Dispatch
- Core Orchestration
- Insights
- Research Draft
- Client Lifecycle and Request Pipeline
- 03 研究说明
- 08 洞察
- 产品契约与演进经验
- 物理基线与报告质量经验
- 洞察草稿
- 2. 业务问题与设计思路
- 4. Terminal Presentation Helpers：在不可见控制序列下保持可读布局
- 5. Internal State and Sentinels：区分“未设置”和“特殊控制值”
- 8. 关键设计权衡与洞察
- Click code-only V1 对比结果
- Analysis Plan
- Cross Validation
- Analysis Plan
- Insights
- 07 交叉验证
- 项目经验库
- 模块叙事与模块规划
- 3. 核心数据结构与边界
- 4. 核心流程
- 4. 核心数据结构
- 7. Public Export Surface：稳定地把内部能力变成 Click API
- Research Context
- 覆盖率汇总
- 4. Graphify code-only
- 3. 两层解析设计
- Module Plan
- Configuration Model
- Non-interactive Execution
- Sandbox Facade
- Execution Log
- Content and Decoding
- Request and Response Models
- Secondary Modules
- Transport Boundary and Adapters
- Checks
- CLI/config 核心模块
- formatter/printer 核心模块
- lint/fix 核心模块
- 次要模块边界
- repeatability-run-1-vs-run-2.md
- checks.md
- 03-plan.md
- 07-cross-validation.md
- 08-coverage.md
- graphify-execution.md
- graphify-failure.md
- input.md
- 10. 覆盖率明细
- 6. 深度模块分析
- 覆盖率
- 覆盖率
- checks.md
- execution-log.md
- input.md
- repeatability-run-1-vs-run-2.md
- checks.md
- 06-module-secondary.md
- 08-coverage.md
- graphify-execution.md
- graphify-failure.md
- input.md
- raw-execution-log.md
- repeatability-run-1-vs-run-2.md
- checks.md
- 05-modules-plan.md
- 07-cross-validation.md
- 08-coverage.md
- execution-log.md
- graphify-execution.md
- graphify-failure.md
- input.md
- raw-execution-log.md
- comparison.md
- 03-plan.md
- 05-modules-plan.md
- 08-coverage.md
- execution-log.md
- graphify-code-only.md
- input.md

## God Nodes (most connected - your core abstractions)
1. `Analysis Plan` - 43 edges
2. `analyze()` - 23 edges
3. `output` - 21 edges
4. `CliContractTests` - 20 edges
5. `resume()` - 19 edges
6. `validate_run_contract()` - 17 edges
7. `RunFailure` - 15 edges
8. `prepare_agent_handoff()` - 15 edges
9. `Hybrid code intelligence rollout and evaluation plan` - 13 edges
10. `Ruff 架构分析报告` - 12 edges

## Surprising Connections (you probably didn't know these)
- `CliContractTests` --uses--> `RunFailure`  [INFERRED]
  tests/test_cli.py → src/stark_repo_analyzer/cli.py
- `CliContractTests` --uses--> `ContractError`  [INFERRED]
  tests/test_cli.py → src/stark_repo_analyzer/contracts.py
- `RunFailure` --uses--> `ContractError`  [INFERRED]
  src/stark_repo_analyzer/cli.py → src/stark_repo_analyzer/contracts.py
- `finalize()` --calls--> `validate_run_contract()`  [EXTRACTED]
  src/stark_repo_analyzer/cli.py → src/stark_repo_analyzer/contracts.py
- `finalize()` --calls--> `write_output_manifest()`  [EXTRACTED]
  src/stark_repo_analyzer/cli.py → src/stark_repo_analyzer/contracts.py

## Import Cycles
- None detected.

## Communities (290 total, 88 thin omitted)

### Community 0 - "参考输出基线"
Cohesion: 0.06
Nodes (31): 1. 领域对象是多条能力表面的共同协议, 2. Agent 系统围绕状态、事件、安全和扩展形成四边界, 3. 复杂度主要集中在边界和生命周期，不在入口数量, 4. 大型仓库必须允许有边界的诚实结果, 产物完整性, 执行编排差异, 覆盖率门控, 跨项目基线验证 (+23 more)

### Community 1 - "codex-plugin-cc 架构基线报告"
Cohesion: 0.11
Nodes (18): 1. 先说结论, 2.1 使用场景, 2.2 为什么不是直接调用 CLI, 2. 项目问题与定位, 3. 全景架构, 4. 一次后台任务如何完成, 5.1 命令与任务编排, 5.2 App Server 会话运行时 (+10 more)

### Community 2 - "Click：可组合命令行运行时的架构基线"
Cohesion: 0.12
Nodes (15): 10. 评价、风险与重新设计建议, 11. 证据与边界, 1. 先给结论, 2. 项目定位与问题, 3. 设计主张与同类位置, 4. 全景：一份元数据，多种表面能力, 5. 主流程：从声明到 callback, 6. Context：运行时的深模块 (+7 more)

### Community 3 - "Claude Code 源码架构基线"
Cohesion: 0.13
Nodes (14): 10. Coverage and Limitations, 1. 定位与边界, 2. 全局架构, 3. Query Loop, 4. Tool Runtime, 5. Tasks and Agents, 6. Commands and Skills, 7. Context and Memory (+6 more)

### Community 4 - "OpenAI Codex 架构分析基线"
Cohesion: 0.13
Nodes (14): 10. 基线限制, 1. 先给结论, 2. 场景化问题与定位, 3. 一次 coding turn 的全景, 4. Session/turn：把 agent 变成可恢复状态机, 5. Execution safety：从模型意图到主机副作用, 6. CLI/TUI：事件驱动的交互壳, 7. Protocol 与 app-server：把 runtime 变成复用接口 (+6 more)

### Community 5 - "HTTPX 架构分析基线"
Cohesion: 0.13
Nodes (14): 10. 证据与限制, 1. 场景与定位, 2. 项目全景, 3. 一次请求如何完成, 4. 消息模型与流生命周期, 5. URL、配置与路由, 6. Transport 边界, 7. 认证、解码和错误 (+6 more)

### Community 6 - "stark-repo-analyzer-skill 保真移植与 Graphify 增强任务分解"
Cohesion: 0.13
Nodes (14): 1. 目标, 2. 不在当前目标内, 3. 需要处理的对象, 4. 阶段分解, 5. 依赖关系, 6. 第一批原子任务候选, 7. 分解阶段完成判定, D0 分解（当前阶段） (+6 more)

### Community 7 - "Ruff 架构分析基线"
Cohesion: 0.15
Nodes (12): 10. 评价与重设计建议, 11. 基线限制, 1. 先给结论, 2. 项目问题与定位, 3. 全景架构, 4. 从 CLI 到输入集合, 5. 配置与文件发现, 6. Python frontend (+4 more)

### Community 8 - "08 Insights"
Cohesion: 0.18
Nodes (10): 08 Insights, 1. 双 API 共享语义，分离 I/O, 2. 显式生命周期比隐式读取更可控, 3. Transport 是扩展点而不是底层细节泄漏点, 4. 兼容性是经过筛选的兼容, 可迁移启发, 如果重新设计, 真实问题 (+2 more)

### Community 9 - "Session/turn orchestration"
Cohesion: 0.20
Nodes (9): Session/turn orchestration, Why > What, 业务问题与设计, 亮点与问题, 在项目中的角色, 核心数据结构, 核心流程, 覆盖率 (+1 more)

### Community 10 - "03 Research"
Cohesion: 0.22
Nodes (8): 03 Research, Evidence Classification, Organizational Motivation, Positioning, Project Problem, Research Gaps, Same-Category Comparison, Why a Separate Project

### Community 11 - "核心模块：命令模型与上下文执行"
Cohesion: 0.22
Nodes (8): 关键设计决策与评价, 在项目中的角色, 核心数据结构, 核心模块：命令模型与上下文执行, 核心流程, 模块间协作, 覆盖率, 解决的问题与设计思路

### Community 12 - "核心模块：参数解析与类型转换"
Cohesion: 0.22
Nodes (8): 关键权衡, 在项目中的角色, 核心数据结构, 核心模块：参数解析与类型转换, 核心流程, 模块间协作, 覆盖率, 设计思路

### Community 13 - "06 Module: Authentication, Decoding and Error Propagation"
Cohesion: 0.22
Nodes (8): 06 Module: Authentication, Decoding and Error Propagation, Authentication, Decoding, Why > What, 亮点与问题, 覆盖率明细, 读者问题, 错误传播

### Community 14 - "06 Module: Request Entry and Client Orchestration"
Cohesion: 0.22
Nodes (8): 06 Module: Request Entry and Client Orchestration, Why > What, 主流程, 亮点与问题, 代价与边界, 结构, 覆盖率明细, 读者问题

### Community 15 - "HTTPX Standard Baseline Execution Log"
Cohesion: 0.22
Nodes (8): Completion, External research, Failures and limitations, HTTPX Standard Baseline Execution Log, Preflight, Read and analysis sequence, Scope and guardrails, Write policy

### Community 16 - "Ruff 项目研究"
Cohesion: 0.22
Nodes (8): Ruff 项目研究, 为什么需要单独做这个项目, 同类对比, 定位与价值主张, 研究结论, 研究边界, 组织动机, 项目解决的核心问题

### Community 17 - "模块：CLI 与执行控制"
Cohesion: 0.22
Nodes (8): Why > What, 叙事衔接, 在项目中的角色, 核心流程, 模块：CLI 与执行控制, 覆盖率, 跨模块协作, 问题与边界

### Community 18 - "模块：项目配置与文件发现"
Cohesion: 0.22
Nodes (8): Why > What, 叙事衔接, 在项目中的角色, 核心流程, 模块：项目配置与文件发现, 覆盖率, 跨模块协作, 问题与边界

### Community 19 - "模块：Formatter document pipeline"
Cohesion: 0.22
Nodes (8): Why > What, 叙事衔接, 在项目中的角色, 核心流程, 模块：Formatter document pipeline, 覆盖率, 跨模块协作, 问题与边界

### Community 20 - "模块：Lint pipeline 与规则/修复"
Cohesion: 0.22
Nodes (8): Why > What, 叙事衔接, 在项目中的角色, 核心流程, 模块：Lint pipeline 与规则/修复, 覆盖率, 跨模块协作, 问题与边界

### Community 21 - "Execution Log: Click Baseline Run"
Cohesion: 0.25
Nodes (7): Execution Log: Click Baseline Run, Exit Status, Phase 1: Project Acquisition, Phase 2: Code Size Estimation, Phase 3: External Research, Phase 4-8: Analysis, Run Overview

### Community 22 - "03 Plan"
Cohesion: 0.25
Nodes (7): 03 Plan, Core Modules, Output Plan, Reading Plan, Scale Estimate, Secondary Modules, Selected Analysis Mode

### Community 23 - "Core Module: Query Loop"
Cohesion: 0.25
Nodes (7): Collaboration, Core Flow, Core Module: Query Loop, Coverage, Data Structures, Design Decisions and Trade-offs, Role and Business Problem

### Community 24 - "Core Module: Tool Runtime"
Cohesion: 0.25
Nodes (7): Collaboration, Core Flow, Core Module: Tool Runtime, Coverage, Data Structures, Design Decisions and Trade-offs, Role and Business Problem

### Community 25 - "Execution Log"
Cohesion: 0.25
Nodes (7): Actual Reading, Execution Log, External Sources, Failures and Limits, Final Verification, Scope Control, Write Discipline

### Community 26 - "研究与定位"
Cohesion: 0.25
Nodes (7): 为什么需要单独做这个项目, 同类对比, 定位与设计主张, 研究与定位, 研究边界, 组织动机, 项目解决的核心问题

### Community 27 - "模块计划与报告叙事"
Cohesion: 0.25
Nodes (7): 关键探索问题, 叙事线, 报告大纲, 核心模块, 模块清单, 模块计划与报告叙事, 次要模块

### Community 28 - "核心模块：终端交互与帮助输出"
Cohesion: 0.25
Nodes (7): 关键权衡与评价, 在项目中的角色, 核心模块：终端交互与帮助输出, 核心流程, 模块间协作, 覆盖率, 设计思路

### Community 29 - "03 Research：Codex 的问题、定位与组织动机"
Cohesion: 0.25
Nodes (7): 03 Research：Codex 的问题、定位与组织动机, 为什么需要单独做这个项目, 同类对比, 定位, 待验证, 组织动机, 项目解决的核心问题

### Community 30 - "05 Modules Plan：按业务功能组织报告"
Cohesion: 0.25
Nodes (7): 05 Modules Plan：按业务功能组织报告, 全局设计哲学, 叙事线, 报告大纲, 核心模块, 模块清单, 次要模块

### Community 31 - "CLI/TUI user loop"
Cohesion: 0.25
Nodes (7): CLI/TUI user loop, TUI 状态模型, Why > What, 亮点与问题, 在项目中的角色, 覆盖率, 跨模块协作

### Community 32 - "08 Insights：架构洞察"
Cohesion: 0.25
Nodes (7): 08 Insights：架构洞察, 1. 统一 runtime 是最重要的架构选择, 2. 上下文管理与安全管理实际上是同一条控制链, 3. 事件协议是复用性的收益来源，也是兼容性债务, 4. 主要亮点, 5. 主要问题与改进方向, 6. 如果重新设计

### Community 33 - "阶段 3：分析计划"
Cohesion: 0.25
Nodes (7): 核心模块, 模块划分, 模式与门槛, 次要模块, 规模估计, 阶段 3：分析计划, 验证计划

### Community 34 - "核心模块：Codex App Server 会话运行时"
Cohesion: 0.25
Nodes (7): Review、Task 与 Transfer, Turn 捕获状态机, 在项目中的角色, 失败恢复与评价, 核心模块：Codex App Server 会话运行时, 覆盖率, 设计思路

### Community 35 - "核心模块：命令与任务编排"
Cohesion: 0.25
Nodes (7): 亮点与问题, 在项目中的角色, 核心数据与流程, 核心模块：命令与任务编排, 模块协作与权衡, 覆盖率, 解决的问题与设计

### Community 36 - "03 Research: HTTPX"
Cohesion: 0.25
Nodes (7): 03 Research: HTTPX, 为什么需要单独做这个项目, 同类对比, 定位, 研究边界, 项目背后的组织动机, 项目解决的核心问题

### Community 37 - "06 Module: Request, Response, Content and Multipart Models"
Cohesion: 0.25
Nodes (7): 06 Module: Request, Response, Content and Multipart Models, Why > What, 亮点与问题, 数据流, 核心模型, 覆盖率明细, 读者问题

### Community 38 - "06 Module: Transport Contract and Execution Adapters"
Cohesion: 0.25
Nodes (7): 06 Module: Transport Contract and Execution Adapters, Contract, Why > What, 代价与边界, 覆盖率明细, 读者问题, 适配器

### Community 39 - "06 Module: URL, Query Parameters and Runtime Configuration"
Cohesion: 0.25
Nodes (7): 06 Module: URL, Query Parameters and Runtime Configuration, Why > What, 亮点与问题, 覆盖率明细, 规范化层, 读者问题, 配置与路由

### Community 40 - "Ruff standard 分析计划"
Cohesion: 0.25
Nodes (7): Ruff standard 分析计划, 报告叙事, 核心模块, 模式和边界, 次要模块, 规模评估, 计划覆盖

### Community 41 - "模块：Python parsing frontend"
Cohesion: 0.25
Nodes (7): Why > What, 叙事衔接, 在项目中的角色, 核心流程, 模块：Python parsing frontend, 覆盖率, 覆盖边界

### Community 42 - "Ruff standard 基线执行日志"
Cohesion: 0.25
Nodes (7): Ruff standard 基线执行日志, 主要读取证据, 写入记录, 失败与限制, 实际过程, 结束验证, 边界

### Community 43 - "Stark Repo Analyzer V1 Implementation Goal"
Cohesion: 0.29
Nodes (7): Graphify And Doctor Boundaries, Objective, Permissions And Failures, Required Order, Stark Repo Analyzer V1 Implementation Goal, Status, Verification

### Community 44 - "物理基线状态"
Cohesion: 0.50
Nodes (4): Current Evidence Boundary, Gate Rules, Physical Baseline Gate, Report Fidelity Boundary

### Community 45 - "分析计划: Click CLI Framework"
Cohesion: 0.29
Nodes (6): 代码规模统计, 分析模式: 标准分析 (standard), 分析计划: Click CLI Framework, 报告大纲, 核心模块, 次要模块

### Community 46 - "调研笔记: Click CLI Framework"
Cohesion: 0.29
Nodes (6): 为什么需要单独做这个项目, 核心文档研读, 竞品/同类项目对比, 调研笔记: Click CLI Framework, 项目背后的组织动机, 项目解决的核心问题

### Community 47 - "ADR 0001: Bounded Standard Scope for a Leaked Source Mirror"
Cohesion: 0.29
Nodes (6): ADR 0001: Bounded Standard Scope for a Leaked Source Mirror, Alternatives Considered, Consequences, Context, Decision, Status

### Community 48 - "Core Module: Command and Skill Extension"
Cohesion: 0.29
Nodes (6): Collaboration, Core Module: Command and Skill Extension, Coverage, Data Structures and Flow, Design Decisions and Trade-offs, Role and Business Problem

### Community 49 - "Core Module: Context and Memory"
Cohesion: 0.29
Nodes (6): Collaboration, Core Module: Context and Memory, Coverage, Data Structures and Flow, Design Decisions and Trade-offs, Role and Business Problem

### Community 50 - "Core Module: Task and Agent Runtime"
Cohesion: 0.29
Nodes (6): Collaboration, Core Module: Task and Agent Runtime, Coverage, Data Structures and Flow, Design Decisions and Trade-offs, Role and Business Problem

### Community 51 - "08 Insights"
Cohesion: 0.29
Nodes (6): 08 Insights, Baseline Use, If Redesigning, Strengths, Systemic Design Philosophy, Tensions and Problems

### Community 52 - "洞察与评价"
Cohesion: 0.29
Nodes (6): 可迁移启发, 如果重新设计, 最有价值的设计, 洞察与评价, 真实代价, 系统性设计哲学

### Community 53 - "执行日志"
Cohesion: 0.29
Nodes (6): 写入纪律, 失败、限制与未执行项, 实际读取过程, 执行日志, 范围确认, 验证命令

### Community 54 - "Execution safety boundary"
Cohesion: 0.29
Nodes (6): Execution safety boundary, Why > What, 亮点与问题, 在项目中的角色, 覆盖率, 跨模块协作

### Community 55 - "Codex standard 基线执行日志"
Cohesion: 0.29
Nodes (6): 1. 范围确认, 2. 实际读取过程, 3. 失败与限制, 4. 覆盖率口径, 5. 结论, Codex standard 基线执行日志

### Community 56 - "核心模块：Claude 生命周期与 Stop review gate"
Cohesion: 0.29
Nodes (6): Stop gate 流程, 在项目中的角色, 核心模块：Claude 生命周期与 Stop review gate, 覆盖率, 设计权衡, 问题

### Community 57 - "核心模块：Job 状态、日志与后台生命周期"
Cohesion: 0.29
Nodes (6): 为什么这样设计, 亮点与问题, 在项目中的角色, 核心模块：Job 状态、日志与后台生命周期, 状态设计, 覆盖率

### Community 58 - "阶段 8：架构洞察"
Cohesion: 0.29
Nodes (6): 三个最有价值的设计选择, 如果重新设计, 学习点, 真实问题与影响, 贯穿全局的设计哲学, 阶段 8：架构洞察

### Community 59 - "执行日志：codex-plugin-cc standard baseline"
Cohesion: 0.29
Nodes (6): 失败与限制, 实际读取过程, 执行日志：codex-plugin-cc standard baseline, 模块与覆盖, 结束状态, 范围与初始化

### Community 60 - "05 Modules Plan: HTTPX"
Cohesion: 0.29
Nodes (6): 05 Modules Plan: HTTPX, Mermaid 主图设计, 报告叙事线, 模块清单, 章节大纲, 过渡逻辑

### Community 61 - "06 Module: CLI and Public API Contract"
Cohesion: 0.29
Nodes (6): 06 Module: CLI and Public API Contract, CLI, 公共契约, 覆盖率明细, 角色, 评价

### Community 62 - "次要模块：语义、LSP 与 ty"
Cohesion: 0.29
Nodes (6): Editor/LSP integration, Python semantic model, ty type-checking platform, 共同角色, 次要模块：语义、LSP 与 ty, 结论

### Community 63 - "05 Modules Plan"
Cohesion: 0.33
Nodes (5): 05 Modules Plan, Business Modules, Module Questions, Narrative Transitions, Report Outline

### Community 64 - "Secondary Module: Entry and Terminal UI"
Cohesion: 0.33
Nodes (5): Coverage, Design Assessment, Evidence, Role, Secondary Module: Entry and Terminal UI

### Community 65 - "Secondary Module: MCP and Plugins"
Cohesion: 0.33
Nodes (5): Coverage, Design Assessment, Evidence, Role, Secondary Module: MCP and Plugins

### Community 66 - "Secondary Module: Remote, IDE and Platform Services"
Cohesion: 0.33
Nodes (5): Coverage, Design Assessment, Evidence, Role, Secondary Module: Remote, IDE and Platform Services

### Community 67 - "07 Cross Validation"
Cohesion: 0.33
Nodes (5): 07 Cross Validation, Corrections and Unverified Items, Cross-Module Design Pattern, Method, Validated Conclusions

### Community 68 - "08 Coverage"
Cohesion: 0.33
Nodes (5): 08 Coverage, Calculation, Core Modules, Secondary Modules, Why the Gaps Exist

### Community 69 - "分析计划"
Cohesion: 0.33
Nodes (5): 分析计划, 分析限制, 模式与门槛, 覆盖计划, 规模估计

### Community 70 - "次要模块：completion、测试与平台基础设施"
Cohesion: 0.33
Nodes (5): Shell completion, 平台、异常与基础设施, 次要模块：completion、测试与平台基础设施, 测试隔离与调用验证, 覆盖率

### Community 71 - "交叉验证"
Cohesion: 0.33
Nodes (5): 交叉洞察, 交叉验证, 已验证结论, 未完全验证项, 验证范围

### Community 72 - "03 Plan：standard 分析计划"
Cohesion: 0.33
Nodes (5): 03 Plan：standard 分析计划, 分析模式, 核心问题, 覆盖计划, 规模估计

### Community 73 - "MCP、skills 与 plugins"
Cohesion: 0.33
Nodes (5): MCP、skills 与 plugins, Why > What, 在项目中的角色, 覆盖率, 跨模块协作

### Community 74 - "Protocol/event contract"
Cohesion: 0.33
Nodes (5): Protocol/event contract, Why > What, 关键模型, 在项目中的角色, 覆盖率

### Community 75 - "07 Cross-validation：交叉验证"
Cohesion: 0.33
Nodes (5): 07 Cross-validation：交叉验证, 交叉结论, 抽查结果, 未能验证, 验证矩阵

### Community 76 - "08 Coverage：覆盖率汇总"
Cohesion: 0.33
Nodes (5): 08 Coverage：覆盖率汇总, 主要原因, 总体结果, 汇总, 统计口径

### Community 77 - "阶段 3：项目调研"
Cohesion: 0.33
Nodes (5): 同类对比, 外部调研边界, 定位与组织动机, 阶段 3：项目调研, 项目解决的核心问题

### Community 78 - "阶段 5：模块计划与报告叙事线"
Cohesion: 0.33
Nodes (5): 业务模块清单, 叙事线, 报告大纲, 过渡逻辑, 阶段 5：模块计划与报告叙事线

### Community 79 - "核心模块：共享 App Server Broker"
Cohesion: 0.33
Nodes (5): 在项目中的角色, 核心模块：共享 App Server Broker, 覆盖率, 设计与边界, 设计决策与评价

### Community 80 - "阶段 7：交叉验证"
Cohesion: 0.33
Nodes (5): 仍未验证, 关键结论抽查, 测试交叉证据, 端到端链路, 阶段 7：交叉验证

### Community 81 - "阶段 8：覆盖率汇总"
Cohesion: 0.33
Nodes (5): 核心模块, 次要模块, 覆盖边界, 计算规则, 阶段 8：覆盖率汇总

### Community 82 - "03 Plan: HTTPX Standard Analysis"
Cohesion: 0.33
Nodes (5): 03 Plan: HTTPX Standard Analysis, 关键探索问题, 分析模式, 覆盖计划, 规模估计

### Community 83 - "07 Cross-Validation"
Cohesion: 0.33
Nodes (5): 07 Cross-Validation, 交叉验证方法, 关键结论抽查, 未通过或待验证, 验证结果

### Community 84 - "08 Coverage"
Cohesion: 0.33
Nodes (5): 08 Coverage, 文件清单口径, 汇总, 统计口径, 限制

### Community 85 - "Ruff 模块规划与报告大纲"
Cohesion: 0.33
Nodes (5): Ruff 模块规划与报告大纲, 业务模块清单, 叙事线, 报告大纲, 覆盖策略

### Community 86 - "交叉验证"
Cohesion: 0.33
Nodes (5): 交叉结论, 交叉验证, 已验证链路, 未完成验证, 验证规则

### Community 87 - "Ruff standard 覆盖率汇总"
Cohesion: 0.33
Nodes (5): Ruff standard 覆盖率汇总, 口径, 核心模块, 次要模块, 解释

### Community 88 - "Ruff 架构洞察"
Cohesion: 0.33
Nodes (5): Ruff 架构洞察, 亮点, 如果重新设计, 贯穿的设计哲学, 问题与改进建议

### Community 89 - "本地参考源码语料"
Cohesion: 0.33
Nodes (5): Acquisition Rule, Purpose, Reproducibility, Storage, 本地参考源码语料

### Community 90 - "Secondary Module: Permission and Shell Security"
Cohesion: 0.40
Nodes (4): Coverage, Evidence and Flow, Role, Secondary Module: Permission and Shell Security

### Community 91 - "App-server integration"
Cohesion: 0.40
Nodes (4): App-server integration, Why > What, 在项目中的角色, 覆盖率

### Community 92 - "physical-baseline-check.sh"
Cohesion: 0.83
Nodes (3): fail(), pass(), physical-baseline-check.sh script

### Community 93 - "Graphify 自动探测必需的 LLM 引擎"
Cohesion: 0.50
Nodes (3): Consequences, Considered Options, Graphify 自动探测必需的 LLM 引擎

### Community 94 - "覆盖率汇总"
Cohesion: 0.50
Nodes (3): 总体, 覆盖率汇总, 限制

### Community 120 - "分析哲学与思维框架"
Cohesion: 0.08
Nodes (23): 亮点的层次, 从项目特征中发现值得深挖的点, 全局关联, 分析哲学与思维框架, 反事实推理, 发现方法, 叙事连贯, 如何与业界对比 (+15 more)

### Community 121 - "cli.py"
Cohesion: 0.06
Nodes (71): Any, CompletedProcess, Namespace, RuntimeError, _adaptive_questions(), analyze(), classify_stream(), cleanup_created_target_graphify() (+63 more)

### Community 122 - "Stark Repo Analyzer"
Cohesion: 0.07
Nodes (26): Analysis Modes, Contributing, Features, File Structure, How It Works, License, Optional Dependencies, Quick Install (+18 more)

### Community 123 - "分析工作流"
Cohesion: 0.08
Nodes (23): 1. 业务视角优先, 2. 抽象层次把控：不贴代码，讲设计, 3. 全局关联, 4. 启发性写作, 5. 深度洞察：Why > What（强制）, Git 项目深度分析技能, When NOT to Use, When to Use (+15 more)

### Community 124 - "doctor.sh"
Cohesion: 0.10
Nodes (19): DOCTOR_EXTRACTION_MODE, DOCTOR_FAILURES, DOCTOR_GRAPH_EXTRACTED, DOCTOR_GRAPH_LINK_SOURCES, DOCTOR_GRAPH_LINKS, DOCTOR_GRAPH_NODE_SOURCES, DOCTOR_GRAPH_NODES, DOCTOR_GRAPH_UNLOCATED_NODES (+11 more)

### Community 125 - "package.json"
Cohesion: 0.22
Nodes (8): description, license, name, repository, type, url, type, version

### Community 126 - "Input and Output Contract"
Cohesion: 0.25
Nodes (7): Failure Contract, Input, Input and Output Contract, Report Contract, Required Flow, Run Workspace, Trigger

### Community 127 - "Graphify Integration Guide"
Cohesion: 0.40
Nodes (4): Bootstrap and Doctor, Consuming the Map, Graphify Integration Guide, Retry Boundary

### Community 128 - "doctor-self-test.sh"
Cohesion: 0.83
Nodes (3): fail(), pass(), doctor-self-test.sh script

### Community 131 - "doctor.sh"
Cohesion: 0.10
Nodes (19): DOCTOR_EXTRACTION_MODE, DOCTOR_FAILURES, DOCTOR_GRAPH_EXTRACTED, DOCTOR_GRAPH_LINK_SOURCES, DOCTOR_GRAPH_LINKS, DOCTOR_GRAPH_NODE_SOURCES, DOCTOR_GRAPH_NODES, DOCTOR_GRAPH_UNLOCATED_NODES (+11 more)

### Community 132 - "真实 UAT 回归测试"
Cohesion: 0.29
Nodes (5): Repository Agent Rules, 分档, 必备证据, 真实 UAT 回归测试, 禁止假通过

### Community 135 - "properties"
Cohesion: 0.04
Nodes (44): const, type, type, type, $id, type, enum, items (+36 more)

### Community 136 - "properties"
Cohesion: 0.06
Nodes (31): const, minimum, type, items, type, type, $id, properties (+23 more)

### Community 137 - "模块分析指南"
Cohesion: 0.15
Nodes (12): Graphify 证据边界, Subagent 协作规范, Subagent 并行分析, 全局视角要求, 分析深度, 核心方法, 核心模块 Subagent Prompt 模板, 模块分析完整性四要素 (+4 more)

### Community 138 - "Reference And Implementation Comparison"
Cohesion: 0.33
Nodes (5): Accepted Differences, Follow-Up Tasks, Real Agent-Gated Runs, Reference And Implementation Comparison, Reimplementation Control-Plane Runs

### Community 141 - "run-contract-check.sh"
Cohesion: 0.83
Nodes (3): fail(), pass(), run-contract-check.sh script

### Community 142 - "skill-structure-check.sh"
Cohesion: 0.83
Nodes (3): fail(), pass(), skill-structure-check.sh script

### Community 144 - "Click 次要模块批量分析"
Cohesion: 0.04
Nodes (45): 1. Shell Completion：把核心参数模型投影到 shell, 2. Testing：在可恢复隔离中重演真实 CLI, 3. Platform Compatibility：把宿主不一致压缩到 I/O 边界, 4. Terminal Presentation Helpers：在不可见控制序列下保持可读布局, 5. Internal State and Sentinels：区分“未设置”和“特殊控制值”, 6. Exceptions：把解析失败转成一致的用户反馈, 7. Public Export Surface：稳定地把内部能力变成 Click API, 8. 设计收束 (+37 more)

### Community 147 - "Stark Repo Analyzer V1 Release Report"
Cohesion: 0.33
Nodes (5): Delivered (Conditional Release), High-Risk Review, Regression Evidence, Residual Scope, Stark Repo Analyzer V1 Release Report

### Community 148 - "output"
Cohesion: 0.05
Nodes (42): includeDiffs, includeLogs, sortByChanges, ignore, customPatterns, useDefaultPatterns, useDotIgnore, useGitignore (+34 more)

### Community 149 - "1. Graphify CLI"
Cohesion: 0.06
Nodes (33): 1. Graphify CLI, 2. Tree-sitter core and py-tree-sitter, 3. Repomix (`yamadashy/repomix`), 4. Comparative implications for a hybrid architecture, 5. Open questions and limitations, `benchmark`, Configuration contract, Core model and parsing API (+25 more)

### Community 150 - "Hybrid code intelligence rollout and evaluation plan"
Cohesion: 0.06
Nodes (31): 10. Go, no-go, and rollback, 11. Required evaluation record, 12. Decision report shape, 1. Decision to be tested, 2. Non-negotiable V1 preservation, 3. Terminology and evidence boundary, 4. Compared paths, 5. Fixed evaluation corpus and run matrix (+23 more)

### Community 151 - "ANALYSIS_REPORT.md"
Cohesion: 0.07
Nodes (26): 1. 场景与项目定位, 2. 项目全景, 3. Graphify 证据边界, 4. 最终业务模块与叙事, 5. 调研与执行计划, Analysis Requirements, Core Modules, External Research (+18 more)

### Community 152 - "Analysis Plan"
Cohesion: 0.08
Nodes (26): 1. 在项目中的角色, 1. 在项目中的角色, 1. 在项目中的角色与业务问题, 2. 业务问题与设计思路, 2. 从装饰器到可执行命令树, 3. 核心数据结构, 4. Context/Command 生命周期, 5. token-to-value 流程 (+18 more)

### Community 153 - "模块：参数解析与类型转换"
Cohesion: 0.10
Nodes (20): 10. 覆盖率明细, 1. 在项目中的角色, 2. 业务问题与设计思路, 3.1 语法层：`_OptionParser`, 3.2 语义层：`Parameter`, 3. 两层解析设计, 4.1 `ParamType`：类型协议而非单一转换函数, 4.2 `Parameter`：值处理所需的声明状态 (+12 more)

### Community 154 - "终端交互与帮助输出"
Cohesion: 0.10
Nodes (19): 1. 在项目中的角色, 2.1 同一份元数据服务人和 CI, 2.2 交互输入必须沿用类型契约, 2.3 TTY 与非 TTY 不是两个 API, 2.4 替代方案及代价, 2. 业务问题与设计思路, 3. 核心数据结构与边界, 4.1 Help 流程 (+11 more)

### Community 155 - "Problems And Resolutions"
Cohesion: 0.13
Nodes (15): 1. Graphify output could cross the source boundary, 2. A graph file alone is not evidence of a usable analysis, 3. Resume needed to preserve raw Graphify evidence, 4. Ruff repeatedly stalled during semantic extraction, 5. Missing detailed Graphify stdout/stderr, 6. Official configuration tuning was investigated, then explicitly deferred, 7. Physical baseline report depth differs from reference reports, 7. Ruff code-only continuation (+7 more)

### Community 156 - "Graph Report - /private/tmp/stark-click-code-only-pilot  (2026-07-13)"
Cohesion: 0.15
Nodes (12): Candidate Source Paths, Communities, Community Hubs (Navigation), Corpus Check, Edge Evidence Samples, God Nodes (most connected - your core abstractions), Graph Report - normalized source evidence, Graph Report - /private/tmp/stark-click-code-only-pilot  (2026-07-13) (+4 more)

### Community 157 - "Ruff 架构分析报告"
Cohesion: 0.15
Nodes (12): 1. CLI 与配置：把用户意图变成可复现状态, 2. lint/fix：诊断先于副作用, 3. formatter 与 printer：两种“打印”共享稳定结果观, 4. 次要边界, 5. 交叉结论与评价, Graphify code-only 与 semantic Graphify, Ruff 架构分析报告, 交付索引 (+4 more)

### Community 158 - "click"
Cohesion: 0.17
Nodes (12): failed_attempts, p2, p4, reference_entrypoint, repeatability, runs, source_commit, v1_code_only_pilot (+4 more)

### Community 160 - "命令模型与上下文执行"
Cohesion: 0.18
Nodes (10): 1. 在项目中的角色与业务问题, 2. 从装饰器到可执行命令树, 3. 核心数据结构, 4. Context/Command 生命周期, 5. 与其他模块的设计协同, 6. 关键权衡与深度洞察, 7. 亮点、问题与改进思考, 8. 涉及源码路径 (+2 more)

### Community 161 - "本地开源工具配置"
Cohesion: 0.18
Nodes (11): 10. 禁止配置, 11. 每次运行必须记录, 1. 版本锁定, 2. 隔离工作目录, 3. Git SourceUniverse, 5. Repomix hotspot pack, 6. Serena OSS-LSP precision adapter, 7. Universal Ctags fallback (+3 more)

### Community 162 - "Codex CLI 架构分析（Physical Baseline）"
Cohesion: 0.20
Nodes (9): 1. CLI 是组合根, 2. Core 把一次 turn 变成受治理的操作, 3. Exec 为自动化建立协议边界, 4. Configuration 与 policy, 5. Sandbox 是跨平台执行隔离层, 6. 评价与启发, Codex CLI 架构分析（Physical Baseline）, 覆盖与限制 (+1 more)

### Community 163 - "Codex CLI 架构分析（Physical Baseline）"
Cohesion: 0.20
Nodes (9): 1. CLI 是组合根, 2. Core 把一次 turn 变成受治理的操作, 3. Exec 为自动化建立协议边界, 4. Configuration 与 policy, 5. Sandbox 是跨平台执行隔离层, 6. 评价与启发, Codex CLI 架构分析（Physical Baseline）, 覆盖与限制 (+1 more)

### Community 164 - "HTTPX 架构分析报告"
Cohesion: 0.20
Nodes (9): 1. 客户端与请求生命周期, 2. Request/Response 模型, 3. Transport 边界, 4. 内容与解码, 5. 评价与启发, HTTPX 架构分析报告, 一句话结论, 证据与限制 (+1 more)

### Community 165 - "HTTPX 架构分析报告"
Cohesion: 0.20
Nodes (9): 1. 客户端与请求生命周期, 2. Request/Response 模型, 3. Transport 边界, 4. 内容与解码, 5. 评价与启发, HTTPX 架构分析报告, 一句话结论, 证据与限制 (+1 more)

### Community 166 - "projects"
Cohesion: 0.20
Nodes (9): analysis_mode, input, pending, projects, schema_version, source_commit, P3 target-output isolation for httpx, claude-code and codex, P4 repeatability comparison for httpx, claude-code and codex (+1 more)

### Community 167 - "claude-code"
Cohesion: 0.20
Nodes (10): comparison, graphify, p2, p4, reference_entrypoint, runs, source_commit, claude-code (+2 more)

### Community 168 - "codex"
Cohesion: 0.20
Nodes (10): comparison, graphify, p2, p4, reference_entrypoint, runs, source_commit, codex (+2 more)

### Community 169 - "codex-plugin-cc"
Cohesion: 0.20
Nodes (10): failed_attempts, p2, p4, reference_entrypoint, repeatability, runs, source_commit, codex-plugin-cc (+2 more)

### Community 170 - "httpx"
Cohesion: 0.20
Nodes (10): comparison, graphify, p2, p4, reference_entrypoint, runs, source_commit, httpx (+2 more)

### Community 171 - "ruff"
Cohesion: 0.20
Nodes (10): ruff, comparison, graphify, p2, p4, reference_entrypoint, runs, source_commit (+2 more)

### Community 172 - "OSS and local-only tool selection for hybrid code intelligence"
Cohesion: 0.20
Nodes (10): 1. Selection policy, 2. Selection matrix, 3. Selected architecture, 4. Corpus and evidence rules, 5. Admission gates, 6. Transitive dependency audit, 7. Explicit exclusions, 8. Final decision summary (+2 more)

### Community 173 - "可复用经验"
Cohesion: 0.22
Nodes (9): 1. 图谱产物必须隔离，且健康检查是分析前提, 2. Graphify 用于导航，源码负责裁决, 3. 失败运行必须保留失败分类，不能被后续文字“修复”, 4. code-only 是独立证据模式，不能替代未完成的语义模式, 5. 物理运行证据、报告深度与项目完成状态必须分开表述, V1 执行与证据边界, 可复用经验, 当前待验证观察 (+1 more)

### Community 174 - "manifest.json"
Cohesion: 0.22
Nodes (8): analysis_mode, files, graph, edges, nodes, schema_version, source_commit, status

### Community 175 - "Research Draft"
Cohesion: 0.22
Nodes (8): Comparable approaches, Core problem, Organization/product motivation, Research Draft, Scope, Sources consulted, Technical value proposition, Unperformed

### Community 176 - "核心模块分析"
Cohesion: 0.25
Nodes (7): 1. 启动与运行时编排, 2. 工具执行循环, 3. MCP, 4. 会话与远程, 核心模块分析, 覆盖率明细, 跨模块判断

### Community 177 - "1. Shell Completion：把核心参数模型投影到 shell"
Cohesion: 0.25
Nodes (8): 1. Shell Completion：把核心参数模型投影到 shell, Why > What, 全局角色, 实现方式, 文件列表, 核心流程, 特别之处, 职责

### Community 178 - "2. Testing：在可恢复隔离中重演真实 CLI"
Cohesion: 0.25
Nodes (8): 2. Testing：在可恢复隔离中重演真实 CLI, Why > What, 全局角色, 实现方式, 文件列表, 核心流程, 特别之处, 职责

### Community 179 - "V2 混合代码智能架构"
Cohesion: 0.25
Nodes (8): 1. 设计目标, 3. V2 统一证据契约, 4. 产物布局, 5. 状态机与失败语义, 6. 缓存和增量更新, 7. 安全、隐私和许可证闸门, 8. 关键不变量, V2 混合代码智能架构

### Community 180 - "2. 模块与接口"
Cohesion: 0.25
Nodes (8): 2.1 `SourceUniverse`, 2.2 `StaticGraph`, 2.3 `HotspotRanker`, 2.4 `PrecisionResolver`, 2.5 `ContextPack`, 2.6 `DeepDataflow`, 2.7 `AgentAnalysis`, 2. 模块与接口

### Community 181 - "2. Repomix 1.16.1 hotspot pack"
Cohesion: 0.25
Nodes (8): 2. Repomix 1.16.1 hotspot pack, 3. 配置样例校验, 4. 当前可证实与不可证实的结论, 只读实验记录, 实验 A：三份全文 + 三份压缩, 实验 B：六份全部压缩, 目标和文件集, 结论

### Community 182 - "开源混合代码智能架构方案"
Cohesion: 0.25
Nodes (8): 为什么不是“只按目录分层”, 决策摘要, 对 V1 的影响, 工具角色与开源约束, 开源混合代码智能架构方案, 推荐流程, 文档导航, 结论

### Community 183 - "Claude Code 源码架构分析"
Cohesion: 0.29
Nodes (6): Claude Code 源码架构分析, 关键设计, 执行边界, 证据索引, 评价与启发, 项目全景

### Community 184 - "执行日志"
Cohesion: 0.29
Nodes (6): Graphify sidecar, 实际命令, 工具与偏差, 执行日志, 来源与限制, 覆盖

### Community 185 - "Claude Code 源码架构分析"
Cohesion: 0.29
Nodes (6): Claude Code 源码架构分析, 关键设计, 执行边界, 证据索引, 评价与启发, 项目全景

### Community 186 - "交叉验证与质量门控"
Cohesion: 0.29
Nodes (6): Graphify 与源码边界, 交叉验证与质量门控, 源码裁决, 覆盖率与限制裁决, 跨模块结论, 验证范围

### Community 187 - "架构洞察与评价"
Cohesion: 0.29
Nodes (6): 如果重新设计, 对 code-only Graphify V1 的判断, 最有价值的设计, 架构洞察与评价, 真实代价, 系统性设计哲学

### Community 188 - "structure_evidence"
Cohesion: 0.29
Nodes (7): structure_evidence, code_files, kind, raw_edges, raw_nodes, semantic_extraction, version

### Community 190 - "1. Graphify 0.9.13 code-only"
Cohesion: 0.29
Nodes (7): 1. Graphify 0.9.13 code-only, 与当前 doctor 的兼容性观察, 命令, 安装/缓存边界, 对旧耗时数据的解释, 目标, 结果

### Community 191 - "V1 固定 Graphify code-only"
Cohesion: 0.33
Nodes (5): Decision, Evidence Boundary, Supersedes, V1 固定 Graphify code-only, Why

### Community 192 - "Meta_Kim 采集清单"
Cohesion: 0.33
Nodes (6): Meta_Kim 采集清单, 为什么不逐字导出 1,414 条记录, 归类方法, 维护边界, 证据等级, 采集范围

### Community 193 - "结构证据与验收经验"
Cohesion: 0.33
Nodes (6): 1. doctor 是强制侧车，不是可选诊断, 2. 图谱输出必须与目标源码隔离, 3. 图谱只能导航，源码才裁决, 4. code-only 必须显式标识，不能伪装成语义图谱, 5. 对工具版本与安装失败要记录事实，不要猜测环境, 结构证据与验收经验

### Community 194 - "失败、恢复与未完成事项"
Cohesion: 0.33
Nodes (6): 1. Ruff 语义提取失败必须保留为失败, 2. 失败原因要停在证据能支持的粒度, 3. 恢复路径需要保留原始证据链, 4. 当前风险与“已完成”必须并列呈现, 5. 真实 UAT 不能由静态证据替代, 失败、恢复与未完成事项

### Community 195 - "协作与执行方法经验"
Cohesion: 0.33
Nodes (6): 1. 每项工作都要有单一产物与验证证据, 2. 代理并发不能降低证据质量, 3. 先做只读审计，再修改控制面, 4. 用户决策要与事实记录分开, 5. 经验库本身也需要可审计边界, 协作与执行方法经验

### Community 196 - "研究草稿"
Cohesion: 0.33
Nodes (5): 为什么需要单独做这个项目, 研究草稿, 竞品/同类项目对比, 组织动机, 项目解决的核心问题

### Community 197 - "执行日志"
Cohesion: 0.33
Nodes (5): 实际命令, 工具与偏差, 执行日志, 来源与限制, 覆盖

### Community 198 - "3. Platform Compatibility：把宿主不一致压缩到 I/O 边界"
Cohesion: 0.33
Nodes (6): 3. Platform Compatibility：把宿主不一致压缩到 I/O 边界, Why > What, 全局角色, 实现方式, 文件列表, 职责

### Community 199 - "6. Exceptions：把解析失败转成一致的用户反馈"
Cohesion: 0.33
Nodes (6): 6. Exceptions：把解析失败转成一致的用户反馈, Why > What, 全局角色, 实现方式与特别之处, 文件列表, 职责

### Community 200 - "Analysis Plan"
Cohesion: 0.33
Nodes (5): Adaptive Questions, Analysis Plan, Required Sequence, Research Boundary, Size by Candidate Area

### Community 201 - "Module Analysis Plan"
Cohesion: 0.33
Nodes (5): Analysis Requirements, Core Modules, Module Analysis Plan, Narrative, Secondary Modules

### Community 202 - "CLI Dispatch"
Cohesion: 0.33
Nodes (5): CLI Dispatch, Core structure and flow, Coverage, Dependencies and tradeoffs, Role

### Community 203 - "Core Orchestration"
Cohesion: 0.33
Nodes (5): Core Orchestration, Coverage, Cross-module contract, Design decisions, Role

### Community 204 - "Insights"
Cohesion: 0.33
Nodes (5): Design philosophy, Insights, Re-design thought experiment, Risks and improvement directions, Strengths

### Community 205 - "Research Draft"
Cohesion: 0.33
Nodes (5): Research Draft, 为什么需要单独做这个项目, 竞品定位, 组织动机, 项目解决的核心问题

### Community 206 - "Client Lifecycle and Request Pipeline"
Cohesion: 0.33
Nodes (5): Client Lifecycle and Request Pipeline, 关键决策, 协作与评价, 覆盖率明细, 角色与流程

### Community 207 - "03 研究说明"
Cohesion: 0.33
Nodes (5): 03 研究说明, 独特价值假设, 研究边界, 竞品定位, 问题与定位

### Community 208 - "08 洞察"
Cohesion: 0.33
Nodes (5): 08 洞察, 1. Ruff 的真正抽象是“可复用结果”，不是命令, 2. 性能目标通过边界组合实现, 3. 显式状态换取可审计性, 4. 改进建议

### Community 209 - "产品契约与演进经验"
Cohesion: 0.40
Nodes (5): 1. V1 的质量边界优先于“尽量给出结果”, 2. 规格需要有确定性实现载体, 3. 版本演进必须保持模式和证据的可比较性, 4. 发布状态必须从目标与证据状态推导, 产品契约与演进经验

### Community 210 - "物理基线与报告质量经验"
Cohesion: 0.40
Nodes (5): 1. reference-runs 与 physical-runs 证明不同事实, 2. P2 与 P4 是独立门槛, 3. 报告深度应按模块分解和验证步骤比较, 4. 物理运行的提示词本身是证据的一部分, 物理基线与报告质量经验

### Community 211 - "洞察草稿"
Cohesion: 0.40
Nodes (4): 亮点, 洞察草稿, 系统性设计哲学, 风险与重设计建议

### Community 212 - "2. 业务问题与设计思路"
Cohesion: 0.40
Nodes (5): 2.1 同一份元数据服务人和 CI, 2.2 交互输入必须沿用类型契约, 2.3 TTY 与非 TTY 不是两个 API, 2.4 替代方案及代价, 2. 业务问题与设计思路

### Community 213 - "4. Terminal Presentation Helpers：在不可见控制序列下保持可读布局"
Cohesion: 0.40
Nodes (5): 4. Terminal Presentation Helpers：在不可见控制序列下保持可读布局, 全局角色, 实现方式与特别之处, 文件列表, 职责

### Community 214 - "5. Internal State and Sentinels：区分“未设置”和“特殊控制值”"
Cohesion: 0.40
Nodes (5): 5. Internal State and Sentinels：区分“未设置”和“特殊控制值”, 全局角色, 实现方式与特别之处, 文件列表, 职责

### Community 215 - "8. 关键设计权衡与洞察"
Cohesion: 0.40
Nodes (5): 8. 关键设计权衡与洞察, 亮点与问题, 决策一：语法 parser 不做类型转换, 决策三：来源是有序元数据，而非布尔标记, 决策二：类型对象同时承担转换、诊断和交互元数据

### Community 216 - "Click code-only V1 对比结果"
Cohesion: 0.40
Nodes (4): Click code-only V1 对比结果, 下一步判定标准, 结果摘要, 质量结论

### Community 217 - "Analysis Plan"
Cohesion: 0.40
Nodes (4): Analysis Plan, Mode and bounded scope, Planned narrative, Required workflow deviations

### Community 218 - "Cross Validation"
Cohesion: 0.40
Nodes (4): Architectural insight, Cross Validation, Unverified, Verified relationships

### Community 219 - "Analysis Plan"
Cohesion: 0.40
Nodes (4): Analysis Plan, Mode and scope, Report outline, Unavailable workflow items

### Community 220 - "Insights"
Cohesion: 0.40
Nodes (4): Insights, 亮点, 系统性设计哲学, 风险与重设计

### Community 221 - "07 交叉验证"
Cohesion: 0.40
Nodes (4): 07 交叉验证, Graphify 边界, 已验证链路, 未决风险

### Community 222 - "项目经验库"
Cohesion: 0.50
Nodes (4): 使用规则, 本次覆盖, 索引, 项目经验库

### Community 223 - "模块叙事与模块规划"
Cohesion: 0.50
Nodes (3): 报告结构, 模块, 模块叙事与模块规划

### Community 224 - "3. 核心数据结构与边界"
Cohesion: 0.50
Nodes (4): 3. 核心数据结构与边界, HelpFormatter 的内存构建模型, Prompt 的值转换边界, 输出与流生命周期

### Community 225 - "4. 核心流程"
Cohesion: 0.50
Nodes (4): 4.1 Help 流程, 4.2 Prompt 流程, 4.3 普通输出、pager 与 progress 流程, 4. 核心流程

### Community 226 - "4. 核心数据结构"
Cohesion: 0.50
Nodes (4): 4.1 `ParamType`：类型协议而非单一转换函数, 4.2 `Parameter`：值处理所需的声明状态, 4.3 `Context` 的两个输出槽, 4. 核心数据结构

### Community 227 - "7. Public Export Surface：稳定地把内部能力变成 Click API"
Cohesion: 0.50
Nodes (4): 7. Public Export Surface：稳定地把内部能力变成 Click API, 全局角色, 实现方式与特别之处, 职责

### Community 228 - "Research Context"
Cohesion: 0.50
Nodes (3): External Research, Local Evidence, Research Context

### Community 229 - "覆盖率汇总"
Cohesion: 0.50
Nodes (3): 总体, 未覆盖与验证边界, 覆盖率汇总

### Community 230 - "4. Graphify code-only"
Cohesion: 0.50
Nodes (4): 4. Graphify code-only, Ignore 与 corpus reconciliation, 初次建立静态图, 增量更新

### Community 231 - "3. 两层解析设计"
Cohesion: 0.67
Nodes (3): 3.1 语法层：`_OptionParser`, 3.2 语义层：`Parameter`, 3. 两层解析设计

## Knowledge Gaps
- **1416 isolated node(s):** `DOCTOR_PHASE`, `DOCTOR_STATUS`, `DOCTOR_TARGET`, `DOCTOR_WORK_DIR`, `DOCTOR_GRAPHIFY_OK` (+1411 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **88 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Analysis Plan` connect `Analysis Plan` to `3. 核心数据结构与边界`, `4. 核心流程`, `4. 核心数据结构`, `7. Public Export Surface：稳定地把内部能力变成 Click API`, `覆盖率`, `覆盖率`, `3. Platform Compatibility：把宿主不一致压缩到 I/O 边界`, `3. 两层解析设计`, `6. Exceptions：把解析失败转成一致的用户反馈`, `1. Shell Completion：把核心参数模型投影到 shell`, `2. Testing：在可恢复隔离中重演真实 CLI`, `2. 业务问题与设计思路`, `4. Terminal Presentation Helpers：在不可见控制序列下保持可读布局`, `5. Internal State and Sentinels：区分“未设置”和“特殊控制值”`, `ANALYSIS_REPORT.md`, `8. 关键设计权衡与洞察`, `10. 覆盖率明细`, `6. 深度模块分析`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `Primary-source tool research for hybrid code intelligence` connect `1. Graphify CLI` to `README.md`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Why does `Hybrid code intelligence rollout and evaluation plan` connect `Hybrid code intelligence rollout and evaluation plan` to `README.md`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `analyze()` (e.g. with `main()` and `.test_analyze_rejects_nonempty_workspace()`) actually correct?**
  _`analyze()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `CliContractTests` (e.g. with `RunFailure` and `ContractError`) actually correct?**
  _`CliContractTests` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DOCTOR_PHASE`, `DOCTOR_STATUS`, `DOCTOR_TARGET` to the rest of the system?**
  _1416 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `参考输出基线` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._