# 对照脚本入口：repo-analyzer quality-contract + 真实UAT 强制调用

## 决策

- Slice A 对照/盖戳通过现有 bin 扩展子命令：
  - `repo-analyzer quality-contract --out <dir> [--repo <path>] [--mode standard|deep] [--stamp-report] [--baseline-root <skill-repo>]`
- **不**并入 `gate` 子步骤，避免被当成 Mechanical Gate hard fail（ADR-0010）。
- 真实UAT 规格（`docs/specs/v2.1-codex-exec-uat.md` 及后续 QC 附录）**强制**在出终稿后调用该命令，产出 `quality-contract-report.json`（及 COMPARE 表）。
- 行为：读 `--out` 下 `ANALYSIS_REPORT.md` + `insight-probes.json`；baseline 默认来自 `docs/benchmarks/density-baselines.md`；可选 `--stamp-report` 将结果写回终稿文首。
- **exit code**：总 `quality_contract=fail` → 非 0（约定 4）；总 `pass` 或 `not_evaluated` → 0（`not_evaluated` 不假红）。

## 非目标

- 不把 QC 结果写入 `allowed_to_synthesize`。
- Slice A 不实现独立第二 bin 名；不强制 `scripts/` 旁路作为主入口。
