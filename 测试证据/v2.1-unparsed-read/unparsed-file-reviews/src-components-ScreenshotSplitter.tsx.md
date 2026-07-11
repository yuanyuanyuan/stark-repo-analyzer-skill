# Unparsed Manual Read · src/components/ScreenshotSplitter.tsx

- path: `src/components/ScreenshotSplitter.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 与 App.tsx 双编排并存，默认路由是否挂载需结合 App switch 判断
- anchors:
  - `src/components/ScreenshotSplitter.tsx:25-36` — 组件内自建 useAppState + useImageProcessor
  - `src/components/ScreenshotSplitter.tsx:60-78` — handleFileUpload → processImage

## observation

这是**可独立运行的第二编排面**：内部再次实例化会话与切图 hook，并组合 FileUploader/ImagePreview/ExportControls。与 AppContent 形成潜在双源状态风险（若两处同时挂载会分裂会话）。主路径 CLAUDE.md 强调 App 为唯一编排入口；本组件更像封装入口或历史/演示路径。

## 不改变 parse_rate
