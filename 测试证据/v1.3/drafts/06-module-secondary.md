# 06 次要模块（简化 Evidence Matrix）

> 次要模块批量草稿。使用简化 Evidence Matrix：职责、入口或涉及文件、关键证据、风险或开放问题。

## i18n

| 字段 | 内容 |
|------|------|
| 职责 | 语言检测、资源动态导入、缓存、插值与偏好保存；横切 UI 文案层。 |
| 入口或涉及文件 | `src/hooks/useI18n.ts`；App/ExportControls 通过 `t(...)` 消费。 |
| 关键证据 | `/tmp/Long_screenshot_splitting_tool/src/hooks/useI18n.ts:5`，`:9`，`:67-103`；`/tmp/Long_screenshot_splitting_tool/src/components/ExportControls.tsx:52`；`/tmp/Long_screenshot_splitting_tool/src/App.tsx:37`。 |
| 风险或开放问题 | 新旧语言 key 兼容增加路径复杂度，但未稀释切割/导出主线；未发现明显阻断风险。 |

## SEO / Enhanced SEO

| 字段 | 内容 |
|------|------|
| 职责 | 按路由/上下文注入 metadata、结构化数据、OG/Twitter、canonical、性能资源提示。 |
| 入口或涉及文件 | App 挂载 `SEOManager`；另有 `EnhancedSEOManager`。 |
| 关键证据 | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:24`，`:539-552`；`/tmp/Long_screenshot_splitting_tool/src/components/SEOManager.tsx:20`，`:364`，`:453`；`/tmp/Long_screenshot_splitting_tool/src/components/EnhancedSEOManager.tsx:18-49`，`:144`，`:326-341`。 |
| 风险或开放问题 | 两套增强 SEO 并存，复杂度高于工具型 SPA 当前需求；性能监控与 SEO 耦合。建议收敛为一套实现。 |

## shared-components

| 字段 | 内容 |
|------|------|
| 职责 | 对外导出通信接口、共享状态协议、CopyrightInfo、Button 等。 |
| 入口或涉及文件 | `shared-components/index.ts`、`interfaces/ComponentInterface.ts`；App 实际主要使用 CopyrightInfo。 |
| 关键证据 | `/tmp/Long_screenshot_splitting_tool/src/App.tsx:21`，`:561-567`；`/tmp/Long_screenshot_splitting_tool/shared-components/index.ts:6-21`；`/tmp/Long_screenshot_splitting_tool/shared-components/interfaces/ComponentInterface.ts:6-61`，`:123-167`。 |
| 风险或开放问题 | 实际使用面窄、接口面宽，是过度工程信号；微内核协议不宜写成当前主架构结论。 |

## 配置 / 部署（边缘支撑）

| 字段 | 内容 |
|------|------|
| 职责 | 统一配置门面与部署适配。 |
| 入口或涉及文件 | `config/index.ts`、`config/build/deployment.config.ts`、`package.json` files 范围。 |
| 关键证据 | `/tmp/Long_screenshot_splitting_tool/config/index.ts:6`；`/tmp/Long_screenshot_splitting_tool/package.json:6-12`。 |
| 风险或开放问题 | 对部署有价值，不应进入核心流水线主叙事；开放问题：各部署模式对路由 history/hash 的实际影响未在本轮深挖。 |
