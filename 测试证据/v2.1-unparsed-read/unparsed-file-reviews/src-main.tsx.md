# Unparsed Manual Read · src/main.tsx

- path: `src/main.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 非枚举单元；仍属 core unparsed / Unsupported Area
- anchors:
  - `src/main.tsx:5` — `createRoot(...).render(<App />)` 作为 SPA 挂载点

## observation

文件仅 5 行：导入 `createRoot`、全局样式、`App`，在 `#root` 上渲染应用。无业务状态。确认应用入口极薄，真正编排在 unparsed 的 `App.tsx` 与 parsed hooks。

## 不改变 parse_rate

本文件仍在 `coverage-units.json#unparsed` 中；本笔记不是 analyzed unit。
