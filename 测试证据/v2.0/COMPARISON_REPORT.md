# v2.0 与历史测试证据对比

对比对象：

- `测试证据/v1.0没改造前`
- `测试证据/测试证据v1.1/Long_screenshot_splitting_tool-20260709`
- `测试证据/v1.2`
- `测试证据/v1.3`
- `测试证据/v1.6`
- `测试证据/v2.0`

## 1. 产物完整性对比

| 版本 | 主要验证对象 | 过程证据 | 最终报告 | 对比报告 | 验收报告 | 判定 |
|---|---|---:|---:|---:|---:|---|
| v1.0 | 旧流程重跑 | 有 | 有 | 有 | 有 | 通过 |
| v1.1 | 源码锚点优先 | 有 | 有 | 有 | 有 | 通过 |
| v1.2 | Evidence Plan | 有 | 有 | 有 | 有 | 通过 |
| v1.3 | Evidence Matrix | 有 | 有 | 无/未列入 | 有 | 通过 |
| v1.6 | Budget Profiles + Risk Sampling + Unsupported Claims + Repo Map | 有 | 有 | 有 | 有 | 部分通过 |
| v2.0 | CLI 硬门控 + 关键单元分母 + gate + 多子代理验收 | 有 | 有 | 有 | 有 | 部分通过 |

## 2. v2.0 已验证的增量

相比 v1.6，v2.0 本次已经验证到的新增能力是：

- Doctor 硬门控真实生效：缺少符号枚举器时阻塞。
- 下游命令遵守 Doctor：`scan` 在 doctor 未放行时拒绝执行。
- 安装 `ast-grep` 后，真实目标仓库 quick / standard / deep 三模式曾可通过旧 gate；Issue #12 与 #13 修正后，三种模式都会被当前质量门阻止。
- `coverage-units.json` 成为关键单元分母，三模式核心覆盖率分别达到 30%、60%、90%。
- gate 通过后才生成 `ANALYSIS_REPORT.md`。
- 发布包边界更清晰：dry-run 包只包含运行时、skill、文档和许可证。
- 自动化测试覆盖 v2 关键规则：coverage 双硬条件、semantic source review、三模式 gate 阈值和 e2e fixture。

## 3. v2.0 未验证的增量

本次仍未验证或未充分验证：

- 更高 parse_rate 下的完整源码覆盖表现。
- graphify 作为正式关键单元枚举器的实现路径。
- 大型多语言仓库上的三模式耗时和质量表现。
- standard/deep 的真实多子代理执行：quick / standard / deep 的 Evidence Plan 都是 `parallelism: degraded`，没有多个子代理参与模块深度分析。
- 每个子代理产物与主 agent 融合过程：本次只有主 agent 串行写入 `module-evidence/src.json` 和最终报告。
- 当前目标仓库的 `parse_rate` 为 48.2%、core 未解析文件占比为 53.57%、core 单元 `partial/missing` 引用占比为 100%，低于当前质量门要求。
- 当前三份报告草稿缺少项目全景和具体改进建议，属于浅报告，不能与 v1.0 baseline 等价。

## 4. 与 v1.6 的关键区别

v1.6 是一次完整标准模式人工证据链，产出了最终分析报告，但没有硬 CLI gate。
v2.0 本次先验证了 doctor 阻塞，再补齐 `ast-grep` 后完成三模式 gate。

这个区别很重要：

- v1.x 更强调“分析过程是否充分”。
- v2.0 同时验证“不满足前提时拒绝开始”和“满足前提后 CLI/gate 机械链路可运行”；Issue #12 后，standard/deep 还必须通过多子代理执行检查；Issue #13 后，所有模式还必须通过解析质量、引用质量和叙事深度检查。
- v2.0 新增的多子代理验收要求不能只看 `allowed_to_synthesize:true`；当 Evidence Plan 写明 `parallelism: degraded` 时，standard/deep 只能算部分通过。

因此 v2.0 相比 v1.6 的核心进步是把手工证据链升级为 CLI 工件链和机器质量门。

## 5. 风险与解释

风险：

- ast-grep 当前 parse_rate 约 48.2%，未解析区域较多。
- graphify 可用，但当前 v2.0 代码只把 graphify 作为可选增强检查，不把它作为 `units` 的符号枚举器。
- 零分母模块 `.` 和 `test-setup` 需要手工 excluded，说明模块分级和覆盖率分母之间还有自动化改进空间。
- 当前证据不能证明多子代理执行质量，因为三模式均为 `parallelism: degraded`。
- 当前证据也不能证明报告质量：旧 gate 曾放行，但新 gate 已明确阻断 synthesis。

## 6. 总结

v2.0 当前证据证明：

- 自动化实现层面通过。
- 发布边界通过。
- 真实环境前置门控通过。
- 安装缺失工具后，真实仓库三模式曾完成旧 gate 正向链路。
- Issue #12 与 #13 修正后，quick 因 parse/reference/report-depth 失败，standard/deep 还同时因 parallelism 失败。
- 历史运行中 gate 通过后生成的最终报告是回归样例，不是当前通过证据。

但它没有证明报告质量或 standard/deep 的多子代理模块分析已经达到 v2.0 标准。最终判定应更新为：**v2.0 部分通过：CLI/gate 工件链可运行，但报告质量与多子代理验收未通过**。

后续要恢复完整通过，先要提升解析与引用质量、补齐报告叙事深度；之后重新跑一次 standard 或 deep 模式的多子代理分析，记录实际子代理分工、每个子代理产物和主 agent 融合过程，并让 `module-evidence/*.json` 与最终报告吸收这些产物。

如果产品目标是“有 graphify 就能跑三模式”，则这不是测试执行问题，而是 v2.0 实现边界问题：需要先让 `doctor` 和 `units` 正式支持 graphify 生成关键单元分母，再补对应测试。
