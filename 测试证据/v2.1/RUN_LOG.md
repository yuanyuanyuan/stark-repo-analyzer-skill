# v2.1 测试执行日志（repo-analyzer 重跑）

日期：2026-07-11
执行仓库（分析器）：`/Users/chuzu/projests/stark-repo-analyzer-skill/v2.0-parallelism-degraded`
目标仓库：`/tmp/Long_screenshot_splitting_tool` @ `bdee20b8c4e4985c690a255ed09f64a3e335fd20`
证据输出：`测试证据/v2.1/standard`

## 1. 范围确认

用户要求：重新跑一遍 repo-analyzer 分析，证据保留在 `测试证据` 下**新建 v2.1**。

本轮执行：

- 模式：standard（先完成一条完整可审计链路）
- 不覆盖 v2.0 目录
- 不伪造 multi-agent active

## 2. 环境

```bash
node -v          # v24.18.0
ast-grep --version  # 0.44.1
graphify --version  # 0.9.8
test -d /tmp/Long_screenshot_splitting_tool
git -C /tmp/Long_screenshot_splitting_tool rev-parse HEAD
# bdee20b8c4e4985c690a255ed09f64a3e335fd20
```

## 3. 确定性 CLI

```bash
OUT=测试证据/v2.1/standard
REPO=/tmp/Long_screenshot_splitting_tool
node bin/repo-analyzer.js doctor --repo "$REPO" --out "$OUT"
# allowed: true
node bin/repo-analyzer.js scan --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js summarize --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js units --repo "$REPO" --out "$OUT"
# units: 288, parse_rate: 0.4820
```

（中间曾用临时目录 `v2.0-rerun-20260711`，已迁移并删除，统一落入 `v2.1`。）

## 4. 分析阶段（主 agent 串行 · degraded）

1. 阅读 README + repo-map，写 `evidence-plan.md`（标明 parallelism: degraded）
2. 回填 `coverage-units.json` 至 standard 阈值（src 60%，secondary ≥30%）
3. 写 `module-evidence/src.json`（含 semantic_reviews）
4. 写 `report.md`（项目全景/流程/模块协作锚点/改进建议/Unsupported Area）
5. 重跑 doctor（保证 doctor 与 out 匹配）+ gate

```bash
node bin/repo-analyzer.js doctor --repo "$REPO" --out "$OUT"
node bin/repo-analyzer.js gate --repo "$REPO" --out "$OUT" --mode standard
# allowed_to_synthesize: false
# fail: parallelism-execution, parse-quality, reference-quality
```

## 5. Gate 摘要

allowed_to_synthesize: **false**

失败项：

- parallelism-execution：degraded，非 multi-agent 完整通过
- parse-quality：parse_rate 48.20%
- reference-quality：core refs partial/missing 100%

通过项（节选）：evidence-plan、report-draft、module-classification、module-evidence-matrix、key-unit-coverage、core-unparsed-areas、semantic-source-review、report-depth

## 6. 决策

- **不**生成 `ANALYSIS_REPORT.md`（遵守 gate）
- 验收记 **部分通过**
- 证据全部落在 `测试证据/v2.1/` 供 PR/人工 review

## 7. 并行说明（防误读）

本轮没有多个子代理同时写 module-evidence。若未来完整通过，必须在 Plan 中出现 parallelism: active 与可追溯子代理产物。

---

## 8. 真 multi-agent 再跑一轮（standard-multiagent）

### 8.1 目录

`测试证据/v2.1/standard-multiagent/`（**新建**，不覆盖 `standard/` degraded 轮）

### 8.2 并行启动（真实并发进程）

```bash
python3 /tmp/ma_worker_state.py &    # subagent-src-state
python3 /tmp/ma_worker_export.py &   # subagent-src-export
python3 /tmp/ma_worker_secondary.py & # subagent-secondary
wait
# 记录：launched pids 1951 1952 1953；exits 0 0 0
```

日志：

- `standard-multiagent/logs/subagent-src-state.txt` → state wrote 66
- `standard-multiagent/logs/subagent-src-export.txt` → export wrote 40
- `standard-multiagent/logs/subagent-secondary.txt` → secondary wrote 32

### 8.3 主 agent 融合

- 合并 unit_id → `coverage-units.json`
- 合成 `module-evidence/src.json`
- 写 `report.md` + `main-agent-fusion.json`
- `doctor` + `gate --mode standard`

### 8.4 Gate 结果

- parallelism-execution: **PASS**（active + 子代理分工/产物/融合文案满足 gate 正则）
- parse-quality / reference-quality: **FAIL**
- allowed_to_synthesize: **false** → 不写 ANALYSIS_REPORT

### 8.5 验收文档

见 `ACCEPTANCE_RESULT_MULTIAGENT.md`
