> **规则提醒**：完整 UAT 定义见 `docs/specs/v2.1-codex-exec-uat.md`（须独立 `codex exec`）。  
> 本文件若未附可复核的 `codex exec` 命令与 `UAT_EXEC_SUMMARY.md`，则**不算**该规则下的 UAT 通过。详见 `UAT_STATUS.md`。

# v2.1-human 验收结果

## 总判定

**部分通过（CLI + 串行分析链路完整；质量门未放行最终合成）**

| 维度 | 结果 | 说明 |
|---|---|---|
| Doctor | 通过 | `allowed: true` |
| Scan / Summarize / Units | 通过 | 288 units，parse_rate 48.20% |
| Evidence Plan | 通过 | 含架构问题、分级、预算、`parallelism: degraded` |
| Coverage 双硬条件 | 通过 | src 60% / secondary ≥30%；analyzed 含 anchor+judgment；core 未分析有 skip_reason |
| Module Evidence Matrix | 通过 | `module-evidence/src.json` 字段齐全 + 风险抽样 + semantic_reviews |
| Semantic Source Review | 通过 | core 3 条，anchor/judgment 与 coverage 一致 |
| Report 草稿深度 | 通过 | 全景/流程/协作锚点/权衡/风险/改进 |
| Parallelism（standard 完整） | 失败 | 本轮故意 degraded（人工串行） |
| Parse quality | 失败 | 枚举器解析率硬阈值未达（项目侧/工具侧限制） |
| Reference quality | 失败 | core refs partial/missing 100% |
| ANALYSIS_REPORT.md | **未生成** | `allowed_to_synthesize: false`，禁止绕过 |

## 合规说明

严格执行 `skills/repo-analyzer/SKILL.md`：

1. 未跳过 Doctor / units / gate  
2. 未用正则生成关键单元分母  
3. 未在 gate 失败时发布最终 `ANALYSIS_REPORT.md`  
4. Unsupported Area 与开放问题保留在 `report.md` / Matrix  
5. 诚实记录 `parallelism: degraded`，不伪装 multi-agent

## 产物清单

- `doctor-report.json`
- `repo-map.json` / `repo-map.md`
- `coverage-units.json`
- `evidence-plan.md`
- `module-evidence/src.json`
- `report.md`
- `quality-gate-report.json`
- `RUN_LOG.md` / `ACCEPTANCE_RESULT.md`
