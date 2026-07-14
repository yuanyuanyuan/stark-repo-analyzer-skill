# Graphify 简化进度记录

文档类型：`progress-log`

计划：[`graphify-simplification-plan.md`](graphify-simplification-plan.md)

生命周期状态以关联 plan 为准，本文件不单独声明 `active`。

## 当前快照

- 主线目标是否完成：是。
- 当前阶段：G0-G4 实施主线已完成。
- 实施阶段完成度：`5/5`（按 roadmap 的 G0-G4 计算）。
- 发布级真实回归：未执行，本轮也未要求执行；不能声明发布就绪。
- 当前阻塞：实施主线无阻塞；工作树包含本次尚未提交的仓库迁移。
- 下一步：当前没有活动实施刀。准备发布时为 G5 建立新的活动执行计划，或为新的跨多轮目标创建 roadmap/plan。

## 2026-07-13：Output Style 路由与文档迁移

目标：

- 将“渐进式陪跑教学”落为 `docs/dev-rules/` 下的可执行规则。
- 让 Agent 打开仓库后先从根 `AGENTS.md` 加载语言和表达规则，再读取其他控制面。
- 将第一方维护性文档迁移为中文；保留专业术语、命令和机器合同原样。

范围：

- 包含根维护文档、`docs/` 下的活动文档以及 `skills/repo-analyzer/` 下的 skill 文档。
- 排除 `docs/archive/` 历史归档、`tests/baseline/` 运行证据、`vendor/` 第三方语料、测试 fixture 和生成工件。

完成：

- 新增 `docs/dev-rules/output-style/README.md`，定义中文回复/文档、英文代码注释和渐进式陪跑教学规则。
- 将 output style 设为根 `AGENTS.md` 启动序列第一步，并在 `docs/README.md` 与 `docs/dev-rules/README.md` 说明路由关系。
- 审计第一方维护性 Markdown；将入口、目录说明、spec、Graphify 指南和残留英文 ADR 内容改为中文，并为复杂长文补充主线总结。
- 将三份英文 research 原始全文移入 `docs/archive/research-source/`，在活动路径保留中文决策版本、关键矩阵、限制和来源索引。
- 明确不改写 `docs/archive/` 历史内容、`tests/baseline/` 运行证据、`vendor/` 第三方语料、fixture 和机器生成工件。

验证：

- `pytest -q`：18 passed。
- `./acceptance/skill-structure-check.sh`：PASS。
- 53 份活动维护性 Markdown 相对链接检查：PASS。
- 活动维护性 Markdown 中文存在性扫描：PASS；不存在整份纯英文活动文档。
- Python/JavaScript/TypeScript/Shell/YAML 中文代码注释扫描：PASS，未发现中文代码注释。
- `git diff --check`：PASS。

未执行：

- 未运行真实 UAT；本次只改变协作与文档表达，不声称产品回归通过。

下一刀：回到活动主线 G1-1，审计产品合同与当前工作树差异。

## 2026-07-13：人类与 Agent 共用的快速读取入口

目标：让两类读者不需要通读目录，就能在 30 秒内找到权威入口，并在 3 分钟内确定当前状态、该读什么和何时维护。

完成：

- 在 `docs/README.md` 增加按问题选择文档的 60 秒入口，避免默认全量读取。
- 为 roadmap 与 exec plan README 增加统一首屏字段、创建步骤和维护边界。
- 新增 `docs/adr/README.md`，提供当前主线决策索引、历史回读边界和 ADR 生命周期规则。
- 新增 `docs/spec/README.md`，区分人类可读合同与机器 schema，并规定冲突时必须阻塞修复。
- 新增 `docs/dev-rules/document-control/README.md`，约束 Agent 的启动读取、创建联动、每刀维护、冲突处理与收尾检查。
- 将 document-control 纳入根 `AGENTS.md` 启动必读，并在根入口写入不可绕过的文档控制硬规则。
- 在 output style 中增加人类与 Agent 共用的快速读取协议，要求同一首屏事实服务两类读者。

验证：

- 56 份活动维护性 Markdown 相对链接检查：PASS。
- 活动状态扫描：`active` roadmap 1 份、`active` plan 1 份、progress 重复 active 声明 0 份。
- `AGENTS.md`、docs map、dev-rules 和四类目录索引的入口存在性检查：PASS。
- `AGENTS.md` 对 document-control、spec 索引和 ADR 索引的路由扫描：PASS。
- `git diff --check`：PASS。

未执行：

- 未运行真实 UAT；本次没有改变 analyzer 产品行为或验收语义。

下一刀：回到活动主线 G1-1，审计产品合同与当前工作树差异。

## 2026-07-13：目录与规则边界

完成：

- 新增 `docs/roadmap/`、`docs/exec-plans/`、`docs/aiprompts/` 及职责 README。
- 将 `AGENTS.md` 限定为仓库硬规则、主线控制与验收声明。
- 明确 roadmap、exec plan、prompt、产品合同和 dev rule 的边界。

验证：

- `git diff --check -- AGENTS.md docs/roadmap/README.md docs/exec-plans/README.md docs/aiprompts/README.md`：通过。
- 文档所引用的现有仓库路径检查：通过。

## 2026-07-13：活动控制面迁移

完成：

- 建立唯一活动 roadmap、exec plan 和 progress。
- 将旧 `goals.txt`、`tasks.txt`、V1 goal 与旧分解计划标记为 superseded。
- 将逐文件 Graphify 方案降为历史设计输入，不再作为活动执行授权。

验证：

- `git diff --check`（本轮治理文件范围）：通过。
- `docs/roadmap/*-roadmap.md` 的 `active` 声明扫描：1 份。
- `docs/exec-plans/*-plan.md` 的 `active` 声明扫描：1 份。
- 五份被替代控制文档的 `superseded` 声明扫描：全部存在。
- roadmap、plan、progress、活动规格、CONTEXT 与真实 UAT 规则的路径存在性检查：通过。

未执行：

- 未修改 analyzer skill、Graphify gate、输出合同或验收语义。
- 未运行单元测试、聚焦 UAT 或真实回归 UAT。

## 2026-07-13：物理目录收敛

完成：

- 将旧 V1 goals、tasks、计划和输入模板移动到 `docs/archive/v1-control-plane/`。
- 将 V1 执行记录和 Meta_Kim 经验材料移动到 `docs/archive/v1-execution/`。
- 将仍有效的领域语言、Issue、triage 与验收规则集中到 `docs/dev-rules/`。
- 删除移动后为空的 `docs/goals/`、`docs/plan/`、`docs/templates/` 和 `docs/agents/`。
- 新增 `docs/README.md`、归档索引和 baseline 过渡边界说明。
- 将小型参考源码移到 `vendor/repo-analyzer-reference/`。
- 用 `tests/fixtures/graphify/` 的最小图替代 doctor self-test 对根 Graphify 输出的依赖。
- 将根 Graphify 输出、Codex 转录、重复 zip 和工具缓存移到 Git 外保留目录，并生成 SHA-256 清单。

验证：

- `pytest -q`：18 passed。
- `./acceptance/doctor-self-test.sh`：PASS。
- 活动文档、归档文档和 `docs/dev-rules/` 的 Markdown 相对链接检查：无断链。
- `git diff --check`：通过。
- Git 外保留目录：177 个文件，约 8.8 MB；`MANIFEST.sha256` 的 SHA-256 为 `a8a473941059fe72efa05cffa96f603b2c8986558164410742456ef1e80f4b5a`。

边界：

- 当时 `docs/baseline/` 仍被测试和验收脚本引用，因此该刀没有提前外置或删除；后续目录治理已将其整体迁至 `tests/baseline/`。
- 当时约 1.1 GB 的 ignored 工件留给 G4；迁移只改变测试证据根目录，不提高其验收等级。

## 2026-07-13：Baseline 测试证据迁移

目标：把只服务测试和 acceptance 的 baseline 从产品文档层迁入 `tests/`，减少 Agent 对权威层级的误判，同时保持历史证据与测试入口可用。

完成：

- 将完整目录从 `docs/baseline/` 移至 `tests/baseline/`，旧路径已不存在。
- 同步根规则、docs map、output/document-control 规则、活动 plan/progress 和 acceptance 脚本中的路径。
- 迁移前后的数据规模保持一致：约 1.1 GB、3,913 个文件；迁移前的 473 个 Git 跟踪文件均在新路径保留，新增测试层 README 后共跟踪 474 个文件。

验证：

- `pytest -q`：18 passed。
- `./acceptance/run-contract-check.sh`：PASS。
- 56 份活动 Markdown 相对链接检查：PASS。
- `docs/baseline/` 路径检查：不存在；`tests/baseline/` 文件计数：3,913。
- `git diff --check`：PASS。

边界：

- 本次只改变测试证据的目录归属，不改写历史运行正文，也不提高任何历史 UAT 声明的等级。
- 大型运行工件是否继续留在 Git 中仍由 G4 和 ADR-0019 处理。

## 2026-07-13：G1-1 活动合同差异审计

目标：把 roadmap 与当前有效 ADR 的结论，逐项对照活动文档、实现和验收入口。G1-1 只确定差异和归属，不在同一刀修复产品行为。

### 权威结论

- 模式：默认 `standard`，用户明确要求深度分析时使用 `deep`；不恢复 `quick`。依据 roadmap“目标行为/非目标”和 ADR-0017。
- Graphify：只使用 `0.9.13+` code-only；缺失或不兼容时由用户选择安装后复检或无 Graphify 兼容流程，Agent 不自动安装。依据 ADR-0016、ADR-0021。
- 控制面：程序层只负责 Graphify gate；`analyze`、`finalize`、`validate`、`resume` 不再是普通用户产品路径。依据 ADR-0017。
- 执行降级：subagent 不可用时必须暂停并取得用户同意；同意后只改变并行方式，不降低质量合同。依据 ADR-0024。
- 范围：大型仓库允许显式有界分析，必须披露纳入、排除、理由和覆盖率分母。依据 ADR-0023。
- 输出与验收：用户只接收一份 `ANALYSIS_REPORT.md`；普通聚焦 UAT 与发布级真实回归分开。依据 roadmap、ADR-0017、ADR-0022。

### 文件级差异矩阵

| 主题 | 当前冲突位置 | 差异 | 修改归属 | 建议验证 |
|---|---|---|---|---|
| 分析模式 | `README.md:76`、`README.zh.md:76`、`docs/spec/input-output-contract.md:17`、`skills/repo-analyzer/SKILL.md:83` | README 仍公开 `quick/standard/deep` 三档并默认让用户选择；spec 与 Skill 又声明只支持 `standard`。两者都不符合“默认 standard、显式 deep、不恢复 quick”。 | G1-2 修活动文档；G2 更新程序合同；G3 更新测试与验收 | 扫描活动文档不存在产品 `quick`，并同时存在 `standard`、`deep` 的准确语义 |
| Graphify 提取语义 | `docs/spec/input-output-contract.md:17` | 仍把 `graphify --mode deep` 描述为提取深度，和 ADR-0016 的纯 `--code-only` 路径直接冲突。 | G1-2 | 扫描活动合同不存在 semantic、provider 或 Graphify `--mode deep` 产品路径 |
| 安装与兼容流程 | `docs/spec/input-output-contract.md:48`、`:57`，`skills/repo-analyzer/SKILL.md:12`，`skills/repo-analyzer/references/graphify-integration-guide.md:9` | spec/Skill 把 Graphify preflight 设为无条件阻断，spec 与指南允许 Agent bootstrap 或直接安装；缺少“用户选择安装或兼容流程”的分支。 | G1-2 修文档；G2 实现 gate 返回边界；G3 验证选择分支 | 聚焦 UAT 分别证明安装后复检、用户选择兼容、建图开始后失败阻断 |
| 程序控制面 | `skills/repo-analyzer/SKILL.md:12-27`、`:88`、`:247`，`skills/repo-analyzer/references/graphify-integration-guide.md:11-15`，`docs/spec/input-output-contract.md:50` | 普通流程仍依赖 `analyze/finalize/validate/resume`，并让 Python 创建计划、模块任务和最终报告合同；这超过薄 Graphify gate 的职责。 | G1-2 删除公开命令语义；G2 收缩 CLI；G3 重建静态合同和 acceptance | 公开文档旧命令扫描；gate 单元测试；Skill 结构与合同检查 |
| subagent 降级 | `skills/repo-analyzer/SKILL.md:188`、`skills/repo-analyzer/references/module-analysis-guide.md:49` | 当前要求运行时无 subagent 时自动顺序执行且不得等待用户，和 ADR-0024 正面冲突。 | G1-2 | 静态合同检查加聚焦 UAT，证明未获同意前不会开始模块深度分析 |
| 大仓库有界范围 | `skills/repo-analyzer/SKILL.md:83`、`:97-98`、`:265` | 只描述 fixed standard 和自动 bounded scope，没有 `deep` 唯一一轮集中确认，也没有完整的纳入、排除、理由和分母披露合同。 | G1-2 | `standard` 不阻塞但披露范围；`deep` 只集中询问一次并记录用户确认 |
| 用户输出与内部工件 | `docs/spec/input-output-contract.md:19-61`、`skills/repo-analyzer/SKILL.md:20-27`，`src/stark_repo_analyzer/contracts.py` | 单一最终报告原则基本保留，但完整 manifest、固定草稿格式和 finalization 被写成普通用户必需产品合同，未区分用户交付、运行支撑证据与开发验收工件。 | G1-2 澄清文档边界；G2 收缩 contracts；G3 重建验收 | 只向用户交付 `ANALYSIS_REPORT.md`；内部证据仍位于隔离工作区且不被表述为第二套交付物 |
| UAT 规则 | `docs/dev-rules/README.md`、`docs/dev-rules/real-uat-regression/README.md` | 规则仍以“V1 只支持 standard”和旧完整控制面命令定义真实 UAT；规则索引仍残留旧模式分档，和 ADR-0022 的三条发布级真实回归组合及薄 gate 路径不一致。 | G1-2 对齐规则文字；G3 重建 UAT 驱动和检查 | 普通 UAT 只声明局部分支；真实回归从用户等价入口完成并保留可核验证据 |
| CLI、schema 与测试 | `src/stark_repo_analyzer/cli.py:960-1165`、`docs/spec/metadata-schema.json`、`docs/spec/output-manifest-schema.json`、`tests/test_cli.py`、`acceptance/implementation-fixture-check.sh` | CLI 仍是完整分析控制面且只接受 `standard`；schema、测试和 fixture acceptance 固定旧 manifest、handoff、finalize、resume 合同。 | G2 修改实现/schema；G3 修改测试/acceptance | gate 返回码、路径规范化、raw 保留、源码只读和负向 fixture 测试 |
| ADR 生命周期 | ADR-0016 至 ADR-0024 及 `docs/adr/README.md` | 新 ADR 已在正文声明取代旧决定，但多数旧 ADR 没有统一的 `superseded` 状态，Agent 仍可能误读为同时有效。 | G1-3 | ADR 索引只能得到一组当前有效决定；旧 ADR 保留历史正文和明确取代链接 |

### G1-2 文件边界

下一刀只修改以下活动文档，不碰 Python、schema、测试、baseline、archive 或旧 ADR：

- `docs/spec/input-output-contract.md`
- `README.md`、`README.zh.md`
- `skills/repo-analyzer/SKILL.md`
- `skills/repo-analyzer/references/graphify-integration-guide.md`
- `skills/repo-analyzer/references/module-analysis-guide.md`
- `docs/dev-rules/README.md`
- `docs/dev-rules/real-uat-regression/README.md`

G1-3 单独处理 ADR 生命周期；G2 处理 Python gate 和 schema；G3 处理测试、acceptance 与聚焦/真实 UAT 证据。这样分层后，文档合同、实现合同和验收证据不会在同一刀互相掩盖。

验证：

- 每项差异均已回挂 roadmap 或 ADR-0016 至 ADR-0024。
- 差异已明确分配到 G1-2、G1-3、G2 或 G3，没有把代码重写混入 G1-1。
- 未执行真实 UAT；本次是只读合同审计和控制面记录，不构成产品回归声明。

下一刀：执行 G1-2，先统一活动产品文档和规则索引；完成静态矛盾扫描与 Skill 合同检查后，再进入 G1-3。

## 2026-07-13：G1-2 活动产品合同对齐

目标：让人类与 Agent 从 README、spec、Skill、references 和 UAT 规则读取到同一套产品行为，同时不提前重写 G2 的 Python gate 或 G3 的测试。

完成：

- 将模式统一为默认 `standard` 与显式 `deep`；删除快速模式，规定 `deep` 快速扫描后只集中询问一次。
- 将 Graphify 统一为 `0.9.13+` code-only 增强流程；依赖缺失时只提供指引，由用户选择安装后复检或本次兼容流程。
- 删除活动产品文档中的 `analyze`、`finalize`、`validate`、`resume` 普通用户路径，程序层只描述单一 Graphify gate 职责。
- 规定 Graphify 增强流程开始后的执行/健康失败必须阻断，不能自动切换兼容流程或补造工件。
- 规定 subagent 不可用时必须在模块深度分析前取得用户同意，顺序执行不降低覆盖率和质量门。
- 补齐大型仓库有界范围的纳入、排除、理由和覆盖率分母披露要求。
- 区分用户唯一交付 `ANALYSIS_REPORT.md`、运行支撑证据和开发验收工件。
- 将 UAT 分为开发期聚焦 UAT 与发布级真实回归；发布级矩阵按 ADR-0022 固定为增强 `standard`、增强 `deep`、无 Graphify `standard` 三条完整流程。

修改范围：

- `docs/spec/input-output-contract.md`
- `README.md`、`README.zh.md`
- `skills/repo-analyzer/SKILL.md`
- `skills/repo-analyzer/references/graphify-integration-guide.md`
- `skills/repo-analyzer/references/module-analysis-guide.md`
- `docs/dev-rules/README.md`
- `docs/dev-rules/real-uat-regression/README.md`

验证：

- `pytest -q`：18 passed。
- `./acceptance/skill-structure-check.sh`：PASS。
- 56 份活动维护性 Markdown 相对链接检查：PASS。
- 活动产品文档旧用户命令扫描：0 个文件命中。
- 活动产品文档旧快速模式合同扫描：0 个文件命中；第三方 URL `anthropic-quickstarts` 不属于产品模式。
- 自动安装肯定授权与无同意顺序降级旧语句复核：不存在；命中项均为“不会/不得/不能”的禁止规则。
- `git diff --check`：PASS。

边界：

- 未修改 `src/`、JSON Schema、`tests/` 或 acceptance 实现；它们仍固定旧完整控制面合同，按 G2/G3 处理。
- 未执行聚焦 UAT 或真实回归 UAT；静态合同与结构检查不能证明产品行为已经实现。
- 未修改历史 ADR；旧 ADR 生命周期由下一刀 G1-3 处理。

下一刀：执行 G1-3，只统一旧 ADR 的 `superseded` 状态、取代链接和 ADR 索引，然后重新判断 G1 阶段是否满足退出条件。

## 2026-07-13：英文 README 与 Graphify 启动路由

目标：修正产品文档语言分工，并确保 Agent 从根 `AGENTS.md` 读取 Graphify 知识图谱使用纪律。

完成：

- 将根 `README.md` 重写为英文产品入口，保留 G1-2 已对齐的两种模式、Graphify 用户选择、subagent 同意和单一报告合同。
- 保持 `README.zh.md` 为中文版本，并修正两份 README 在文件结构中的语言说明。
- 在根 `AGENTS.md` 启动区增加 Graphify 路由：图存在时优先 `query/path/explain`，宽泛导航优先 wiki，只有必要时读取完整报告，代码修改后执行 `graphify update .`。
- 在 `AGENTS.md` 和 output-style 规则中声明 `README.md` 英文、`README.zh.md` 中文的固定例外，防止后续 Agent 再次把两份文档改成同一语言。

验证：

- `README.md` 中文字符扫描：0；`README.zh.md` 中文正文存在。
- 两份 README 的 `standard`/`deep`、Graphify 选择、subagent 同意和 `ANALYSIS_REPORT.md` 合同检查：PASS。
- `AGENTS.md` 的 `graphify query/path/explain/update`、wiki 与 `GRAPH_REPORT.md` 路由检查：PASS。
- 当前 `graphify-out/graph.json` 与 wiki 不存在，本机 `graphify` 可执行文件存在；本轮没有代码改动，因此未运行 query 或 `graphify update .`。

## 2026-07-13：G1-3 ADR 生命周期收口

目标：让 Agent 只从 ADR 索引得到当前有效决定，同时保留早期 ADR 的历史原貌和可追溯取代链。

完成：

- 为 ADR-0003、0004、0005、0007、0008、0010、0013、0015、0020 增加 `status: superseded` 和 `superseded_by` front matter。
- 在每份旧 ADR 标题后增加当前替代链接；旧决策正文未删除、未改写。
- 在 `docs/adr/README.md` 增加已取代决策索引，区分当前必读集、直接取代关系和仅用于历史回读的早期记录。
- G1 退出条件已满足：活动产品文档不再保留旧快速模式、semantic/provider 执行路径、自动安装、无同意顺序降级或旧四命令产品语义。

验证：

- `status: superseded`：9 份；`superseded_by`：9 份。
- 九条直接取代链与 ADR-0016、0018、0021、0022 正文声明一致。
- 活动维护性 Markdown 相对链接检查：PASS。
- `git diff --check`：PASS。

边界：

- 未把没有明确直接取代关系的早期 ADR 武断标成整体失效；它们默认只作为历史输入，当前执行权仍以 ADR 索引和活动 roadmap 为准。
- 未修改 Python、schema、测试或 acceptance 实现；这些旧合同进入 G2/G3 处理。
- 未执行聚焦 UAT 或发布级真实回归，本轮不声明产品行为已经实现或回归通过。

下一刀：执行 G2-1，先定义薄 gate 的唯一输入、最小状态输出和 `0/10/30` 返回边界，再迁移现有 code-only、规范化与健康检查能力。

## 2026-07-13：开发规则纳入 docs

完成：

- 将根 `dev-rules/` 整体移动到 `docs/dev-rules/`。
- 更新 `AGENTS.md`、文档地图、活动 roadmap/plan、研究和归档材料中的规则路径。
- 保持 `AGENTS.md` 为仓库入口，`docs/dev-rules/` 只承载被入口引用的可执行规则。
- 在根 `AGENTS.md` 增加强制启动读取顺序，并直接链接活动 progress。

验证：

- `pytest -q`：18 passed。
- `./acceptance/doctor-self-test.sh`：PASS。
- 非 baseline Markdown 相对链接检查：无断链。
- `git diff --check`：通过。
- 根目录不存在残留 `dev-rules/`；唯一规则目录为 `docs/dev-rules/`。
- `AGENTS.md` 的 docs map、roadmap、plan、progress 和真实 UAT 入口均存在。

## 2026-07-13：G2-1 薄 Graphify gate 入口与状态合同

目标：先固定单一 Graphify gate 的调用入口和最小状态语言，让 Agent 只依赖 `0/10/30` 边界；本刀不把分析模式、模块计划或最终报告重新放入 Python。

完成：

- 新增 `src/stark_repo_analyzer/graphify_gate.py`，固定 `preflight → extract → postprocess → post-graph` 调用顺序。
- 新增 console script `stark-repo-analyzer-graphify-gate`，唯一输入为 `--target` 和 `--work-dir`，stdout 输出与进程返回码一致的 JSON 终态。
- 新增 `docs/spec/graphify-gate-status-schema.json`，只暴露 schema 版本、`0/10/30`、终态、阶段、目标/工作区、Graphify 版本、`code-only`、工件和失败摘要。
- 明确阻止 `backend`、`model`、分析模式、模块状态和报告生成状态进入 gate 合同。
- 在创建工作区前拒绝目标仓库内部的 `$WORK_DIR`，避免无效输入先改写只读源码树。
- 新增 9 个聚焦单元测试，覆盖依赖不可用、preflight 阻断、完整成功顺序、extract/postprocess/post-graph 失败、状态落盘、CLI 一致性、schema 和工作区边界。

验证：

- `pytest -q tests/test_graphify_gate.py`：9 passed。
- `pytest -q`：串行复检 27 passed。
- `./acceptance/skill-structure-check.sh`：PASS。
- `PYTHONPATH=src python -m stark_repo_analyzer.graphify_gate --help`：PASS；当前环境未安装 editable package，因此不带 `PYTHONPATH` 的模块启动不作为失败合同。
- 设置不存在的 `GRAPHIFY_CLI` 运行新模块：进程返回 `10`，stdout 与 `graphify-gate-status.json` 的终态语义一致，extract 未开始。
- `git diff --check`：PASS。
- `/Users/chuzu/anaconda3/bin/graphify update .`：成功，最终更新后为 3,696 个节点、3,569 条边、489 个 community；工具提示 78 个来源文件没有产生节点。
- `graphify query` 已确认 `run_gate()` 与旧 `doctor`、extract、postprocess 适配点的局部关系。

边界：

- G2-1 仍通过窄适配器复用 `cli.py` 的实现；路径规范化、raw 工件、导航 map 和完整源码只读保护将在 G2-2 迁入新模块。
- 旧 `analyze/finalize/validate/resume` 控制面和重复 doctor 尚未删除，由 G2-3 处理。
- 未执行聚焦 UAT 或发布级真实回归 UAT；单元测试、结构检查和 Graphify 图更新都不能被称为真实 UAT。
- G2 尚未满足阶段退出条件，因此实施阶段完成度保持 `2/5`。

下一刀：执行 G2-2，把路径规范化、raw 工件保留、导航 map 和源码只读保护迁入独立 gate，并用正向噪声图与负向 fixture 证明边界。

## 2026-07-13：G2-2 规范化、导航与源码只读边界迁移

目标：让独立 gate 自己拥有 Graphify raw 保留、路径规范化、健康前置、导航 map 和目标源码只读保护，不再调用旧 `cli.py` 中对应的完整控制面函数。

完成：

- 将 code-only raw 图/报告原样保留为 `raw-code-only-graph.json` 与 `raw-code-only-GRAPH_REPORT.md`；规范化失败时只在 status 中列出真实保留的 raw 工件。
- 将绝对路径、目标相对路径和唯一的 workspace-rooted 路径统一规范为目标仓库相对路径；拒绝 `..`、越界、缺失文件和无效行号。
- 允许过滤 raw 噪声并记录节点/关系过滤计数；规范化后没有来源可定位的节点或关系时返回 `30`。
- 只保留被有效关系引用的无来源 symbol 节点，并要求每条保留关系的两端都存在，避免产生悬空关系。
- post-graph 通过后生成中文 `drafts/01-graphify-map.md`，包含计数、community、候选源码路径和关系证据样本。
- 在 preflight、extract、postprocess、post-graph 和 map 生成后比较完整目标树元数据签名，检测 tracked、untracked 与 ignored 路径变化。
- 任意未知源码改写立即阻断且不自动回滚；Graphify 明确新建在目标仓库内的 `graphify-out/` 会被清除后返回源码边界失败。
- 新增 G2 正向噪声图、规范化后空图和最小目标源码 fixture；gate 聚焦测试从 9 个增加到 14 个。

验证：

- `pytest -q tests/test_graphify_gate.py`：14 passed。
- `pytest -q`：32 passed。
- 正向噪声 fixture 通过真实 `doctor post-graph`；空图、源码改写和目标内 Graphify 输出均被阻断。
- `./acceptance/doctor-self-test.sh`：PASS。
- `./acceptance/skill-structure-check.sh`：PASS。
- Python 语法、JSON Schema 解析和 `git diff --check`：PASS。
- `/Users/chuzu/anaconda3/bin/graphify update .`：成功，更新后为 3,720 个节点、3,625 条边、491 个 community；工具提示 80 个来源文件没有产生节点。
- `graphify query` 已确认新 gate 内的签名、规范化、postprocess 和 map 调用关系，同时定位到待 G2-3 删除的旧重复实现。

边界：

- 新 gate 仍复用旧模块中的 Graphify extract、底层进程执行和 doctor 适配器；它们将在 G2-3 收入最终薄模块或删除重复表面。
- 旧 `analyze/finalize/validate/resume`、metadata/manifest contracts 及对应旧测试尚未删除，不能声明 G2 已完成。
- 未执行聚焦 UAT 或发布级真实回归 UAT；fixture、单元测试、doctor self-test 和图更新都不是 UAT。
- G2 尚未满足阶段退出条件，因此实施阶段完成度保持 `2/5`。

下一刀：执行 G2-3，删除旧完整控制面、重复 doctor/Graphify 实现和失效 contracts，并用旧命令静态扫描与全量测试证明产品表面收敛。

## 2026-07-13：G2-3 单一 Python gate 收口

目标：删除旧完整分析控制面、重复 Graphify/doctor 实现和失效 contracts，让程序化产品表面只剩一个可打包、可测试的 Graphify gate。

完成：

- 将 `RunFailure`、安全子进程、Graphify `0.9.13+`/code-only preflight、extract 重试和 post-graph 健康检查迁入 `graphify_gate.py`。
- 删除 `src/stark_repo_analyzer/cli.py`、`contracts.py` 和包内 `doctor.sh`，新 gate 不再导入旧模块。
- 删除 `analyze/finalize/validate/resume` console script，只保留 `stark-repo-analyzer-graphify-gate`。
- 删除旧 `metadata-schema.json`、`output-manifest-schema.json`，spec 机器合同只保留 gate status schema。
- 删除 `tests/test_cli.py`，将仍有效的 preflight、code-only extract、超时、规范化与源码边界检查集中到 17 个 gate 测试。
- 删除重复 `acceptance/doctor.sh` 及只服务旧完整控制面的 doctor self-test、implementation fixture 和 run-contract 脚本。
- 保留 physical baseline integrity/repeatability 脚本作为历史证据检查输入；其大型证据归属和后续清理由 G4 处理。
- 清除本轮 wheel 构建产生的 `build/` 与 `.egg-info`，避免增量构建把已删除模块带入发行包。

验证：

- `pytest -q`：17 passed。
- `./acceptance/skill-structure-check.sh`：PASS。
- 真实进程级依赖缺失检查：返回 `10`，status JSON 可解析，extract 未开始。
- 全新 wheel 只包含 `__init__.py`、`graphify_gate.py` 和单一 gate console script，不包含旧 CLI/contracts/doctor。
- 活动 `src/`、`tests/`、`acceptance/`、spec、Skill 和 README 的旧模块、旧 schema、旧命令与旧 acceptance 入口扫描：0 命中。
- JSON Schema 解析与 `git diff --check`：PASS。
- `/Users/chuzu/anaconda3/bin/graphify update .`：成功，更新后为 3,479 个节点、3,254 条边、471 个 community；工具提示 79 个来源文件没有产生节点。
- `graphify query` 确认活动 Python 产品表面只剩新 gate；旧控制面节点只来自 archive、baseline 或参考语料。

边界：

- 未执行 G3 聚焦 UAT 或发布级真实回归 UAT；进程检查、单元测试、静态扫描和 wheel 审计都不是 UAT。
- physical baseline 脚本仍描述历史运行工件，不代表当前 gate 或当前 Skill 的活动验收合同；G3/G4 将继续分层处理。
- G2 阶段退出条件已满足，实施完成度更新为 `3/5`。

下一刀：执行 G3-1，重建 Skill 静态合同与结构检查，再按 G3-2 的模式、依赖选择、健康门和 subagent 分支执行聚焦 UAT。

## 2026-07-13：G3-1 Skill 静态合同与结构检查

目标：把已经写入 Skill 的模式、Graphify、subagent、范围和单一输出规则变成可执行静态门，防止后续文档或打包修改重新引入旧产品语义。

完成：

- 在 `SKILL.md` 增加唯一 Graphify gate 调用协议，明确 console script 与完整仓库 checkout 下的 Python 模块回退入口。
- 明确 gate `0/10/30` 的 Agent 分支：成功继续、依赖不可用等待用户选择、执行/健康/源码边界失败立即停止。
- 明确 stdout/status 是机器判断证据，不是第二份用户报告；Skill 仍只向用户交付 `ANALYSIS_REPORT.md`。
- 新增 `acceptance/skill-contract-check.sh`，跨 Skill、references、spec、`pyproject.toml` 和 Python 表面检查 24 项活动合同。
- 静态门覆盖默认 `standard`、显式 `deep` 唯一一轮集中询问、60/30 与 90/60 覆盖率、Graphify `0.9.13+` code-only、用户选择、禁止自动安装/回退、失败阻断、有界范围披露、subagent 同意和单一报告。
- 静态门同时检查单一 console script、旧控制面文件不存在、status schema 为 `0/10/30`/code-only、gate 不含 backend/model 状态，以及 Skill 不含旧用户命令或快速模式。
- `skill-structure-check.sh` 在基础结构通过后自动调用新合同检查，避免两套检查入口各自漂移。

验证：

- `./acceptance/skill-structure-check.sh`：结构检查 PASS，24 项 Skill 合同检查全部 PASS。
- `pytest -q`：17 passed。
- `bash -n acceptance/skill-structure-check.sh acceptance/skill-contract-check.sh`：PASS。
- `git diff --check`：PASS。
- `/Users/chuzu/anaconda3/bin/graphify update .`：成功，更新后为 3,483 个节点、3,257 条边、474 个 community；工具提示 79 个来源文件没有产生节点。

边界：

- 本刀只证明活动文档、打包入口、schema 和实现表面静态一致，不能证明 Agent 在真实会话中按这些规则行动。
- 未执行任何聚焦 UAT 或发布级真实回归 UAT，G3 阶段仍未完成，实施完成度保持 `3/5`。

下一刀：执行 G3-2，用独立 Agent 和用户等价输入分别验证模式、Graphify 依赖选择、健康失败阻断与 subagent 同意分支，并逐项记录入口、转录、退出状态和未覆盖边界。

## 2026-07-13：G3-2 四类聚焦 UAT

目标：从用户等价 Skill 入口运行独立 Agent，真实证明模式、Graphify 依赖选择、执行失败阻断和 subagent 同意边界；聚焦分支通过不能冒充发布级完整回归。

完成：

- 默认 `standard` 没有展示模式菜单，直接开始；计划保留核心 60%/次要 30% 覆盖率门。
- 显式 `deep` 使用真实 Graphify `0.9.13` code-only gate，快速扫描后只进行一次集中询问；用户回答后没有第二次范围确认，计划保留 90%/60% 门。
- Graphify 依赖缺失时 gate 返回 `10`；Agent 没有安装或自动降级，在同一 session 等待用户选择。用户选择兼容流程后明确记录未使用 Graphify，且没有生成伪造图谱。
- Graphify capability preflight 通过而 extract 返回 `23` 时，gate 返回 `30`；Agent 立即停止，没有切换兼容流程、补写报告或伪造成功工件。
- 在真正移除协作工具的独立 Codex 会话中，Agent 在模块深读前暂停；用户同意后才顺序执行，记录 `parallelism: degraded`，仍保留 60%/30% 门。
- 三个固定目标仓库在运行前后均保持干净，commit 未变化。

验证：

- `pytest -q`：17 passed。
- `./acceptance/skill-structure-check.sh`：结构检查 PASS，24 项 Skill 合同检查全部 PASS。
- `bash -n acceptance/skill-structure-check.sh acceptance/skill-contract-check.sh`：PASS。
- roadmap、plan、progress 的 G4 当前阶段与 `4/5` 完成度唯一性检查：PASS；G3-2 在活动 plan 中为完成。
- 三个目标源码仓库 `git status --short` 均为空，固定 commit 未变化。
- `git diff --check`：PASS。
- `graphify update .`：成功，更新后为 3,485 个节点、3,259 条边、475 个 community；工具提示 79 个来源文件没有产生节点。

证据：

- Git 外根目录：`/Users/chuzu/repo-analyses/stark-repo-analyzer-g3-uat-20260713/`。
- 证据摘要：`/Users/chuzu/repo-analyses/stark-repo-analyzer-g3-uat-20260713/SUMMARY.md`。
- 完整 JSONL 转录、最后一条 Agent 消息、stderr、故障替身和各运行工作区均保存在 Git 外；摘要记录 session ID、时间、固定 commit、结果、偏差和声明上限。

已知偏差与边界：

- 一次兼容流程 `resume` 因额外写目录权限丢失改用 `/private/tmp`；它只作为模式和兼容分支证据，不作为默认工作目录合同通过证据。
- 隔离 subagent 场景的低推理主 Agent 漏用了 console script 缺失时的 Python module fallback；用户选择兼容流程后才进入 subagent 分支。该运行只证明 subagent 同意边界，不证明 Graphify 增强路径。
- Codex 用户级协作配置未被普通 `--disable multi_agent` 真正隔离、Claude 低成本端点 `429` 和首次隔离 Codex 官方端点 `401` 的运行均已排除，未计入通过证据。
- 本轮未执行发布级增强 `standard`、增强 `deep` 和无 Graphify `standard` 三条完整回归，不声明真实回归通过或发布就绪。

阶段结论：G3 的静态合同和四类聚焦 UAT 退出条件已满足，实施完成度更新为 `4/5`。

下一刀：执行 G4-1，先盘点、外置和索引 Git 中仍需保存的大型真实运行证据，再进行 G4-2 清理；不能先删除再补摘要。

## 2026-07-14：G4-1 大型历史运行证据外置

目标：在删除任何 baseline 证据之前，保存完整 Git 外副本并建立可定位、可核验的轻量索引，为 G4-2 仓库减重提供恢复边界。

完成：

- 盘点 `tests/baseline/`：3,913 个常规文件、158 个目录、1,224,337,092 个逻辑字节；其中 `physical-runs/` 是主要体积来源。
- 将完整物理目录复制到 `/Users/chuzu/repo-analyses/stark-repo-analyzer-skill-g4-artifacts-20260714/`，保留原有相对路径 `tests/baseline/`。
- 在外部归档记录源仓库 HEAD、时间、规模、工作树状态和恢复边界；明确副本来自包含已有 staged/dirty 迁移的物理工作树，而不是仅由 HEAD 重建。
- 分别从源目录和归档目录生成 3,913 条 SHA-256 清单，两份清单逐字比较通过。
- 更新本机工件索引和 baseline README，使人类与 Agent 都能从仓库内快速定位外部副本。
- 本刀没有删除或改写 `tests/baseline/` 中的任何证据，也没有修改 acceptance 行为。

验证：

- 源与归档均为 3,913 个常规文件、158 个目录、1,224,337,092 个逻辑字节：一致。
- `cmp SOURCE_MANIFEST.sha256 ARCHIVE_MANIFEST.sha256`：PASS。
- 两份清单 SHA-256：`25899571e64847607e533f866a61115e2d658273d3a784e3d0a0d5a890ece215`。
- 清单条目数：3,913。
- `./acceptance/physical-baseline-check.sh`：完整性门 PASS；脚本按原边界继续报告 P5 dynamic behavior 未就绪。
- `pytest -q`：17 passed。
- 本刀修改文档的相对链接检查：PASS。
- `git diff --check`：PASS。

边界：

- 归档和清单只能证明历史材料被完整保存，不能证明其中旧运行通过当前产品合同或真实回归。
- 发布级真实回归仍未执行；G4-1 不改变 `4/5` 的 roadmap 阶段完成度。
- 仓库源证据仍完整保留，只有 G4-2 在确认 acceptance 最小输入和引用边界后才能清理。

下一刀：执行 G4-2，先区分 acceptance 必需的轻量参考输入与可删除的完整运行/生成状态，再分组清理并用 `git ls-files`、引用扫描和聚焦测试验证仓库收敛。

## 2026-07-14：G4-2 仓库运行证据与生成状态收敛

目标：在 G4-1 已验证外部副本的前提下，让旧六仓库运行目录和生成状态退出 Git，并确保当前 acceptance 不再依赖旧 V1 证据形状。

完成：

- 删除 `tests/baseline/physical-runs/`、`reference-runs/` 及其余旧六仓库清单、对比报告、发布报告和验收清单；baseline 从 474 个跟踪文件收敛为 1 个入口 README。
- 删除 `acceptance/physical-baseline-check.sh` 和 `physical-repeatability-check.sh`；它们只验证旧完整运行目录，不是当前产品 gate。
- 保留 `acceptance/skill-structure-check.sh` 与 `skill-contract-check.sh` 作为当前 Skill 静态验收入口。
- 重写 baseline README，记录外部目录、清单哈希、当前验收入口和不得重新提交完整运行证据的边界。
- 更新 `.gitignore`，默认忽略 `tests/baseline/` 下的新工件，只允许入口 README 被跟踪。
- 更新 docs map 和本机工件索引，明确 baseline 只负责 Git 外材料定位，不再是当前 acceptance 输入。
- 删除本机 baseline 源目录中的 ignored 运行工件后，目录物理规模从约 1.1 GB 收敛到 4 KB；完整副本仍保存在 G4-1 外部归档。

验证：

- `pytest -q`：17 passed。
- `./acceptance/skill-structure-check.sh`：结构检查 PASS，24 项 Skill 合同检查全部 PASS。
- `bash -n acceptance/skill-structure-check.sh acceptance/skill-contract-check.sh`：PASS。
- `git ls-files` 收敛扫描：baseline 入口 1 个、acceptance 脚本 2 个；完整运行目录、`.meta-kim`、`__pycache__`、根 `graphify-out/`、Codex 转录和 zip 均为 0。
- 活动文档、Skill、实现、测试和 acceptance 对已删除脚本/目录的失效引用扫描：PASS。
- `.gitignore` 行为检查：新的 baseline 运行工件被忽略，入口 README 仍可跟踪。
- 外部归档仍存在，`ARCHIVE_MANIFEST.sha256` 的 SHA-256 仍为 `25899571e64847607e533f866a61115e2d658273d3a784e3d0a0d5a890ece215`。
- `git diff --check`：PASS。

边界：

- 本刀删除的是已外置的旧运行证据和与其强耦合的旧自检，不改变 analyzer Skill、Graphify gate 或真实 UAT 合同。
- 历史 progress 和 archive 可以继续提到已删除路径，用于解释演进；活动入口不能把这些路径当作当前输入。
- 发布级真实回归仍未执行，G4-2 不单独把实施完成度提升到 `5/5`。

下一刀：执行 G4-3，运行当前必需的全量实施验收和包表面审计，逐项确认 roadmap 的 G0-G4 退出条件；通过后才能声明实施主线完成，同时继续明确真实回归未执行。

## 2026-07-14：G4-3 实施主线最终验收

目标：从源码、Skill、发行包、文档控制面和 Git 跟踪面五个角度证明 G0-G4 退出条件全部成立，并把实施完成与发布级真实回归明确分开。

完成：

- 重新运行当前 Graphify gate 单元测试与 Skill 静态合同门。
- 在 `/tmp` 的独立源码副本中构建 wheel，检查包内容、console script、临时安装和 CLI 启动，不在仓库生成 build 工件。
- 核对中英文 README 的 `standard`/`deep`、禁止快速模式、Graphify `0.9.13+` code-only 和单一报告合同。
- 检查活动维护性 Markdown 链接、活动 JSON、Python/acceptance 表面和 Git 生成状态残留。
- 核验 G4-1 外部归档的清单条目、清单哈希和源/副本清单一致性。
- 将 roadmap 与 plan 标记为 `completed`，并同步根 `AGENTS.md`、docs map 和两个目录索引，明确当前没有活动实施控制面。

验证：

- `pytest -q`：17 passed。
- `./acceptance/skill-structure-check.sh`：结构检查 PASS，24 项 Skill 合同检查全部 PASS。
- `bash -n acceptance/skill-structure-check.sh acceptance/skill-contract-check.sh`：PASS。
- 临时构建 `stark_repo_analyzer-1.0.0-py3-none-any.whl`：PASS；包内只有 2 个 Python 文件和 1 个 console script，不含旧 `cli`、`contracts` 或 `doctor`。
- wheel 临时安装、模块 import 与 `stark-repo-analyzer-graphify-gate --help`：PASS。
- 57 份活动维护性 Markdown 相对链接检查：PASS；活动 JSON 解析：PASS。
- 中英文 README 核心产品合同语义对齐：PASS。
- 实现表面检查：`src/stark_repo_analyzer/` 只有 `__init__.py` 与 `graphify_gate.py`；acceptance 2 个、baseline 入口 1 个。
- 工作树未因验收产生新的未暂存或未跟踪文件；`git diff --check` 与 `git diff --cached --check`：PASS。
- 外部归档 3,913 条清单仍可定位，源/副本清单一致，清单 SHA-256 仍为 `25899571e64847607e533f866a61115e2d658273d3a784e3d0a0d5a890ece215`。

验收口径：

- G0：根 `AGENTS.md` 可唯一定位规则、文档分层和已完成控制面；旧 V1 控制面已归档。
- G1：中英文入口、Skill、spec 与当前 ADR 合同一致，静态合同门通过。
- G2：单一 Graphify gate、`0/10/30` 边界、路径规范化和源码只读保护由 17 个测试覆盖，发行包不包含旧控制面。
- G3：Skill 结构/合同门与四类聚焦 UAT 已完成；聚焦结果没有被冒充为发布级真实回归。
- G4：Git 不再跟踪完整运行目录、生成状态或缓存，大型历史证据已外置并可校验，活动入口无失效引用。

边界与结论：

- G0-G4 实施主线完成，完成度为 `5/5`。
- 发布级增强 `standard`、增强 `deep` 和无 Graphify `standard` 三条真实回归未执行，因此不能声明发布就绪或真实回归通过。
- 当前没有活动实施计划。G5 只在准备发布或用户明确要求时触发，并且必须使用新的活动执行计划记录会话和证据。
