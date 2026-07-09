# 阶段 8：洞察融合

## 系统性设计哲学

这个项目的真实设计哲学可以概括为：**纯前端、低依赖、自造关键胶水、用状态守卫保护任务流程**。

它没有把自己做成通用图片处理框架，而是围绕一个明确任务闭环组织：上传长图、后台切割、预览选择、导出交付。路由、状态、Worker 和导出器都服务于这条链路。

## 最值得学习的设计

1. **算法与 I/O 分离**：`splitAnalyzer` 是纯函数，Worker 只做图像 I/O 和消息胶水。这让内容感知算法可以独立测试和迭代。
2. **内容感知 + 等分回退双轨**：项目没有为了“智能”牺牲稳定性。分析失败时，用户仍能得到固定高度切图结果。
3. **状态驱动导航**：等第一个切片真正进入状态后再跳转，避免异步任务未完成时被守卫踢回上传页。
4. **页序契约贯穿全链路**：`index` 从 Worker 到 reducer 再到导出器，是异步环境下保持顺序的关键。

## 主要架构风险

1. **外围复杂度稀释主线**：SEO、EnhancedSEO、shared-components 的复杂度超过了长截图分割工具当前所需。
2. **数组表示与异步回填存在张力**：按 index 写入解决乱序，但数组可能变稀疏，预览/导出/UI 计数都需要防御。
3. **Worker 生命周期所有权不清**：`useWorker` 是实际所有者，`AppState.worker` 看起来未接上。
4. **导出配置链路未闭合**：ExportControls 提供高级选项，但 App.handleExport 只实际使用 filename。

## 如果重新设计

- 保留纯前端和 Worker 架构。
- 用 `Map<number, ImageSlice>` 或 dense sorted projection 表达切片集合，避免 sparse array。
- 给 Worker 消息加 `sessionId`，防止旧会话 chunk 写入新状态。
- 用 Worker ready/handshake 替换 `setTimeout(200)`。
- 抽出 `normalizeSelectedSlices`，复用导出过滤排序规则，但不急于抽象完整 ExportEngine。
- 收敛 SEO 为一套实现，把 shared-components 的微内核协议降级为未来扩展。
