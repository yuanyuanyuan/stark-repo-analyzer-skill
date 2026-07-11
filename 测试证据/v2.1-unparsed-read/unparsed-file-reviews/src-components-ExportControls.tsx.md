# Unparsed Manual Read · src/components/ExportControls.tsx

- path: `src/components/ExportControls.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 组件内本地 ImageSlice 接口与 types 是否完全一致未交叉证明
- anchors:
  - `src/components/ExportControls.tsx:43` — ExportControls 导出
  - `src/components/ExportControls.tsx:82-104` — handleExport 组装 options
  - `src/components/ExportControls.tsx:129` — canExport = 有选中且非 disabled/exporting

## observation

UI 选择 pdf/zip、文件名、质量，通过 onExport 回调把控制权交还 App；`canExport` 在控件层挡空选择，与 exporter 空选择 throw 形成双层防御。不拥有 blobs 生命周期。

## 不改变 parse_rate
