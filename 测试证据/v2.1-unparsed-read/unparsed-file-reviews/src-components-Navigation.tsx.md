# Unparsed Manual Read · src/components/Navigation.tsx

- path: `src/components/Navigation.tsx`
- tools_used: [rg, read, wc]
- confidence: manual-read
- residual_gap: 与 useNavigationState 守卫完整状态机未逐分支验证
- anchors:
  - `src/components/Navigation.tsx:184` — Navigation memo 主组件
  - `src/components/Navigation.tsx:219-236` — handleNavigate / next / previous

## observation

步骤导航 UI + 性能监控包装；导航可用性依赖外部 navigationItems 与 getNextAvailableStep。属于流程 UX 层，不持有 imageSlices 源真值。

## 不改变 parse_rate
