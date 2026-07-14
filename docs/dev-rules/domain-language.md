# 领域文档规则

本仓库采用 single-context 领域文档布局。

## 探索前读取

- 根目录 `CONTEXT.md`
- 与当前工作相关的 `docs/adr/`

文件不存在时静默继续，不把缺少领域文档本身当作 blocker，也不提前创建空文档。领域术语或架构决策真正被澄清后，再由相应建模流程按需生成。

## 词汇约束

Issue 标题、规格、测试名、架构提案以及协作/质量门术语优先使用 `CONTEXT.md` 已定义术语。 Delivery Task、Task Quality Gates、Worker、Judge、Orchestrator、Blindspot Pass、Deviations、Boundary Check 等流程词以 `CONTEXT.md` 为准；流程正文在 `docs/dev-rules/task-quality-gates/` 与 `dual-agent-review/`，不在本文件展开。

需要的新概念若不在 glossary 中，应先判断它是语言漂移还是实际领域缺口。

## ADR 冲突

若新方案与既有 ADR 冲突，必须显式指出冲突和重新开启决策的理由，不得静默覆盖。

## 布局

```text
/
├── CONTEXT.md
├── docs/adr/
└── src/
```
