# Repo Analyzer

面向真实仓库的架构分析技能与确定性工具链：产出可决策的架构报告，并用可审计证据约束结论。

## Language

**Primary Reader**:
一次分析的共同主用户，包含两类消费者，成功标准必须同时照顾两者，而不是只服务其一：
1. **Human Decision Reader** — 要据此改代码、做 onboarding 或架构决策的人；
2. **Agent Consumer** — 要继续自动改代码、开 issue、做 review 或二次推理的 AI agent。
_Avoid_: 只把人当主用户、只把验收脚本当主用户、把 Agent 降级为“附带读者”

**Human Decision Reader**:
需要可读叙事、优先级与改造建议的人类读者。
_Avoid_: 仅门禁日志消费者

**Agent Consumer**:
需要稳定结构、锚点、机器可读证据与明确边界声明的 AI agent 消费者。
_Avoid_: 仅聊天摘要读者、无结构自由文本消费者

**Acceptance Auditor**:
验证分析流程可复查、可回归的角色。其 gate/工件要求是约束，不是产品北极星。
_Avoid_: 主用户、Primary Reader

**Delivery Contract**:
一次分析对 Primary Reader 的交付约定：必须有可决策终稿；对人可读，对 agent 可解析/可引用（锚点、结构化证据、明确 unsupported）。审计工件为附属。
_Avoid_: 仅 UAT 摘要、仅 gate 通过、仅草稿 report.md、仅给人读的散文、仅给机器的 JSON 无叙事

**Insight Probe**:
跨仓库通用的定向取证规则：沿「用户可感知承诺 / 多处规则 / 配置真相」追到实现，用来抬高准确度与有用性。探针类别必须可迁移到任意项目，不得绑定某一示例仓的业务名词。
_Avoid_: 覆盖率抽样、仓库专用检查单当主机制、只适用于单一 demo 项目的规则

**Insight Probe Catalog**:
一小份稳定的通用探针类别清单（首批：UI Promise → Runtime Path、Multi-Source Rules、Config Dual-Write / Dead Implementation），standard/deep 默认启用。具体仓库只提供命中实例，不改写类别本身。
_Avoid_: 每个目标仓手写全套探针、用 secondary 覆盖率代替探针目录

**Probe Promotion**:
将 `status=hit` 的 Insight Probe 结论升格写入终稿 `ANALYSIS_REPORT.md`「风险与改造优先级」的义务与结果。仅 JSON hit、仅草稿锚点、或仅非空 `report_ref` 均不算完成。
_Avoid_: 侧车命中即过线、report_ref 摆设、hit 吞没在流程产物里

**Probe Promotion Marker**:
写入终稿风险/改造条目内的稳定机器标记，用于把 hit 探针一对一关联到该条目。规范形态为 `<!-- probe-promotion: <probe_id> -->`（或等价单行），`probe_id` 取自 Catalog 固定 id。
_Avoid_: 仅靠中文类别全名 grep、章节级一锅端绑定多个 hit、agent 手填升格 sidecar

**Probe Hit Promotion Rate**:

Density Proxy 指标：终稿中成功完成 Probe Promotion 的 hit 数 / 全部 hit 数。Slice A 要求该比率为 100%。
_Avoid_: 有 insight-probes.json 即准确、只数 hit 不数升格

**Probe Obligation**:

对 Insight Probe Catalog 的执行义务：每个启用类别必须产出结论（命中 / 未命中 / 不适用且含理由），写入结构化证据与终稿；未执行或无结论视为流程不合格。发现硬伤必须进入风险与改造优先级，不得吞没。**不**因「未发现硬伤」而拒绝合成终稿。
_Avoid_: 软提醒即可、用“没挖到 bug”阻塞 Synthesis Permit、静默跳过类别

**Probe Budget Policy**:
Insight Probe **不设**固定时间/文件硬顶；以查清类别结论为停条件，而不是触达配额就停。不得以截断探针换交付。
_Avoid_: 用覆盖率顶替探针、为保 wall-clock 而跳过探针

**Quality-over-Speed**:
有用性、分析质量、准确度优先于速度。本阶段「压过 v1.0」的验收**不把速度列为必达维度**；允许更慢。速度仅作浪费治理，不是过线 KPI。
_Avoid_: 以快于 v1.0 为硬 KPI、用砍深度换 benchmark 数字、把速度与另外三维并列硬验收

**Beats-v1.0 Bar**:
本阶段相对 v1.0 的必达维度三项：对 Primary Reader 更有用、分析质量更高、分析更准确。速度暂不纳入必达。
_Avoid_: 四维捆绑硬过线、无金样的自我感觉良好

**Gold Sample**:
用于准确度回归的已知高价值硬伤样本（含仓库、探针类别、期望命中结论与必须出现在终稿中的表达）。新版本分析必须命中；命中若未进入终稿优先级视为失败。金样用通用探针类别描述，不把单一 demo 业务名词写成产品唯一范围。
_Avoid_: 只跑探针流程无期望结果、仅 JSON 命中人看不见

**Gold Sample Set v1**:
第一批准确度金样：G1 UI Promise → Runtime Path；G2 Multi-Source Rules；G3 Config Dual-Write / Dead Implementation；G4 非 UI 形态仓的 N/A 或真实命中（通用性护栏）。G1–G3 为必达命中类；G4 防止探针只会报单一形态仓。
_Avoid_: 仅长截图业务 checklist、无 G4 的单形态过拟合

**Accuracy Bar**:
准确度压过 v1.0 的过线标准：Gold Sample Set v1 按规则必中（或 G4 合法 N/A），且命中必须进入终稿风险/改造优先级（人对得上叙事，agent 对得上结构化字段）。仅「跑过探针」不算过线。
_Avoid_: 形式主义跑满三类、只靠 coverage 声称更准

**Usefulness Bar**:
有用性压过 v1.0 的过线标准：Human Decision Reader 能从终稿直接拿到主链理解与可执行改造优先级；Agent Consumer 能稳定抽出 `delivery_status`、锚点、探针结论与改造项。相对 v1.0 对照清单不退步，且探针硬伤进入优先级。
_Avoid_: 只增清单长度、只堆章节标题、只给散文或只给 JSON

**Quality Bar**:
分析质量压过 v1.0 的过线标准：主链叙事完整、证据锚点与判断一致、无模板化重复灌水、Unsupported/降级边界清楚；不把 coverage 或章节齐全当成质量本身。
_Avoid_: report-depth 凑字数、同义段落重复、用门禁全绿代替洞见质量

**Reader Rubric**:
有用性与分析质量的固定对照清单（相对 v1.0 逐项：主链是否说清、改造是否可执行且有锚点、双主用户是否可消费、有无模板废话、探针硬伤是否进优先级等）。
_Avoid_: 纯印象分、每次临时换标准

**Agent Smoke**:
对终稿/结构化产物的最小可解析检查：能否读出 delivery_status、探针结论、锚点与改造项，供 agent 继续工作。
_Avoid_: 仅人工目测有用性

**Probe Execution Model**:
Insight Probe 采用「确定性辅助 + LLM 判定」：确定性步骤只负责枚举候选入口（如表单/选项字段、多份规则定义、配置/平行实现候选），不宣布硬伤成立；LLM 沿候选追到实现并写入结构化结论。禁止纯自觉 markdown、禁止仅靠脆弱全自动正则充当准确度。
_Avoid_: 纯 LLM 无 schema、纯脚本判定跨仓硬伤、无候选枚举的盲搜

**Delivery PR Cadence**:
第一交付切片（P1+P2+P3）以多 PR 串联落地，便于审阅与回滚；**全部落地前不得宣称 Beats-v1.0 Bar 已达成**。单个 PR 的阶段性合并不等于切片完成。
_Avoid_: 单巨型 PR、每个半成品 PR 都宣布压过 v1.0

**First Delivery Slice**:
第一交付切片包含 P1+P2+P3（Insight Probe、Full/Degraded Delivery、Gold Sample/Reader Rubric/Agent Smoke）。P4 deep reference Tooling Debt 不在本切片必达内，可并行另开。
_Avoid_: 只写 ADR 无行为变化、把 P4 塞进第一切片挡合并、用 coverage 扩建冒充本切片

**Implementation Wave**:
压过 v1.0 的工作包顺序仍为 P1→P2→P3、P4 可并行；但第一交付切片一次性包含 P1+P2+P3，合并后须能用金样与 rubric 证明 Beats-v1.0 Bar。
_Avoid_: 先刷 coverage、先只救 deep 门禁、四包一次性大爆炸

**Probe Process Gate**:
Mechanical Gate 的一项：检查 Insight Probe 流程是否完成（`insight-probes.json` 存在、Catalog 各类有结论）。缺产物/缺类别 → gate fail → 不得 Full Delivery；可走 Degraded Delivery。**不**因 status=miss（未发现硬伤）而 fail。
_Avoid_: 仅警告可忽略、因没挖到 bug 挡报告、流程失败就连 Degraded 都不给

**Final Report Quality Skeleton**:
references 中的最小终稿骨架模板，预置 Main Chain / claim / risk 标记占位与元数据字段，供 agent 套用填肉。用于降低漏标记与合规浅写之间的操作摩擦。
_Avoid_: agent 手填 QC sidecar、把 QC-1 全量 JSON 脚手架塞进 Slice A 冒充骨架

**Recommended Report Sections**:

终稿推荐给人读的稳定章节标题：主链、关键设计决策、风险与改造优先级（可带编号前缀）。偏离仅 UAT 警告；硬判仍靠标记与条目结构。
_Avoid_: 标题用词 hard fail、无标记只靠标题猜合同表面

**Final Report Quality Contract**:

对终稿 `ANALYSIS_REPORT.md`（及合成前 `report.md`）的读者向交付合同：主链完整、可枚举独立架构 claim、风险/改造可执行且有锚点、probe hit 必须升格进终稿优先级。用于抬高洞见与可执行性上限。
_Avoid_: Mechanical Gate 成功条件、仅靠 report-depth 关键词过门、把锚点/claim 数量 hard fail 当质量充分条件

**Quality Contract Layer**:
Final Report Quality Contract 的默认执行位置：Skill 交付义务 + 真实UAT / Reader Rubric / 对照脚本（及可选 soft warning）。**默认不**进入 Mechanical Gate hard fail；unique anchors 下限与独立 claim 数量下限尤其不得 hard fail。
_Avoid_: 用 gate 全红逼刷密度、把 Beats-v1.0 等同于 checks 全绿

**Quality Correction Workstream (QC)**:
针对「Gate 易绿、终稿仍薄于 v1」的纠偏工作包集合，编号 `QC-0`…`QC-5`（终稿质量合同、降 JSON 税、业务模块叙事、深读预算、对照指标、Reader 闭环执行）。与 First Delivery Slice 的 P1–P4 **分轨**，不得混用裸 P 编号指代纠偏包。
_Avoid_: 用 P0–P5 同时指纠偏与 First Delivery、宣称 First Delivery 齐备即 Beats-v1.0

**QC-0**:
终稿质量合同工作包：主链槽位、Probe Promotion、可枚举 claim、风险/改造结构等读者向交付要求。
_Avoid_: Mechanical Gate 扩建包、doctor 能力扩张包

**Slice A Quality Minimum**:
纠偏第一刀的最小质量闭环与可比场景下 `quality_contract=pass` 条件：Probe Promotion 100% + Main Chain 五槽标记 + 至少 1 条可解析 Architecture Claim + 相对 `baseline_v2_standard_pre_qc` 的 合同表面 unique anchors 与结构化 risk_count 双严格上升。完成定义是脚本/skill 落地且真实UAT 盖戳链路可解释，不要求第一次 UAT 必 pass，禁止为冲 pass 造假。
_Avoid_: 第一刀夹带 QC-1/2/3 大改、硬绝对数量门禁冒充趋势双升、缺 baseline 却判 fail、宣称已 Beats-v1.0


**Main Chain**:
终稿中按数据/控制流展开的强制叙事骨架，固定 **5 个角色槽**（Ingress → Core Transform → State/Truth → Boundary/Guard → Egress）；槽位标签可按仓命名，角色不可缺，每槽须有 `file:line` 锚点。Evidence Plan 须先声明本仓槽位映射。
_Avoid_: 长截图业务五段当唯一产品语义、单一 src 大章糊弄、无锚点空标题、整条主链 n_a

**Main Chain Slot Marker**:
终稿主链块内的稳定机器标记，形态 `<!-- main-chain: <slot_id> -->`，`slot_id` 为 ingress|core_transform|state_truth|boundary_guard|egress。Slice A 用其做 quality_contract 硬判；Evidence Plan 槽位声明为过程软要求。
_Avoid_: 仅靠上传/导出等业务词猜槽位、章节级一锅端无分槽标记

**Main Chain Role Slot**:

Main Chain 上的五个跨仓角色位置之一：Ingress、Core Transform、State/Truth、Boundary/Guard、Egress。终稿必须覆盖全部槽位；具体标题与文件由目标仓映射。
_Avoid_: 固定业务名词阶段、可任意省略的装饰章节

**Risk Item**:
终稿「风险与改造」类章节中一条**结构化**可执行风险/改造条目：须含源码锚点与改造方向（可含 Probe Promotion Marker）。`risk_count` 只计此类条目；散文中的风险叙述不计。pre-QC 终稿按此规则可为 0。
_Avoid_: 无锚点抱怨、纯现象罗列、用「文中提到风险」冒充 risk_count、matrix risk_areas 替代终稿条目

**Architecture Claim**:

终稿中一条可争辩的架构判断（含判断句与证据锚点），供读者理解设计取舍。机判容器为「关键设计决策」类章节 + `<!-- arch-claim -->` 标记；不是风险项，也不是纯事实清单。
_Avoid_: 任意列表项都算 claim、把风险/探针升格条当 claim、无锚点口号

**Density Proxy**:


可机读的终稿密度对照指标（如 unique anchors、粗计独立 claim 数、风险/改造条数、probe→终稿映射率）。用于 UAT 对照与回归，**不是**洞见本身，也**不是** Full Delivery 的充分条件。
_Avoid_: 质量本身、Beats-v1.0 唯一判据、Mechanical Gate hard 阈值

**Mechanical Gate**:

不依赖智力判断的确定性质量门（覆盖率、parse-quality、reference-quality、report-depth 等）。
_Avoid_: 洞见质量、有用性评价

**Synthesis Rule**:
gate 全绿 → 合成 Full `ANALYSIS_REPORT.md`（`delivery_status=full`）。gate 未放行 → 仍合成同路径 `ANALYSIS_REPORT.md` 为 Degraded（横幅 + `delivery_status=degraded` + 失败项），**不得**宣称产品分析完整通过。旧规则「gate 红禁止任何 ANALYSIS_REPORT」废止，替换为本规则。
_Avoid_: gate 红就主用户空手、gate 红却无标记假完整、用写文件冒充完整通过

**Synthesis Permit**:
`quality-gate-report.json` 中 `allowed_to_synthesize: true` 所代表的「允许合成 **Full Delivery**」许可。许可失败不等于对 Primary Reader 无交付，但不得宣称完整通过。
_Avoid_: 分析成功、产品完整通过、主用户交付成功

**Contract Surface Anchors**:
落在 Final Report Quality Contract 表面内的 unique anchors：Main Chain 标记块、Architecture Claim 条目、Risk Item 条目。Slice A 用其相对 baseline 的严格上升作为 `quality_contract` 密度硬条件之一。
_Avoid_: 文末堆锚点充全文 unique_anchors、用全文密度硬过线

**Unique Anchors**:

终稿 `ANALYSIS_REPORT.md` 中按固定规则规范化后的不重复 `file:line`（或 `file:start-end`）锚点集合大小。用于 Density Proxy 与 COMPARE，不代表洞见质量本身。
_Avoid_: basename-only 假合并、把 matrix 锚点当读者密度、锚点数 hard gate

**Comparable UAT Profile**:
启用密度双升硬条件时的固定对照场景声明（目标仓路径、commit、mode 与 baseline 集）。不满足时 `quality_contract` 对密度维度为 `not_evaluated`，不得静默乱比。
_Avoid_: 换仓仍宣称相对 213622 上升、commit 漂移却硬判 pass/fail

**Density Baseline**:


质量对照的固定参照终稿集合：至少包含 `baseline_v1`（v1.0 未改造终稿）与 `baseline_v2_standard_pre_qc`（纠偏前 standard 回归终稿）。COMPARE 必须相对两者出表；更换路径须显式记录。
_Avoid_: 每次换对照稿、只与上次 run 比、用 deep 参考冒充 standard 主 baseline

**Quality Contract Structure Layer**:
质量合同中不依赖 v1/pre-QC baseline 的结构层：Probe Promotion、Main Chain 五槽、Architecture Claim 可枚举、轻量防刷。任意仓可判 pass/fail。
_Avoid_: 仅在长截图可比 UAT 才要求结构

**Quality Contract Density Layer**:
质量合同中相对固定 baseline 的密度层：合同表面 anchors 与结构化 risk_count 双升。仅 Comparable UAT Profile 下判定；否则 `not_evaluated`。
_Avoid_: 换仓仍硬比 213622、用全文堆锚点充密度层

**Quality Contract CLI**:
确定性子命令 `repo-analyzer quality-contract`：对照终稿与 baseline、写出 `quality-contract-report.json` 并 `--stamp-report` 盖戳终稿。Skill 在合成终稿后强制调用；真实UAT 复跑校验。不属于 Mechanical Gate，fail 不回滚 `delivery_status`。
_Avoid_: 并入 gate 当 hard fail、agent 自报 pass 替代 CLI、漏跑仍宣称质量过线


**Quality Contract Report**:



确定性对照脚本产出的机读盖戳结果，路径约定为工作目录 `quality-contract-report.json`。是 `quality_contract` 字段的 SSOT；终稿文首必须与之一致，分析 agent 自报 pass 无效。
_Avoid_: agent 手写 pass 当过线、只改 markdown 不改 json、无脚本的自我感觉良好

**Quality Contract Status**:
终稿/UAT 上对 Final Report Quality Contract 的判定：`pass` | `fail` | `not_evaluated`。与 `delivery_status` 正交；fail 不自动降为 Degraded；Degraded 时仍可盖戳且允许 `degraded+pass`（不得宣传 Beats 或产品完整通过）。
_Avoid_: 用 delivery_status 表达质量合同、gate 全绿即 quality_contract=pass、Degraded 强制 skip/fail QC


**Beats-v1 Status**:
终稿/UAT 上对 Beats-v1.0 Bar 的判定：`pass` | `fail` | `not_evaluated`。只认 Accuracy/Usefulness/Quality Reader 三维，不认 checks 全绿。
_Avoid_: gate 13/13 即压过 v1、Full Delivery 即 Beats-v1.0

**Full Delivery**:

Mechanical Gate 全绿后的完整终稿：统一路径 `ANALYSIS_REPORT.md`，`delivery_status=full`。可作为 UAT「产品分析完整通过」的前提之一。
_Avoid_: 有任意 markdown 就算完整通过

**Degraded Delivery**:
Mechanical Gate 未放行时仍向 Primary Reader 交付的可用终稿：仍写入同一路径 `ANALYSIS_REPORT.md`（不另起文件名），但必须含文首降级横幅、`delivery_status=degraded`、失败门禁列表与结论可信度边界。验收上不得算产品分析完整通过，也不得让主用户空手。
_Avoid_: 用草稿冒充完整通过、gate 红就完全不写终稿、无标记的“假完整”报告、另用 `.degraded.md` 作为主路径

**Tooling Debt**:
阻碍 Full Delivery 的分析器自身缺陷（例如 Graphify 边未写入 units `refs_status`）。本阶段 deep 的 reference 接线债必须偿还；不能靠放宽 Mechanical Gate、也不能靠长期 Degraded Delivery 假装 deep 完整通过。
_Avoid_: 目标仓库的业务缺陷、用改阈值冒充能力具备
