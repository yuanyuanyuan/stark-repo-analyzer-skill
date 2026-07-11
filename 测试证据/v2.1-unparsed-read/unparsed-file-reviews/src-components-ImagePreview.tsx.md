# Unparsed Manual Read · src/components/ImagePreview.tsx

- path: `src/components/ImagePreview.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 虚拟列表/性能细节未深读
- anchors:
  - `src/components/ImagePreview.tsx:31` — ImagePreview
  - `src/components/ImagePreview.tsx:57-73` — handleSliceSelect 切换选中并 onSelectionChange
  - `src/components/ImagePreview.tsx:111+` — 全选/反选

## observation

受控多选预览：本地 selectedSlices 数组与父回调同步，支持模态查看与滑动手势。不修改 blob/objectUrl，只操作选择集合语义。

## 不改变 parse_rate
