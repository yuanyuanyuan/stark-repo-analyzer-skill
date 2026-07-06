---
Status: Accepted
Date: 2026-07-06
Round: 5 (R5-Q5)
---

# ADR-0015 报告末尾新增 `§9 未完成模块明细`

## Context

ADR-0009 规定：单模块 3 次重试耗尽 → 标 `FAILED`，**不再 retry**。

后果：

- 最终报告读者（老板 / 技术负责人 / 业务方）看到的报告看起来"完整"
- 但其中某些模块是 FAILED 状态，**没有任何痕迹**
- 读者不知道：
  1. 哪些模块没做完
  2. 为什么没做完（是 timeout？覆盖率不达标？LLM-judge 评分低？）
  3. 下次能不能补？预计多久？

老板看到一份 5 章报告，只听到"做完了"——**但其实缺 1 章**。

## Decision

**报告末尾新增 `§9 未完成模块明细`，每个 FAILED 模块列详细上下文**。

### §9 章节结构

```markdown
## §9 未完成模块明细

> 本章由 `analysis/STATE_REPORT.md` 中 `failed_modules[]` 字段生成。
> 若全部模块 PASS，本章不出现，`analysis/STATE_REPORT.md` 中设 `failed_modules: []`。

### 模块状态汇总

| 模块 ID | tier | 失败次数 | 最后错误 | 预计恢复 |
|---------|------|---------|----------|---------|
| module_007 | core | 3 | TIMEOUT | 改 haiku 重跑 / 30 分钟 |
| module_009 | core | 3 | COVERAGE_FAILED | 调整 sub-agent prompt / 60 分钟 |

### 失败详情

#### module_007（CLI Surface）

**最后错误时间**：2026-07-06T16:34:12+08:00
**最后错误类型**：TIMEOUT（阶段五 sub-agent 10 分钟无响应）
**失败历史**：
  - 14:00 启动（attempt 1）→ TIMEOUT 14:10
  - 14:15 启动（attempt 2）→ TIMEOUT 14:25
  - 14:30 启动（attempt 3）→ TIMEOUT 14:40
**最后部分输出**：`drafts/06-module-007.partial.md`（保留以便接力）
**建议恢复路径**：
  ```bash
  repo-analyzer --resume --from-stage=5 --module=module_007
  ```

#### module_009（Configuration Loader）

**最后错误时间**：2026-07-06T16:50:00+08:00
**最后错误类型**：COVERAGE_FAILED（52% < 80% 阈值）
**缺失 API 清单（top 20）**：
  - `ConfigParser.load_yaml`
  - `ConfigMerger.merge`
  - ...（见 `08-coverage-failure.md`）
**失败历史**：
  - 14:30 启动 → 52% 覆盖率 → 触发回退
  - 15:00 启动 → 48% 覆盖率（反而降）→ 触发回退
  - 15:30 启动 → 51% 覆盖率 → 触发回退耗尽
**建议恢复路径**：手动检查 `drafts/06-module-009.md`，补充缺失 API 后重跑。
```

### 集成位置

```python
# stage 7 renderer template 增加条件 block
{% if failed_modules | length > 0 %}
## §9 未完成模块明细
... (above structure)
{% endif %}
```

- 三受众模板（`tech-lead.tmpl.md` / `business.tmpl.md` / `learning.tmpl.md`）**都**包含 §9 块
- 若全部模块 PASS → §9 块不渲染（条件判断）
- `analysis/STATE_REPORT.md` 中 `failed_modules: []` 是 PASS 的硬条件

### STATE_REPORT 字段扩展

```yaml
# analysis/STATE_REPORT.md（YAML frontmatter）
failed_modules:
  - id: module_007
    tier: core
    attempts: 3
    last_error: TIMEOUT
    last_error_at: 2026-07-06T14:40:00+08:00
    partial_output: drafts/06-module-007.partial.md
    suggested_recovery: --resume --from-stage=5 --module=module_007
  - id: module_009
    tier: core
    attempts: 3
    last_error: COVERAGE_FAILED
    last_error_at: 2026-07-06T15:30:00+08:00
    coverage_ratio: 0.51
    missing_symbols_count: 47
    suggested_recovery: manual_review_then_rerun
```

## Alternatives

- **M1. 仅在 STATE_REPORT.md** —— 正式报告不暴露，最隐蔽，老板看不到。
- **M2. TL;DR footer 一行摘要** —— "本期未完成: N 模块"，详情链 STATE_REPORT.md。
- **M3. 独立成章 §9（本 ADR）** —— 报告末尾加 §9，FAILED 模块列详细上下文，最完整。

## Consequences

- 报告模板增加 1 个可选 block（grep 标志 `## §9 未完成模块明细`），不影响 PASS 时的渲染。
- `STATE_REPORT.md` YAML schema 增加 `failed_modules[]` 字段，必填（即使为空数组）。
- 阶段九渲染器 `render_report.py` 扩展模板条件块逻辑（约 +30 行）。
- ADR-0011 验收脚本中 §10 的"`STATE_REPORT.md` 必含 failed_modules"成为断言 9（JSON Schema 校验）。

## Open Questions

- [ ] §9 是否应该按 tier 排序（core 在前、minor 在后）？
- [ ] "建议恢复路径" 是否提供具体命令字符串，还是只指 `STATE_REPORT.md` 链接？
- [ ] 全部 PASS 时 §9 不渲染——但要不要 §0 TL;DR 中加一行 "本期 100% 模块覆盖" 作为正向反馈？

## Linked

- ADR-0004（cross-ref pass 触发回退，重试配额共享）
- ADR-0005（覆盖率门控失败触发 §9）
- ADR-0007（重试预算耗尽触发 §9 与 STATE_REPORT）
- ADR-0009（风险表 R5 命中后写入 STATE_REPORT.failed_modules[]）
- ADR-0011（§10 验收脚本断言 §9 存在性 + 字段完整性）
- 阶段七 §9 / 阶段八 §8
