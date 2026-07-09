# Long_screenshot_splitting_tool 架构分析报告 v1.3

> 仓库：`yuanyuanyuan/Long_screenshot_splitting_tool`
> 本地源码：`/tmp/Long_screenshot_splitting_tool`
> 分析模式：标准分析（Evidence Plan + Markdown Evidence Matrix）
> 日期：2026-07-09
> 技能：`skills/repo-analyzer/SKILL.md`（含 v1.3 Evidence Matrix）

## 1. 项目全景

这个项目不是截图捕获器，而是一个**纯前端长截图分割与交付工具**：用户上传已有长图，浏览器内完成解码、内容感知切割、预览选择，并导出 PDF 或 ZIP。核心技术栈是 React 19、TypeScript、Vite、Web Worker、OffscreenCanvas、jsPDF 和 JSZip。

```mermaid
flowchart LR
  A[上传图片 File] --> B[useImageProcessor 协调]
  B --> C[useWorker 传输]
  C --> D[split.worker 图像 I/O]
  D --> E[splitAnalyzer 内容感知切点]
  E --> F[AppState 收集切片]
  F --> G[ImagePreview 选择]
  G --> H[PDF / ZIP 导出]
```

项目哲学：**纯前端、低依赖、自造关键胶水、用状态守卫保护任务流程**。

## 2. 业务问题：为什么它不只是“按高度裁图”

长截图的真实痛点是交付：聊天窗口、文档归档、打印与二次编辑都不适合直接处理超长图。系统把问题拆成上传 → 切割 → 选择 → 导出，并用页面守卫保证用户处在正确阶段。

## 3. 路由与导航守卫：状态驱动，而不是事件乐观

为什么不用 React Router？当前运行时用极小 hash Hook 读 `window.location.hash` 并监听 `hashchange`（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:15-34`）。这适配 GitHub Pages 静态托管，也降低依赖。仓库里有更完整路由配置工具，但 App 实际以 `switch(currentPath)` 分发（`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:66-178`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430`）——配置层与运行时分叉是维护风险。

更关键的设计是**状态驱动导航**：上传后不立即跳 `/split`，而是等 `imageSlices` 从 0 变为 >0（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`）。硬守卫在渲染前校验路径前置条件并恢复，软守卫在页面分支给降级 UI（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`，`:305-430`）。

**开放问题（未验证）**：`src/router/index.ts` 的作者意图；`Navigation` 组件是否阻止 disabled 点击。

## 4. 切割流水线：算法与 I/O 分离 + 失败可回退

流水线分层清楚：

- 协调：`useImageProcessor`
- 传输：`useWorker`
- 图像 I/O：`split.worker`（createImageBitmap / OffscreenCanvas / getImageData）
- 算法：`splitAnalyzer` 纯函数，文件头明确无 DOM/canvas/Worker 依赖（`/tmp/Long_screenshot_splitting_tool/src/utils/splitAnalyzer.ts:6-13`）

最重要的权衡是**内容感知 + 安全回退**。Worker 分析异常时置空 `splitPoints`，随后走固定高度等分（`/tmp/Long_screenshot_splitting_tool/src/workers/split.worker.js:125-129`）。“智能”失败不会让任务失败。

风险（有锚点，未做压测复现）：

- `setTimeout(200)` 等待 Worker 就绪（`/tmp/Long_screenshot_splitting_tool/src/hooks/useImageProcessor.ts:124-125`）
- 全图 `getImageData` 内存峰值（`/tmp/Long_screenshot_splitting_tool/src/workers/split.worker.js:112-116`）
- 现代图像 API 缺少能力探测

**开放问题**：具体浏览器兼容矩阵；30MB 最坏分辨率是否崩溃。

## 5. 状态管理：异步流水线的承接层

`AppState` 把 Worker、Object URL、原图、切片、选择集与处理态收成一次会话（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:11-28`）。`useReducer` 足够：状态规模小但耦合强。

核心决策：`ADD_IMAGE_SLICE` **按 index 写入**，修复异步 onload 乱序（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-55`）。`CLEANUP_SESSION` 集中释放 objectUrls 并尝试 terminate worker（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:89-112`）。

代价：

- sparse array 风险：高 index 先到可能空洞；预览混用 array index 与 `slice.index`（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:72-73`，`/tmp/Long_screenshot_splitting_tool/src/components/ImagePreview.tsx:210-222`）
- Worker 所有权疑似脱节：实际更依赖 `useWorker` ref，`AppState.worker/SET_WORKER` 可能遗留（见交叉验证）

## 6. 导出系统：简单分导出器优于过早统一引擎

PDF/ZIP 都先 `filter(selectedIndices)` 再 `sort(index)`（`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59-61`，`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51-53`）。页序契约与状态层 index 写入贯通三层。

为什么不抽象 ExportEngine？PDF 与 ZIP 语义不同；现阶段更该复用 `normalizeSelectedSlices`。三层空选防御偏保守但安全（页面/组件/导出器）。

更实际的问题是选项链路断裂：ExportControls 有质量与格式配置，`App.handleExport` 主要只消费 filename（`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:66-89`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:233-249`）；另有 `isExporting` 双重状态与本地 `ImageSlice` 类型重复。

**开放问题**：`ScreenshotSplitter` 导出是否遗留；`options.slices` 是否仍有用途。

## 7. 次要模块边界

i18n 是合理横切层。SEO 必要但两套增强实现并存；shared-components 实际主要服务版权展示，却暴露宽通信/共享状态协议。这些是演进复杂度，不是核心链路故障。

## 8. 总体评价

### 亮点

- 核心流水线边界清晰：协调 / 传输 / I/O / 算法分离
- `splitAnalyzer` 纯函数化
- 内容感知失败可回退
- 状态驱动导航
- `slice.index` 跨模块顺序契约

### 问题

- Worker 就绪时序补偿脆弱
- 切片数组稀疏风险
- Worker 所有权边界不清
- 导出高级选项未闭合
- SEO/shared-components 过度工程

## 9. 如果重新设计

1. Worker ready/handshake 替换 `setTimeout(200)`
2. 切片用 Map 或 `{byIndex, orderedIndices}`，渲染/导出前 dense sort
3. 处理会话加 sessionId
4. 明确 Worker 唯一所有权
5. 抽出 `normalizeSelectedSlices` 并打通导出选项
6. 收敛 SEO / 标注 shared-components 扩展边界

## 10. 结论

v1.3 在 v1.2 的锚点与 Evidence Plan 之上，用 Markdown Evidence Matrix 把模块角色、入口、流程、依赖、风险与开放问题收成可比较索引，再合成叙事报告。结论不变：核心业务架构健康；主要风险在异步状态边界与外围复杂度。

一句话：**完成度较高的纯前端长截图处理工具；最值得学的是 Worker + 纯函数算法 + 状态守卫，最需要收敛的是外围过度工程与异步状态边界。**
