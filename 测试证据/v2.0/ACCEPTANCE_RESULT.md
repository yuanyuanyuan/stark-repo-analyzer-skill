# v2.0 验收结果

日期：2026-07-10
被测版本：`repo-analyzer@2.0.0`
目标仓库：`/tmp/Long_screenshot_splitting_tool`
目标仓库 commit：`bdee20b8c4e4985c690a255ed09f64a3e335fd20`
证据目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/测试证据/v2.0`

## 总判定

**部分通过：CLI/gate 机械链路通过，但多子代理验收未通过。**

通过项：

- 自动化基线通过：`npm test` 29/29 通过。
- 语法检查通过：`npm run typecheck` 通过。
- 发布包 dry-run 通过：未包含测试证据、本机 hook、graphify 输出和绝对路径配置。
- 初始真实环境负向门控通过：缺少符号枚举器时 `doctor allowed:false`，`scan` 拒绝继续。
- 用户授权后安装 `ast-grep 0.44.1`。
- 安装后 quick / standard / deep 三模式 doctor 均 `allowed:true`。
- 三模式均生成完整 v2 工件链。
- 历史运行中三模式 gate 曾均为 `allowed_to_synthesize:true`，并生成 `ANALYSIS_REPORT.md`。
- Issue #12 修正后重新运行 gate：quick 仍 `allowed_to_synthesize:true`；standard/deep 因 `parallelism: degraded` 更新为 `allowed_to_synthesize:false`。

限制说明：

- `ast-grep` 对目标仓库的 `parse_rate` 约为 48.2%。
- 未解析 core 文件已在报告中声明为 Unsupported Area。
- graphify 可用，但当前 v2.0 实现仍不把 graphify 作为 `coverage-units.json` 的正式枚举器来源。
- quick / standard / deep 的 Evidence Plan 均记录为 `parallelism: degraded`，由主 agent 串行生成证据，没有实际开启多个子代理执行模块深度分析。
- 因此 standard/deep 不能按 v2.0 多子代理验收口径算完整通过；`allowed_to_synthesize:true` 不能替代真实子代理执行记录。

## 验收矩阵

| 编号 | 测试项 | 判定 | 证据 | 说明 |
|---|---|---|---|---|
| T01 | 自动化基线 | 通过 | `npm test` 输出 | 29 个 node test 全部通过。 |
| T02 | Typecheck | 通过 | `npm run typecheck` 输出 | `node --check` 通过。 |
| T03 | 发布包边界 | 通过 | `package/npm-pack-dry-run.txt` | dry-run 包含 19 个文件，未包含测试证据和 graphify 产物。 |
| T04 | 真实目标 doctor 负向 | 通过 | `RUN_LOG.md` | 安装前缺少枚举器时 `allowed:false`。 |
| T05 | doctor 失败原因可解释 | 通过 | `RUN_LOG.md` | `symbol-enumerator` 和 `language-support` fail，有 remediation。 |
| T06 | graphify 状态记录 | 通过 | `standard/doctor-report.json` | graphify pass，但不是阻塞原因。 |
| T07 | doctor 未放行阻止 scan | 通过 | `RUN_LOG.md` | `scan` 输出 doctor 未放行。 |
| T08 | 安装缺失工具 | 通过 | `RUN_LOG.md` | `ast-grep 0.44.1` 安装成功。 |
| T09 | quick 正向链路 | 部分通过 | `quick/quality-gate-report.json`、`quick/evidence-plan.md` | 当前 gate `allowed_to_synthesize:true`，但 `parallelism: degraded`，只能证明串行 quick 链路。 |
| T10 | standard 正向链路 | 未通过 | `standard/quality-gate-report.json`、`standard/evidence-plan.md` | 当前 gate 因 `parallelism: degraded` 输出 `allowed_to_synthesize:false`，没有多子代理执行记录。 |
| T11 | deep 正向链路 | 未通过 | `deep/quality-gate-report.json`、`deep/evidence-plan.md` | 当前 gate 因 `parallelism: degraded` 输出 `allowed_to_synthesize:false`，没有多子代理执行记录。 |
| T12 | 三模式差异对比 | 通过 | `RUN_LOG.md` | 覆盖率、预算和报告长度均有差异。 |
| T13 | 真实目标 Evidence Matrix | 通过 | `*/module-evidence/src.json` | core 模块 `src` 有 Evidence Matrix。 |
| T14 | 真实目标 Semantic Source Review | 通过 | `*/quality-gate-report.json` | 三模式均满足 semantic review gate。 |
| T15 | 真实目标最终报告质量 | 通过 | `*/ANALYSIS_REPORT.md` | gate 通过后生成。 |

## 关键证据

安装前 `standard/doctor-report.json` 曾显示：

- `allowed`: `false`
- `symbol-enumerator`: `fail`
- `language-support`: `fail`
- `graphify`: `pass`
- `primary_languages`: `TypeScript`
- `unsupported`: `TypeScript`
- remediation: 安装 `universal-ctags` 或 `ast-grep`

scan 负向结果：

```text
Doctor 未放行：修复 doctor-report.json 中的必需检查后重跑 doctor。
```

安装后：

| 模式 | gate | src 覆盖 | semantic review | 最终报告大小 |
|---|---|---:|---:|---:|
| quick | allowed | 57/190 = 30% | 2 | 3981 bytes |
| standard | blocked by parallelism | 114/190 = 60% | 1 | 4564 bytes |
| deep | blocked by parallelism | 171/190 = 90% | 3 | 4813 bytes |

## 为什么仍保留限制

本次三模式历史 gate 曾通过；Issue #12 修正后，standard/deep 已被 parallelism gate 阻止。即使忽略并行执行，也不能宣称“完全源码覆盖”：

- `parse_rate` 只有约 48.2%。
- 未解析 core 文件需要继续作为 Unsupported Area。
- `refs_status` 大量为 partial，跨模块关系判断仍应保守。
- standard/deep 没有记录实际子代理分工、每个子代理产物和主 agent 融合过程。

## 多子代理验收规则

v2.0 从本次修正开始采用以下验收口径：

- quick 可以在无 subagent 或低预算场景下记录 `parallelism: degraded`，但结论必须说明这是串行链路。
- standard/deep 在运行环境支持 subagent 时，必须实际执行多个子代理模块分析。
- standard/deep 要算完整通过，`evidence-plan.md` 必须记录实际子代理分工、每个子代理产物和主 agent 融合过程。
- `quality-gate-report.json` 的 `allowed_to_synthesize:true` 只代表 CLI/gate 机械条件满足；当 `parallelism: degraded` 时，不能等价为多子代理验收通过。

## 后续补全条件

后续增强方向：

1. 重新跑一次至少 standard 或 deep 模式的多子代理分析。
2. 让 `module-evidence/*.json` 和最终报告吸收各子代理产物，并记录主 agent 融合过程。
3. 改进 ast-grep 解析模式，提高 TypeScript/TSX parse_rate。
4. 评估 graphify 是否应成为正式关键单元枚举器。
5. 增加对零分母模块自动 excluded 的 CLI 支持，避免手工调整。
