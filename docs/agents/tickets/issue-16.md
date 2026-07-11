# Issue #16

- url: https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/16
- title: Spec: unparsed/core Unsupported 时强制子代理基线工具补读（rg/find/wc）
- labels: ready-for-agent
- created: 2026-07-11
- source: to-spec from conversation (v2.1-human Unsupported Area 语义 + 用户要求补读)
- home-branch: main（自 v2.0-parallelism-degraded 工作区迁入；该功能分支使命结束）

## 摘要

core `unparsed` / Unsupported Area 出现时，不得只列路径；必须调度 Unparsed File Read Pass（优先子代理，工具：rg/find/wc/读文件），落盘可审计观察；不豁免 parse-quality，不伪造 units。

## Seams

- A: SKILL/references 契约（主）
- B: 可选 gate unparsed-manual-review
- C: 真实UAT回归测试

完整正文见 GitHub Issue #16。
