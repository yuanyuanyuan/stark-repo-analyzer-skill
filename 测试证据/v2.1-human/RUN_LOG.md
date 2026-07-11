# v2.1-human 测试执行日志（人工串行 · repo-analyzer standard）

日期：2026-07-11  
执行仓库（分析器）：`/Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded`  
目标仓库：`/tmp/Long_screenshot_splitting_tool` @ `bdee20b8c4e4985c690a255ed09f64a3e335fd20`  
证据输出：`测试证据/v2.1-human`

## 1. 范围确认

用户要求：严格执行 `skills/repo-analyzer/SKILL.md`，分析 `/tmp/Long_screenshot_splitting_tool`，输出到 `测试证据/v2.1-human`。

本轮执行：

- 模式：standard
- 执行主体：主 agent **人工串行**（`parallelism: degraded`）
- 不伪造 multi-agent active
- 不覆盖 `v2.1/standard` / `v2.1/standard-multiagent`

## 2. 环境

```bash
node -v
# 本地 Node 可用
ast-grep --version   # 0.44.1（doctor 记录）
graphify --version   # 0.9.8（可选增强，可用）
test -d /tmp/Long_screenshot_splitting_tool
git -C /tmp/Long_screenshot_splitting_tool rev-parse HEAD
# bdee20b8c4e4985c690a255ed09f64a3e335fd20
```

## 3. 确定性 CLI（Phase 0–2）

```bash
OUT=测试证据/v2.1-human
REPO=/tmp/Long_screenshot_splitting_tool
node bin/repo-analyzer.js doctor --repo "$REPO" --out "$OUT"
# allowed: true
node bin/repo-analyzer.js scan --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js summarize --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js units --repo "$REPO" --out "$OUT"
# units: 288, parse_rate: 0.4820
```

## 4. 分析阶段（主 agent 串行 · degraded）

1. 阅读 README / docs/ARCHITECTURE.md / CLAUDE.md + repo-map
2. 写 `evidence-plan.md`（标明 `parallelism: degraded`）
3. 深读主链源码：useAppState / useImageProcessor / useWorker / split.worker / splitAnalyzer / pdfExporter / zipExporter
4. 回填 `coverage-units.json` 至 standard 阈值（src 60%，secondary ≥30%）；core 未分析单元写 skip_reason
5. 写 `module-evidence/src.json`（含 3 条 semantic_reviews，与 coverage 逐值匹配）
6. 写 `report.md`（全景/流程/模块协作锚点/权衡/风险/Unsupported Area/改进建议）
7. 重跑 doctor + gate

```bash
node bin/repo-analyzer.js doctor --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js gate --repo "$REPO" --out "$OUT" --mode standard
# allowed_to_synthesize: false
```

## 5. Gate 摘要

allowed_to_synthesize: **false**

失败项：

- parallelism-execution：degraded，非 multi-agent 完整通过
- parse-quality：parse_rate 48.20% / TS 42.73% / core unparsed 53.57%
- reference-quality：core refs partial/missing 100%

通过项：

- evidence-plan、report-draft、module-classification
- module-evidence-matrix、key-unit-coverage
- core-unparsed-areas、reference-completeness
- semantic-source-review、report-depth

## 6. 决策

- **不**生成 `ANALYSIS_REPORT.md`（遵守 Phase 10：gate 未放行不得最终合成）
- 验收记 **部分通过**（CLI 机械链路 + 串行分析证据完整；multi-agent 与 parse/refs 硬门未过）
- 全部工件落在 `测试证据/v2.1-human/`

## 7. 并行说明（防误读）

本轮没有多个子代理同时写 module-evidence。完整 multi-agent 验收见 `测试证据/v2.1/standard-multiagent/`（另一轮）。
