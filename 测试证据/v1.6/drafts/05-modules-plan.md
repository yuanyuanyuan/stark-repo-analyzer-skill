# v1.6 模块计划与 Evidence Plan

分析对象：`/tmp/Long_screenshot_splitting_tool`
分析模式：标准分析

## 1. 报告叙事线

本项目最自然的叙事不是按目录讲，而是按用户完成一次处理任务的路径讲：

上传图片与参数配置 → 图片处理与切割 → 状态编排与结果预览 → PDF/ZIP 导出 → SEO/i18n/导航让工具成为可上线 Web 应用 → 构建部署与共享基础设施支撑维护。

这种顺序能解释为什么一个看似简单的“切图工具”会长出 Worker、状态管理、导出引擎、SEO、i18n、构建脚本和共享组件：核心不是算法炫技，而是把浏览器本地处理能力包装成完整产品体验。

## 2. 核心模块清单

| 模块 | 草稿文件 | 分析预算 |
|---|---|---|
| 截图切割核心流水线 | `drafts/06-module-splitting-pipeline.md` | 标准：聚焦主路径、Worker/Hook 边界、错误与大图风险 |
| 状态管理与导出 | `drafts/06-module-state-export.md` | 标准：覆盖状态结构、导出流程、Blob/文件内存风险 |
| SEO、国际化与导航 | `drafts/06-module-seo-i18n-navigation.md` | 标准：覆盖可上线 Web 应用边界、配置加载、路由语言一致性 |
| 构建部署与共享组件基础设施 | `drafts/06-module-build-shared-infra.md` | 标准：覆盖构建脚本、环境配置、共享组件管理器重复/边界风险 |

## 3. Evidence Plan：截图切割核心流水线

| 字段 | 内容 |
|---|---|
| 模块 | 截图切割核心流水线 |
| 架构问题 | 浏览器端如何把“用户上传图片”转成可预览、可导出的分割结果？为什么拆成 UI 组件、Hook、Worker/工具函数，而不是全写在组件里？ |
| 候选文件或入口 | `src/components/ScreenshotSplitter.tsx`、`src/hooks/useImageProcessor.ts`、`src/hooks/useWorker.ts`、`src/workers/split.worker.js`、`src/utils/splitAnalyzer.ts`、`src/components/ImagePreview.tsx` |
| 必需证据类型 | 文件校验、图片加载、分割参数、Worker 通信、分割结果结构、错误处理、对象 URL/内存释放 |
| 风险路径候选 | 大图内存、Worker 初始化失败、文件格式不支持、用户取消/重复触发处理、generated/test 边界 |
| 预期判断范围 | 判断模块主流程、同步/异步边界、性能取舍；不做像素级算法正确性证明。 |

## 4. Evidence Plan：状态管理与导出

| 字段 | 内容 |
|---|---|
| 模块 | 状态管理与导出 |
| 架构问题 | 项目如何协调“上传-处理-预览-导出”的状态变化？导出 PDF/ZIP 为什么作为独立控制与工具函数存在？ |
| 候选文件或入口 | `src/hooks/useAppState.ts`、`src/components/ScreenshotSplitter.tsx`、`src/components/ExportControls.tsx`、`src/utils/zipExporter.ts`、`src/utils/pdfExporter.ts`、`src/utils/persistence.ts`、`src/types/index.ts` |
| 必需证据类型 | reducer/action 或状态更新、导出输入输出类型、PDF/ZIP 生成逻辑、导出错误处理、持久化边界 |
| 风险路径候选 | Blob/对象 URL 泄漏、导出大文件内存峰值、处理状态与导出状态不同步、浏览器兼容性 |
| 预期判断范围 | 判断状态与导出职责边界、用户体验收益与复杂度；不执行真实文件导出 benchmark。 |

## 5. Evidence Plan：SEO、国际化与导航

| 字段 | 内容 |
|---|---|
| 模块 | SEO、国际化与导航 |
| 架构问题 | 一个本地图片处理工具为什么需要 SEO/i18n/导航层？这些横切能力如何与核心功能隔离，避免污染截图处理主路径？ |
| 候选文件或入口 | `src/components/EnhancedSEOManager.tsx`、`src/components/SEOManager.tsx`、`src/config/seo.config.ts`、`src/config/seo/configLoader.ts`、`src/hooks/useI18n.ts`、`src/hooks/useSEOI18n.tsx`、`src/hooks/useNavigationState.ts`、`src/router/index.ts`、`src/components/Navigation.tsx`、`src/locales/*.json` |
| 必需证据类型 | meta/structured data 管理、语言资源加载、语言切换、路由状态、默认配置与错误处理 |
| 风险路径候选 | 配置缺失、meta 重复或不一致、语言与路由不同步、localStorage/URL 状态漂移 |
| 预期判断范围 | 判断横切层是否提升产品化能力，以及它与核心处理的隔离程度；不做搜索引擎效果评价。 |

## 6. Evidence Plan：构建部署与共享组件基础设施

| 字段 | 内容 |
|---|---|
| 模块 | 构建部署与共享组件基础设施 |
| 架构问题 | 扁平化单仓库如何维持可构建、可测试、可部署？shared-components 是真实复用边界，还是迁移残留/过度抽象？ |
| 候选文件或入口 | `package.json`、`vite.config.ts`、`vitest.config.ts`、`config/index.ts`、`config/env/*.ts`、`config/build/deployment.config.ts`、`tools/build-scripts/*.js`、`shared-components/index.ts`、`shared-components/core/ComponentCommunicationManager.ts`、`shared-components/managers/SharedStateManager.ts` |
| 必需证据类型 | npm scripts、构建插件、环境配置、部署目标、共享组件导出、通信/状态管理器职责 |
| 风险路径候选 | 脚本引用不存在、环境配置漂移、构建脚本过度分散、shared-components 与 src 重复职责 |
| 预期判断范围 | 判断基础设施是否服务于单仓库效率目标；不执行部署、不做性能 benchmark。 |

## 7. 标准模式对计划的影响

- 核心模块全部覆盖，每个模块必须有 Evidence Matrix 和至少一条风险抽样。
- 次要模块不单独开草稿，通过构建/共享基础设施与最终报告评价合并处理。
- 风险抽样聚焦最相关路径，不要求覆盖所有风险类别。
- 外部调研只用本地 README/docs，避免扩大成本。
- 源码锚点是确定性结论前提；证据不足的内容保留为限制、假设或开放问题。

## 8. Subagent 输入预算

每个 subagent 的工作边界：

- 只深读分配给自己的候选文件和必要邻接文件。
- 不读取其他模块候选源码，避免重复劳动。
- 输出控制在模块草稿级别，先 Evidence Matrix，再叙事分析。
- 不执行生态命令，不运行测试，不修改非目标草稿文件。
