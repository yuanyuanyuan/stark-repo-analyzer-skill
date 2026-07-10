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
