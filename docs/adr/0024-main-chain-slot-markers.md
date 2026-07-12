# 主链五槽机判：终稿 slot 标记硬判 + Evidence Plan 声明软要求

## 决策

- 主链五角色槽使用稳定 `slot_id` 机器标记（与 probe/claim 标记族一致）：
  - `ingress`
  - `core_transform`
  - `state_truth`
  - `boundary_guard`
  - `egress`
- 规范形态：`<!-- main-chain: <slot_id> -->`（或等价单行 `main-chain: <slot_id>`），位于该槽叙事块内。
- **quality_contract 硬判**（Slice A）：五个 `slot_id` 均至少出现一次，且标记所在块内 ≥1 合法 `file:line` 锚点。
- Evidence Plan 仍应声明「槽位 → 拟用标题/关键文件」（ADR-0012）；**缺 Plan 声明不单独导致 quality_contract=fail**，仅作真实UAT 过程警告。
- 禁止仅靠中文业务关键词（上传/导出等）作为主链机判依据。
