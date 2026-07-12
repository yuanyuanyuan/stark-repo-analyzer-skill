# quality-contract 调用生命周期：Skill 合成后强制 + UAT 复跑

## 决策

1. Skill 在写出终稿 `ANALYSIS_REPORT.md` 之后、交付收尾之前，**必须**执行：
   `repo-analyzer quality-contract --out <out> --repo <repo> --mode <mode> --stamp-report`
2. 真实UAT 在独立 `codex exec` 流程中 **再执行一次**（防漏跑）；以目录内最后一次 `quality-contract-report.json` 为准。
3. 分析 agent **禁止**手改 `quality_contract: pass`；只能通过 CLI 盖戳（ADR-0018）。
4. CLI 总结果 `fail`（exit 4）**不**回滚终稿文件，**不**改写 `delivery_status` / `allowed_to_synthesize`。
5. 漏跑 CLI 导致终稿仍为 `not_evaluated` 或缺失 `quality-contract-report.json`：真实UAT 判过程不合格（可与 structure 细则对齐为 fail 或过程红，实现时 UAT 清单硬勾）。

## 与既有 ADR

- 落实 ADR-0034 入口与 ADR-0016/0025 正交状态。
