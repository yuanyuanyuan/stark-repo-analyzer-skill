# Evidence Plan · 真实UAT回归测试·standard · 2026-07-11

## 架构问题

- 长截图切割如何把「上传 → Worker 内容感知切图 → 按 index 落库 → 预览多选 → PDF/ZIP 导出」串成主链？回答将决定核心流程叙事与模块边界。
- 为什么状态集中在 `useAppState`，计算放在 `split.worker` + `splitAnalyzer`，而导出成为旁路？回答将支撑设计哲学与权衡评价。
- `src` 与 `shared-components` / `config` / `tools` / `scripts` 的职责边界如何影响可维护性与覆盖策略？
- standard 基线启发式（refs partial/missing）下，哪些跨模块结论可成立，哪些必须标为开放问题？

## 候选证据

- 确定性工件：本目录 `doctor-report.json` / `repo-map.json` / `coverage-units.json`（mode=standard，enumerator=heuristic-text）
- 入口与编排：`src/main.tsx:5`、`src/App.tsx:28`、`src/App.tsx:196`、`src/App.tsx:224`
- 会话：`src/hooks/useAppState.ts:14`、`:33`、`:47`、`:89`、`:122`
- 切图编排：`src/hooks/useImageProcessor.ts:19`、`:92`；`src/hooks/useWorker.ts:23`
- Worker：`src/workers/split.worker.js:20`、`:75`、`:228`、`:259`
- 内容感知：`src/utils/splitAnalyzer.ts:50`、`:88`、`:250`
- 导出：`src/utils/pdfExporter.ts:37`、`:51`、`:208`；`src/utils/zipExporter.ts:34`、`:44`；UI `ExportControls`/`FileUploader`
- 类型契约：`src/types/index.ts:3` 起 ImageSlice/AppState/WorkerMessage
- 次要：`config/index.ts:77`、`shared-components/index.ts:40`、`tools/build-scripts/*`、`scripts/generate-seo-files.js`
- 文档：目标仓 README、docs/ARCHITECTURE.md、CLAUDE.md

## 模块分级

- **core · src**：业务主路径与绝大部分运行时逻辑（LOC/单元最大）
- **secondary · config**：应用/构建/环境配置聚合
- **secondary · shared-components**：可复用 UI/版权/通信管理，不拥有会话
- **secondary · tools / scripts**：工具链与工程脚本
- **excluded · test-setup / `.`**：测试夹具与根杂项，不进产品主数据流

分级已同步写入 `coverage-units.json#modules`（source 字段可审计）。

## 分工（parallelism: active）

本轮在支持并发工具调用的 Codex 会话中**真实并行**启动 3 个分析 worker（子代理角色），各自独立读写产物，再由主 agent 融合。

| 子代理 ID | 职责 / scope | 产物路径 |
|---|---|---|
| `subagent-src-state` | 会话状态 + Worker 内容感知切图主链（useAppState / useImageProcessor / useWorker / split.worker / splitAnalyzer / App 编排） | `subagent-artifacts/subagent-src-state.json`；贡献 `module-evidence/src.json` |
| `subagent-src-export` | 上传 UI + PDF/ZIP 导出边界（FileUploader / ExportControls / pdfExporter / zipExporter / 预览选择） | `subagent-artifacts/subagent-src-export.json` |
| `subagent-secondary` | config / shared-components / tools / scripts 次要模块抽样（≥30%） | `subagent-artifacts/subagent-secondary.json` |

### 实际子代理分工

- 子代理分工：subagent-src-state 负责 src 会话状态与 Worker 切图主链。
- 子代理分工：subagent-src-export 负责上传 UI 与 PDF/ZIP 导出边界。
- 子代理分工：subagent-secondary 负责 config/shared-components/tools/scripts 次要模块抽样。

### 每个子代理产物

- 子代理产物：subagent-src-state 写入 subagent-artifacts/subagent-src-state.json 与贡献 module-evidence/src.json。
- 子代理产物：subagent-src-export 写入 subagent-artifacts/subagent-src-export.json。
- 子代理产物：subagent-secondary 写入 subagent-artifacts/subagent-secondary.json。

### 主 agent 融合过程

主 agent 融合过程：

1. 校验三份 subagent JSON 的 unit_id / anchor / judgment 非空  
2. 合并写入 `coverage-units.json` 回填（core≥60% / secondary≥30%，未分析 core 填 skip_reason）  
3. 合成 `module-evidence/src.json`（吸收 state+export 发现；secondary 进入跨模块依赖与次要叙事）  
4. 主 agent 对高影响单元做 Semantic Source Review（standard：每 core ≥1，本轮 5 条）  
5. 写 `report.md` 叙事线：问题 → 全景 → 主链（state）→ 导出（export）→ 次要模块 → 风险/建议  
6. 跑 `gate --mode standard`  
7. 记录预算与并行摘要  

- parallelism: active

## 预算

- mode: standard
- time: 90 分钟
- token: 90000
- subagent 上限: 6（**本轮实际并行 3**）
- 单 agent 证据预算: 主链深读 + 次要抽样，不为凑行数读低价值文件
- 覆盖目标: core 60% / secondary 30%
- Semantic Source Review: 每 core ≥1（实际 5 条高影响）
- 报告长度: 中等，含全景/流程/协作/权衡/风险/改进/Mermaid
- tooling: 仅 baseline（git / 文件发现 / rg）；**禁止** Graphify / Universal Ctags / ast-grep

## 风险抽样

- 异步切片乱序（useAppState ADD_IMAGE_SLICE）
- Object URL / Worker 生命周期（CLEANUP_SESSION）
- 全图 getImageData 内存峰值（split.worker）
- 导出空选择 / 单片失败 continue（pdfExporter）
- 引用完整性：standard 启发式 partial/missing → 开放问题

## 报告结构

场景问题 → 项目全景 → 设计哲学 → 核心流程 Mermaid → 模块协作 → src 深度（状态/Worker/内容感知/导出）→ 次要模块 → 风险与开放问题 → 批判性评价与改进 → 业界对比 → 预算与并行执行摘要
