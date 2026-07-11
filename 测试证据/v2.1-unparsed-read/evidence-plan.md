# Evidence Plan · v2.1-unparsed-read · standard

## 架构问题

- 长截图切割如何把「上传 → Worker 内容感知切图 → 按 index 落库 → 预览多选 → PDF/ZIP 导出」串成主链？
- 为什么状态集中在 `useAppState`，计算放在 `split.worker` + `splitAnalyzer`，而导出成为旁路？
- 在 parse_rate≈48% 时，哪些结论可从 hooks/utils/worker 成立，哪些必须标 Unsupported Area？
- 对 core unparsed 的高影响 UI（App/FileUploader/ExportControls/ScreenshotSplitter 等）如何通过 Unparsed File Read Pass 补读，而不伪装为 parse_rate 提升？
- `src` 与 `shared-components` / `config` / `tools` 的职责边界如何影响可维护性？

## 候选证据

- Repo Map / coverage-units（本目录 doctor/scan/units，commit `bdee20b8c4e4985c690a255ed09f64a3e335fd20`）
- 入口与编排：`src/main.tsx:5`（unparsed, manual-read）、`src/App.tsx`（unparsed, manual-read）
- 会话：`src/hooks/useAppState.ts:14-122`（reducer、按 index 写入、CLEANUP_SESSION）
- 切图：`src/hooks/useImageProcessor.ts:19+`、`src/hooks/useWorker.ts:23+`、`src/workers/split.worker.js:75+`
- 内容感知：`src/utils/splitAnalyzer.ts`（纯函数；失败回退等分）
- 导出：`src/utils/pdfExporter.ts:37+`、`src/utils/zipExporter.ts:34+`；UI ExportControls/FileUploader（unparsed，补读）
- 类型契约：`src/types/index.ts` ImageSlice/AppState/WorkerMessage
- 次要：`config/*`、`shared-components/*`、`tools/*`、`scripts/*` 抽样
- 文档：目标仓 README、docs/ARCHITECTURE.md、CLAUDE.md

## 模块分级

- **core · src**：业务主路径与绝大部分运行时逻辑（LOC 最大）
- **secondary · config**：应用/构建/环境配置聚合
- **secondary · shared-components**：可复用 UI/版权/通信管理，不拥有会话
- **secondary · tools / scripts**：工具链与工程脚本
- **excluded · test-setup / `.`**：测试夹具与根杂项，不进产品主数据流

（将同步写入 `coverage-units.json#modules` 的 classification/reason/source。）

## 分工

- **parallelism: degraded**
- **原因**：本轮为真实 UAT 主 Agent 串行执行（单会话、无并发子代理 worker）；严格记录降级，不得伪装 multi-agent 完整通过。
- **串行顺序**：
  1. Phase -1/0/1/2：doctor → scan → summarize → units
  2. 文档研读（README/ARCHITECTURE/CLAUDE）+ 写本 Plan
  3. Unparsed File Read Pass（core unparsed 高影响文件）
  4. src 核心主链深读（hooks/worker/utils）→ coverage 回填 + `module-evidence/src.json`
  5. 次要模块抽样回填（config/shared-components/tools/scripts ≥30%）
  6. 风险抽样 + Semantic Source Review（standard：每 core ≥1，本轮 ≥3 条高影响）
  7. 写 `report.md` → `gate --mode standard`
- **子代理产物**：无真实并行 subagent；目录 `subagent-artifacts/` 仅保留占位说明，全部证据由主 agent 写入本目录。
- **融合过程**：不适用多路 merge；叙事按数据流问题驱动由单一作者合成。
- **验收含义**：可证明 CLI 工件链 + 串行分析 + unparsed 补读；**不得**按 multi-agent 完整通过计。

## 预算

- mode: standard
- time: 90 分钟
- token: 90000
- subagent 上限: 6（**实际 0**，degraded）
- 覆盖目标: core 60% / secondary 30%
- Semantic Source Review: 每 core ≥1（实际 3 条）
- Unparsed File Read Pass: standard 覆盖 core 主路径相关 unparsed 子集（预算内其余 skip_reason）
- 报告长度: 中等，含全景/流程/协作/权衡/风险/改进/Mermaid/manual-read 锚点

## 风险抽样

- 异步切片乱序（useAppState ADD_IMAGE_SLICE）
- Object URL / Worker 生命周期（CLEANUP_SESSION）
- 导出空选择（pdfExporter）
- 全图 getImageData 内存峰值（split.worker）
- 解析盲区：大量 components unparsed → Unsupported Area + 补读记录

## Unparsed File Read Pass

- **触发**：core 模块 `src` 存在 unparsed 文件（units 阶段统计约 45 个 core unparsed）
- **unparsed_read_pass.parallelism: degraded**（主 Agent 串行补读，无 subagent）
- **工具白名单**：`rg`/`grep`、`wc`、文件读取、`nl`；git 只读。禁止安装依赖/改目标仓/抬高 parse_rate。
- **选样优先级与文件列表**（主路径优先）：
  1. `src/main.tsx` — 入口
  2. `src/App.tsx` — 唯一编排
  3. `src/components/FileUploader.tsx` — 上传 UI
  4. `src/components/ExportControls.tsx` — 导出 UI
  5. `src/components/ScreenshotSplitter.tsx` — 备选编排组件
  6. `src/components/ImagePreview.tsx` — 预览多选
  7. `src/components/Navigation.tsx` — 步骤导航
  8. 其余 SEO/debug/example/mobile 浅读或预算 skip
- **预算**：standard 覆盖主路径相关子集；本轮重点 7 个高影响 + 若干次要；SEO/debug 写 skip_reason
- **产物路径**：
  - `unparsed-file-reviews/*.md`
  - `unparsed-file-reviews.json`
  - `module-evidence/src.json#unparsed_manual_reads`
- **语义边界**：补读 confidence=`manual-read`；**不**清除 unparsed、**不**提升 parse_rate、**不**计为 analyzed unit；报告引用须标明 manual-read / 非枚举单元

## 报告结构

场景问题 → 项目全景 → 设计哲学 → 核心流程 Mermaid → 模块协作 → src 深度（状态/Worker/内容感知/导出）→ unparsed 补读锚点 → 次要模块 → 风险与 Unsupported → 批判性评价与改进 → 业界对比 → 预算执行摘要
