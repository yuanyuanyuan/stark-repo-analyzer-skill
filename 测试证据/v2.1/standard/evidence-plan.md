# Evidence Plan · v2.1 · standard

## 架构问题

- 长截图切割工具如何把「上传 → 切割 → 预览选择 → 导出」串成主流程？状态放在哪里，谁驱动副作用？
- `src` 为何同时承担 UI 编排、会话状态、Worker 切图与导出，而 `shared-components` / `config` / `tools` 只做支撑？
- 在 parse_rate ≈ 48% 的前提下，哪些区域必须标 Unsupported Area，哪些结论仍可从可解析 hooks/utils 成立？

## 候选证据

- Repo Map: `repo-map.json` / `repo-map.md`
- 关键单元: `coverage-units.json`（src 190 单元为核心分母）
- 入口与编排: `src/main.tsx:5`、`src/App.tsx`（createRoot + AppContent 组装 hooks/组件）
- 会话状态: `src/hooks/useAppState.ts:14-122`（reducer + 持久化 splitHeight/fileName）
- 切图管线: `src/hooks/useImageProcessor.ts:19+`、`src/hooks/useWorker.ts`（Worker 回调 → blob/objectURL → imageSlices）
- 导出: `src/utils/pdfExporter.ts:37+`、`src/utils/zipExporter.ts:34+`；UI `ExportControls.tsx`
- 上传: `src/components/FileUploader.tsx`；可选移动端整合 `ScreenshotSplitter.tsx`
- i18n: `src/hooks/useI18n.ts:52`（localStorage + 动态 import locales）
- 配置/SEO: `src/config/seo/configLoader.ts:25`（次要于主切割链路）
- 文档: 目标仓 `README.md`、`docs/ARCHITECTURE.md`（若可解析路径）

## 模块分级

- **core · src**: 业务主路径与绝大部分运行时逻辑（LOC 最大，承载上传/切割/状态/导出）
- **secondary · config**: 应用/构建/SEO 配置，服务主应用但不实现切割算法
- **secondary · shared-components**: 可复用 UI/版权等，不拥有会话状态
- **secondary · tools / scripts**: 工具链与脚本，非运行时主路径
- **excluded · test-setup / `.` 零业务分母**: 测试与根杂项；排除理由：不进入产品主数据流（若 coverage 中无单元则仅声明）

## 分工

- **parallelism: degraded**
- **原因**: 本会话 Codex 运行时未对模块分析派发多个可并发 subagent worker；由**主 agent 串行**完成 Evidence Plan、src 模块 Matrix、次要模块抽样、report 草稿与 gate。
- **串行顺序**:
  1. 主 agent：Repo Map + 文档研读 + 写本 Plan
  2. 主 agent：src 核心模块深度分析 → `module-evidence/src.json` + coverage 回填
  3. 主 agent：config / shared-components / tools 次要抽样回填
  4. 主 agent：风险抽样 + Semantic Source Review（standard：每 core ≥1）
  5. 主 agent：写 `report.md` → 跑 `repo-analyzer gate --mode standard`
- **子代理产物**: 无独立 subagent 产物目录；全部由主 agent 写入上述路径。
- **融合过程**: 不适用多路 merge；叙事以 Plan 数据流顺序组织，单一作者合成 `report.md`。
- **验收含义**: 本轮可证明 CLI 工件链与串行分析过程；**不得**按 v2.0 multi-agent 完整通过计（见 `docs/specs/v2.0-multi-agent-acceptance.md`）。

## 预算

- mode: standard
- time: 90 分钟级（本轮压缩执行）
- token: 按会话预算
- subagent 上限: 6（**实际使用 0**，degraded）
- 单 agent 证据预算: 优先 hooks/utils/导出路径，components 大量 unparsed 记 Unsupported
- 报告长度: 中等，必须含项目全景、模块协作、改进建议、Mermaid

## 风险抽样计划

- 异步切片乱序：`ADD_IMAGE_SLICE` 按 index 写入（useAppState）
- Object URL / Worker 生命周期：`CLEANUP_SESSION` / processImage 开头 cleanup
- 导出空选择：PDF/ZIP exporter 对空 selected 抛错
- 解析盲区：大量 `src/components/*.tsx` unparsed → Unsupported Area

## 报告结构

1. 使用场景与问题
2. 项目全景与技术栈
3. 核心设计哲学（状态 + Worker 切图 + 导出旁路）
4. 模块协作（数据流 Mermaid）
5. 核心模块 src 深度
6. 次要模块角色
7. 风险、限制、Unsupported Area
8. 批判性评价与具体改进建议
9. 预算与并行执行摘要
