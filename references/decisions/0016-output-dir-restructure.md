---
Status: Accepted
Date: 2026-07-08
Round: 6 (T08)
---

# ADR-0016 输出目录重命名与结构重组

## Context

T08 之前，所有分析产物平铺在 `analysis/` 目录下，文件名使用数字前缀（`00-meta.txt`、`02a-manifest-card.md`、`05-module-ids.yaml`、`06-module-*.md`、`07-cross-ref-checks.md`、`08-coverage.md`、`12-history-hotspot.txt` 等）。这导致：

1. 产物目录与用户手写文件混在一起，难以区分。
2. 数字前缀脆弱——新增产物需要手动分配编号，删除产物留下空洞。
3. JSON/MD 混排，没有按用途分组。
4. `analysis` 是一个常见目录名，容易与用户仓库自身的 `analysis/` 冲突。

## Decision

**将输出目录从 `analysis` 改为 `.stark-repo-analyzer`，并按用途分为 5 个子目录。**

### 目录结构

```
.stark-repo-analyzer/
├── data/              # 结构化数据（JSON/YAML/TXT）
│   ├── meta.txt
│   ├── repo-type.yaml
│   ├── manifest-card.md
│   ├── question-answers.md
│   ├── research.md
│   ├── module-ids.yaml
│   ├── modules-plan.md
│   ├── coverage.md
│   ├── coverage-failure.md
│   ├── expected-symbols.json
│   ├── coverage-symbols.json
│   ├── mcp-tools.json
│   ├── performance-report.json
│   ├── config-effective.json
│   ├── report-data.json
│   └── agent-summary.json
├── reports/           # 人读 Markdown 报告
│   ├── ANALYSIS_REPORT.md
│   ├── ANALYSIS_REPORT.tech-lead.md
│   ├── ANALYSIS_REPORT.business.md
│   ├── ANALYSIS_REPORT.learning.md
│   ├── README.md
│   ├── STATE_REPORT.md
│   ├── SLA_REPORT.md
│   └── PERFORMANCE_REPORT.md
├── diagnostics/       # 诊断中间产物
│   ├── slices/
│   │   ├── 01-frontend.xml
│   │   └── history-hotspot.txt
│   ├── module-drafts/
│   │   └── module-module_001.md
│   ├── cross-ref-checks.md
│   ├── cross-ref-review-input.md
│   └── cross-ref-agent-review.md
├── logs/              # 运行日志
│   └── run-YYYYMMDD-HHMMSS.md
├── acceptance/        # 验收脚本
│   └── check.sh
└── agent-runs/        # agent 调用证据
    └── modules-batch/
```

### 文件名变更

- 去除所有数字前缀（`00-meta.txt` → `data/meta.txt`）
- JSON 文件名统一小写（`REPORT_DATA.json` → `data/report-data.json`）
- 模块草稿去除 `06-` 前缀（`06-module-*.md` → `module-*.md`）
- 切片文件保持原名但移入 `diagnostics/slices/`

## Alternatives

- **M1. 保留 `analysis/` 目录名** —— 冲突风险高，且不符合 dotfile 惯例。
- **M2. 用 `output/`** —— 过于通用，不具辨识度。
- **M3. `.stark-repo-analyzer/`（本 ADR）** —— dotfile 惯例，工具名可识别，不与用户文件冲突。

## Consequences

- `IGNORE_DIRS` 新增 `.stark-repo-analyzer`，避免分析自身产物。
- `prepare_output()` 和 `GENERATED_DIRS` 更新为新路径集。
- 所有 `analyzer_*.py` 模块的输出路径更新。
- `render_report.py` 新增 `--output-dir` 参数，从 `--data` 目录读取 `report-data.json`。
- 验收脚本 `analyzer_acceptance.py` 重写路径检查列表。
- `acceptance/04-link.sh` 和 `05-mermaid-judge.sh` 扫描 `reports/` 子目录。
- 全部测试路径引用更新。

## Linked

- ADR-0011（验收脚本路径检查列表更新）
- T08 任务说明
