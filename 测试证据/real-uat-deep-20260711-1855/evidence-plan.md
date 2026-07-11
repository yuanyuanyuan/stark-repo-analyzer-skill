# Evidence Plan · 真实UAT回归测试·deep · 2026-07-11

## 架构问题

- 长截图切割如何把「上传 → module Worker 内容感知切图 → 按 index 落库 → 预览多选 → PDF/ZIP 导出」串成主链？回答决定核心流程叙事与模块边界。
- 为什么状态集中在 `useAppState`，计算放在 `split.worker` + `splitAnalyzer`，导出成为旁路？回答支撑设计哲学与权衡评价。
- deep 能力合同（graph-queries / symbol-enumeration / reference-edges）下，Graphify 图与 Universal Ctags 符号分母如何增强证据？哪些引用边仍只能 partial？
- `src` 与 `shared-components` / `config` / `tools` / `scripts` 的职责边界如何影响可维护性与 90%/60% 覆盖策略？
- 内容感知参数（thresholdRatio 等）被标为经验值时，产品风险与可校准性如何评价？

## 候选证据

- 确定性工件：本目录 `doctor-report.json` / `repo-map.json` / `coverage-units.json`（mode=deep，enumerator=universal-ctags，graph_provider=graphify，parse_rate=1.0）
- Graphify：目标仓 `graphify-out/graph.json`（AST rebuild，~2875 nodes / 4550 edges）；`graphify query/explain` 用于跨文件候选
- 入口与编排：`src/main.tsx:5`、`src/App.tsx:28`、`src/App.tsx:196`、`src/App.tsx:224`
- 会话：`src/hooks/useAppState.ts:14`、`:33`、`:47`、`:89`、`:122`
- 切图编排：`src/hooks/useImageProcessor.ts:19`、`:92`；`src/hooks/useWorker.ts:23`、`:42`、`:133`
- Worker：`src/workers/split.worker.js:20`、`:75`、`:117`、`:228`、`:259`
- 内容感知：`src/utils/splitAnalyzer.ts:50`、`:88`、`:194`、`:250`
- 导出：`src/utils/pdfExporter.ts:37`、`:51`；`src/utils/zipExporter.ts:34`、`:44`
- 类型契约：`src/types/index.ts:3` 起 ImageSlice/AppState/WorkerMessage
- 次要：`config/index.ts:77`、`shared-components/index.ts:40`、`tools/build-scripts/*`、`scripts/generate-seo-files.js`
- 文档：目标仓 README、docs/ARCHITECTURE.md、CLAUDE.md、设计注释中的 spec §4

## 模块分级

- **core · src**：业务主路径与绝大部分运行时逻辑（LOC/单元最大）
- **secondary · config**：应用/构建/环境配置聚合
- **secondary · shared-components**：可复用 UI/版权/通信管理，不拥有会话
- **secondary · tools / scripts**：工具链与工程脚本
- **excluded · test-setup / `.`**：测试夹具与根杂项，不进产品主数据流

分级已同步写入 `coverage-units.json#modules`（source 可审计）。

## 分工（parallelism: active）

本轮在支持并发工具调用的 Codex 会话中**真实并行**启动 3 个分析 worker（子代理角色），各自独立读写产物，再由主 Agent 融合。

| 子代理 ID | 职责 / scope | 产物路径 |
|---|---|---|
| `subagent-src-pipeline` | 会话状态 + Worker 内容感知切图主链（useAppState / useImageProcessor / useWorker / split.worker / splitAnalyzer / App 编排） | `subagent-artifacts/subagent-src-pipeline.json`；贡献 `module-evidence/src.json` |
| `subagent-src-export-ui` | 上传 UI + PDF/ZIP 导出边界 + 类型契约 | `subagent-artifacts/subagent-src-export-ui.json` |
| `subagent-secondary-deep` | config / shared-components / tools / scripts 次要模块抽样（≥60%）+ Graphify 跨模块边观察 | `subagent-artifacts/subagent-secondary-deep.json` |

### 实际子代理分工

- 子代理分工：subagent-src-pipeline 负责 src 会话状态与 Worker 切图主链，并使用 graphify explain/query 验证 splitAnalyzer↔worker 边。
- 子代理分工：subagent-src-export-ui 负责上传 UI、PDF/ZIP 导出边界与 ImageSlice 契约。
- 子代理分工：subagent-secondary-deep 负责 config/shared-components/tools/scripts 次要模块 60%+ 抽样与跨模块依赖记录。

### 每个子代理产物

- 子代理产物：subagent-src-pipeline 写入 subagent-artifacts/subagent-src-pipeline.json 并贡献 module-evidence/src.json。
- 子代理产物：subagent-src-export-ui 写入 subagent-artifacts/subagent-src-export-ui.json。
- 子代理产物：subagent-secondary-deep 写入 subagent-artifacts/subagent-secondary-deep.json。

### 主 agent 融合过程

主 agent 融合过程：

1. 校验三份 subagent JSON 的 unit_id / anchor / judgment 非空  
2. 合并写入 `coverage-units.json` 回填（core≥90% / secondary≥60%，未分析 core 填 skip_reason）  
3. 合成 `module-evidence/src.json`（吸收 pipeline+export 发现；secondary 进入跨模块依赖）  
4. 主 agent 对高影响单元做 Semantic Source Review（deep：每 core 最多 3 条代表性 unit）  
5. 写 `report.md` 叙事线：问题 → 全景 → 主链 → 导出 → 次要模块 → Graphify 观察 → 风险/建议  
6. 跑 `gate --mode deep`  
7. 记录预算、并行摘要与 reference-edges 限制  

- parallelism: active

## 预算

- mode: deep
- time: 240 分钟
- token: 240000
- subagent 上限: 8（**本轮实际并行 3**）
- 单 agent 证据预算: 主链深读 + 次要 60% 抽样 + graphify 查询；不为凑行数读低价值 SEO 类型膨胀
- 覆盖目标: core 90% / secondary 60%
- Semantic Source Review: 每 core 最多 3 条代表性 analyzed unit
- 报告长度: deep 预算，含全景/流程/协作/权衡/风险/改进/Mermaid/Unsupported
- tooling: enhanced（graphify + universal-ctags + baseline rg/git）；doctor 三能力已放行

## 风险抽样

- error-handling：Worker 分析失败回退等分（split.worker.js:125-128）；导出无选中告警（App.tsx:225-227）
- concurrency：img.onload 异步与 index 写入（useAppState ADD_IMAGE_SLICE；useImageProcessor handleChunk）
- resource-lifecycle：ObjectURL revoke 与 worker.terminate（CLEANUP_SESSION）
- performance：全图 getImageData 大图风险（split.worker.js 注释 §4.6）
- parameter-risk：DEFAULT_SPLIT_OPTIONS 经验阈值未校准
- reference-quality：ctags 对 TS/JS 未产出 roles=reference，core refs 全为 partial/missing（预期 gate 压力点）

## 预期 Unsupported Area / 开放问题

- Universal Ctags 对 TypeScript/JavaScript 的 reference roles 未启用有效引用边 → `refs_status` 无法达到 complete；跨模块调用图依赖 Graphify EXTRACTED 边与人工读码，不得把 partial 文本启发式写成已完全验证。
- SEO 相关大体量类型/组件在业务主链外；深读抽样但不宣称 SEO 子系统覆盖充分。
- graphify path 对部分符号别名存在歧义，最短路径查询可能 miss。

## 报告章节结构（叙事线）

1. 问题场景：长截图难分享/难打印  
2. 项目全景与定位  
3. 核心设计哲学：状态集中、计算下沉、导出旁路、算法 I/O 分离  
4. 主链模块深读（pipeline）  
5. 导出与 UI 边界  
6. 次要模块与工程边界  
7. 权衡、风险、竞品路线差异  
8. Unsupported / 开放问题 / 可借鉴经验  
