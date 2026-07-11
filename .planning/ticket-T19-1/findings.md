# Findings · T19-1

## P0 Restore · 避坑要点（≤3）

1. PR body 必须含可复制命令 + 日志摘录，不能只写 pass（lesson: PR 测试证据）。
2. `miss` 不得 fail；`allowed_to_synthesize` 仍表示 Full Delivery 许可，不改 T19-4 写稿行为。
3. 用户可覆写分支策略：本轮 **不新建** `feat/T19-1`，在当前工作分支交付（同 ticket 11 先例）。

## Codebase 现状

- `src/gate.js` 现有 checks 无 `insight-probe-process`；`allowed_to_synthesize = every check pass`。
- `test/gate.test.js` 的 `prepareArtifacts()` 可扩展写入 `insight-probes.json`。
- Spec/ADR/CONTEXT 已定义 schema 与三类 Catalog id。
- Catalog ids 稳定：`ui_promise_runtime_path`、`multi_source_rules`、`config_dual_write_dead_impl`。

## G1（待确认）

见 progress / 会话 Decision Card。

## G1 · 2026-07-11

- 用户回复：`a` → 批准 Goal+Loop
- 路线：在当前分支实现；不新建 feat/T19-1
- 进入 P2/P3


## Code-review 摘要

- 无高危 finding
- 建议级：`hit` 不强制 anchors 非空（T19-3 范围）；本票仅 process gate
- 测试基建：helpers 子进程剥离 NODE_OPTIONS、fixture shebang 用 process.execPath；common.runCommand 增加 timeout/NODE_OPTIONS 清理，避免 agent 宿主环境卡死
