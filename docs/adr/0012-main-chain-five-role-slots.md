# 主链采用五角色槽 + Evidence Plan 声明，而非固定业务五段

## 决策

- **Main Chain** 合同层固定 **5 个角色槽**（标签可按仓命名，角色不可缺）：
  1. `Ingress` — 入口 / 请求或用户动作进入系统
  2. `Core Transform` — 核心变换 / 领域处理
  3. `State/Truth` — 状态或事实源落点
  4. `Boundary/Guard` — 边界、守卫、权限或失败路径
  5. `Egress` — 输出 / 导出 / 对外契约
- Evidence Plan 须声明：本仓各槽 → 拟用标题 + 关键文件候选。
- 终稿主链小节必须覆盖 5 槽，**每槽 ≥1 个 `file:line` 锚点**。
- 长截图「上传→Worker→状态→导航→导出」仅为实例映射，不是产品唯一语义。
- 无 UI / 纯库仓：Ingress=公共 API 入口，Egress=导出符号或返回契约；**禁止**整条主链 `n_a`。
- 主链 5 槽属于 Final Report Quality Contract / Slice A 硬必达，**不是** Mechanical Gate hard 项（ADR-0010/0011）。

## 机判（ADR-0024）

终稿以 `<!-- main-chain: <slot_id> -->` 硬判五槽；Evidence Plan 声明为 UAT 过程软要求，不单杀 quality_contract。
