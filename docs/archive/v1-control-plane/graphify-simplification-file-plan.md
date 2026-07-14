# Repo Analyzer + Graphify 精简方案（逐文件）

状态：`superseded`（仅指活动控制面）。当前执行顺序以
[`docs/exec-plans/graphify-simplification-plan.md`](../../exec-plans/graphify-simplification-plan.md)
为准；本文保留为逐文件迁移清单和设计输入，不能单独授权实施，且冲突时服从活动 roadmap、执行计划与 ADR。

## 1. 目标

在参考 `repo-analyzer` 的分析方法上保留一个低侵入 Graphify 增强层：Graphify 可用时执行 code-only 提取、本地聚类、规范化、健康验证和导航 map；Graphify 不可用时引导用户安装，并在用户明确选择后允许进入原版兼容流程。程序层不接管模式交互、模块划分、源码阅读、覆盖率、交叉验证或报告融合。

迁移完成后的产品主线：

```text
用户输入
  -> Agent 解析仓库与 standard/deep
  -> 检查 Graphify
     -> 可用：graphify gate -> 导航 map -> 原参考分析流程
     -> 不可用：安装指引 -> 用户选择安装复检或原版兼容流程
  -> Agent 划分业务模块并阅读源码
  -> subagent 分析（不可用时先征得用户同意）
  -> 主 Agent 交叉验证与覆盖率汇总
  -> 单一 ANALYSIS_REPORT.md
```

## 2. 不做事项

- 本方案不直接改实现，不删除文件，不移动历史证据，也不运行真实回归 UAT。
- 不恢复 `quick`；产品只保留 `standard` 与 `deep`。
- 不引入 Graphify semantic extraction、provider、模型探测或网络重试。
- 不让 Graphify 自动决定最终模块边界或架构结论。
- 不把 `analyze/finalize/validate/resume` 全流程控制面换成另一套同等复杂的新控制面。
- 不将普通 UAT、fixture 或中断运行描述成真实回归通过。

## 3. 工作树保护规则

当前工作树已有用户暂存改动，实施时必须从当前工作树继续，禁止 reset、checkout 或覆盖式恢复：

- `src/stark_repo_analyzer/cli.py` 与 `tests/test_cli.py` 中的 workspace-rooted `source/...` 路径规范化修复必须提取到新的 Graphify gate 及其测试中，不能随重写丢失。
- `.meta-kim/**` 的现有暂存删除与本方案的生成状态清理方向一致，应保留。
- `skills/repo-analyzer/SKILL.md`、Graphify 指南和真实 UAT 规则的现有暂存修改需要逐段与本文目标合同合并，不能整文件覆盖。
- 已跟踪的 `__pycache__` 修改不保留内容；实施清理阶段将其从 Git 删除并加入忽略规则。
- 每阶段开始前记录 `git status --short`；只修改该阶段明确拥有的文件。

## 4. 目标程序边界

程序入口保留为 `stark-repo-analyzer`，但只暴露一个 Graphify 专属命令，例如：

```text
stark-repo-analyzer graphify-gate --target <repo> --work-dir <dir>
```

该命令只负责：

1. 检查 Graphify CLI 是否存在、版本是否兼容以及是否支持 code-only。
2. 缺失或不兼容时返回结构化的 `unavailable`，不安装、不升级、不自动进入兼容流程。
3. 运行 `extract --code-only --no-cluster` 和 `cluster-only --no-label --no-viz`。
4. 保留 raw graph/report，过滤并记录不可定位噪声，生成规范化 graph/report。
5. 只有规范化后仍有来源可定位的节点和关系时通过健康门。
6. 生成 `drafts/01-graphify-map.md` 和一份精简 `graphify-status.json`。
7. 确认目标源码未被 Graphify 修改。

不负责：克隆仓库、选择分析模式、生成模块任务、创建分析草稿、计算 Agent 阅读覆盖率、融合报告、全目录哈希、恢复分析状态或裁决最终报告质量。

## 5. 动作说明

- **保留**：职责与目标一致，只允许必要的文字或导入同步。
- **精简**：保留文件和核心职责，删除与目标无关的控制面或历史负担。
- **重写**：路径保留，但公开合同或主要实现需要按新边界重新建立。
- **删除**：迁移完成后不再属于活动产品、测试或轻量证据合同；删除前按本文要求保存必要信息。

## 6. 根目录与打包文件

| 文件 | 动作 | 方案 |
|---|---|---|
| `AGENTS.md` | 精简 | 继续指向 `docs/dev-rules/real-uat-regression/README.md`；补充“真实回归仅发布前或用户要求时执行”，不嵌入具体运行步骤。 |
| `CONTEXT.md` | 保留 | 作为领域语言唯一真源；实施中只同步最终命名，不写实现步骤。 |
| `LICENSE` | 保留 | 不变。 |
| `README.md` | 重写 | 删除 quick 和“每次都交互”的描述；说明双模式、Graphify 安装引导、增强/兼容流程、单一报告交付和源码裁决。 |
| `README.zh.md` | 重写 | 与英文 README 同步，不再把 Graphify 描述成全局不可降级门或完整控制面。 |
| `package.json` | 精简 | 保留 skill 包元数据；仓库 URL、描述和版本与当前项目一致，不声明不存在的控制面能力。 |
| `pyproject.toml` | 精简 | 保留 Python 包和单一 CLI；移除 `doctor.sh` package-data，入口指向精简 CLI。版本只在发布阶段调整。 |
| `.gitignore` | 重写 | 忽略 `.meta-kim/`、`**/__pycache__/`、`.pytest_cache/`、`.ruff_cache/`、`graphify-out/`、用户分析工作区、Graphify cache、`codex-events.jsonl` 和本地 UAT 原始证据目录。 |
| `goals.txt` | 重写 | 缩为当前产品目标、非目标、双模式和 Graphify/兼容边界；删除六仓库和完整控制面完成标准。 |
| `tasks.txt` | 重写 | 替换为本文实施阶段的有限迁移清单；不保留旧 assembly-line 完成记录作为活动任务。 |
| `codex-events.jsonl` | 删除 | 生成转录，不属于源码或轻量发布摘要。 |
| `.DS_Store` | 删除 | 本机生成文件。 |
| `.meta-kim/**` | 删除 | 接受当前暂存删除；加入 `.gitignore`，不再提交运行状态。 |
| `graphify-out/**` | 删除 | 根目录生成产物；产品运行只能写入外部 `$WORK_DIR`。 |
| `参考仓库源代码/repo-analyzer-master/**` | 保留 | 仅作小型开发参考语料，不参与运行和打包；后续若改为外部固定 commit，再单独决策。 |
| `参考仓库源代码/repo-analyzer-master.zip` | 删除 | 与解压后的参考语料重复。 |
| `.claude-plugin/plugin.json` | 精简 | 更新双模式和 Graphify 增强/兼容描述，保留插件结构。 |
| `.claude-plugin/marketplace.json` | 精简 | 与插件元数据同步，不承载运行合同。 |
| `.claude/settings.json` | 保留 | 开发环境配置，不纳入产品重构。 |
| `.codex/config.toml` | 保留 | 开发环境配置，不纳入产品重构。 |
| `.codex/hooks.json` | 保留 | 开发环境配置，不纳入产品重构。 |

## 7. Skill 产品文件

| 文件 | 动作 | 方案 |
|---|---|---|
| `skills/repo-analyzer/SKILL.md` | 重写 | 以参考八阶段流程为骨架；加入 Graphify 可用性分支、`standard` 默认一键执行、显式 `deep` 单轮询问、bounded scope 披露、subagent 不可用需用户同意、源码裁决和单一报告交付。删除 `analyze/finalize/validate/resume` 产品合同。 |
| `skills/repo-analyzer/references/analysis-guide.md` | 保留 | 保持与参考版本一致，不加入 Graphify 运行细节。 |
| `skills/repo-analyzer/references/module-analysis-guide.md` | 精简 | 保留业务模块方法、subagent prompt、覆盖率和全局视角；Graphify 只作为候选 map；把自动顺序降级改为暂停并征得用户同意；加入 bounded scope 的纳入/排除/理由表。 |
| `skills/repo-analyzer/references/graphify-integration-guide.md` | 重写 | 删除 Agent 自动安装、网络重试和完整控制面入口；描述安装指引、用户显式兼容选择、单一 gate 命令、raw/normalized 产物、噪声过滤、硬失败边界和 map 消费规则。 |

## 8. Python 实现

| 文件 | 动作 | 方案 |
|---|---|---|
| `src/stark_repo_analyzer/__init__.py` | 保留 | 仅保留包说明和版本；版本变更留到发布。 |
| `src/stark_repo_analyzer/cli.py` | 重写 | 缩为 argparse 与退出状态适配层；只解析 `graphify-gate --target --work-dir`，调用 `graphify_gate.py`，不再包含分析规划、模块任务、初始报告、finalize、resume 或完整 validate。 |
| `src/stark_repo_analyzer/graphify_gate.py` | 新增 | 从旧 CLI 提取并收拢 Graphify 版本检查、命令执行、raw 保留、workspace-rooted 路径修复、噪声过滤、规范化、健康判定、map/status 生成和源码只读检查。 |
| `src/stark_repo_analyzer/contracts.py` | 删除 | 当前 manifest、模块草稿、coverage marker 和最终报告机械合同超出 Graphify 边界；Graphify status 的最小校验由 `graphify_gate.py` 提供。 |
| `src/stark_repo_analyzer/doctor.sh` | 删除 | 与 `acceptance/doctor.sh` 重复；Python gate 成为唯一实现，避免 shell 内嵌 Python 的双份来源校验。 |
| `src/stark_repo_analyzer/__pycache__/**` | 删除 | 生成文件，加入忽略规则。 |

建议的精简退出语义：

| 退出码 | 含义 | Skill 行为 |
|---:|---|---|
| `0` | Graphify 增强证据可用 | 读取 map，继续参考分析流程。 |
| `10` | Graphify 缺失或版本不兼容 | 展示安装指引，询问用户安装复检或本次兼容运行。 |
| `30` | 已开始 Graphify 后执行、产物、来源或健康门失败 | 终止增强流程，不自动降级。 |

## 9. 规格与规则

| 文件 | 动作 | 方案 |
|---|---|---|
| `docs/spec/input-output-contract.md` | 重写 | 成为公开合同真源：输入、双模式、增强/兼容分支、工作区最小产物、单一报告、失败语义和源码裁决。 |
| `docs/spec/metadata-schema.json` | 删除 | 当前 schema 固定 standard 并覆盖完整分析状态，不再适用。 |
| `docs/spec/output-manifest-schema.json` | 删除 | 全目录文件哈希和完整 manifest 不再是用户分析合同。 |
| `docs/spec/graphify-status-schema.json` | 新增 | 只包含 schema version、状态、Graphify 版本、命令结果、raw/normalized 数量、过滤数量、目标源码状态和失败分类；不包含 provider/model。 |
| `docs/templates/analysis-run-input.md` | 删除 | YAML 内部运行表单与“一句话分析”冲突，且仍包含 semantic/deep/provider 旧字段。 |
| `docs/dev-rules/README.md` | 重写 | 删除 quick；索引普通 UAT 与真实回归 UAT 两层规则。 |
| `docs/dev-rules/real-uat-regression/README.md` | 重写 | 真实回归只在发布前或用户要求时执行；完整跑增强 standard、增强 deep、兼容 standard 三条；兼容 deep 用普通 UAT。保留“不得用内部直调、静态 fixture 或中断运行冒充通过”。 |
| `docs/goals/stark-repo-analyzer-v1-implementation.md` | 删除 | 与新目标、安装权限、双模式和 UAT 分层全面冲突；目标真源改为 `goals.txt`、CONTEXT 与 ADR。 |
| `docs/plan/reimplementation-decomposition.md` | 删除 | 被本文取代，避免两个活动实施计划。 |
| `docs/plan/graphify-simplification-file-plan.md` | 保留 | 本次迁移的实施计划；实施结束后标记完成，不变成永久产品合同。 |

## 10. ADR 文件

ADR 保留历史，不通过删除历史决定来制造“从未偏离”的假象；对已取代决定补充 status，活动决定保持简短。

| 文件 | 动作 | 方案 |
|---|---|---|
| `docs/adr/0001-baseline-starts-from-current-worktree.md` | 保留 | 历史背景。 |
| `docs/adr/0002-create-reference-output-baseline-first.md` | 精简 | 标记为历史；六仓库 baseline 不再是活动发布门。 |
| `docs/adr/0003-graphify-is-a-required-structure-evidence-gate.md` | 精简 | 标记 `superseded by ADR-0021`。 |
| `docs/adr/0004-graphify-autodetects-the-required-llm-engine.md` | 精简 | 标记 `superseded by ADR-0016`。 |
| `docs/adr/0005-use-graphify-headless-cli-for-automated-analysis.md` | 保留 | headless code-only 仍有效。 |
| `docs/adr/0006-isolate-graphify-output-in-the-analysis-workspace.md` | 保留 | 仍有效。 |
| `docs/adr/0007-bound-graphify-retries-by-failure-class.md` | 精简 | 标记 `superseded by ADR-0016`，移除活动网络重试含义。 |
| `docs/adr/0008-require-a-healthy-graphify-graph.md` | 精简 | 标记 `superseded by ADR-0018`。 |
| `docs/adr/0009-source-code-adjudicates-graphify-conflicts.md` | 保留 | 仍有效。 |
| `docs/adr/0010-separate-graphify-deep-extraction-from-analysis-depth.md` | 精简 | 标记 `superseded by ADR-0016`；产品 deep 与 Graphify code-only 的区分由 CONTEXT 保留。 |
| `docs/adr/0011-preserve-the-reference-workflow-and-add-graphify.md` | 保留 | 仍是产品边界基础。 |
| `docs/adr/0012-copy-the-reference-files-with-a-minimal-graphify-diff.md` | 保留 | 仍有效。 |
| `docs/adr/0013-agent-led-graphify-bootstrap-with-secret-boundaries.md` | 精简 | 标记 `superseded by ADR-0021`。 |
| `docs/adr/0014-add-a-doctor-preflight-script-to-v1.md` | 精简 | 标记 `superseded by ADR-0017`；实现改为单一 Python gate。 |
| `docs/adr/0015-use-doctor-as-a-non-invasive-graphify-sidecar.md` | 保留 | 已由 ADR-0016 声明取代，继续作为历史。 |
| `docs/adr/0016-graphify-code-only-v1.md` | 保留 | 当前 Graphify 执行基础。 |
| `docs/adr/0017-limit-the-control-plane-to-the-graphify-gate.md` | 保留 | 当前程序边界。 |
| `docs/adr/0018-validate-the-normalized-usable-graph.md` | 保留 | 当前健康门。 |
| `docs/adr/0019-keep-large-run-artifacts-out-of-git.md` | 保留 | 当前证据存储规则。 |
| `docs/adr/0020-use-two-mode-focused-real-uats.md` | 保留 | 已标记 `superseded by ADR-0022`。 |
| `docs/adr/0021-guide-graphify-installation-and-allow-compatibility-fallback.md` | 保留 | 当前依赖与兼容行为。 |
| `docs/adr/0022-separate-focused-uat-from-real-regression-uat.md` | 保留 | 当前 UAT 分层。 |
| `docs/adr/0023-allow-explicit-bounded-analysis-for-large-repositories.md` | 保留 | 当前大型仓库范围规则。 |
| `docs/adr/0024-require-consent-for-subagent-degradation.md` | 保留 | 当前协作降级规则。 |

## 11. 测试与 acceptance

| 文件 | 动作 | 方案 |
|---|---|---|
| `tests/test_cli.py` | 删除 | 现有测试绑定完整控制面；其中 workspace-rooted source 路径修复迁移到新 gate 测试后再删除。 |
| `tests/test_graphify_gate.py` | 新增 | 覆盖缺失/旧版本、code-only 与 cluster-only 命令、raw 保留、路径规范化、噪声过滤、空规范化图阻断、源码未修改、状态摘要和 map。 |
| `tests/test_skill_contract.py` | 新增 | 静态检查双模式、standard 默认、deep 一轮询问、Graphify 安装引导/兼容选择、subagent 用户同意、单一报告和无 `quick`。 |
| `tests/__pycache__/**` | 删除 | 生成文件，加入忽略规则。 |
| `acceptance/doctor.sh` | 删除 | 被 Python Graphify gate 取代。 |
| `acceptance/doctor-self-test.sh` | 删除 | 被 `tests/test_graphify_gate.py` 的 fixture 覆盖。 |
| `acceptance/implementation-fixture-check.sh` | 删除 | 合成完整模块报告和 manifest，验证的是被移除的控制面。 |
| `acceptance/physical-baseline-check.sh` | 删除 | 六仓库 baseline 不再是发布门。 |
| `acceptance/physical-repeatability-check.sh` | 删除 | 对完整历史运行目录的强耦合不再需要；Graphify 规范化确定性改由单元测试覆盖。 |
| `acceptance/run-contract-check.sh` | 删除 | 依赖完整 manifest/finalize 和六仓库证据。 |
| `acceptance/skill-structure-check.sh` | 重写 | 只检查插件元数据、必需 skill 文件、双模式、Graphify 增强/兼容、单一报告和已删除旧命令未再出现。 |

普通 UAT 在开发期间按需验证：

1. Graphify 可用的 standard 能生成 map 并交接给参考流程，不要求完整报告。
2. deep 会在建图/扫描后只询问一轮，并展示分析范围与理由。
3. Graphify 不可用时展示安装指引，并等待用户选择，不能自动安装或回退。
4. subagent 不可用时暂停并等待用户确认，不能默认顺序执行。

真实回归 UAT 不在本次重构日常步骤中运行；只有发布前或用户明确要求时，完整执行 ADR-0022 的三条流程并保存 Git 外证据。

## 12. 历史与生成证据

删除前必须先把仍需核验的真实 UAT 原始证据迁移到 Git 外位置，并生成轻量索引，至少记录固定 commit、Graphify 版本、命令、退出状态、耗时、失败分类、外部路径和内容摘要/校验值。没有外部证据时，不得把旧摘要继续称为真实 UAT 通过。

| 文件或路径 | 动作 | 方案 |
|---|---|---|
| `docs/baseline/physical-runs/**` | 删除 | 364 个已跟踪运行文件及大量本地缓存退出 Git；必要证据先外部归档。 |
| `docs/baseline/reference-runs/**` | 删除 | 100 个已跟踪完整报告/草稿不再作为活动六仓库门；Git 历史保留。 |
| `docs/baseline/cross-project-validation.md` | 删除 | 六仓库活动验证结论已失效。 |
| `docs/baseline/implementation-comparison.md` | 删除 | 描述旧 semantic/control-plane 状态，不能继续作为当前实现对比。 |
| `docs/baseline/physical-baseline.md` | 删除 | 旧物理基线规则失效。 |
| `docs/baseline/reference-output-baseline.md` | 删除 | 六仓库 reference baseline 不再是活动门。 |
| `docs/baseline/reference-run-manifest.json` | 删除 | 固定六仓库运行清单不再是活动合同。 |
| `docs/baseline/reimplementation-acceptance-checklist.md` | 删除 | 被双层 UAT 和精简测试合同取代。 |
| `docs/baseline/reimplementation-release-report.md` | 删除 | 是旧控制面发布记录，且包含 semantic/deep 旧语义。 |
| `docs/baseline/source-corpus-manifest.json` | 删除 | 六仓库源码集合不再是强制发布输入。 |
| `docs/baseline/source-corpus.md` | 删除 | 同上。 |
| `docs/baseline/README.md` | 新增 | 说明大型证据外置、轻量摘要格式和真实回归触发条件。 |
| `docs/agents/domain.md` | 删除 | `CONTEXT.md` 已是领域语言真源。 |
| `docs/agents/experience/**` | 删除 | meta-kim 过程证据和观察目录退出活动仓库，Git 历史保留。 |
| `docs/agents/goal-execution-record.md` | 删除 | 旧执行流水线记录，不再是产品或发布合同。 |
| `docs/agents/issue-tracker.md` | 保留 | 独立开发流程说明，不属于 analyzer 产品复杂度。 |
| `docs/agents/triage-labels.md` | 保留 | 独立开发流程说明。 |
| `docs/research/hybrid-code-intelligence-architecture/**` | 保留 | 作为历史研究材料，不作为活动实现或验收合同；README 顶部增加“non-normative”。 |

## 13. 实施顺序

### 阶段 A：锁定合同

1. 重写 `docs/spec/input-output-contract.md`、README、goals 和 dev rules。
2. 给旧 ADR 补 status，确保活动决定唯一。
3. 重写 skill 与两份集成指南，但暂不删除旧运行代码。

通过条件：静态搜索中不存在活动 `quick`、semantic/provider、Agent 自动安装、默认 subagent 降级或用户产品路径 `finalize/resume`。

### 阶段 B：建立薄 Graphify gate

1. 新增 `graphify_gate.py` 和最小 status schema。
2. 重写 `cli.py` 为单命令适配层。
3. 迁移当前暂存的 `source/...` 路径修复及 raw 证据保留逻辑。
4. 完成新 gate 单元测试后删除 contracts 和 doctor 双份实现。

通过条件：Graphify 缺失返回 `10` 且不安装；有效噪声图过滤后通过；规范化空图返回 `30`；目标仓库保持不变。

### 阶段 C：收敛测试与普通 UAT

1. 新增 skill 合同静态测试。
2. 重写 skill structure check。
3. 删除完整控制面、六仓库和 repeatability acceptance 脚本。
4. 执行四个聚焦普通 UAT；只报告被验证的局部行为。

通过条件：单元测试、skill structure 和普通 UAT 全部通过；不声称真实回归完成。

### 阶段 D：清理仓库

1. 外置仍需保存的真实 UAT 原始证据并记录摘要/校验。
2. 删除 physical/reference runs、meta-kim、root graphify output、pycache 和旧过程文档。
3. 更新 `.gitignore`，确认生成一次测试后工作树仍干净。

通过条件：`git ls-files` 不再包含 Graphify cache、完整运行目录、`.meta-kim` 或 `__pycache__`；活动文档不引用已删除的控制面命令。

### 阶段 E：发布前真实回归（条件触发）

只在准备上线发布或用户明确要求时执行：

1. Graphify 增强 `standard` 完整运行。
2. Graphify 增强 `deep` 完整运行并完成一轮用户回答。
3. Graphify 不可用的 `standard` 兼容流程完整运行。

通过条件：三次均从用户等价入口完成到 `ANALYSIS_REPORT.md`；原始证据位于 Git 外，仓库中只有轻量摘要。任何中断或局部门通过不得称为真实回归通过。

## 14. 预期结果

- 产品方法仍以参考 repo-analyzer 为主体，Graphify 只增加导航能力。
- Python 从完整分析控制面收缩为单一 Graphify gate。
- shell doctor 双份实现、manifest/contracts/finalizer/resume 和六仓库强制门被移除。
- 用户可使用默认 standard 或显式 deep；Graphify 未安装时拥有透明、需确认的兼容路径。
- 最终交付仍是一份 `ANALYSIS_REPORT.md`，大型运行证据不再进入 Git。
- 当前路径规范化修复被保留在更小、可测试的 Graphify 模块中。

## 15. 实施授权边界

本文获批准后仍需单独获得“开始实施”的明确指令。未获得该指令前，只允许审阅和修改本方案文档，不得执行阶段 A-E 中的文件变更、删除或 UAT。
