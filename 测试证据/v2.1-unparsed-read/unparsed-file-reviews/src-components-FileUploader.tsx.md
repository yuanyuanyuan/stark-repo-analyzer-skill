# Unparsed Manual Read · src/components/FileUploader.tsx

- path: `src/components/FileUploader.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 交互与无障碍细节未进枚举单元
- anchors:
  - `src/components/FileUploader.tsx:22` — FileUploader 导出组件
  - `src/components/FileUploader.tsx:51-72` — validateFile + handleFileSelect
  - `src/components/FileUploader.tsx:101-117` — drag/drop 与 click 触发

## observation

纯展示/交互组件：校验 MIME/大小后回调上层 `onFileSelect`，自身不直接创建 Worker。支持拖拽、点击、触控反馈；`disabled || isProcessing` 时禁用。主数据面仍在 App/useImageProcessor。

## 不改变 parse_rate
