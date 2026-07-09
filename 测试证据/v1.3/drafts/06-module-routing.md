# 06 路由与导航守卫模块

## Evidence Matrix

| 字段 | 内容 |
|------|------|
| Module Role | 把浏览器 hash 转成页面状态，并在刷新/直达/流程未完成时阻止渲染到不满足前置条件的页面；服务 GitHub Pages/SPA 场景下的多步骤工作流定位与恢复（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:15-34`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`）。回应 Evidence Plan 问题：自定义 hash 路由优先于 React Router；页面守卫避免未完成时白屏/错页。 |
| Entry Points | `useRouter` 初始化与 `hashchange` 监听；App 注入 `currentPath/push`；`validateNavigation` + `navigationErrorHandler` 硬守卫；页面分支内软守卫（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:15-50`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:38-44`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-430`）。 |
| Core Data Structures | `SimpleRouterState{currentPath,params,query}`；`NavigationError` 与恢复策略；路由配置雏形 `RouterConfig`（运行时未主导）（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:7-20`，`/tmp/Long_screenshot_splitting_tool/src/utils/navigationErrorHandler.ts:55-105`，`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:20-68`）。 |
| Main Flow | hash → currentPath → App switch 分发；进入 `/split`/`/export` 前硬守卫校验原图/切片/选择；失败则清理/提示/redirect；页面内再做软守卫（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430`）。上传后等待切片 0→>0 再 push `/split`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`）。 |
| Cross-Module Dependencies | 依赖状态层最小事实（原图/切片/选择）；与切割流水线协同：切片到达后才导航；向导航组件提供 `appState/currentPath/onNavigate`。【待主 agent 验证】导航组件内部 disabled 点击行为（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-430`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:582-589`）。 |
| Key Design Decisions | 1) 自定义 hash Hook 而非 React Router：降低依赖、适配静态托管（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:16-50`，`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:60-68`）。2) 硬守卫+软守卫双层：URL/状态一致性 + UI 兜底（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-430`）。3) 状态驱动导航：等 imageSlices 成形再跳转，而非 processImage Promise 完成（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`）。 |
| Risk Areas | 配置层 `src/router/index.ts` 未接入运行时，维护者误以为改配置即可加路由（`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:66-178`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430`）。守卫条件在 errorHandler / useNavigationState / App 分支多处重复，可能不同步（`/tmp/Long_screenshot_splitting_tool/src/utils/navigationErrorHandler.ts:55-105`，`/tmp/Long_screenshot_splitting_tool/src/hooks/useNavigationState.ts:105-134`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-430`）。 |
| Source Evidence | `/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:15-50`；`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`；`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`；`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430`；`/tmp/Long_screenshot_splitting_tool/src/utils/navigationErrorHandler.ts:55-105`；`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:66-178`。 |
| Open Questions | 1) `src/router/index.ts` 是遗留、规划还是构建模式产物？只能证明未被 App 导入，不能证明作者意图。2) Navigation 是否阻止 disabled 点击？边界未分析 `Navigation.tsx`。3) 假设：选 hash 主因是静态部署与减依赖（无 ADR）。 |

## 叙事分析

本模块回答读者在进入切割/导出前的问题：页面如何被 URL 定位，以及状态未就绪时如何不白屏、不错页。它不是复杂路由框架，而是“多步骤前端工作流在静态部署下的定位与守卫”。

### 1. 模块角色

「路由与导航守卫」承担两件事：把 `window.location.hash` 转成当前页面状态；在用户直达、刷新或处理未完成时，阻止渲染不满足前置条件的页面。去掉它后仍可在单页内靠 React state 切 UI，但会失去刷新定位、浏览器前进后退、以及缺失图片/切片时的恢复路径（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:15-34`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:38-44`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`）。

### 2. 设计思路

运行时没有接入 React Router，而是极小 `useRouter` 维护 `currentPath` 与 `push/replace`（`/tmp/Long_screenshot_splitting_tool/src/hooks/useRouter.ts:16-50`）。仓库中存在更完整的 `RouterConfig` 与匹配工具，但 `rg` 与导入关系表明它们未主导 App 分发；实际是 `switch(currentPath)`（`/tmp/Long_screenshot_splitting_tool/src/router/index.ts:66-178`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:284-430`）。

守卫分硬/软两层：硬守卫在渲染前 `validateNavigation` 并 redirect；软守卫在页面分支内给降级 UI（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:137-182`，`/tmp/Long_screenshot_splitting_tool/src/App.tsx:305-430`）。与切割流水线的契约是状态驱动：等 `imageSlices` 0→>0 再 push `/split`（`/tmp/Long_screenshot_splitting_tool/src/App.tsx:121-135`）。

### 3. 关键权衡

双层守卫提升鲁棒性，代价是条件多处重复。配置层与运行时分叉是主要演进风险：改配置不等于改行为。

### 4. 铺垫

路由保证用户在正确阶段，但真正把 File 变成切片的是切割流水线。
