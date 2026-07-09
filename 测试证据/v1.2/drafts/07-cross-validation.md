# 阶段 7：交叉验证与质量管控

## 1. Evidence Plan 回应核查

| 模块 | 草稿 | Evidence Plan 回应情况 |
|------|------|------------------------|
| 路由与导航守卫 | `06-module-routing.md` | 已覆盖 hash 路由、App switch、硬守卫/软守卫、恢复策略、配置层未接入运行时 |
| 切割流水线 | `06-module-split-pipeline.md` | 已覆盖 Worker 创建、消息契约、OffscreenCanvas、splitAnalyzer、回退策略、进度/chunk/done |
| 状态管理与资源生命周期 | `06-module-state-management.md` | 已覆盖 AppState/AppAction、CLEANUP_SESSION、按 index 写入、Object URL、Worker 所有权、稀疏数组风险 |
| 导出系统与次要模块边界 | `06-module-export-secondary.md` | 已覆盖 PDF/ZIP 过滤排序、三层空选防御、导出选项断裂、i18n/SEO/shared/config 抽样 |

结论：四个核心模块均回应了 `05-modules-plan.md` 中的架构问题，没有核心模块遗漏。

## 2. 锚点抽查

| 抽查结论 | 锚点 | 抽查结果 |
|----------|------|----------|
| 上传后等待首个切片到达再跳 `/split` | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135` | 源码注释和逻辑一致，确实用 `prevSliceCountRef` 检测 0→>0 |
| 内容感知分析失败回退等分 | `/tmp/Long_screenshot_splitting_tool/src/workers/split.worker.js:125-129`、`:228-249` | catch 中设置 `splitPoints=[]`，`computeSliceBounds` 对空点走固定高度等分 |
| splitAnalyzer 是纯函数算法层 | `/tmp/Long_screenshot_splitting_tool/src/utils/splitAnalyzer.ts:6-13`、`:250-270` | 文件头声明无 DOM/canvas/Worker 依赖，入口只接收像素数组与尺寸 |
| 切片按 index 写入而非 push | `/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-55` | 源码使用 `newImageSlices[action.payload.index] = action.payload` |
| PDF/ZIP 均按 index 过滤排序 | `/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59-61`、`/tmp/Long_screenshot_splitting_tool/src/utils/zipExporter.ts:51-53` | 两个导出器均先 filter selected，再 sort index |
| 路由配置层未主导运行时分发 | `/tmp/Long_screenshot_splitting_tool/src/router/index.ts:66-178`、`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430` | 配置层有 route 工具，但 App 以 `switch(currentPath)` 分发 |

## 3. 跨模块结论验证

### 3.1 状态驱动导航，而不是事件驱动导航

路由草稿认为 App 等业务状态成形后再导航。状态草稿与切割草稿共同支持该结论：切割流水线产出 chunk 后，主线程生成 `ImageSlice` 并派发 `ADD_IMAGE_SLICE`；App 监听 `imageSlices.length` 从 0 变为大于 0 再跳转。该结论可写为确定性结论。

### 3.2 `slice.index` 是跨模块顺序契约

Worker chunk 带 `index`，状态层按 `index` 回填，导出层按 `slice.index` 过滤排序。这个契约贯穿切割、状态、导出三层，是保证异步切片不会打乱预览/导出顺序的核心设计。但状态层按 index 写入数组也引入 sparse array 风险，最终报告需要同时写亮点和代价。

### 3.3 Worker 所有权存在边界不清

状态草稿指出 `AppState.worker` 与 `useWorker.workerRef` 可能重复；切割草稿显示 `useImageProcessor` 创建 Worker 后并未把 `workerRef.current` 写回 `AppState.worker`。因此最终报告可确定写出：当前实际 Worker 生命周期主要由 `useWorker` 管理，而 `AppState.worker/SET_WORKER` 更像遗留或未接上的设计。

### 3.4 外围模块过度工程是真问题，但不是核心流程错误

导出草稿与 v1.1 报告一致：SEO、EnhancedSEO、shared-components 的复杂度明显高于当前工具核心主线需求。最终报告应把它描述为演进风险，而非阻断核心功能的问题。

## 4. 质量结论

- 核心结论均有源码锚点。
- 不确定内容已标为假设、开放问题或风险推断。
- 报告可复查性优于 v1.0/v1.1：v1.2 保留了阶段计划、模块草稿、交叉验证与最终报告。
