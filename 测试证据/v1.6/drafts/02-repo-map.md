# v1.6 Markdown Repo Map

分析对象：`/tmp/Long_screenshot_splitting_tool`
输出目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v1.6`
生成时间：2026-07-09

> 本 Repo Map 是深读前的候选信号，不写最终架构结论。模块边界、设计决策和权衡判断留给 Evidence Plan、模块草稿与最终报告验证。

## 1. 目录结构候选

目标仓库是一个 React + TypeScript + Vite 前端工具项目。顶层目录信号如下：

| 路径 | 候选含义 | 证据 |
|---|---|---|
| `src/components/` | 主 UI 与业务组件候选区 | `README.md:60-65`、`docs/ARCHITECTURE.md:121-123` |
| `src/hooks/` | 应用逻辑和业务 Hook 候选区 | `README.md:62`、`docs/ARCHITECTURE.md:124-127` |
| `src/utils/` | 核心算法、导出、错误处理、性能工具候选区 | `README.md:63`、`docs/ARCHITECTURE.md:128-134` |
| `src/workers/` | Web Worker 图片处理候选区 | `docs/ARCHITECTURE.md:57-61`、`docs/ARCHITECTURE.md:167-169` |
| `src/router/` | SPA 路由候选区 | `docs/ARCHITECTURE.md:124-127` |
| `src/locales/` | 国际化资源候选区 | `docs/ARCHITECTURE.md:131-134` |
| `src/config/seo/`、`src/config/seo.config.ts` | SEO 配置候选区 | 文件清单与 `docs/ARCHITECTURE.md:171-178` |
| `config/` | 环境、应用、构建配置候选区 | `README.md:71-74` |
| `shared-components/` | 共享组件与共享状态基础设施候选区 | `README.md:66-70` |
| `tools/build-scripts/`、`scripts/` | 构建、部署、测试辅助脚本候选区 | `docs/ARCHITECTURE.md:187-193` |
| `tests/`、`src/**/__tests__` | 测试候选区，后续只用于验证覆盖信号，不作为核心业务深读主线 | `README.md:84-103` |
| `.github/`、`.vercel/`、`.playwright-mcp/` | CI/部署/工具元数据候选区 | 目录枚举 |

## 2. 语言与规模候选

使用 `find`、`wc`、`awk` 等系统命令统计，未执行 `npm`、`pnpm`、`pip`、`cargo` 等生态命令。

| 类型 | 文件数候选 |
|---|---:|
| `.ts` | 93 |
| `.tsx` | 46 |
| `.md` | 42 |
| `.js` | 33 |
| `.json` | 16 |
| `.css` | 12 |
| `.yml/.yaml` | 10 |

规模参考：对 `.ts/.tsx/.js/.css/.json/.md` 文件排除 `node_modules`、`package-lock.json`、`pnpm-lock.yaml` 后，`wc -l` 汇总约 `67974` 行。该数字只是规模参考，不作为质量门。

## 3. 入口候选

| 候选入口 | 候选理由 |
|---|---|
| `src/main.tsx` | React 应用挂载入口候选。 |
| `src/App.tsx` | 应用根组件候选，可能连接 SEO、导航和核心功能组件。 |
| `src/components/ScreenshotSplitter.tsx` | 长截图分割主交互入口候选，文档组件树将其列为核心功能组件：`docs/ARCHITECTURE.md:273-278`。 |
| `src/hooks/useImageProcessor.ts` | 图片处理业务 Hook 候选，文档数据流称 UI 调用 `useImageProcessor`：`docs/ARCHITECTURE.md:210-216`。 |
| `src/workers/split.worker.js` | Web Worker 分割处理候选，文档将 Worker 放入核心处理层：`docs/ARCHITECTURE.md:57-61`。 |
| `src/components/ExportControls.tsx` | 导出控制入口候选，文档数据流称导出从 UI 到 Hook 再到 Export：`docs/ARCHITECTURE.md:219-222`。 |
| `src/router/index.ts` | SPA 路由入口候选，文档将路由归入应用逻辑层：`docs/ARCHITECTURE.md:124-127`。 |

## 4. Manifest 与核心配置候选

| 文件 | 候选含义 | 证据 |
|---|---|---|
| `package.json` | 项目依赖、脚本、构建入口 | `package.json:21-54`、`package.json:55-91` |
| `vite.config.ts` | Vite 构建配置候选 | 文件清单 |
| `vitest.config.ts` | 测试配置候选 | 文件清单 |
| `tsconfig.json`、`tsconfig.test.json` | TypeScript 配置候选 | 文件清单 |
| `config/env/*.ts` | 环境配置候选 | 文件清单 |
| `config/build/deployment.config.ts` | 部署配置候选 | 文件清单 |
| `.env.*` | 环境变量模板/配置候选 | 文件清单 |

## 5. 核心文档候选

| 文件 | 候选价值 |
|---|---|
| `README.md` | 产品定位、特性、目录结构、脚本入口；例如项目定位见 `README.md:1-14`。 |
| `docs/ARCHITECTURE.md` | 架构分层、ADR、数据流、组件树；例如单仓库决策见 `docs/ARCHITECTURE.md:11-35`。 |
| `docs/API-REFERENCE.md` | API/组件接口候选说明。 |
| `docs/TESTING-GUIDE.md` | 测试策略候选说明。 |
| `docs/SEO-INTEGRATION-GUIDE.md`、`docs/SEO-CONFIG-STATUS.md` | SEO 配置与集成候选说明。 |
| `shared-components/README.md` | 共享组件库候选说明。 |

## 6. 测试、generated、vendor 候选

| 候选区域 | 处理策略 |
|---|---|
| `src/**/__tests__`、`*.test.tsx`、`*.test.ts` | 作为测试覆盖和行为预期证据抽样，不作为核心架构深读主线。 |
| `tests/e2e/`、`tests/integration/`、`test-setup/`、`test-results/` | 作为验收/测试基础设施证据，标准模式只抽样。 |
| `package-lock.json`、`pnpm-lock.yaml` | lock 文件视为生成/低价值文件，统计时排除，不深读。 |
| `.git/`、`.vercel/`、`.serena/`、`.playwright-mcp/` | 工具状态或元数据，不纳入核心分析。 |
| `dist/` | 当前文件清单未见构建产物目录；若存在应视为 generated。 |

## 7. 可能高风险区域候选

这些只是候选风险入口，是否成立由模块草稿通过源码锚点验证。

| 风险候选 | 候选原因 |
|---|---|
| 图片分割与 Worker 生命周期 | 大图处理可能涉及内存、异步取消、错误传播、对象 URL 释放。 |
| 导出 PDF/ZIP | 大量 Blob、canvas、压缩包生成可能触发内存与浏览器兼容风险。 |
| SEO 配置加载 | 配置 JSON/schema/运行时 meta 管理可能存在默认值、环境差异和重复声明风险。 |
| i18n 与导航状态 | 路由、语言、持久化状态可能出现不同步或刷新丢失。 |
| 构建部署脚本 | 多脚本路径和环境配置可能增加漂移风险。 |
| shared-components 双路径 | `shared-components/core` 与 `shared-components/managers` 同名管理器候选，可能存在职责重复或迁移残留。 |

## 8. Repo Map 对后续阅读范围的约束

- 核心模块候选集中在 `src/components`、`src/hooks`、`src/utils`、`src/workers`、`src/config/seo`、`config` 和 `shared-components`。
- 测试、lock、工具元数据只做抽样或验证，不作为核心模块逐行阅读对象。
- Evidence Plan 必须从上面的入口候选和风险候选出发，提出 Why/How/Trade-off 问题。
