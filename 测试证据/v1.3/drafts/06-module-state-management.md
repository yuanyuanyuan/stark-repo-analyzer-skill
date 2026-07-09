# 06 状态管理与资源生命周期模块

## Evidence Matrix

| 字段 | 内容 |
|------|------|
| Module Role | 以小型会话状态机承接切割、预览、导出之间的共享事实，并集中管理 Object URL / 会话清理；是异步流水线与 UI 的领域边界。回应 Evidence Plan：`useReducer` 是否足够；如何承接切割/预览/导出；资源释放是否集中。 |
| Entry Points | `useAppState` 暴露 state + action creators；`useImageProcessor` 注入 cleanup/setProcessing/addImageSlice 等；App 读取 state 做导航守卫、预览、导出（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:151-215`，`/tmp/Long_screenshot_splitting_tool/src/hooks/useImageProcessor.ts:5-15`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:29`）。 |
| Core Data Structures | `AppState`（worker/blobs/objectUrls/originalImage/imageSlices/selectedSlices/processing/...）；`AppAction` 联合；`ImageSlice`（`/tmp/Long_screenshot_splitting_tool/src/types/index.ts:3-42`）。 |
| Main Flow | processImage → CLEANUP_SESSION → setProcessing → Worker chunk → ADD_IMAGE_SLICE(按 index 写入) → 选择 SET_SELECTED → 导出消费 selectedSlices；错误/新上传复用 CLEANUP（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-112`，`/tmp/Long_screenshot_splitting_tool/src/hooks/useImageProcessor.ts:96-101`）。 |
| Cross-Module Dependencies | 上游切割依赖状态写入协议；下游预览/导出依赖 imageSlices 与 selectedSlices 的 index 契约；路由守卫依赖“是否有原图/切片/选择”（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:237-250`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-405`，`/tmp/Long_screenshot_splitting_tool/src/utils/pdfExporter.ts:59`）。 |
| Key Design Decisions | 1) 局部 `useReducer` 而非 Redux/Zustand：状态耦合强但规模小（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:33`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:29`）。2) `ADD_IMAGE_SLICE` 按 index 写入修复异步乱序（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-55`）。3) `CLEANUP_SESSION` 集中 revoke objectUrls 并尝试 terminate worker（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:89-112`）。 |
| Risk Areas | sparse array：按 index 回填可能空洞；SELECT_ALL 与预览混用 array index / slice.index（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-55`，`:72-73`，`/tmp/Long_screenshot_splitting_tool/src/components/ImagePreview.tsx:210-222`）。Worker 所有权：`AppState.worker/SET_WORKER` 与 `useWorker` ref 可能脱节（`/tmp/Long_screenshot_splitting_tool/src/hooks/useWorker.ts:30-33`，`:145`，`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:35`，`:152`）。旧 Worker 消息缺 sessionId 校验（`/tmp/Long_screenshot_splitting_tool/src/hooks/useImageProcessor.ts:30-101`）。 |
| Source Evidence | `/tmp/Long_screenshot_splitting_tool/src/types/index.ts:11-42`；`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-112`；`/tmp/Long_screenshot_splitting_tool/src/hooks/useImageProcessor.ts:96-101`；`/tmp/Long_screenshot_splitting_tool/src/components/ImagePreview.tsx:210-222`；`/tmp/Long_screenshot_splitting_tool/src/hooks/useWorker.ts:30-33`。 |
| Open Questions | 1) `SET_WORKER` 是否遗留设计？2) 稀疏数组在端到端场景是否真实触发错选（未复现测试）。3) 未抽样的独立页面是否直接读写同一状态。 |

## 叙事分析

状态层把“异步切片到达”与“UI/导出可用事实”隔开。选择 `useReducer` 是因为状态字段相互耦合：切片、Object URL、处理态、选择集必须作为一次会话处理。

### 1. 核心写入与清理

`ADD_IMAGE_SLICE` 按 `payload.index` 写数组，注释明确为修复 onload 乱序（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:47-55`）。这与导出按 index 排序共同构成页序契约。`CLEANUP_SESSION` 是集中释放入口，新上传与导航错误恢复复用它（`/tmp/Long_screenshot_splitting_tool/src/hooks/useAppState.ts:89-112`）。

### 2. 权衡

放弃 Redux 生态换更小依赖面与直观生命周期。代价是 sparse array 与 Worker 所有权边界需要人工纪律，而不是类型系统强制。

### 3. 铺垫

有了稳定的 `imageSlices + selectedSlices`，导出系统只需决定如何把选择变成 PDF/ZIP。
