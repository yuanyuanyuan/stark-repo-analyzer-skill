# 06 导出系统模块

## Evidence Matrix

| 字段 | 内容 |
|------|------|
| Module Role | 结果交付层：把 `imageSlices + selectedSlices` 变成可下载 PDF/ZIP。回应 Evidence Plan：如何保持页序；为何暂不抽象统一导出引擎。 |
| Entry Points | 导出页渲染 `ExportControls`；`ExportControls.handleExport` → `App.handleExport` → `exportToPDF`/`exportToZIP`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:450-454`，`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82-91`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:224-250`）。 |
| Core Data Structures | 共享 `ImageSlice`；`selectedSlices: Set<number>`；导出器输入 imageSlices + selectedIndices（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3-20`，`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59-61`）。注意 ExportControls 本地重复声明同形接口（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10-15`）。 |
| Main Flow | 选择切片 → ExportControls 校验 → onExport(format, options) → App 再校验 → filter selectedIndices + sort by slice.index → jsPDF/JSZip 生成下载（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82-91`，`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59-65`，`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51-56`）。 |
| Cross-Module Dependencies | 依赖状态层 imageSlices/selectedSlices；依赖路由导出页前置条件；UI 使用 i18n 文案；不直接依赖切割算法（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237-250`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:375-430`，`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:52`）。 |
| Key Design Decisions | 1) PDF/ZIP 分导出器而非统一 ExportEngine：语义不同（页面尺寸 vs 压缩命名）（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:68-132`，`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:59-96`）。2) 两端共享 filter+sort 规则保证页序。3) 页面/组件/导出器三层空选防御（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:405`，`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:83`，`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:63`）。 |
| Risk Areas | 导出选项链路断裂：UI 有 quality/pdf/zip 配置，App 只读 filename（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:66-89`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:233-249`）。`isExporting` 双重状态（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:40`，`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:56`）。类型重复。 |
| Source Evidence | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:224-250`，`:450-454`；`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10-15`，`:66-91`；`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59-65`；`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51-56`。 |
| Open Questions | 1) `ScreenshotSplitter.tsx` 中导出只打日志，是遗留还是未完成入口？（`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:107-112`，`:240-243`）。2) `options.slices` 是否还有计划用途？主链路未使用（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:91`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237-250`）。 |

## 叙事分析

导出系统保持“轻量 UI + 格式专用导出器”。最关键的契约不是格式库，而是 `slice.index`：过滤选中并按 index 排序，使页序独立于点击顺序与异步到达顺序。

### 1. 为何不急于统一引擎

PDF 需要页面几何与 addImage；ZIP 需要命名、压缩与 Blob 下载。当前阶段抽出 `normalizeSelectedSlices` 比抽象 ExportEngine 更划算。

### 2. 真实问题

比“没有统一引擎”更实际的问题是：高级导出选项 UI 与导出器参数未闭合；`isExporting` 父子双状态。

### 3. 铺垫

核心主线之外的 i18n/SEO/shared-components 应使用简化 Evidence Matrix 单独评估，避免稀释交付层叙事。
