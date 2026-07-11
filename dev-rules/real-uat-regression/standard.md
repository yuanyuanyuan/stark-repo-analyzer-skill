# 真实UAT回归测试 · standard 模式

- **模式**：`standard`
- **正式名称**：真实UAT回归测试（standard）
- **标签**：`real-uat-regression` · `mode:standard`
- **父规则**：[README.md](README.md)
- **产品契约**：`skills/repo-analyzer/SKILL.md`；`docs/specs/v2.1-codex-exec-uat.md`；`docs/specs/v2.0-multi-agent-acceptance.md`

## 1. 目的

验证 **标准深度** 真实分析路径：核心约 60% / 次要约 30% 关键单元覆盖预算、Evidence Matrix、Semantic Source Review（每 core ≥1）、**Unparsed File Read Pass（主路径相关 unparsed 子集）**。  
多子代理：**目标 active**；运行时不支持则 degraded 并 **降级结论**（过程仍可有效）。

## 2. 运行命令

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILL="$(pwd)/skills/repo-analyzer/SKILL.md"
REPO="${REPO:-/tmp/Long_screenshot_splitting_tool}"
OUT="$(pwd)/测试证据/real-uat-standard-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"

codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  -C "$(pwd)" \
  "严格执行 $SKILL 分析 $REPO ，输出报告到 $OUT

## 模式（强制）
- analysis mode = **standard**
- gate：\`repo-analyzer gate ... --mode standard\`
- 不得静默按 quick 预算交差

## 并行（诚实）
- 若运行时支持 subagent：必须真实并行模块分析，Evidence Plan 写 **parallelism: active**，并记录：
  - 实际子代理分工
  - 每个子代理产物路径（建议 subagent-artifacts/ 与 module-evidence）
  - 主 Agent 融合过程
- 若不支持：写 **parallelism: degraded** + 串行顺序；**禁止**声称 multi-agent 完整通过；subagent-artifacts 可仅放说明 README

## Unparsed File Read Pass（core unparsed 非空时强制）
- 覆盖各 core **主路径相关** unparsed 子集（入口/编排/主 UI/跨模块点名/风险路径优先）
- 优先子代理；无则主 agent 串行，并写 unparsed_read_pass.parallelism: active|degraded
- 工具白名单：rg/grep、find、wc、读文件、git 只读
- 产物：unparsed-file-reviews* 和/或 unparsed_manual_reads[]
- 报告对 App/上传/导出等写 manual-read 锚点；仍声明 Unsupported；不抬高 parse_rate

## 交付
1. 完整工件链 + module-evidence 满足 standard
2. $OUT/UAT_EXEC_SUMMARY.md（必须含 mode=standard、parallelism、补读列表/数量、gate 各项关键 fail 原因）
3. gate 未放行禁止 ANALYSIS_REPORT 冒充完整通过
4. 不改目标仓；不覆盖历史证据目录
"
```

## 3. 通过检查清单

### 3.1 过程有效（本档最低）

- [ ] 独立 `codex exec` + skill 绝对路径 + **mode=standard**
- [ ] 关键工件齐全；`UAT_EXEC_SUMMARY.md` 完整
- [ ] parallelism **诚实**（active 或 degraded 二选一，记录原因）
- [ ] core unparsed 非空 → 有补读产物；高影响路径有 manual-read 叙述（非仅路径列表）
- [ ] 未把 degraded 写成 multi-agent 完整通过
- [ ] 未在 gate 失败时伪造完整通过报告

### 3.2 产品分析完整通过（更严）

- [ ] `allowed_to_synthesize: true`
- [ ] 存在 gate 通过后最终 `ANALYSIS_REPORT.md`（或 skill 规定的最终交付名）
- [ ] parse-quality / reference-quality / report-depth / unparsed-manual-review 等均 pass

### 3.3 多子代理完整通过（更严，可与 3.2 分离）

- [ ] Evidence Plan：`parallelism: active`
- [ ] 分工 + 每子代理产物 + 主 agent 融合均可追溯
- [ ] **不是** 仅存在 `subagent-artifacts/README.md` 占位

若 3.1 成立而 3.2/3.3 失败：结论必须分层写清，不得合并成一句「UAT 通过」。

## 4. 与 ticket 16 / unparsed 专项

standard 档是验证 **Unparsed File Read Pass** 的主推荐档：样例仓若含 `App.tsx` 等 unparsed，输出目录应出现 reviews 与 report 锚点。专项目录名（如 `v2.1-unparsed-read`）可作为一次 standard 真实UAT 的别名，但新跑优先 `real-uat-standard-*`。

## 5. 变更联动

standard 覆盖率、semantic review 每 core 条数、unparsed 选样、gate `parallelism-execution` / `unparsed-manual-review` 变化时，**必须**更新本文件。
