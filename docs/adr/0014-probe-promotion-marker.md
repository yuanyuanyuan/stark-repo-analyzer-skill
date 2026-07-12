# Probe 升格关联：条目内机器标记 + 可读类别名

## 决策

- 每个 `status=hit` 的探针在终稿「风险与改造优先级」中对应 **一条** 列表项/小节（一对一，禁止章节级笼统绑定多个 hit）。
- 该条目内必须含机器标记（Primary Reader 几乎不可见）：
  - HTML 注释：`<!-- probe-promotion: <probe_id> -->`
  - 或等价单行：`probe-promotion: <probe_id>`
- 同时建议条目标题/首行出现可读类别名（人工扫读）。
- Catalog 稳定 `probe_id`：
  - `ui_promise_runtime_path` — UI Promise → Runtime Path
  - `multi_source_rules` — Multi-Source Rules
  - `config_dual_write_dead_impl` — Config Dual-Write / Dead Implementation
- 对照脚本以机器标记为主判定关联；可读名不作为唯一机判依据。
- 不新增 agent 手填的 `probe-promotions.json` 侧车（避免 JSON 税）；若未来需要 sidecar，须由确定性工具从终稿反生成。
