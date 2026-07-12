# 独立架构 claim 的定义与计数边界

## 决策

- **Architecture Claim** 是可争辩的架构判断，不是纯事实罗列。
- Slice A 机判一条 claim 须同时满足：
  1. 位于约定容器：`## 关键设计决策`（或等价稳定标题）**且**条目含 `<!-- arch-claim -->`（或等价 `arch-claim` 标记）
  2. 至少 1 个 `file:line` 锚点
  3. 与同稿其它 claim 的锚点鼓励互不相同（同文件不同行允许；跨文件更佳）
- 脚本输出 `claim_count` 作 Density Proxy；**不设** standard≥12 / deep≥20 的失败阈值（仅观测）。
- **不计入** claim_count：风险/改造条目、Probe Promotion 条目、纯项目事实句。
- 「是否真有洞察 / 是否模板废话」由 Reader Rubric 判定，不由 regex 单独定罪。
