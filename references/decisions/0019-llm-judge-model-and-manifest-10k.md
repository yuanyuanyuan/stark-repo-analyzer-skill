---
Status: Accepted
Date: 2026-07-08
Round: 6 (T06/T07)
---

# ADR-0019 LLM-judge 模型默认置空与项目名片扩容至 10KB

## Context

### T06: LLM-judge 模型默认问题

`llm_judge.py` 的 `DEFAULT_MODEL` 硬编码为 `"haiku-4.5"`。问题：
1. 用户环境没有 `haiku-4.5` 模型时，`codex exec --model haiku-4.5` 直接失败。
2. 失败信息只有 stderr 全文，没有提取关键错误摘要。
3. 用户不知道实际使用了哪个模型。

### T07: 项目名片过小

`manifest-card.md` 限制为 5KB，只能放 README 前 1500 字符和少量元数据。问题：
1. 大型项目的 README 前 1500 字符不足以覆盖核心信息。
2. 缺少 Git 远程地址、代码行数、许可证、依赖摘要、顶层目录、运行命令等关键信息。
3. 项目名片是 agent 和用户快速了解项目的入口，信息不足导致后续分析质量下降。

## Decision

### T06: LLM-judge 修复

- `DEFAULT_MODEL` 从 `"haiku-4.5"` 改为 `""`（空字符串）。
- `judge()` 函数在 model 为空时不传 `--model` 参数，让 `codex exec` 使用其内置默认模型。
- 新增 `_extract_error_summary(stderr, max_len=200)` 提取 stderr 最后一行非空行作为错误摘要。
- 失败输出包含 `[model={model_label}]` 和 stderr 摘要。

### T07: 项目名片扩容至 10KB

- 卡片大小限制从 5KB 提升到 10KB（`[:10_000]`）。
- README 摘要从 1500 字符扩展到 4000 字符。
- 标题从 "5KB 项目名片" 改为 "10KB 项目名片"。
- 新增 8 个信息区块：
  1. **Git 信息** — HEAD short hash、提交日期、作者、远程 URL
  2. **代码规模** — 估算总行数、二进制文件数
  3. **许可证** — 文件名检测（LICENSE/LICENCE/COPYING）
  4. **顶层目录** — 一级目录列表
  5. **依赖摘要** — 检测 package.json/pyproject.toml/go.mod/Cargo.toml 等
  6. **运行命令** — 从 pyproject.toml [project.scripts] / Makefile / package.json scripts 提取
  7. **顶层文件快照** — 最多 60 个顶层文件
  8. **README 前 30 行** — 扩展到 4000 字符

## Alternatives

### T06

- **M1. 保留 haiku-4.5 默认** —— 不可用环境直接失败。
- **M2. 改为空字符串 + codex 内置默认（本 ADR）** —— 最大兼容性。

### T07

- **M1. 保持 5KB** —— 信息不足。
- **M2. 扩容到 10KB + 新增 8 个区块（本 ADR）** —— agent 获得更丰富上下文。

## Consequences

- `llm_judge.py` 的 `--model` 参数变为可选，不传时由 codex 决定。
- 失败时的错误信息更简洁（`[model=...]` + 摘要），不再输出完整 stderr。
- `analyzer_metadata.py` 新增 8 个辅助函数（`_git_head_info`、`_git_remote_url`、`_estimate_loc`、`_binary_file_count`、`_dependency_summary`、`_top_level_dirs`、`_license_detect`、`_file_size_stats`）。
- 项目名片大小翻倍，但仍在合理范围内（10KB < LLM context 限制）。
- 验收脚本中对项目名片大小的检查从 5KB 调整为 10KB。

## Linked

- ADR-0004（Token 预算 500K，项目名片是 agent 主要上下文来源）
- ADR-0011（验收脚本中项目名片大小检查）
- T06/T07 任务说明
