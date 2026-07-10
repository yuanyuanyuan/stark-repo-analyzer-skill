# v2.0 quick 架构分析草稿

## 架构问题与模式边界

快速模式聚焦主干入口、状态、导出和核心流程，只保留最小风险抽样。

为什么采用关键单元覆盖率：v2.0 要验证的是架构判断是否有源码锚点和实质判断，而不是读取了多少源码行。当前 quick 模式已按预算回填 coverage-units.json。

## 核心流程

已验证的 src 关键单元包括 `src/config/seo/configLoader.ts:25`、`src/hooks/useAppState.ts:122`、`src/hooks/useDebugState.ts:8`、`src/hooks/useI18n.ts:52`。这些锚点支撑的设计判断是：src 集中承载上传、切割、状态和导出相关业务，次要模块提供配置、共享组件和工具链支撑。

```mermaid
flowchart LR
  U[用户上传长截图] --> S[src 核心处理]
  S --> C[切割与状态]
  C --> E[导出/展示]
  CFG[config/shared/tools] --> S
```

## 设计权衡

核心权衡是把分析预算集中到 src：这样能优先回答主业务链路为什么这样组织，同时避免把测试、脚本或共享组件的低影响单元误当成核心结论。替代方案是按目录平均阅读，但会增加 token 成本并削弱 Why > What。

## 风险、限制与 Unsupported Area

风险：解析率约为 48.2%，refs_status 大量为 partial，所以跨模块依赖只能作为受限结论。

- unsupported area: src/App.tsx
- unsupported area: src/components/DebugInfoControl.tsx
- unsupported area: src/components/DebugPanel.tsx
- unsupported area: src/components/EnhancedHelmetProvider.tsx
- unsupported area: src/components/EnhancedSEOManager.tsx
- unsupported area: src/components/ExportControls.tsx
- unsupported area: src/components/FileUploader.tsx
- unsupported area: src/components/I18nTestPanel.tsx
- unsupported area: src/components/ImagePreview.tsx
- unsupported area: src/components/ImagePreviewWrapper.tsx
- unsupported area: src/components/LanguageSwitcher.tsx
- unsupported area: src/components/LazyImage.tsx
- unsupported area: src/components/Navigation.tsx
- unsupported area: src/components/PerformanceOptimizer.tsx
- unsupported area: src/components/ResponsiveContainer.tsx
- unsupported area: src/components/SEOManager.tsx
- unsupported area: src/components/ScreenshotSplitter.tsx
- unsupported area: src/components/StructuredDataProvider.tsx
- unsupported area: src/components/TextDisplayConfig.tsx
- unsupported area: src/components/ViewportDebugger.tsx
- unsupported area: src/components/examples/EnhancedSEOExample.tsx
- unsupported area: src/components/mobile/Footer.tsx
- unsupported area: src/components/mobile/TouchImageSlicer.tsx
- unsupported area: src/components/mobile/TouchNav.tsx
- unsupported area: src/components/responsive/index.ts
- unsupported area: src/components/seo/EnhancedSEOManager.tsx
- unsupported area: src/components/seo/HeadingHierarchy.tsx
- unsupported area: src/components/seo/HeadingStructure.tsx
- unsupported area: src/components/seo/SEOIntegration.tsx
- unsupported area: src/components/seo/StructuredDataProvider.tsx
- unsupported area: src/config/seo.config.ts
- unsupported area: src/context/SEOContext.tsx
- unsupported area: src/hooks/useI18nContext.tsx
- unsupported area: src/hooks/useSEOConfig.tsx
- unsupported area: src/hooks/useSEOI18n.tsx
- unsupported area: src/hooks/useSEOOptimization.ts
- unsupported area: src/main.tsx
- unsupported area: src/test-setup.ts
- unsupported area: src/types/cssmodule.d.ts
- unsupported area: src/utils/config-helper.ts
- unsupported area: src/utils/i18nTestCoverage.ts
- unsupported area: src/utils/navigationState.ts
- unsupported area: src/utils/seo/metadataGenerator.ts
- unsupported area: src/utils/styleMapping.ts
- unsupported area: src/vite-env.d.ts

## 开放问题

- 是否需要为 TSX/复杂泛型补充更强 AST 模式，以提升 parse_rate。
- 是否需要让 graphify 参与关键单元分母，而不只是导航增强。


## Gate 放行摘要

- mode: quick
- allowed_to_synthesize: true
- checks: 8/8 pass
