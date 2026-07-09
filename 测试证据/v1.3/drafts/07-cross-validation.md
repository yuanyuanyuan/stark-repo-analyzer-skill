# 阶段 7：交叉验证与质量管控（v1.3）

## 1. Evidence Plan 回应核查

| 模块 | 草稿 | Evidence Plan 回应 |
|------|------|--------------------|
| 路由与导航守卫 | `06-module-routing.md` | Evidence Matrix 覆盖 hash 路由选择、硬/软守卫、状态驱动跳转、配置层未接入 |
| 切割流水线 | `06-module-split-pipeline.md` | 覆盖分层、Worker 消息、纯函数算法、失败回退、风险路径 |
| 状态管理与资源生命周期 | `06-module-state-management.md` | 覆盖 useReducer 充分性、ADD_IMAGE_SLICE 按 index、CLEANUP_SESSION、稀疏数组/Worker 所有权 |
| 导出系统 | `06-module-export.md` | 覆盖页序契约、分导出器、三层空选防御、选项链路断裂 |

结论：核心模块 Evidence Matrix 均回应 `05-modules-plan.md` 架构问题。

## 2. Evidence Matrix 完整性核查

| 检查项 | 结果 |
|--------|------|
| 每个核心模块草稿先有 Evidence Matrix 再叙事 | 通过 |
| 字段语义：角色/入口/数据结构/主流程/依赖/决策/风险/源码证据/开放问题 | 通过 |
| 关键判断带源码锚点 | 通过（抽样见下） |
| 次要模块使用简化矩阵（`06-module-secondary.md`） | 通过 |
| 无 `module-evidence/*.json` / 新 CLI / 自动 gate | 通过 |

## 3. 锚点抽查（回源码）

| 结论 | 锚点 | 抽查 |
|------|------|------|
| hash 路由初始化与监听 | `useRouter.ts:15-34` | 确认从 location.hash 初始化并监听 hashchange |
| 切片 0→>0 再跳 /split | `App.tsx:121-135` | 确认 prevSliceCountRef 逻辑与注释 |
| 分析失败回退等分 | `split.worker.js:125-129` | catch 置空 splitPoints |
| 算法纯函数声明 | `splitAnalyzer.ts:6-13` | 文件头声明无 DOM/canvas/Worker 依赖 |
| 按 index 写入切片 | `useAppState.ts:47-55` | newImageSlices[index]=payload |
| PDF/ZIP 过滤排序 | `pdfExporter.ts:59-61`，`zipExporter.ts:51-53` | filter selected + sort index |

## 4. 开放问题保留

来自各 Evidence Matrix 的 Open Questions 汇总，进入交叉验证限制说明：

1. `src/router/index.ts` 意图（遗留/规划/构建模式）未证实。
2. Navigation disabled 点击行为未分析。
3. 浏览器兼容矩阵与 30MB 峰值内存未压测。
4. `SET_WORKER` 是否遗留；稀疏数组端到端是否触发错选。
5. `ScreenshotSplitter` 导出入口与 `options.slices` 用途不明。
6. SEO 两套实现与 shared-components 宽接口是否计划收敛。

处理规则：以上均不得在最终报告写成已验证结论；已解决项需有交叉证据。本轮全部保留为开放问题/风险。

## 5. 跨模块结论（基于 Evidence Matrix 对比）

### 5.1 状态驱动导航

路由矩阵与切割/状态矩阵一致：导航等待 imageSlices 成形，不是事件乐观跳转。可写确定性结论。

### 5.2 `slice.index` 跨模块顺序契约

切割产出 index → 状态按 index 回填 → 导出按 index 过滤排序。这是融合最终报告的主线。同时状态矩阵指出 sparse array 代价，报告需并列写亮点与风险。

### 5.3 Worker 所有权边界

状态矩阵与切割矩阵共同支持：实际生命周期更依赖 `useWorker`；`AppState.worker` 更像未接上设计。结论降级为“边界不清/疑似遗留”，并保留开放问题。

### 5.4 外围过度工程

次要模块简化矩阵支持：SEO/shared-components 复杂度高于当前主线使用面。作为演进风险，不是核心流程阻断。

## 6. 质量结论

- Evidence Matrix 使模块草稿可比较、可审计。
- 开放问题被保留到本文件，并将在最终报告以“限制/开放问题”呈现。
- v1.3 未引入 JSON schema、自动解析或硬 quality gate。
