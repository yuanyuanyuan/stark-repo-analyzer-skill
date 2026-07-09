# 导出系统与次要模块边界

> 本草稿按 `module-analysis-guide.md` 的模块分析要求编写：按业务能力划分模块，而不是按目录列文件；确定性判断均附源码锚点。没有直接源码支撑的内容标为“基于证据的推断”或“开放问题”。

## 1. 模块角色

导出系统是长截图分割工具的“结果交付层”：前面的上传、切片、选择流程最终都要把 `imageSlices + selectedSlices` 转成用户可下载的 PDF 或 ZIP。去掉该模块，系统仍能完成切片预览，但无法把处理结果沉淀为文件交付；这一点体现在 `App` 的导出页会把 `state.imageSlices`、`state.selectedSlices` 和 `handleExport` 传给 `ExportControls`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:450`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:451`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:452`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:453`）。

在整体设计中，导出系统不是独立引擎，而是一个“轻量 UI 控制 + 格式专用导出器”的组合：`App` 决定导出格式和全局状态，`ExportControls` 提供用户操作入口，`pdfExporter` / `zipExporter` 负责具体文件生成（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:224`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:51`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:44`）。

## 2. 核心数据结构

导出主数据结构是 `ImageSlice`：它包含 `blob`、预览 `url`、稳定排序用的 `index`、以及 PDF 缩放所需的 `width` / `height`（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:4`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:5`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:6`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:7`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:8`）。

`AppState` 把切片数组和选中集合放在同一个应用状态里：`imageSlices` 是有序候选集，`selectedSlices: Set<number>` 是用户选择集（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:17`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:19`、`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:20`）。这解释了导出器为什么接收 `imageSlices + selectedIndices`，而不是接收 UI 已经裁剪后的数组：导出器可以重新按 `slice.index` 做最后一次确定性过滤与排序（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:60`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:61`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:52`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:53`）。

风险：`ExportControls` 又在组件内部重复声明了一个同形的 `ImageSlice` 接口（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:11`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:12`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:13`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:14`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:15`）。这会让类型演进出现两处修改点；例如未来给切片增加 `sourceFileName` 或 `rotation` 时，导出器使用的共享类型和 UI 本地类型可能漂移。

## 3. 核心流程

```mermaid
flowchart TD
  A[用户在 ImagePreview 选择切片] --> B[App 将 Set 转成数组传入 ExportControls]
  B --> C[ExportControls 判断 disabled / 空选择 / 本地 isExporting]
  C --> D[ExportControls 调用 onExport(format, options)]
  D --> E[App.handleExport 再次校验 selectedSlices.size]
  E --> F{format}
  F -->|pdf| G[exportToPDF]
  F -->|zip| H[exportToZIP]
  G --> I[filter selectedIndices + sort by slice.index]
  H --> I
  I --> J{是否为空}
  J -->|空| K[抛出没有选中的图片切片]
  J -->|非空| L[格式专用生成]
  L -->|PDF| M[jsPDF addImage + save]
  L -->|ZIP| N[JSZip file + generateAsync + a.download]
```

流程锚点如下：

- `App` 从全局状态中取选中切片并传给 `ExportControls`，包括导出页和首页内联导出区两处入口（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:450`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:451`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:452`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:453`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:520`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:521`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:522`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:523`）。
- `ExportControls` 在用户点击导出时先挡住 `disabled` 和空选，再把格式、配置、选中索引和映射后的切片传给 `onExport`（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:83`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:88`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:89`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:90`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:91`）。
- `App.handleExport` 再用全局 `state.selectedSlices.size` 做空选校验，并根据 `format` 分支调用 PDF 或 ZIP 导出器（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:224`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:225`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:226`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:235`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:246`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:248`）。
- PDF 和 ZIP 导出器都在内部按 `selectedIndices.has(slice.index)` 过滤，再按 `a.index - b.index` 排序，保证文件页序不依赖 UI 数组顺序或用户点击顺序（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:60`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:61`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:52`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:53`）。

## 4. 关键设计决策

### 决策 1：用 `slice.index` 作为导出顺序真相

导出页序的可预测性不是靠 React 渲染顺序，而是靠导出器最终按 `slice.index` 排序。PDF 与 ZIP 都执行同样的过滤和排序逻辑（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:60`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:61`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:52`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:53`）。这对长截图切片很关键：用户关心的是从上到下的原始切片顺序，而不是点击选择顺序。

基于证据的推断：`Set<number>` 适合表示“是否选中”，但不适合表达业务顺序；因此导出器把 `Set` 当过滤条件，把 `ImageSlice.index` 当排序键，是更稳妥的分工（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:20`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:60`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:52`）。

### 决策 2：PDF / ZIP 分成两个简单导出器，而不是统一导出引擎

PDF 与 ZIP 的业务语义不同。PDF 导出器依赖 `jsPDF`，创建页面、计算毫米单位页面尺寸、把 Blob 转 base64 后 `addImage` 并 `save`（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:1`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:68`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:75`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:76`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:98`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:101`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:115`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:131`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:132`）。ZIP 导出器依赖 `JSZip`，生成每个图片文件名、可选转换图片格式、`zip.file` 后 `generateAsync`，最后用临时 `<a>` 下载 Blob（`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:1`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:65`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:66`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:67`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:83`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:95`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:96`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:188`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:196`）。

基于证据的推断：当前拆成两个导出器，比抽象一个统一 `ExportEngine` 更贴近格式差异。统一引擎能复用过滤排序和进度协议，但会把 PDF 的页面布局、ZIP 的文件命名/压缩/格式转换强行塞进同一抽象，容易早期过度设计。当前真正需要抽出的只是“选择切片规范化”这一小函数，而不是完整导出引擎。

### 决策 3：三层空选防御偏保守，但有合理性

第一层是路由/页面层：导出页在没有原图或切片时展示上传引导，在没有选中切片时展示返回分割页的提示（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:375`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:377`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:405`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:424`）。第二层是组件层：`ExportControls` 的 `handleExport` 遇到 `disabled` 或空选择直接返回，按钮的 `canExport` 也绑定空选和本地导出状态（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:83`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:129`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:337`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:338`）。第三层是导出器层：PDF 和 ZIP 在过滤后再次检查 `selectedSlices.length === 0` 并抛错（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:63`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:64`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:55`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:56`）。

评价：三层防御对用户体验和 API 健壮性都有意义。页面层提供可理解的恢复路径，组件层避免误点，导出器层保护未来绕过 UI 的调用。但 `App.handleExport` 还有一层 alert 式空选校验（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:224`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:225`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:226`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:227`），在当前页面已经阻止空选渲染 `ExportControls` 的情况下略显重复；如果保留，应把它定位为“命令层防御”，而不是主要 UX。

## 5. 模块间依赖与协同

导出系统的依赖方向整体清晰：`App` 依赖应用状态和两个导出函数，`ExportControls` 依赖 `onExport` 回调而不直接依赖 `jsPDF` / `JSZip`，格式库只出现在格式专用导出器内（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:13`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:14`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:21`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:1`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:1`）。这个边界的好处是 UI 可以新增移动端触控、选项面板和国际化文案，而不污染实际生成文件的逻辑（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:52`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:53`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:60`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:61`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:62`）。

协同上的主要裂缝是配置契约没有闭合。`ExportControls` 维护了质量、PDF 页面配置、ZIP 压缩和图片格式选项（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:66`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:68`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:70`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:75`），并把这些选项传给 `onExport`（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:88`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:89`）。但 `App.handleExport` 只读取 `options?.filename`，没有把 `quality`、`pdfOptions` 或 `zipOptions` 转给导出器（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:233`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:235`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:248`）。这意味着 UI 上看似可配置的选项对实际导出可能不生效，是比“没有统一引擎”更实际的架构问题。

## 6. 次要模块边界抽样

### 6.1 i18n

职责：i18n 提供语言检测、资源动态导入、缓存、插值和语言切换能力（`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:5`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:9`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:67`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:74`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:96`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:103`）。

在整体中的角色：它是横切 UI 文案层，`App` 和 `ExportControls` 都通过 `t(...)` 使用文案，而不是在导出器内部处理语言（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:37`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:52`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:140`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:143`）。

特别之处：语言偏好同时兼容新持久化状态和旧 `app-language` key，并通过 `LanguageDetector.saveLanguagePreference` 保存偏好（`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:31`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:32`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:40`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:41`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:54`、`/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:58`）。这属于合理的兼容性复杂度，不直接稀释导出主线。

### 6.2 SEO / Enhanced SEO

职责：当前 `App` 实际挂载的是 `SEOManager`，它根据路由页类型和上下文注入 metadata、结构化数据、Open Graph、Twitter Card、canonical、性能资源提示等（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:24`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:539`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:540`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:542`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:548`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:549`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:550`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:551`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:552`）。

过度工程风险：`SEOManager.tsx` 单文件内已有性能观察器、视窗检测、动态元数据、配置管理器回退、结构化数据和预加载逻辑（`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:20`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:82`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:131`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:142`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:182`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:453`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:582`、`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:620`）。同时项目还存在另一套 `EnhancedSEOManager`，动态导入 `web-vitals`、lazy load 结构化数据、再导出 memo 化的 `SEOManager`（`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:18`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:19`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:28`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:49`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:144`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:326`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:341`）。

评价：对一个客户端长截图分割工具来说，SEO 是获客必要能力，但两套增强 SEO 管理器并存会稀释核心主线。这个复杂度不参与导出、切片或选择，却引入性能监控、配置管理、结构化数据、资源预加载等多个决策面；建议收敛为一套 SEO 边界，并把性能监控从 SEO 组件中拆出去。

### 6.3 shared-components

职责：`shared-components` 对外导出组件通信接口、通信管理器、共享状态管理器、`CopyrightInfo` 和 `Button`（`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:6`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:7`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:9`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:16`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:17`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:19`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:20`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:21`）。

在当前应用中的实际角色更窄：`App` 只从包入口引入 `CopyrightInfo` 并渲染到 header 右上角（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:21`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:561`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:567`）。但共享组件接口文件定义了组件注册、消息、事件、生命周期、共享状态等一整套微前端式协议（`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:6`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:25`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:52`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:61`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:123`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:167`）。

评价：这是次要模块过度工程的典型信号。当前证据显示核心业务只需要版权展示，`CopyrightInfo` 自身还带独立 i18n、移动端检测和调试日志（`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:6`、`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:12`、`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:91`、`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:103`、`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:189`、`/tmp/Long_screenshot_splitting_tool/shared-components/components/CopyrightInfo/CopyrightInfo.tsx:190`）。如果项目目标是单页工具，组件通信管理器和共享状态管理器应降级为未来扩展，而不是架构主线。

### 6.4 配置 / 部署

职责：`config/index.ts` 是统一配置门面，重新导出 app、routing、deployment、environment 和 constants，并汇总成 `config` 与 `configUtils`（`/tmp/Long_screenshot_splitting_tool/config/index.ts:6`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:7`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:15`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:22`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:29`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:77`、`/tmp/Long_screenshot_splitting_tool/config/index.ts:102`）。

部署配置聚焦在环境变量驱动的 basePath、assets URL、GitHub Pages、CDN 和动态导入 URL 生成（`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:6`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:43`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:46`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:57`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:60`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:144`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:185`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:200`、`/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:216`）。

评价：配置/部署复杂度与“扁平化单仓库架构”的包定位有关，`package.json` 描述项目为扁平化单仓库架构，并把 `shared-components` 放入发布文件范围（`/tmp/Long_screenshot_splitting_tool/package.json:6`、`/tmp/Long_screenshot_splitting_tool/package.json:10`、`/tmp/Long_screenshot_splitting_tool/package.json:11`、`/tmp/Long_screenshot_splitting_tool/package.json:12`）。这类配置对部署适配有实际价值，但不应进入导出系统主叙事；报告中宜作为“边缘支撑层”处理。

## 7. 问题与风险

1. 导出逻辑重复：PDF 和 ZIP 都重复了 `filter selectedIndices + sort by index + empty check`，这是稳定页序的关键规则，却散落在两个导出器中（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:60`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:61`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:63`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:52`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:53`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:55`）。
2. `ImageSlice` 接口重复：共享类型定义在 `src/types/index.ts`，但 `ExportControls` 本地重新声明同形接口（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10`）。
3. `isExporting` 双重状态：`App` 维护全局导出状态并传入 `disabled`，`ExportControls` 又维护本地 `isExporting` 并参与 `canExport`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:40`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:230`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:231`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:261`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:262`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:454`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:56`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:86`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:96`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:129`）。如果父子状态更新不同步，按钮禁用和实际命令执行可能出现短暂不一致。
4. 导出选项链路断裂：`ExportControls` 提供质量、PDF、ZIP 配置，但 `App.handleExport` 只使用文件名，格式导出器也通过默认工厂创建（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:66`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:70`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:75`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:88`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:233`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:214`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:223`）。
5. 次要模块稀释核心主线：SEO 管理存在两套增强实现，shared-components 暴露通用通信/共享状态协议，但当前核心业务主要使用版权组件和 SEO 注入（`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:364`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:144`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:341`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:123`、`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:167`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:21`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:539`）。

## 8. 改进建议

1. 抽出 `normalizeSelectedSlices(imageSlices, selectedIndices)`：只复用过滤、排序、空选错误这条核心规则，不急于抽象完整 `ExportEngine`。这样能减少重复，又保留 PDF / ZIP 各自的生成语义（证据问题对应重复点：`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51`）。
2. 让 `ExportControls` 直接导入共享 `ImageSlice` 类型，删除本地接口，避免类型漂移（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10`）。
3. 明确导出状态唯一来源：如果 `App` 负责真实导出命令，就让 `App.isExporting` 成为单一事实源；`ExportControls` 只展示 `disabled`，或通过 `onExport` 返回状态事件（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:40`、`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:56`）。
4. 打通选项契约：把 `ExportControls` 的 `quality`、`pdfOptions`、`zipOptions` 映射为 `PDFExportOptions` / `ZIPExportOptions` 后传入 `createPDFExporter` / `createZIPExporter`，否则应隐藏高级选项，避免虚假配置（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:66`、`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:7`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:7`）。
5. 收敛次要模块：SEO 保留一套实现；shared-components 若当前只服务版权展示，应把组件通信和共享状态协议标注为未来扩展或拆出，不要让它们成为理解主流程的前置概念（`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:364`、`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:144`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:10`、`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:14`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:567`）。

## 9. 开放问题

- `ScreenshotSplitter.tsx` 也渲染 `ExportControls`，但它的 `handleExport` 只记录日志并提示“导出逻辑将在 ExportControls 组件中处理”（`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:107`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:108`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:109`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:110`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:112`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:240`、`/tmp/Long_screenshot_splitting_tool/src/components/ScreenshotSplitter.tsx:243`）。开放问题：这是遗留组件、备用页面，还是未完成的导出入口？当前草稿不把它视为主导出链路。
- `ExportControls` 把 `selectedSlices.map(index => slices[index])` 传给 `onExport`（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:91`），但主链路 `App.handleExport` 实际使用全局 `state.imageSlices` 和 `state.selectedSlices`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:238`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:239`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:248`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:249`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:250`）。开放问题：组件传出的 `options.slices` 是否还有计划用途？如果没有，应删除以减少误导。

## 10. 源码锚点清单

| 结论 | 锚点 |
|---|---|
| 导出系统是结果交付层，入口在 App + ExportControls | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:450`, `/tmp/Long_screenshot_splitting_tool/src/App.tsx:520`, `/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:82` |
| 页序可预测依赖 `slice.index` 过滤后排序 | `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`, `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51` |
| PDF 生成路径是 jsPDF 文档、addImage、save | `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:68`, `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:115`, `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:132` |
| ZIP 生成路径是 JSZip、zip.file、generateAsync、Blob 下载 | `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:59`, `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:67`, `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:83`, `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:188` |
| 三层空选防御存在 | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:405`, `/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:83`, `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:63`, `/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:55` |
| `ImageSlice` 类型重复 | `/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3`, `/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:10` |
| `isExporting` 双重状态 | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:40`, `/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:56` |
| i18n 是横切 UI 文案层 | `/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:103`, `/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:52` |
| SEO 模块复杂度高且存在增强实现并存 | `/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:364`, `/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:144`, `/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:341` |
| shared-components 实际使用窄，但接口面宽 | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:21`, `/tmp/Long_screenshot_splitting_tool/src/App.tsx:567`, `/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:123`, `/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:167` |
| 配置/部署是边缘支撑层 | `/tmp/Long_screenshot_splitting_tool/config/index.ts:77`, `/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:144`, `/tmp/Long_screenshot_splitting_tool/config/build/deployment.config.ts:185` |
