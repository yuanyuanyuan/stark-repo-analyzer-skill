# Unparsed File Read Pass Spec

- 状态：已发布 GitHub Issue #16（`ready-for-agent`）
- 日期：2026-07-11
- 关联证据：`测试证据/v2.1-human`
- 正式名称：Unparsed File Read Pass（未解析文件补读 pass）

## Problem Statement

当前 repo-analyzer 在 `coverage-units.json#unparsed` 命中 core 文件时，流程要求把这些路径写入报告的 **Unsupported Area**，并禁止把它们当作「覆盖充分 / 已验证实现细节」。

真实UAT（如 `测试证据/v2.1-human`）里会出现大量：

- `unsupported area: src/App.tsx`
- `unsupported area: src/components/FileUploader.tsx`
- `unsupported area: src/components/ExportControls.tsx`
- …

这容易被误读为「skill 完全不分析这些文件」。实际上 Unsupported 限制的是证据等级，不是禁止阅读。更关键的产品问题是：

**现有 skill 文本没有强制要求：一旦出现 unparsed/core Unsupported 列表，必须主动发起补读 pass（优先子代理，用 `rg`/`find`/`wc` 与直接读文件等基线工具）去阅读这些文件，并把可审计观察写回产物。**

结果是：主链 hooks/utils 可能分析充分，但编排入口与 UI 边界（App、上传、导出控件）长期停在「只列路径、不读内容」的状态，架构报告对用户可见主路径仍然偏弱。

## Solution

修改 skill 工作流契约：

当 Phase 2 `units` 之后（或模块分析过程中）发现 **core 模块存在 unparsed 文件** 时：

1. **必须**调度一次 **Unparsed File Read Pass**（未解析文件补读 pass）。
2. **优先派子代理**执行；运行时无 subagent 时主 agent **串行**执行同一 pass，并在 Evidence Plan 记录降级（`unparsed_read_pass: serial` 或等价字段）。
3. 子代理/执行者 **只使用基线只读工具**阅读这些文件，例如：
   - `rg` / `grep`（符号、调用、import、关键字符串）
   - `find`（路径枚举与范围确认）
   - `wc`（规模/是否值得深读）
   - 直接打开文件读取关键 span（`nl`/`sed`/read 工具）
4. **禁止**用正则表达式「发明」关键单元分母，或把手工补读伪装成 enumerator `parsed`。
5. 补读结果必须落盘为可审计工件（见实现决策），报告中的相关结论可引用 `文件:行号`，但必须标明 **manual-read / 非枚举单元** 置信度。
6. **不**因补读成功而自动清除 `unparsed` 列表，也 **不**豁免现有 `parse-quality` / `reference-quality` 硬门（除非另开独立票明确改阈值）。

用户侧感知：遇到 Unsupported Area 时，skill 不再「只列不读」，而是「先补读再分级声明剩余盲区」。

## User Stories

1. As a 使用 repo-analyzer 的开发者, I want 当出现 unparsed core 文件时 skill 自动补读这些文件, so that 我不会只看到一串路径却得不到架构信息。
2. As a 使用 repo-analyzer 的开发者, I want 补读优先由子代理完成, so that 主 agent 预算不被大量 TSX 文件拖垮且可并行。
3. As a 使用 repo-analyzer 的开发者, I want 子代理使用 rg/find/wc 等基线工具, so that 即使无 ctags/ast-grep 符号单元也能阅读源码。
4. As a 使用 repo-analyzer 的开发者, I want 补读结论带文件:行号锚点, so that 我能核对 App 编排/上传/导出等 UI 边界行为。
5. As a 使用 repo-analyzer 的开发者, I want 报告区分「枚举单元已分析」与「unparsed 手工补读」, so that 我不会误判证据强度。
6. As a 使用 repo-analyzer 的开发者, I want 补读后仍诚实保留剩余 Unsupported 盲区, so that 未读到的文件不会被静默吞掉。
7. As a 使用 repo-analyzer 的开发者, I want skill 明确「Unsupported ≠ 禁止分析」, so that 文档语义与真实行为一致。
8. As a 报告读者, I want 看到 unparsed 补读 pass 的执行摘要, so that 我知道哪些路径被读过、用了什么工具、置信度如何。
9. As a 报告读者, I want FileUploader/ExportControls/App 等关键 UI 文件在 unparsed 时仍有行为描述, so that 主用户路径叙事完整。
10. As a 报告读者, I want 调试/SEO/示例类 unparsed 文件可按预算浅读或跳过并写原因, so that 分析时间花在高影响路径上。
11. As a skill 维护者, I want SKILL.md Phase 明确触发条件与工具白名单, so that 不同 runtime 的 agent 执行一致。
12. As a skill 维护者, I want Evidence Plan 记录 unparsed_read_pass 分工与产物路径, so that 可审计且可验收。
13. As a skill 维护者, I want 补读产物有稳定目录约定, so that gate/UAT 能检查「是否发生过补读」。
14. As a skill 维护者, I want 禁止把补读写成 units 枚举成功, so that 不会绕过 parse-quality 语义。
15. As a skill 维护者, I want 无 subagent 时串行补读仍强制执行, so that degraded 不降低「必须读」要求。
16. As a skill 维护者, I want 补读选样有优先级规则, so that 预算内先读主链相关 unparsed 文件。
17. As a skill 维护者, I want module-evidence 能吸收补读观察, so that Matrix 与 report 叙事一致。
18. As a gate 维护者, I want（可选）机器检查「core unparsed 非空时必须有补读记录」, so that 只声明 Unsupported 却完全不读会被拦住。
19. As a gate 维护者, I want parse-quality 阈值默认保持不变, so that 补读不会伪装成解析率提升。
20. As a UAT 执行者, I want 真实UAT回归测试检查 unparsed 补读工件, so that Long_screenshot 类仓库能验证 App.tsx 等被补读。
21. As a 子代理执行者, I want 明确输入：unparsed 文件列表 + 问题边界 + 预算, so that 我不会乱读全仓。
22. As a 子代理执行者, I want 输出固定字段：path、tools_used、anchors、observation、confidence、residual_gap, so that 主 agent 可融合。
23. As a 主 agent, I want 按影响排序派发多个 unparsed 子代理, so that standard/deep 并行模型可复用。
24. As a 主 agent, I want 融合时把补读结论降级写入 narrative 与 open_questions, so that 不与 analyzed unit 混淆。
25. As a 安全审查者, I want 补读只使用只读工具且不执行目标仓构建/安装, so that 分析不污染被分析仓库。
26. As a 多语言仓库用户, I want 次要语言 unparsed 也可走同一补读 pass, so that 盲区处理一致。
27. As a quick/standard/deep 用户, I want 各模式有不同的补读预算上限, so that 深度与成本可控。
28. As a 竞品/对比模式用户, I want 两个仓库各自跑 unparsed 补读, so that 对比仍证据优先。
29. As a 文档作者, I want analysis-guide / evidence-first-v2 同步更新 Unsupported 语义, so that 「声明」与「补读」不再矛盾。
30. As an AFK agent, I want 本 issue 达到 ready-for-agent 且 seams 清晰, so that 可直接改 skill 文案与可选 gate 而不重开调研。

## Implementation Decisions

### 行为契约（必须）

- **触发条件**：`coverage-units.json` 中存在 classification=core 的模块，且 `unparsed` 列表中有属于该模块 path_globs 的文件。
- **强制动作**：进入 **Unparsed File Read Pass**，不得仅追加 Unsupported 列表后结束分析。
- **执行者**：优先 subagent；无 subagent → 主 agent 串行，Evidence Plan 记录 `unparsed_read_pass.parallelism: active|degraded`（可与模块分析 parallelism 字段并列，勿混用语义）。
- **工具白名单（基线只读）**：`rg`/`grep`、`find`、`wc`、文件读取类工具。可用 `git` 只读查询。  
  **禁止**：安装依赖、启动服务、用正则生成 `coverage-units` 分母、修改目标仓源码、把 unparsed 文件静默移出 `unparsed`。
- **选样优先级（固定）**：
  1. 入口/编排（如 `main`/`App`）
  2. 主用户路径 UI（上传/预览/导出控件）
  3. 被 Matrix 跨模块依赖点名但 unparsed 的文件
  4. 影响批判性评价的风险路径
  5. 其余 SEO/debug/example 按预算浅读或 skip_reason
- **模式预算建议**：
  - quick：全局最多 N 个高影响 unparsed 文件（实现时在 budgets 或 skill 写死具体数字，建议 3–5）
  - standard：每个 core 模块覆盖「主路径相关」unparsed 子集；其余写 skip_reason
  - deep：提高补读比例，但仍允许预算内 skip 并记录原因
- **产物约定（可审计）**：在 `$WORK_DIR` 写入其一或组合：
  - `unparsed-file-reviews/*.md` 或 `unparsed-file-reviews.json`
  - 和/或 `module-evidence/{module}.json` 新增可选字段，例如 `unparsed_manual_reads: [{ path, anchors, observation, confidence, tools_used, residual_gap }]`
  - Evidence Plan 增加「Unparsed File Read Pass」节：分工、文件列表、产物路径、预算
- **报告语义**：
  - 仍须逐路径声明 core unparsed 为 Unsupported Area（gate `core-unparsed-areas` 保持）
  - 新增「已补读但非枚举单元」分层：可引用锚点，confidence=`manual-read`
  - 未补读文件必须保留在 Unsupported，并写预算/优先级 skip 原因
- **与 parse-quality 关系**：**补读不提升 parse_rate，不豁免 parse-quality**。若未来要改阈值，另开 issue。
- **与关键单元覆盖率关系**：补读 **不** 把文件计为 `status: analyzed` unit（因为没有 unit id）；覆盖率分母逻辑不变。
- **与 multi-agent 验收关系**：unparsed 子代理是**额外 pass**；不能替代 module-evidence 的 standard/deep `parallelism: active` 要求，但可计入「真实多子代理执行」的补充证据。

### 文档/skill 修改面

- 更新 skill 工作流：Phase 2 之后 / Phase 6–7 之间插入或并入明确步骤
- 更新 `evidence-first-v2.md` Unsupported Area 模板：从「只声明」扩展为「声明 + 强制补读 pass + residual」
- 更新 `module-analysis-guide.md`：跨模块依赖指向 unparsed 文件时必须触发补读
- 更新真实UAT规则：检查补读产物是否存在（当目标仓 core unparsed 非空时）
- README/中文文档用一句话澄清：Unsupported ≠ 不分析

### 可选机器门（Seam B，推荐做但可第二 PR）

- 新增 gate check（例如 `unparsed-manual-review`）：
  - 若 core unparsed 非空，则要求 Evidence Plan 或 `unparsed-file-reviews*` 或 Matrix 字段存在补读记录
  - 失败 reasons 明确「只声明 Unsupported 未执行补读 pass」
- **不**改变 `minParseRate` / `maxCoreUnparsedRate` 默认值

### 原型字段形状（决策精炼，非可运行代码）

```json
{
  "unparsed_manual_reads": [
    {
      "path": "src/App.tsx",
      "tools_used": ["rg", "wc", "read"],
      "anchors": ["src/App.tsx:29", "src/App.tsx:198"],
      "observation": "AppContent 组装 useAppState/useImageProcessor/useRouter，上传后 processImage，切片就绪后导航 /split。",
      "confidence": "manual-read",
      "residual_gap": "无 enumerator unit；未做全文件逐函数覆盖"
    }
  ]
}
```

## Testing Decisions

### 什么是好测试

- 只断言**外部行为与产物**，不测内部 helper 调用顺序。
- 不依赖真实 LLM 输出；用 fixture 工件模拟 unparsed 列表与补读记录。

### 模块与 seams

1. **Seam A（主）— skill/references 契约**  
   - 以文档/技能契约 + UAT checklist 验收「必须补读」行为。  
   - 实现 PR 应能在 skill 文本中定位触发条件、工具白名单、产物路径、与 parse-quality 边界。

2. **Seam B（可选）— gate**  
   - `node:test` 扩展：  
     - core unparsed 非空且无补读记录 → 新 check fail  
     - 有 `unparsed-file-reviews` 或 Matrix 字段 → pass  
     - 有补读记录仍不改变 parse-quality 失败（若 parse_rate 低）

3. **Seam C — 真实UAT回归测试**  
   - 对 `/tmp/Long_screenshot_splitting_tool` 独立 `codex exec`：当 unparsed 含 `src/App.tsx` 等时，输出目录必须出现补读产物，且 report 对 App/上传/导出有 manual-read 锚点叙述，而不是仅路径列表。

### 既有 prior art

- `test/gate.test.js`：`core-unparsed-areas`、`parse-quality`、`parallelism-execution`
- `docs/specs/v2.1-codex-exec-uat.md`：真实UAT回归测试
- `docs/specs/v2.0-multi-agent-acceptance.md`：子代理分工/产物/融合记录口径
- v2.1-human 证据：展示「仅 Unsupported 列表」的现状痛点

## Out of Scope

- 用正则/启发式重写 enumerator，把 TSX 强行变成 parsed units
- 因手工补读自动 `allowed_to_synthesize: true` 或降低 parse-quality 阈值
- 把 unparsed 补读计为 key-unit coverage 的 analyzed 百分比
- 修改目标仓库源码以「更好解析」
- 完整实现 Issue #11（v2.2 standard/deep 工具规则重构）；本票可与之协调但独立可交付
- 引入必须联网的第二分析服务（DeepWiki 等）

## Further Notes

### 背景事实（来自 v2.1-human 实测）

- `parse_rate ≈ 48%`，core unparsed 含 `App.tsx`、大量 components、部分 hooks/utils
- hooks/utils/worker 主链可分析；UI 编排文件 unparsed 导致「主路径可见但不可计单元」
- 用户确认问题后要求：**遇到这些情况就直接派子代理用 rg/find/wc 等工具阅读这些文件**

### 测试 Seams 确认（本 spec 采用）

| Seam | 是否本票默认范围 | 说明 |
|---|---|---|
| A skill/references 契约 | **是** | 最高产品 seam |
| B gate `unparsed-manual-review` | **推荐，可同 PR 或紧随** | 机器强制「必须补读」 |
| C 真实UAT回归测试条款 | **是** | 用 Long_screenshot 回归 |

### 与现有术语对齐

- **unparsed**：enumerator 未解析出单元的文件  
- **Unsupported Area**：报告对未充分覆盖/未解析区域的声明  
- **manual-read**：本票新增置信度档，表示基线工具补读，**不等于** analyzed unit  
- **Unparsed File Read Pass**：本票新增强制步骤名称

### 建议实现顺序

1. 改 SKILL + references 文案与模板  
2. （可选）gate check + 单测  
3. 更新真实UAT规则与一次真实UAT回归测试证据目录  
4. README 一句话语义澄清

