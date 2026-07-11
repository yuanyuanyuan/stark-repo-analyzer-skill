## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:

- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).



**## 响应语言**

- 简体中文(使用中文或者英文来思考，但是回复需要用中文,专业术语除外，输出落盘也需要中文。)

  


**## 核心原则**

- IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any tasks.

- 所有确定性的、不需要智力判断的环节，用代码实现。只有需要智力判断的环节，才调用大模型。

## Agent skills

### Issue tracker

工作项与 PRD 使用当前仓库的 GitHub Issues；外部 PR 不作为 triage 请求入口。详见 `docs/agents/issue-tracker.md`。

### Triage labels

使用 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix` 五个 canonical 状态标签。详见 `docs/agents/triage-labels.md`。

### Domain docs

采用 single-context 布局：根目录 `CONTEXT.md` 与全局 `docs/adr/`。详见 `docs/agents/domain.md`。

## 真实UAT回归测试

本仓库**真实UAT回归测试**（正式名称）默认指：**新开独立 `codex exec` 进程**，提示词要求**严格执行** `skills/repo-analyzer/SKILL.md`，对真实目标仓分析，并把工件输出到 `测试证据/` 下**新建**目录。

### 规则入口（dev-rules · 优先阅读）

- **Dev 规则目录（操作与分档 SSOT）**：[`dev-rules/`](dev-rules/)  
  - **真实UAT 总览与变更联动**：[`dev-rules/real-uat-regression/README.md`](dev-rules/real-uat-regression/README.md)  
  - **quick 档**：[`dev-rules/real-uat-regression/quick.md`](dev-rules/real-uat-regression/quick.md)  
  - **standard 档**：[`dev-rules/real-uat-regression/standard.md`](dev-rules/real-uat-regression/standard.md)  
  - **deep 档**：[`dev-rules/real-uat-regression/deep.md`](dev-rules/real-uat-regression/deep.md)
- **产品层定义（独立 exec / 过程 vs 产品分层）**：[`docs/specs/v2.1-codex-exec-uat.md`](docs/specs/v2.1-codex-exec-uat.md)
- **多子代理口径**（active/degraded）：[`docs/specs/v2.0-multi-agent-acceptance.md`](docs/specs/v2.0-multi-agent-acceptance.md)

### 硬口径摘要

- **正式名称**：**真实UAT回归测试**（标签：`real-uat-regression`）
- **三档必须分开跑、分开落盘**：quick / standard / deep（命令与检查清单见上列三文件）；禁止用一档结果冒充另一档。
- **不要**用同会话 docs-only 勾选、或仅主线程手写 `report.md`，替代「真实UAT回归测试」。
- 执行后在输出目录检查 `UAT_EXEC_SUMMARY.md` 与 gate 工件；gate 未放行时不得声称产品分析完整通过；`parallelism: degraded` 时不得声称 multi-agent 完整通过。

### 变更联动（强制）

当 **代码、skill、gate、需求/Issue/ticket** 发生会改变分析行为或验收语义的变更时，**必须同步更新** [`dev-rules/real-uat-regression/`](dev-rules/real-uat-regression/) 中的真实UAT回归规则（含受影响的 quick/standard/deep 档），并在 PR 中说明规则 diff 或「规则无影响」理由。禁止只改实现不改回归规则。

### 示例（完整提示词以对应 mode 规则文件为准）

```bash
# standard 示例；quick/deep 见 dev-rules/real-uat-regression/{quick,deep}.md
codex exec "严格执行 $(pwd)/skills/repo-analyzer/SKILL.md 分析 /tmp/Long_screenshot_splitting_tool ，输出报告到 $(pwd)/测试证据/real-uat-standard-$(date +%Y%m%d) 。模式必须为 standard。"
```

