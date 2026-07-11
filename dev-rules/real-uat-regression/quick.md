# 真实UAT回归测试 · quick 模式

- **模式**：`quick`
- **正式名称**：真实UAT回归测试（quick）
- **标签**：`real-uat-regression` · `mode:quick`
- **父规则**：[README.md](README.md)
- **产品契约**：`skills/repo-analyzer/SKILL.md` 分析模式表；`docs/specs/v2.1-codex-exec-uat.md`

## 1. 目的

用最短真实 exec 路径验证：Doctor→units→Evidence Plan→（必要补读）→gate 链路可跑通；**不**要求多子代理；unparsed 补读仅覆盖 **少量高影响** 文件。

## 2. 运行命令

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILL="$(pwd)/skills/repo-analyzer/SKILL.md"
REPO="${REPO:-/tmp/Long_screenshot_splitting_tool}"
OUT="$(pwd)/测试证据/real-uat-quick-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"

codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  -C "$(pwd)" \
  "严格执行 $SKILL 分析 $REPO ，输出报告到 $OUT

## 模式（强制）
- analysis mode = **quick**（核心关键单元约 30%、次要约 10%；不得按 standard/deep 预算执行）
- Evidence Plan 与 gate 均按 **quick** 记录与调用：\`repo-analyzer gate ... --mode quick\`

## 并行
- quick **允许** parallelism: degraded + 串行；若实际有 subagent 可写 active，但本档验收不强制多子代理完整通过。

## Unparsed File Read Pass（若 core unparsed 非空）
- 全局最多约 **3–5** 个高影响 unparsed（入口/编排/主路径 UI 优先）
- 落盘 unparsed-file-reviews* 和/或 module-evidence.unparsed_manual_reads
- confidence=manual-read；不抬高 parse_rate；不标 analyzed unit
- 预算外写 skip_reason，仍保留 Unsupported Area

## 交付
1. 完整 v2 工件链（doctor/scan/units、evidence-plan、module-evidence 按 quick 深度、report、quality-gate-report）
2. $OUT/UAT_EXEC_SUMMARY.md（中文：命令、时间、mode=quick、parallelism、gate、补读、分层结论）
3. gate 未放行则禁止写 ANALYSIS_REPORT 冒充完整通过
4. 不修改被分析仓源码；不覆盖 $OUT 以外历史证据目录
"
```

## 3. 通过检查清单

### 3.1 过程有效（本档最低）

- [ ] 独立 `codex exec` 可复核
- [ ] `$OUT` 含 doctor / repo-map / coverage-units / evidence-plan / quality-gate-report / report（或 skill 等价草稿）
- [ ] Evidence Plan 与摘要写明 **mode: quick**
- [ ] parallelism 诚实（degraded 可接受）
- [ ] core unparsed 非空 → 有补读记录（3–5 高影响量级）或明确说明无 unparsed
- [ ] 未把 degraded 写成 multi-agent 完整通过；gate 失败未伪造 ANALYSIS_REPORT

### 3.2 产品完整通过（可选更严）

- [ ] `allowed_to_synthesize: true` 且存在 gate 通过后的最终报告
- [ ] 其它 quality checks 按 quick 阈值全绿

### 3.3 本档明确不要求

- standard/deep 覆盖率
- multi-agent `parallelism: active` 完整验收
- unparsed 接近全量补读

## 4. 期望结论话术

- 默认：`真实UAT回归测试（quick）过程有效；…`
- 若仅机械链路或未 exec：不得使用正式名称「真实UAT回归测试」

## 5. 变更联动

skill quick 预算、gate quick 特例（如允许 degraded）、补读 quick 上限变化时，**必须**改本文件与 [README.md](README.md) 矩阵。
