# Unparsed Manual Read · src/App.tsx

- path: `src/App.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 745 行大编排组件，ast-grep 未枚举；细节仍属 Unsupported，结论仅限补读锚点
- anchors:
  - `src/App.tsx:28-38` — AppContent 装配 useAppState / useImageProcessor / useRouter
  - `src/App.tsx:196-198` — handleFileSelect → processImage
  - `src/App.tsx:124-135` — imageSlices 从 0→>0 时跳转 /split
  - `src/App.tsx:226-248` — 导出空选择拦截 + exportToPDF/ZIP
  - `src/App.tsx:297` / `src/App.tsx:450` — FileUploader / ExportControls 挂载

## observation

AppContent 是唯一运行时编排中心：同时持有会话 hook、切图 hook、hash 路由，并按 `currentPath` switch 渲染上传/切分/导出页。上传成功后**不立刻跳转**，等切片计数 effect 再 push `/split`，与导航守卫配合避免空状态。导出路径调用 parsed 的 pdf/zip 工具函数，UI 层先 alert 无选择。组件层还叠 SEO/debug/viewport，抬高文件体量。

## 不改变 parse_rate

仍为 unparsed；不得计 analyzed unit。
