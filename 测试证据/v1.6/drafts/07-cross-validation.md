# v1.6 交叉验证

分析对象：`/tmp/Long_screenshot_splitting_tool`
模式：标准分析

## 1. 模块草稿完整性核查

| 模块 | 草稿 | Evidence Matrix | 风险抽样 | 开放问题 | 结论 |
|---|---|---:|---:|---:|---|
| 截图切割核心流水线 | `06-module-splitting-pipeline.md` | 有 | 有 | 有 | 通过 |
| 状态管理与导出 | `06-module-state-export.md` | 有 | 有 | 有 | 通过 |
| SEO、国际化与导航 | `06-module-seo-i18n-navigation.md` | 有 | 有 | 有 | 通过 |
| 构建部署与共享组件基础设施 | `06-module-build-shared-infra.md` | 有 | 有 | 有 | 通过 |

4 个核心模块均按 v1.3-v1.5 要求先给 Evidence Matrix，再进入叙事分析，并包含源码锚点、风险路径抽样和开放问题。

## 2. 关键锚点抽查

| 抽查结论 | 草稿来源 | 复核结果 |
|---|---|---|
| App 主路径的导出会调用 `exportToPDF` / `exportToZIP` | 状态与导出 | `src/App.tsx:224-264` 确认。 |
| `ScreenshotSplitter` 的本地导出处理只记录日志 | 状态与导出、切割流水线 | `src/components/ScreenshotSplitter.tsx:108-115` 确认；但 `App.tsx` 未导入该组件，降级为备用/遗留入口风险。 |
| SEO 语言固定为中文 | SEO/i18n/导航 | `src/App.tsx:539-542` 确认 `language="zh-CN"`，且语言切换在导航组件中发生。 |
| 图片切片按 index 写入以抵抗异步乱序 | 状态与导出、切割流水线 | `src/hooks/useAppState.ts:47-59` 与 `src/hooks/__tests__/useAppState.test.ts:18-49` 支撑。 |
| Worker 内容感知失败回退等分 | 切割流水线 | `src/workers/split.worker.js:125-128` 和 `src/workers/split.worker.js:228-241` 支撑。 |
| 部署 workflow 弱化质量门 | 构建/共享基础设施 | `.github/workflows/deploy.yml:43-50` 使用 `|| echo`，确认。 |

## 3. 跨模块一致性判断

已验证：

- 运行时真实主线是 `App.tsx`，它直接编排上传、处理、预览、导出、SEO、导航和 i18n。截图切割、状态导出、SEO 导航三份草稿都把 `App.tsx` 作为关键交汇点，结论一致。
- `ImageSlice[] + selectedSlices` 是处理、预览和导出的共享契约。切割流水线负责产生切片，状态层按 index 管理，导出器按 selected set 过滤排序。
- 项目整体设计哲学符合文档中的“扁平化单仓库架构”：核心业务不拆多包，使用目录、hook、工具函数和别名维持边界。

降级为限制或开放问题：

- `ScreenshotSplitter` 是否仍被某些页面或外部导入使用，当前主 App 未使用；最终报告只把它列为备用/遗留组件接线风险。
- `routerConfig` 是否有未来用途，当前运行时使用 `useRouter` hash 路由；最终报告不把 `routerConfig` 写成当前运行路由核心。
- SEOManager 引用的 `/manifest.json`、`/sw.js`、字体和健康检查资源是否存在于最终部署产物，本次未构建验证，只列为资源引用开放问题。
- 构建脚本中面向 `packages/*` 的工具是否仍是目标架构，本次只根据源码判断它与当前扁平结构漂移，不断言运行时一定被调用。

## 4. 风险抽样汇总

| 风险主题 | 证据 | 架构影响 |
|---|---|---|
| Worker 任务缺少 task id/cancel | `useImageProcessor.ts:121-130`、`useWorker.ts:121`、`split.worker.js` 消息协议 | 单任务 happy path 清晰，连续上传/旧任务回写防线不足。 |
| 大图内存峰值 | `split.worker.js:111-116` | Worker 避免主线程阻塞，但全图 `getImageData` 没有解决内存峰值。 |
| 导出配置未完整闭环 | `ExportControls.tsx:66-106`、`App.tsx:233-255` | UI 有质量/PDF/ZIP 选项，App 主路径只消费 filename；配置能力未完全落到 exporter。 |
| SEO/i18n 语言不同步 | `App.tsx:541`、`LanguageSwitcher.tsx:151-154` | UI 可切英文，但 head 仍按中文生成，属于产品化外壳的跨模块契约缺口。 |
| 部署质量门偏软 | `.github/workflows/deploy.yml:43-50` | 发布链路偏“尽量继续”，不适合严格生产质量门。 |
| 工具脚本与扁平仓库漂移 | `tools/build-scripts/build-all.js:11-20` 等 | 基础设施文档感强于真实接入，维护者容易误判可用能力。 |

## 5. Unsupported Claims 检查

可进入最终报告的确定性结论：

- 项目是 React + TypeScript + Vite 的浏览器端长截图分割工具，证据：`README.md:1-14`、`package.json:55-91`。
- 项目文档明确采用扁平化单仓库架构，证据：`README.md:16-23`、`docs/ARCHITECTURE.md:11-35`。
- 主 App 路径真实调用 PDF/ZIP exporter，证据：`src/App.tsx:224-264`。
- SEO 语言在主路径固定为 `zh-CN`，证据：`src/App.tsx:539-542`。
- 部分构建脚本与 `packages/*` monorepo 假设相关，证据来自对应脚本源码。

不得写成确定事实的内容：

- 真实用户长截图切割视觉质量。
- npm build/test 是否在当前机器全部通过。
- GitHub Pages 线上部署是否可访问。
- SEOManager 引用的全部静态资源是否在 dist 中存在。

## 6. 实际执行摘要

- 实际 subagent 数量：4。
- 核心模块覆盖：4 个核心模块全部覆盖。
- 次要模块处理：测试、移动端、docs、工具元数据没有单独开草稿，作为风险或边界抽样进入相关模块。
- 风险抽样数量：每个核心模块至少 1 条，合计超过 10 条。
- 外部调研范围：本地 README、架构文档、源码；未联网调研。
- 报告长度：标准模式完整报告，未扩展到深度模式的三套运行对比。
- 超预算/降级：未执行生态命令、未运行快速/深度两种额外模式；因此 v1.6 acceptance checklist 中“三模式对比”只能判为部分通过。
