# Evidence Plan · 真实UAT回归测试·deep · 2026-07-11

## 架构问题

- 长截图切割如何把「上传 → module Worker 内容感知切图 → 按 index 落库 → 预览多选 → PDF/ZIP 导出」串成主链？回答将决定核心流程叙事与模块边界。
- 为什么状态集中在 `useAppState`，计算放在 `split.worker` + `splitAnalyzer`，而导出成为旁路？回答将支撑设计哲学与权衡评价。
- 导航子系统如何用 AppState 守卫 `/upload`→`/split`→`/export` 可达性，并与「切片未就绪不跳转」协同？
- SEO 配置为何存在 JSON/Manager/桥接层/多 Manager 并行面？是否 dual-write 或死实现？
- deep 模式下 Graphify EXTRACTED 引用边是否足以支撑跨模块结论？`refs_status=partial/missing` 的边界如何诚实披露？
- UI 可感知选项（导出格式/高级项）是否都进入真实执行路径？

## 候选证据

- 确定性工件：本目录 `doctor-report.json`（`allowed_deep=true`）/ `repo-map.json` / `coverage-units.json`（mode=deep，`graphify_refs.wired=true`，nodes=2875，extracted_ref_links=1507）
- Graphify 查询：`worker split navigation export SEO architecture` 关联 Navigation / splitAnalyzer / WorkerMessage / SEOConfigManager 等
- 入口与编排：`src/main.tsx:5`、`src/App.tsx:28`、`src/App.tsx:121-135`、`src/App.tsx:196`、`src/App.tsx:224`
- 会话：`src/hooks/useAppState.ts:14`、`:33`、`:47`、`:89`、`:122`
- 切图编排：`src/hooks/useImageProcessor.ts:19`、`:92`；`src/hooks/useWorker.ts:23`、`:42`
- Worker：`src/workers/split.worker.js:20`、`:75`、`:117`、`:228`、`:259`
- 内容感知：`src/utils/splitAnalyzer.ts:50`、`:88`、`:250`
- 导出：`src/utils/pdfExporter.ts:37`、`:208`；`src/utils/zipExporter.ts:34`；UI `src/components/ExportControls.tsx:43`、`:82`
- 导航：`src/hooks/useNavigationState.ts:53`、`:105`；`src/components/Navigation.tsx:1`；`src/utils/navigationErrorHandler.ts`
- SEO：`src/components/SEOManager.tsx:1`、`src/components/EnhancedSEOManager.tsx`、`src/utils/seo/SEOConfigManager.ts:142`、`src/config/seo.config.ts:48`
- 类型契约：`src/types/index.ts` ImageSlice/AppState/WorkerMessage
- 次要：`config/*`、`shared-components/*`、`tools/build-scripts/*`、`scripts/generate-seo-files.js`
- 文档：目标仓 README、docs/ARCHITECTURE.md ADR-001、docs/PROJECT-INDEX.md

## 模块分级

- **core · src**：业务主路径与绝大部分运行时逻辑（单元 721，deep 目标 ≥90%）
- **secondary · config**：应用/构建/环境配置聚合（≥60%）
- **secondary · shared-components**：可复用 UI/版权/通信管理，不拥有会话（≥60%）
- **secondary · tools / scripts**：工具链与工程脚本（≥60%）
- **excluded · test-setup / `.`**：测试夹具与根杂项，不进产品主数据流

分级已同步写入 `coverage-units.json#modules`（source=`evidence-plan.md`，可审计）。

## 分工（parallelism: active）

本轮在支持并发工具调用的 Codex 会话中**真实并行**启动 3 个分析 worker（子代理角色），各自独立读写产物，再由主 agent 融合。

| 子代理 ID | 职责 / scope | 产物路径 |
|---|---|---|
| `subagent-src-pipeline` | 会话状态 + Worker 内容感知切图主链（useAppState / useImageProcessor / useWorker / split.worker / splitAnalyzer / App 编排） | `subagent-artifacts/subagent-src-pipeline.json`；贡献 `module-evidence/src.json` |
| `subagent-src-nav-export-seo` | 导航守卫 + 上传/导出 UI + PDF/ZIP + SEO 配置面（Navigation / useNavigationState / ExportControls / pdf/zipExporter / SEOManager / SEOConfigManager） | `subagent-artifacts/subagent-src-nav-export-seo.json` |
| `subagent-secondary-deep` | config / shared-components / tools / scripts 次要模块抽样（≥60%） | `subagent-artifacts/subagent-secondary-deep.json` |

### 实际子代理分工

- 子代理分工：subagent-src-pipeline 负责 src 会话状态与 Worker 切图主链。
- 子代理分工：subagent-src-nav-export-seo 负责导航/导出/SEO 边界与 insight probes。
- 子代理分工：subagent-secondary-deep 负责 config/shared-components/tools/scripts 次要模块抽样。

### 每个子代理产物

- 子代理产物：subagent-src-pipeline 写入 subagent-artifacts/subagent-src-pipeline.json 与贡献 module-evidence/src.json。
- 子代理产物：subagent-src-nav-export-seo 写入 subagent-artifacts/subagent-src-nav-export-seo.json。
- 子代理产物：subagent-secondary-deep 写入 subagent-artifacts/subagent-secondary-deep.json。

### 主 agent 融合过程

主 agent 融合过程：
1. 合并三份子代理的锚点判断与风险抽样，去重后回填 `coverage-units.json`（core≥90%、secondary≥60%，未分析 core 写 skip_reason）。
2. 合成单一 `module-evidence/src.json`（含 semantic_reviews 最多 3 条），并写 `insight-probes.json`。
3. 按数据流叙事写 `report.md`（上传→Worker→导航→导出→SEO），插入 Mermaid，披露 partial refs 与开放问题。
4. 运行 `repo-analyzer gate --mode deep`；仅 `allowed_to_synthesize:true` 时写 `ANALYSIS_REPORT.md`。
5. 写中文 `UAT_EXEC_SUMMARY.md`，诚实区分过程有效 vs 产品完整通过。

- parallelism: active
- mode: deep
- tooling: Graphify wired + universal-ctags enumerator + ast-grep available

## 预算

- mode: **deep**
- time: 约 45–90 分钟墙钟（本轮独立 codex 会话）
- token: 高预算（deep 覆盖 90%/60% + SSR + Graphify 查询）
- subagent 上限: 8（本轮实际 3）
- 单 agent 证据预算: 优先 PRIORITY 文件全读 + 其余单元模板化判断
- 报告长度: report.md 约 6–12k 字；终稿同量级

## 风险抽样

| 核心模块 | 风险类别 | 候选路径 | 停止条件 |
|---|---|---|---|
| src | performance | `split.worker.js` 全图 getImageData（>4000px 未分块） | 确认注释与代码一致即可 |
| src | correctness | `ADD_IMAGE_SLICE` 按 index 写入 vs img.onload 乱序 | 读 reducer 与 ImageProcessor |
| src | error-handling | 内容分析 catch 后等分回退；导航 MISSING_SLICES 踢回 | 读 worker + App effect |
| src | config-drift | SEO JSON/TS 桥接 + EnhancedSEOManager 并行面 | 形成 insight probe 结论 |
| src | reference-quality | core incomplete refs 约 76.7% <80% 阈值 | doctor/units graphify 已接线 |

## 报告叙事线

问题场景 → 项目全景 → 核心设计哲学（状态集中/计算下沉/导出旁路）→ 模块深度（状态→Worker/Analyzer→导航→导出→SEO）→ 权衡与批判 → 业界对比 → 可借鉴经验 → Unsupported/开放问题。
