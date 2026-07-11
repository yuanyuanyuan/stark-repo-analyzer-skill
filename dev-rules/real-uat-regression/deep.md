# 真实UAT回归测试 · deep 模式

- **模式**：`deep`
- **正式名称**：真实UAT回归测试（deep）
- **标签**：`real-uat-regression` · `mode:deep`
- **父规则**：[README.md](README.md)
- **产品契约**：`skills/repo-analyzer/SKILL.md`；`docs/specs/v2.1-codex-exec-uat.md`；`docs/specs/v2.0-multi-agent-acceptance.md`

## 1. 目的

验证 **深度** 真实分析：核心约 90% / 次要约 60% 关键单元预算、更广风险抽样与替代方案叙述、Semantic Source Review（每 core 最多 3 条代表性 analyzed unit）、**Unparsed File Read Pass 提高补读比例**（仍允许预算内 skip 并记原因）。  
多子代理：与 standard 相同，**目标 active**；degraded 则不得称 multi-agent 完整通过。

## 2. 运行命令

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILL="$(pwd)/skills/repo-analyzer/SKILL.md"
REPO="${REPO:-/tmp/Long_screenshot_splitting_tool}"
OUT="$(pwd)/测试证据/real-uat-deep-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"

codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  -C "$(pwd)" \
  "严格执行 $SKILL 分析 $REPO ，输出报告到 $OUT

## 模式（强制）
- analysis mode = **deep**
- gate：\`repo-analyzer gate ... --mode deep\`
- 不得用 quick/standard 预算冒充 deep

## 并行（诚实）
- 支持 subagent：parallelism: active + 分工/产物/融合（建议更多并行边界：模块 + 风险 + unparsed 补读）
- 不支持：parallelism: degraded；禁止 multi-agent 完整通过话术

## Unparsed File Read Pass（core unparsed 非空时强制）
- 在 standard 主路径子集之上 **提高补读比例**（仍可对 SEO/debug/example 等预算 skip 并写 skip_reason）
- unparsed_read_pass.parallelism 与模块分析 parallelism 分字段记录
- 产物与 manual-read 语义同 skill Phase 6.5
- 报告须区分：已补读 unparsed vs 仅 Unsupported 列表

## 交付
1. 深度叙事 + Matrix + 风险抽样满足 deep
2. $OUT/UAT_EXEC_SUMMARY.md（mode=deep；补读数量/skip 统计；gate 分层结论）
3. gate 未放行禁止伪造 ANALYSIS_REPORT
4. 不改目标仓；不覆盖历史证据
"
```

## 3. 通过检查清单

### 3.1 过程有效（本档最低）

- [ ] 独立 exec + **mode=deep** 可复核
- [ ] 工件齐全；摘要写明 deep 预算执行情况（是否收缩范围）
- [ ] parallelism 诚实
- [ ] unparsed：补读比例高于「仅 3–5 个 quick 级」；skip 有原因；高影响路径有 manual-read
- [ ] 无假完整通过 / 假 multi-agent

### 3.2 产品分析完整通过（更严）

- [ ] `allowed_to_synthesize: true` + 最终报告
- [ ] deep 相关 gate（含 semantic-source-review 的 deep 阈值）pass

### 3.3 多子代理完整通过（更严）

- [ ] `parallelism: active` + 分工/产物/融合
- [ ] 建议 unparsed 补读若并行，亦有可追溯子产物

## 4. 成本与排期

deep 真实UAT 耗时与 token 显著高于 quick/standard；可作为发版前或重大 skill/gate 变更后的 **可选加强回归**，但一旦声称跑过 deep，必须满足本文件检查项。

## 5. 变更联动

deep 覆盖率、semantic 上限/下限、补读比例约定、gate deep 分支变化时，**必须**更新本文件与父 README 矩阵。
