# v2.0 deep Evidence Plan

## 架构问题

- 长截图切割工具如何把上传、切割、状态和导出串成主流程？
- src 核心模块为什么承担最大业务复杂度，次要模块如何提供配置、共享组件和工具链支撑？
- 当前解析率不足时，哪些区域必须作为 Unsupported Area 保留？

## 候选证据

- Repo Map: repo-map.json / repo-map.md
- 关键单元分母: coverage-units.json
- 核心源码锚点: src/config/seo/configLoader.ts:25、src/hooks/useAppState.ts:122、src/hooks/useDebugState.ts:8、src/hooks/useI18n.ts:52、src/hooks/useImageProcessor.ts:5、src/hooks/useLazyLoading.ts:10、src/hooks/useLazyLoading.ts:18、src/hooks/useLazyLoading.ts:169
- 未解析文件清单: coverage-units.json#unparsed

## 分工

- parallelism: degraded，当前由主 agent 串行生成 deep 模式证据。
- core module: src
- secondary sampling: config、scripts、shared-components、tools

## 预算

- mode: deep
- time: 240 分钟
- token: 240000

## 风险抽样计划

- 抽样数量: 3
- 优先级: 入口/状态/导出/配置边界，以及 refs_status 为 partial 的单元。

## 报告结构

- 使用场景与架构问题
- Repo Map 候选信号
- src 核心流程
- 次要模块协同
- 风险、限制与 Unsupported Area
