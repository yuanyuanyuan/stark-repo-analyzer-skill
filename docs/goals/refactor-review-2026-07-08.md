# Review 文档：12 项问题根因分析 + 解决方案（2026-07-08）

> **状态：待用户审阅** | 审阅通过后启动工程师实施（T01-T12）
> 输入：PM 增量 PRD + 架构师设计文档（均已通过 file:line 代码核实）

---

## 一、12 项问题 → 10 个需求 → 逐项根因（一句话版）

| 原问题# | 需求 | 优先级 | 根因（file:line） | 解决方案核心 |
|---------|------|--------|-------------------|-------------|
| #1 | REQ-01 输出目录重命名 | P0 | `build_parser()` default `"analysis"`（:2716）；`IGNORE_DIRS` 写死旧名（:37-62）；无 gitignore 提醒（:2741） | default 改 `.stark-repo-analyzer`；IGNORE_DIRS 同步更新；完成后 stdout 提醒 + 自动追加 .gitignore |
| #2 | REQ-02 运行时预检 | P0 | `analyze()` 在 `apply_config` 后直接 `checkout_target`（:2629），无环境检查；npx/codex 缺失跑到一半才报错 | 新增 `preflight_check()` 插入 `apply_config` 之后，5 项检查（Python/git/npx/tree-sitter/codex），必需项 FAIL→exit(1) |
| #3 | REQ-03 LLM-judge 修复 | P0 | `DEFAULT_MODEL="haiku-4.5"`（llm_judge.py:22）硬编码不可用模型；失败只输出退出码（:92）无模型名无 stderr | default 改空字符串→不传 `--model`→用 codex 默认模型；失败输出含模型名+stderr 摘要 |
| #4 | REQ-04 执行进度反馈 | P0 | `timed_stage()`（:157-176）只写 performance dict 不向 stdout 输出；用户只看到最终 `print("分析完成")` | `timed_stage` 升级为 `ProgressReporter` 类，每个 stage 开始/完成输出 `[N/M]` 进度行 + agent 子任务进度 |
| #5 | REQ-05 Agent 默认开启 | P0 | `--agent-mode` default `"deterministic"`（:2727）；`set_if_default` defaults 同步（:408） | default 改 `"codex"`；预检 codex 不可用时自动降级 deterministic + WARN + CONFIG_EFFECTIVE 记 `agent_mode_degraded: true` |
| #6/#8/#9 | REQ-06 产物结构重组 | P0 | 26 个文件平铺根目录，人机混杂；`write_*` 函数都直接写 `output / "filename"` | 分层：`reports/`（人类）+ `data/`（agent）+ `diagnostics/`（诊断）+ `logs/`（日志）+ 保留 slices/drafts/agent-runs/acceptance |
| #7 | REQ-07 任务运行日志 | P1 | 只有最终产物文件，无过程记录目录；`timed_stage` 的 performance dict 仅落盘为 PERFORMANCE_REPORT | 新增 `LogWriter` 类写 `logs/run-YYYYMMDD-HHMMSS.md`，按 step 分节记录开始/结束/耗时/状态 |
| #10 | REQ-08 PERF_REPORT 定位 | P1 | 内容是性能诊断但放根目录与 ANALYSIS_REPORT 平级，用户不清楚定位；SKILL.md 未强调"不是分析结论" | 移入 `diagnostics/`；顶部加定位说明段落；README 标注"🔧 诊断报告"；新增"如何阅读本报告"小节 |
| #11 | REQ-09 名片扩容 | P1 | `write_manifest_card()` 硬截断 `card[:5_000]`（:1389）；标题"5KB 项目名片"（:1373）；信息量不足 | 截断改 `card[:10_000]`；新增 8 字段（包管理/依赖数/入口点/CI-CD/测试框架/最近提交/贡献者数/目录树2层） |
| #12 | REQ-10 模块拆分 | P1(先行) | 单文件 2746 行 ~60 个函数（`wc -l` 确认）；`_LOADER`（:31）`_TOKEN_COLLECTOR`（:34）全局状态 | 拆为 11 个 `analyzer_*.py` + 入口 < 200 行；全局状态放 `analyzer_common.py` 模块级单例 |

---

## 二、关键架构决策（需你拍板）

### 2.1 模块拆分方案（REQ-10）

**11 个模块 + 入口文件**，放在 `scripts/` 目录下：

| 模块 | 职责 |
|------|------|
| `analyzer_common.py` | 常量/共享状态(`_LOADER`/`_TOKEN_COLLECTOR`)/通用工具/`ProgressReporter`/`LogWriter` |
| `analyzer_config.py` | 配置加载与合并 |
| `analyzer_checkout.py` | 仓库检出与文件枚举 |
| `analyzer_slicing.py` | repomix 切片生成 |
| `analyzer_metadata.py` | 元数据与项目名片 |
| `analyzer_coverage.py` | 符号提取与覆盖率门控 |
| `analyzer_modules.py` | 模块计划与草稿 |
| `analyzer_crossref.py` | Cross-ref 校验 |
| `analyzer_agent.py` | Agent 执行与调度 |
| `analyzer_reports.py` | 报告渲染与索引 |
| `analyzer_reporting.py` | SLA/性能/状态/配置报告 |
| `analyzer_acceptance.py` | 验收脚本生成 |
| `repo_analyzer.py`（入口） | `analyze`/`build_parser`/`main`/`preflight_check`/`count_stages`（< 200 行） |

- **全局状态处理**：`_LOADER`/`_TOKEN_COLLECTOR` 保持模块级单例放 `analyzer_common.py`（不改参数传递，最小变更）
- **拆分顺序**：从依赖最少的 common 开始，每抽一个模块立即跑 `pytest + acceptance/check.sh`
- **依赖图无循环**（架构师已验证）

### 2.2 产物目录终案（REQ-06）

```
.stark-repo-analyzer/
├── README.md                 # 顶层索引（人类入口，含目录说明表）
├── reports/                  # 📖 人类阅读（ANALYSIS_REPORT*、manifest-card、coverage、sla、state）
├── data/                     # 🤖 AI agent（AGENT_SUMMARY、REPORT_DATA、CONFIG_EFFECTIVE、repo-type、module-ids、symbols、mcp-tools）
├── slices/                   # 🤖 原料切片
├── drafts/                   # 🤖 模块草稿
├── agent-runs/               # 🤖 agent 证据
├── diagnostics/              # 🔧 诊断（meta.txt、PERFORMANCE_REPORT.{md,json}）
├── logs/                     # 📋 运行日志（run-YYYYMMDD-HHMMSS.md）
└── acceptance/               # ✅ 验收脚本
```

- **文件名去编号前缀**：`02a-manifest-card.md` → `manifest-card.md`（架构师已核实无外部消费者依赖原文件名；`ANALYSIS_REPORT*` 语义前缀保留）
- **render_report.py** 新增 `--output-dir` 参数；**llm_judge.py** `_read_reports()` 改从 `reports/` 读取

### 2.3 执行顺序（T01-T12）

```
Phase 0（先行，纯搬迁）     Phase 1（独立，可并行）    Phase 2（核心体验）        Phase 3（收尾）
T01 analyzer_common ──┐     T06 LLM-judge 修复 ───┐   T08 目录重命名+结构重组    T11 PERF定位
T02 analyzer_config ──┤     T07 名片扩容 10KB ────┤   T09 预检+Agent默认+降级    T12 SKILL.md更新
T03 checkout+slicing ─┤                           │   T10 进度输出+任务日志
T04 modules+coverage ─┤                           │
T05 agent+reports ────┘                           │
    ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    T05 完成后 → T08/T09/T10 并行 → T11/T12 收尾
```

---

## 三、10 个待确认问题（Q1-Q10）及建议

| # | 问题 | PM 建议 | 架构师决议 | 需你拍板？ |
|---|------|---------|-----------|-----------|
| Q1 | 产物放 CWD 还是仓库根目录？ | 保持 CWD（避免远程仓库产物随 /tmp 丢失） | 保持 CWD | ✅ 确认即可 |
| Q2 | codex 不可用时如何处理？ | 自动降级 deterministic + WARN | 自动降级 + CONFIG_EFFECTIVE 记 `agent_mode_degraded: true` | ✅ 确认即可 |
| Q3 | 10KB 名片增加哪些字段？ | 全部采纳 8 项（包管理/依赖数/入口点/CI-CD/测试框架/最近提交/贡献者数/目录树2层） | 全部采纳，优先保证入口点+依赖数+CI/CD+测试框架 | ✅ 确认即可 |
| Q4 | PERFORMANCE_REPORT 保留还是并入？ | 保留+加定位说明，移入 diagnostics/ | 保留+加定位说明+加"如何阅读"小节 | ✅ 确认即可 |
| Q5 | 文件名去编号前缀？ | 建议保留（降低外部消费者破坏风险） | **建议去掉**（已核实无外部消费者依赖；子目录已提供组织上下文） | ⚠️ PM 和架构师意见不同，需你决定 |
| Q6 | 模块拆分边界？ | PM 只定验收标准，交架构师 | 11 模块方案（见 2.1） | ❌ 架构师已定 |
| Q7 | 进度输出纯文本还是 JSON？ | 纯文本（主要读者是主会话转述） | 纯文本（`[N/M]` 格式） | ✅ 确认即可 |
| Q8 | 日志单文件还是按 step 拆？ | 单 Markdown 文件 | 单文件 `run-YYYYMMDD-HHMMSS.md` | ✅ 确认即可 |
| Q9 | SKILL.md 本轮改？ | 必须改，作为最后一道工序 | 必须改（T12） | ❌ 已确认 |
| Q10 | 支持自定义目录名？ | 通过 `--output` 已支持 | 默认 `.stark-repo-analyzer`，可 `--output` 覆盖 | ❌ 已有能力 |

**唯一分歧点：Q5 文件名编号前缀**
- PM 倾向保留（保守，防外部消费者）
- 架构师建议去掉（已核实 graphify 解耦、check.sh 自生成、SKILL.md/测试本轮同步改，无外部依赖）
- **如果你没有其他外部脚本依赖 `02a-` 等编号前缀文件名，建议去掉（更简洁）**

---

## 四、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 拆分遗漏隐式依赖 | import 错误 | 每抽一个模块立即跑 pytest + 245+ 验收 |
| 路径变更面广（~15 个 write_* + check.sh + render_report + llm_judge + SKILL.md + 测试） | 遗漏路径→验收失败 | 245+ 验收是安全网，遗漏立即暴露 |
| agent 默认开启后无 codex 环境降级 | 用户可能不期望降级 | WARN 提示 + CONFIG_EFFECTIVE 记录，降级透明 |
| 名片 10KB 影响 agent prompt 上下文 | agent prompt 变长 | 10KB 仍在合理范围；高优先级字段排前面 |

---

## 五、实施计划摘要

- **Phase 0**（T01-T05）：模块拆分，纯搬迁行为不变，245+ 验收做安全网
- **Phase 1**（T06-T07）：LLM-judge 修复 + 名片扩容，与 Phase 0 可并行
- **Phase 2**（T08-T10）：目录重命名+结构重组 / 预检+Agent默认 / 进度+日志，Phase 0 完成后并行
- **Phase 3**（T11-T12）：PERF 定位澄清 + SKILL.md 全面更新

**预计交付物**：
- 12 个 `analyzer_*.py` 新模块 + 瘦身后 `repo_analyzer.py`
- 修改 `llm_judge.py`、`render_report.py`、`SKILL.md`、`tests/`
- 新增 4 个 ADR（0016-0019）
- 245+ 验收全 PASS + 测试全 PASS

---

## 六、下一步

**等你 review 通过后**，我将启动工程师寇豆码按 T01→T12 顺序实施，QA 严过关做回归测试。

如有任何调整意见，请直接指出。
