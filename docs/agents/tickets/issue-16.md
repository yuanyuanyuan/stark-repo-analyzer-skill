# Ticket

- id: "16"
- title: "Spec: unparsed/core Unsupported 时强制子代理基线工具补读（rg/find/wc）"
- requirement_ref: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/16"
- source_issue: "https://github.com/yuanyuanyuan/stark-repo-analyzer-skill/issues/16"
- labels: ready-for-agent
- blocked_by: none
- saved_from: "GitHub Issue #16 + docs/specs/unparsed-manual-read-pass-spec.md + Stage A 结构化补全（test_plan / acceptance 字段）"
- saved_at: "2026-07-11T17:51:00+08:00"
- home-branch: main（自 v2.0-parallelism-degraded 工作区迁入；该功能分支使命结束）

## what_to_build

当 Phase 2 `coverage-units.json` 之后（或模块分析过程中）发现 **core 模块存在 unparsed 文件** 时，skill **不得**仅把路径写入报告 Unsupported Area 后结束；必须强制调度一次 **Unparsed File Read Pass（未解析文件补读 pass）**：

1. **优先子代理**执行；无 subagent 时主 agent **串行**同一 pass，并在 Evidence Plan 记录 `unparsed_read_pass.parallelism: active|degraded`（勿与模块分析 parallelism 语义混用）。
2. **基线只读工具白名单**：`rg`/`grep`、`find`、`wc`、文件读取类工具；可用 `git` 只读。禁止安装依赖、启动服务、用正则发明 units 分母、修改目标仓源码、把 unparsed 静默移出列表。
3. **选样优先级**：入口/编排 → 主用户路径 UI → Matrix 跨模块点名的 unparsed → 风险路径 → 其余 SEO/debug/example 按预算浅读或 `skip_reason`。
4. **模式预算**：quick 全局最多约 3–5 个高影响 unparsed；standard 覆盖各 core 主路径相关子集；deep 提高比例但仍允许预算内 skip 并记录原因（具体数字写死在 skill/budgets）。
5. **可审计产物**（`$WORK_DIR`）：`unparsed-file-reviews/*.md` 或 `unparsed-file-reviews.json`，和/或 `module-evidence/{module}.json` 的 `unparsed_manual_reads[]`（path、tools_used、anchors、observation、confidence=`manual-read`、residual_gap）；Evidence Plan 增加「Unparsed File Read Pass」节。
6. **语义边界**：仍须声明 core unparsed 为 Unsupported Area；补读 **不**清除 unparsed、**不**提升 parse_rate、**不**豁免 parse-quality/reference-quality、**不**把文件计为 `status: analyzed` unit。

### 默认交付 Seams

| Seam | 范围 | 说明 |
|------|------|------|
| **A** skill/references 契约 | **本票默认必须** | SKILL Phase、evidence-first-v2 Unsupported 模板、module-analysis-guide、README 一句「Unsupported ≠ 不分析」 |
| **B** gate `unparsed-manual-review` | **推荐同 PR，可拆第二 PR** | core unparsed 非空且无补读记录 → fail；不改 minParseRate 默认 |
| **C** 真实UAT回归测试条款 | **本票默认必须** | 更新 `docs/specs/v2.1-codex-exec-uat.md` / 相关 checklist：core unparsed 非空时输出目录须有补读产物 |

### Out of scope（勿做）

- 用正则/启发式把 TSX 强行变成 parsed units
- 因补读自动 `allowed_to_synthesize: true` 或降低 parse-quality 阈值
- 把 unparsed 补读计入 key-unit coverage analyzed 百分比
- 修改目标仓库源码；完整实现 Issue #11；引入必须联网的第二分析服务

## acceptance_criteria

1. **SKILL/references 契约可见**：能在 skill 文本中定位触发条件（core + unparsed）、强制 Unparsed File Read Pass、工具白名单、选样优先级、模式预算、产物路径、`confidence=manual-read`、与 parse-quality / units 的边界；`evidence-first-v2` Unsupported 模板从「只声明」扩展为「声明 + 强制补读 + residual」；`module-analysis-guide` 对跨模块指向 unparsed 文件要求触发补读。
2. **Evidence Plan**：存在「Unparsed File Read Pass」节（分工/文件列表/产物路径/预算/parallelism）；core unparsed 非空时流程不得以「仅追加 Unsupported 路径列表」结束。
3. **不伪造解析成功**：补读成功后 `unparsed` 列表语义保持；parse_rate 不因补读提高；报告可引用 `文件:行号` 但标明 manual-read / 非枚举单元；未补读文件仍在 Unsupported 并写 skip 原因。
4. **README/中文文档**：至少一句话澄清 Unsupported ≠ 禁止分析 / 不等于完全不读。
5. **Seam B（若本 PR 包含）**：新增或扩展 gate check（如 `unparsed-manual-review`）：core unparsed 非空且无 Evidence Plan/`unparsed-file-reviews*`/Matrix 补读字段 → fail，reasons 明确「只声明 Unsupported 未执行补读」；有补读记录仍不豁免既有 parse-quality 失败；`node:test` 覆盖上述行为。
6. **Seam C**：真实UAT回归测试规则要求：当目标仓 core unparsed 非空时，输出目录必须出现补读产物；report 对高影响 unparsed（如 App/上传/导出）有 manual-read 锚点叙述，而非仅路径列表。
7. **回归基线**：`npm test` 与 `npm run typecheck` 退出码 0。

## test_plan

### unit

- **若实现 Seam B（gate）**：在 `test/gate.test.js`（或等价）增加/更新用例：
  1. core unparsed 非空 + 无补读记录 → 新 check fail
  2. 存在 `unparsed-file-reviews*` 或 `unparsed_manual_reads` / Evidence Plan 等价记录 → 该 check pass
  3. 有补读记录但 parse_rate 仍低 → parse-quality 仍 fail（补读不豁免）
  - 命令：在业务仓库根目录执行 `npm test`
- **若本 PR 仅 Seam A+C（文档/skill 契约）**：unit 记 **N/A** — 理由：无 gate/生产代码路径变更；**仍须**跑 `npm test` 作为回归基线（绿测证明未误伤）。

### e2e

- **可选**：用 fixture 工件模拟「core unparsed 非空 + 有/无补读记录」，跑 doctor→…→gate 链路核对 `unparsed-manual-review`（若已实现）。
- **默认**：e2e: **N/A** — 理由：主验收为 skill/references 契约 + 规则文档 +（可选）gate 单测；完整「真实UAT回归测试」属 uat 节与 AC6，不强制本票默认 e2e 重跑全仓 multi-agent。
- 替代证据：`npm test` 摘录 + skill/规则文件 diff 中可定位的触发条件与产物约定段落。

### uat

在 acceptance_env（local-cli + docs-only；真实UAT 时升格为独立 `codex exec`）下由 agent 代跑核对：

1. **契约对照**：SKILL + evidence-first-v2 + module-analysis-guide（及 README 一句）满足 AC1–4；能指出 Phase/章节位置。
2. **Seam B（若实现）**：对 fixture 或合成工件验证 unparsed-manual-review fail/pass 与「不豁免 parse-quality」。
3. **Seam C 规则**：`docs/specs/v2.1-codex-exec-uat.md`（及相关 checklist）含「core unparsed 非空 → 须有补读产物」检查项。
4. **真实UAT回归测试（推荐本票内跑一次，或 PR 标明 deferred + draft 理由）**：
   - 按 `docs/specs/v2.1-codex-exec-uat.md` **新开独立** `codex exec` 进程，严格执行 `skills/repo-analyzer/SKILL.md`；
   - 目标仓建议：`/tmp/Long_screenshot_splitting_tool`（或用户指定）；
   - 输出到本仓**新建**目录，如 `测试证据/v2.1-unparsed-read` 或 `测试证据/v2.1-human` 的新 run；
   - 当 unparsed 含 `src/App.tsx` 等时：目录须有 `unparsed-file-reviews*` 或 module-evidence 补读字段；report 对 App/上传/导出有 manual-read 锚点，而非仅 Unsupported 路径列表；
   - 检查 `UAT_EXEC_SUMMARY.md` 与 gate 工件；gate 未放行时不得声称产品分析完整通过。
5. **基线**：`npm test` 与 `npm run typecheck` 退出码 0。
6. **禁止**：把同会话 docs-only 勾选或主线程手写 report 称为「真实UAT回归测试」；把补读成功写成 parse_rate 提升或 analyzed unit。

## 摘要（只读）

core `unparsed` / Unsupported Area 出现时，不得只列路径；必须调度 Unparsed File Read Pass（优先子代理，工具：rg/find/wc/读文件），落盘可审计观察；不豁免 parse-quality，不伪造 units。

## Seams 速查

- A: SKILL/references 契约（主，必须）
- B: 可选 gate unparsed-manual-review（推荐）
- C: 真实UAT回归测试条款（必须）

完整需求正文见 GitHub Issue #16 与 `docs/specs/unparsed-manual-read-pass-spec.md`。
