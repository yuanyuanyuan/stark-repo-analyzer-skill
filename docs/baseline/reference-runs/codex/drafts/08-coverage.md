# 08 Coverage：覆盖率汇总

## 统计口径

分母是本次纳入 bounded standard 的代表性生产文件，不是全仓库生产代码。测试、lock、生成文件、外围 crate 和没有进入主叙事的文件被排除。已读数是实际请求的源码范围估算；不把文件名扫描当作逐行阅读。

## 汇总

| 模块 | 类型 | 文件/范围 | 有效行 | 已读行 | 覆盖率 | standard 门槛 | 达标 |
|---|---|---|---:|---:|---:|---:|---|
| Session/turn | 核心 | session/mod.rs, turn.rs | 6581 | 3300 | 50.1% | 60% | 未通过 |
| Execution safety | 核心 | exec facade + execpolicy/sandbox facades | 2147 | 452 | 21.1% | 60% | 未通过 |
| CLI/TUI | 核心 | cli main + tui lib/app/chatwidget | 10591 | 2300 | 21.7% | 60% | 未通过 |
| Protocol/event | 次要 | protocol.rs/models.rs/permissions.rs | 13170 | 4100 | 31.1% | 30% | 部分通过 |
| App-server | 次要 | lib + thread processor + transport | 6008 | 652 | 10.9% | 30% | 未通过 |
| Extensibility | 次要 | skills loader + plugins manager | 4038 | 880 | 21.8% | 30% | 未通过 |

## 总体结果

- 核心模块合计：各模块分母为 6581 + 2147 + 10591 = 19319 行，已读 6052 行，31.3%，未达 60%。
- 次要模块合计：23216 行，已读 5632 行，24.3%，未达 30%。其中 protocol 单模块达到，app-server 和 extensibility 未达到。
- 不能把本次结果称为全仓库 standard 达标；它是有边界、可复核的 baseline。

## 主要原因

仓库约 69 万生产 Rust 行，且 TUI/core/app-server 的大编排文件占据主要复杂度。当前 runtime 没有暴露 subagent 工具，不能按参考流程并行深读；本轮优先保证系统级主线和证据诚实性。
