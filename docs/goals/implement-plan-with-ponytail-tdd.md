# 使用 Ponytail + TDD 实现 PLAN.md

Goal Prompt:

```markdown
目标:
使用 $ponytail 和 $tdd 实现 /Users/chuzu/projests/stark-repo-analyzer-skill/references/PLAN.md，把 PLAN.md 中的仓库分析流程落成当前仓库里可运行、可测试、可验收的最小可用 skill。

真实意图:
用户真正要的是让 PLAN.md 不再停留在方案文档，而是变成一个能被小白用户实际调用、能分析真实仓库、并能产出可信分析结果的 skill。最大误伤点是做成庞大的通用分析平台，或者只写包装文档却没有真实可运行证据。

战略结果:
完成后，stark-repo-analyzer-skill 应具备一条清晰的实现路径：按 PLAN.md 执行仓库分析，关键行为有公共接口测试覆盖，并通过 https://github.com/adminhuan/smart-search-mcp 的真实验收案例。实现必须容易运行、容易检查，并且不能在缺少证据时声称完成。

决策标准:
- 优先复用当前仓库已有风格、文件结构、命令和 skill 约定，而不是新增抽象。
- 执行 $ponytail full：先判断代码是否真的需要存在，再找本仓库已有模式，再用标准库/原生能力，再用已安装依赖，最后才写最少的新代码。
- 执行 $tdd：用纵向 red-green 切片推进。一次只写一个通过公共接口验证行为的失败测试，再写最小实现让它通过，然后继续下一片。
- 通过标准是可观察行为正确，不是内部函数形状符合预期。
- 如果一个更简单的实现已经完整满足 PLAN.md，就选择简单实现，并明确跳过 speculative extensibility。

证据标准:
- 本地证据：PLAN.md、现有项目文件、AGENTS.md 指令、graphify-out/graph.json 存在时的 graphify query 输出、当前测试和脚本。
- 测试证据：每个非平凡行为都必须有公共接口测试或最小可运行 self-check。期望值必须来自独立字面量、手算示例或明确规格，不能用实现逻辑重新计算。
- 运行证据：最终命令在当前仓库真实运行通过。
- 终验收证据：新建一个小白用户子代理，作为第一次使用该 skill 的用户，使用它完成对 https://github.com/adminhuan/smart-search-mcp 的分析；再新建一个裁决代理，对整个分析过程、AI agent 的反应和分析结果打分。满分 10 分，9.5 分以上才算通过。

范围:
- 阅读 PLAN.md，只实现让该计划在当前仓库中成为可执行 skill 所需的行为。
- 只新增或修改 skill、测试、脚本和用户说明中必要的最小文件。
- 确定性的、不需要智力判断的环节必须用代码实现。
- 只有分析、综合、优先级判断、评分等需要智力判断的环节才调用 LLM/agent。
- 最终交付必须符合当前项目布局和本地 agent skill 约定。

非目标:
- 不做通用多仓库 SaaS、队列系统、Dashboard 或插件框架，除非 PLAN.md 已明确要求且没有更小实现能满足。
- 不新增依赖，除非标准库、原生工具和现有依赖都无法合理完成。
- 不重写无关项目结构，不清理无关死代码，不格式化未触碰文件。
- 不把 smart-search-mcp 分析验收当成可选项；它是最终通过条件的一部分。

优先阅读上下文:
- /Users/chuzu/projests/stark-repo-analyzer-skill/AGENTS.md 或当前会话提供的 AGENTS.md 指令。
- /Users/chuzu/projests/stark-repo-analyzer-skill/references/PLAN.md。
- 如果存在 graphify-out/wiki/index.md，先用它做广义导航。
- 如果存在 graphify-out/graph.json，先运行：`graphify query "How should PLAN.md be implemented as a skill in this repository?"`，再做原始源码浏览。
- 用 `rg --files` 查看现有仓库文件，重点看 skill 元数据、scripts、tests、README/docs 和现有命令入口。

约束:
- 用 $ponytail full 控制实现规模和依赖选择。
- 用 $tdd 覆盖非平凡行为：一个失败测试、最小通过实现、重复推进。
- 本地搜索优先使用 `rg` / `rg --files`。
- 手工编辑文件使用 `apply_patch`。
- 不回滚用户已有改动。
- 修改代码后，如果 graphify 可用，按项目指令运行 `graphify update .`。
- 报告中不得暴露密钥、token、无关隐私数据，或超过必要范围的本地路径信息。

执行策略:
1. 先做 inventory：
   - 确认该 skill 应暴露的当前公共接口。
   - 确认已有测试或脚本。
   - 找到映射 PLAN.md 的最小实现面。
2. TDD 纵向切片：
   - 第 1 片应证明主命令/公共接口能接收目标仓库，并创建预期分析输出位置或计划产物。
   - 后续每片只在 PLAN.md 需要时增加一个可观察行为。
   - 禁止先一次性写完全部测试再写全部实现。
3. Ponytail 实现：
   - 复用现有项目模式和已安装工具。
   - 确定性步骤放进脚本/代码。
   - 只在判断型分析和最终评分处使用 LLM/subagent。
4. 最终验收：
   - 新建/运行小白用户子代理场景：该子代理表现为第一次使用这个 skill 的用户，并用它分析 https://github.com/adminhuan/smart-search-mcp。
   - 新建/运行裁决代理场景：裁决代理检查完整过程、agent 反应、命令证据、生成的分析结果和使用体验。
   - 裁决代理必须按 10 分制评分，至少覆盖：任务完成度、小白用户易用性、仓库分析正确性、证据质量、克制/简单性、失败处理。
   - 只有最终分数 >= 9.5/10 才算通过；如果低于 9.5，针对最高影响扣分项再做一轮 TDD 修复，并重新跑裁决验收。

检查点:
- Checkpoint 1：inventory 报告列出受影响文件、当前公共接口、测试命令和最小切片方案。
- Checkpoint 2：第一个 red-green TDD 切片通过，并证明主公共接口可用。
- Checkpoint 3：PLAN.md 要求的确定性流程已用最小代码实现，非平凡逻辑有测试。
- Checkpoint 4：只在必要处更新用户可见 skill 说明。
- Checkpoint 5：本地验证命令通过。
- Checkpoint 6：小白用户子代理完成 smart-search-mcp 分析。
- Checkpoint 7：裁决代理给出 >= 9.5/10 的分数；否则标记为未完成，并列出最高影响差距。

验证:
- 展示实际运行的测试/检查命令和结果。
- 展示 smart-search-mcp 终验收运行生成的分析产物路径。
- 包含小白用户子代理的简短过程摘要或 action summary。
- 包含裁决代理的评分 rubric 和分数。
- 包含 `graphify update .` 结果，或说明 graphify 不可用的原因。
- 给出最终 pass/fail：只有测试/检查通过且裁决分数 >= 9.5/10 才能标记 pass。

暂停条件:
- 如果 PLAN.md 与当前仓库架构冲突，且需要大规模重写才能继续，暂停并询问用户。
- 删除文件、修改发布身份、引入外部付费服务、commit/push 前必须暂停。
- 如果 smart-search-mcp 无法访问或 clone，在合理重试后仍失败，报告阻塞原因，不得伪造验收。
- 如果两轮聚焦修复后裁决分仍低于 9.5，暂停并报告剩余差距，不得声称完成。

最终报告:
- 汇总修改了哪些文件以及原因。
- 汇总 TDD 切片：失败测试、最小实现、通过证据。
- 汇总 Ponytail 下跳过了哪些复杂度，以及什么时候才需要补。
- 提供 smart-search-mcp 分析产物路径，并摘录一小段能证明 skill 有效工作的结果。
- 提供小白用户子代理结果、裁决代理 rubric、裁决分数，以及是否通过 >= 9.5/10 验收门槛。
```

Loop Prompt:

```markdown
时间参数:
手动：贴入上一轮最终报告、diff 摘要、测试输出、smart-search-mcp 分析产物路径、小白用户子代理结果和裁决代理评分后继续。若要定时或后台循环，需要另行明确授权创建 automation。

循环使命:
持续推进 PLAN.md 实现，直到该 skill 真实可用、实现足够克制、测试证据充分，并通过小白用户子代理 + 裁决代理的真实终验收，裁决分数 >= 9.5/10。

循环状态:
- 原始目标：使用 $ponytail 和 $tdd 实现 /Users/chuzu/projests/stark-repo-analyzer-skill/references/PLAN.md。
- 必须验收的目标仓库：https://github.com/adminhuan/smart-search-mcp。
- 必须通过的终验收门槛：小白用户子代理完成分析；裁决代理对过程、agent 反应和分析结果评分 >= 9.5/10。
- 当前轮次：从上一轮报告填写。
- 已关闭证据：填写已通过的测试/检查。
- 开放差距：填写失败项、裁决扣分项、缺失行为或不清晰的使用体验。

上一轮结果检查:
- 上一轮最终报告。
- Git diff 或 changed-file list。
- 测试输出和命令日志。
- 已生成的分析产物，尤其是 smart-search-mcp 报告。
- 小白用户子代理 action summary。
- 裁决代理 rubric、分数和扣分原因。
- 用户在上一轮之后给出的反馈。

证据复盘:
- “agent 说已完成”不算证据，除非有文件、命令输出或分析产物支撑。
- 分清结构检查、本地自动化测试、真实目标仓库验收和裁决评分。
- 确认每个非平凡行为仍然通过公共接口测试或最小可运行检查覆盖。
- 确认 $ponytail 被遵守：没有 speculative abstraction、没有不必要依赖、没有无关重构。
- 确认确定性流程已代码化，LLM/subagent 只用于判断型工作。

差距诊断:
- 优先排序会阻止裁决分达到 9.5 的差距。
- 其次排序失败测试或缺失的 PLAN.md 行为。
- 再排序小白用户困惑点或缺失说明。
- 最后只处理能真实降低复杂度的清理/重构机会。

本轮动作:
- 只选择最高价值的一个差距处理。
- 如果是代码行为，做一个 TDD 纵向切片：red test、minimal green implementation、必要时在 green 状态做小重构。
- 如果是说明或 UX 问题，做最小文档/命令调整，并重跑受影响的验收路径。
- 如果是裁决或小白验收问题，只在修复后重跑最小必要场景。

验证增量:
- 说明本轮比上一轮多证明了什么。
- 重跑最窄相关测试，以及被改动影响的端到端检查。
- 只有当改动可能影响最终分数时，才重跑小白用户和裁决代理验收。

循环护栏:
- 如果裁决分仍低于 9.5，最多做两轮聚焦修复后升级给用户。
- 不把范围扩大到 PLAN.md 和 smart-search-mcp 终验收之外。
- 不新增依赖或框架，除非上一轮证据证明最小实现无法通过。
- 未经明确授权，不删除、发布、commit 或 push。

继续协议:
- 每轮结尾必须给出 Done / Continue / Pause 之一。
- Done 需要测试/检查通过、smart-search-mcp 分析产物已生成、小白用户子代理已完成、裁决分数 >= 9.5/10。
- Continue 需要一个具体的下一最高价值差距和验证计划。
- Pause 需要说明阻塞、缺少权限、目标仓库不可访问或连续低于分数门槛。

停止 / 升级条件:
- 如果目标仓库访问失败，无法诚实运行终验收，则停止。
- 如果所需改动意味着 PLAN.md 范围外的大规模重写，则停止。
- 如果需要密钥、隐私数据、破坏性命令、发布或 git 历史变更，则停止。
- 如果两轮聚焦修复后裁决分仍低于 9.5，则升级给用户。

下一轮 LOOP 包:
每轮结束时输出：
- Status: Done / Continue / Pause。
- 当前分数，以及是否通过 >= 9.5。
- 已关闭证据。
- 按影响排序的剩余差距。
- 下一步唯一动作。
- 下一轮要运行的命令/测试。
- 需要用户决定的事项。
```
