# 阶段 5：模块计划、叙事线与 Evidence Plan

## 报告叙事线

长截图交付问题
→ 浏览器内工具的全景架构
→ 路由与导航守卫确保用户在正确阶段
→ 切割流水线把文件转成有序切片
→ 状态管理承接异步切片并管理资源生命周期
→ 导出系统把选择结果变成 PDF/ZIP
→ 次要模块与过度工程边界
→ 架构评价与 v1.0/v1.1/v1.2 对比

## 核心模块

1. 路由与导航守卫
2. 切割流水线
3. 状态管理与资源生命周期
4. 导出系统与次要模块边界

## Evidence Plan：路由与导航守卫

- 架构问题：为什么项目选择自定义 hash 路由而不是 React Router？页面守卫如何避免处理未完成时白屏或错页？
- 候选文件：`src/hooks/useRouter.ts`、`src/router/index.ts`、`src/utils/navigationErrorHandler.ts`、`src/App.tsx`
- 必需证据：hashchange 监听、push/replace、路由配置、App switch、状态验证与恢复策略
- 风险路径：配置层是否真实参与运行时；App 守卫和 navigationErrorHandler 是否重复
- 预期输出：说明轻路由服务单页工具，而不是抽象应用框架

## Evidence Plan：切割流水线

- 架构问题：如何把文件输入、Worker 传输、图像 I/O、内容感知算法分层？为什么 splitAnalyzer 是纯函数？
- 候选文件：`src/hooks/useImageProcessor.ts`、`src/hooks/useWorker.ts`、`src/workers/split.worker.js`、`src/utils/splitAnalyzer.ts`
- 必需证据：Worker 创建、消息契约、OffscreenCanvas/createImageBitmap、analyzeSplitPoints、computeSliceBounds、progress/chunk/done
- 风险路径：`setTimeout(200)` 时序补偿、全图 `getImageData` 内存压力、OffscreenCanvas 兼容性
- 预期输出：说明核心亮点是算法与 I/O 分离、内容感知与等分回退双轨

## Evidence Plan：状态管理与资源生命周期

- 架构问题：为什么 `useReducer` 足够？状态层如何承接切割、预览、导出？资源释放是否集中？
- 候选文件：`src/hooks/useAppState.ts`、`src/types/index.ts`、`src/hooks/useImageProcessor.ts`、`src/App.tsx`
- 必需证据：`AppState`、`AppAction`、`ADD_IMAGE_SLICE`、`SELECT_ALL_SLICES`、`CLEANUP_SESSION`、调用点
- 风险路径：稀疏数组、Object URL 生命周期、Worker terminate 竞态
- 预期输出：说明状态层是异步流水线与 UI/导出之间的领域边界

## Evidence Plan：导出系统与次要模块边界

- 架构问题：导出系统如何保持页序？为什么暂时不抽象统一导出引擎？次要模块是否过度工程？
- 候选文件：`src/utils/pdfExporter.ts`、`src/utils/zipExporter.ts`、`src/components/ExportControls.tsx`、`src/App.tsx`、`src/hooks/useI18n.ts`、`src/components/SEOManager.tsx`、`shared-components/interfaces/ComponentInterface.ts`
- 必需证据：selectedIndices 过滤排序、PDF/ZIP 生成、三层空选防御、次要模块复杂度锚点
- 风险路径：导出重复、接口重复、isExporting 双重状态、SEO/shared-components 稀释核心主线
- 预期输出：说明导出层保持简单是合理取舍，外围模块是主要复杂度风险
