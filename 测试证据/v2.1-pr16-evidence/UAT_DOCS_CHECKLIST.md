# docs-only UAT 核对（ticket 16 · 同会话契约对照，≠ 真实UAT回归测试）

日期：2026-07-11  
分支：feat/16  
核对人：agent（session-user 授权）

## AC 对照

1. SKILL Phase 6.5 / Phase 5 Unparsed 节 / Phase 9 unparsed-manual-review / 产物表 / 禁止事项：可定位 — pass
2. evidence-first-v2 Evidence Plan Unparsed 节 + Unsupported 扩展 + Matrix unparsed_manual_reads 模板 — pass
3. module-analysis-guide 跨模块指向 unparsed 触发补读 + 合成前自检 — pass
4. README / README.zh 「Unsupported ≠ 禁止分析」一句 — pass
5. Seam B gate unparsed-manual-review + 4 单测（无记录 fail / reviews pass / matrix pass / 不豁免 parse-quality）— pass
6. v2.1-codex-exec-uat.md core unparsed 补读产物检查项 + 失败定义 — pass
7. npm test 39 pass / typecheck 0 — pass

## 真实UAT回归测试

见 `测试证据/v2.1-unparsed-read/UAT_EXEC_SUMMARY.md`（独立 codex exec）。

Verdict（docs-only）：pass  
Verdict（真实UAT过程）：pass；产品完整合成：blocked（目标仓 parse_rate 等，非本票回归失败）
