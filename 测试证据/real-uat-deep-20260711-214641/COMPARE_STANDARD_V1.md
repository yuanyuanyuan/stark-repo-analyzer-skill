# deep UAT 对照 · standard / v1.0

对照时间：2026-07-11

## 对照目录

| 轮次 | 路径 | mode | Full 报告 |
|---|---|---|---|
| standard Full（主对照） | `测试证据/real-uat-regression-20260711-213622/` | standard | `ANALYSIS_REPORT.md` 203L / ~12KB |
| standard 同日（锚点更密） | `测试证据/real-uat-standard-20260711-1855/` | standard | `ANALYSIS_REPORT.md` 197L / ~13KB |
| **deep 本轮** | `测试证据/real-uat-deep-20260711-214641/` | deep | **无** `ANALYSIS_REPORT.md`；仅阻塞草稿 `report.md` 55L |
| v1.0 改造前 | `测试证据/v1.0没改造前/ANALYSIS_REPORT.md` | n/a | 135L / ~13KB |

## 门禁与执行

| 项 | standard 213622 | deep 214641 | v1.0 |
|---|---|---|---|
| Doctor | allowed=true, tooling=baseline | allowed=false（缺 reference-edges）, tooling=enhanced 目标 | 无 v2 doctor |
| Gate | allowed_to_synthesize=**true**（13/13） | **false** | 无 v2 gate |
| parallelism | active（3 子代理） | degraded | n/a |
| 产品完整通过 | **是** | **否** | 有终稿报告（旧流程） |

## 报告厚度与主题锚点（近似）

唯一 `path.ext:line` 锚点计数为启发式（正则），用于相对比较。

| 报告 | 行数 | 唯一锚点≈ | 200ms | ready | 稀疏 | ExportControls | SEO | Worker | 导航 | 切片 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1.0 | 135 | **62** | 2 | 2 | 1 | 6 | 21 | 15 | 6 | 13 |
| standard 1855 | 197 | 27 | **5** | **3** | **3** | 2 | 4 | 16 | 0 | 7 |
| standard 213622 | 203 | 20 | 0 | 0 | 0 | 4 | 12 | 17 | 0 | 8 |
| deep 214641 report | 55 | 0 | 0 | 0 | 0 | 0 | 1* | 1* | 1* | 1* |

\*deep 阻塞草稿仅提及主题名，**无源码锚点分析**。

## insight probes

| 类 | standard 213622 | deep 214641 |
|---|---|---|
| ui_promise_runtime_path | **hit**（导出选项未贯通） | n_a（未进入分析） |
| multi_source_rules | **hit**（SEO 多源） | n_a |
| config_dual_write_dead_impl | miss | n_a |

## 用户问题：「报告比 v1.0 薄」是否因为 standard 而不是 deep？

### 结论（有证据）

1. **standard 会压薄「证据风格」**：v2 standard 禁止 Graphify/ctags，终稿更偏模块矩阵 + 抽样锚点；v1.0 锚点密度更高（≈62 vs standard ≈20–27）。
2. **但 standard 不是「必然更薄到丢关键洞见」**：同日 standard `1855` 仍写出 **200ms / ready / 稀疏数组**；`213622` 也有 ExportControls 贯通缺口与 SEO 多源 **probe hit**。
3. **本轮 deep 并不能验证「deep 会更厚」**：deep 因 **reference-edges 对本仓不可验证** 在 doctor 被拦，**没有 Full 报告**。历史 deep `1855` 同样未产出可对比的 Full `ANALYSIS_REPORT`。
4. 因此：**「比 v1.0 薄」只有一部分可用 standard 解释；不能指望未放行的 deep 自动补厚。** 厚度差异还来自：合成模板、probe 覆盖、子代理抽样、以及 v1 叙事密度。

### deep 若要 Full 需要什么（非本轮伪造成功）

- Graphify → `coverage-units.refs_status` 真实接线，或
- 能对 TS/JS 产出 reference 的符号提供方进入能力合同；
- 然后重新跑真实UAT·deep，再比 standard/v1.0 的行数与锚点。

## 一句话

**standard Full 通过但锚点/主题覆盖弱于 v1.0；deep 本轮过程有效但产品未通过，无法用 deep 否定或证明厚度问题。**
