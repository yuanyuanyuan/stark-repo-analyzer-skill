# Glossary — `repo-analyzer` skill

> 基于 R4 全部决策（Q1~Q10）整理的术语表。
> 维护规则：新词进入时按字母顺序插入；ADR 链接用相对路径。

---

## A

### Adapter

运行时适配器。`ask_user()` 抽象的具体实现，分 3 种：

- `ClaudeCodeAskAdapter`（调用 `AskUserQuestion`）
- `CodexAskAdapter`（调用 `codex ask`）
- `CursorAskAdapter`（退化为 `questions.json` 写入）

详见 ADR-0003。

### Adaptive Slicing（自适应切片）

Phase-2a 识别 Repo 类型后，按 `config/repo-types.yaml` 动态生成 7-12 维切片清单。

与「写死 12 维」相对。详见 ADR-0002。

### Audience Template（受众模板）

三变体之一：

- `tech-lead.tmpl.md`（架构 / 风险 / 复现）
- `business.tmpl.md`（价值 / 流程 / 部署）
- `learning.tmpl.md`（动机 / 入口 / 复现路径）

详见 ADR-0006。

---

## B

### Backward-Compatible Selector

模板与数据分离后，`--mode` 切换无需重跑数据采集阶段。详见 ADR-0006 / ADR-0008。

---

## C

### Coverage Gate（覆盖率门控）

`tree-sitter` 解析 API 名 + `grep` 抓 draft 符号名 → 交集比例 ≥ 阈值。

| Tier | 阈值 |
|------|------|
| core | ≥ 80% |
| important | ≥ 50% |
| minor | ≥ 20% |

详见 ADR-0005。

### Cross-Ref Pass（交叉审稿）

阶段五内自检 + 阶段六独立 cross-ref 的双层质检。详见 ADR-0004。

### CQRS-flavored（命令查询责任分离）

模板 + renderer（命令）与数据层 drafts（查询）的分离。在本 skill 中以「视图与数据分离」形式体现，详见 ADR-0006。

---

## D

### Data Layer / View Layer（数据层 / 视图层）

- **数据层**：`analysis/drafts/`、`02a-repo-type.yaml` 等，永远不改结构
- **视图层**：`templates/*.tmpl.md` + `render_report.py`

详见 ADR-0006。

---

## F

### Flag Tier（开关档）

- **真开关**（runtime argv 透传）：`--offline` / `--mode` / `--no-question` / `--max-discovery-rounds` / `--workspace`
- **内部变量**（`~/.config/repo-analyzer/defaults.yaml`）：`target_coverage.*` / `sla_budget.*`

详见 ADR-0008。

---

## I

### IGNORE_GLOB

`repomix --ignore` 模式，过滤 `*.lock` / `.claude/**` / 二进制等。

**注意**：阶段一被砍后（ADR-0001），本配置在 Phase-2a 不再使用；`tree-sitter` 解析不受 IGNORE_GLOB 影响。

---

## M

### Manifest Card（5KB 名片）

Phase-2a 产出的 ≤ 5KB 项目元信息快查清单（不压缩，源文件直读）。详见 ADR-0001。

### Mode（受众档）

- `interactive` —— 默认，阶段三发起 `ask_user()` 4 道题
- `autonomous` —— 跳过提问，读 `defaults.yaml`

详见 ADR-0003 / ADR-0008。

---

## P

### Phase-2a

阶段二开始前的轻量级探测，同时承担：

1. Repo 类型识别（产出 `02a-repo-type.yaml`）
2. 5KB 名片生成（产出 `02a-manifest-card.md`）

详见 ADR-0002 / ADR-0001。

### Pitch（电梯演讲）

三档稿件：

- 短版本（< 30 字）
- 中版本（~100 字，用于 README）
- 长版本（≥ 200 字，用于企业 deck）

详见 ADR-0010。

---

## R

### Repo Type Tagger

Phase-2a 识别的 6 种 Repo 类型之一：

- `web-fullstack`
- `single-lang-CLI`
- `single-lang-lib`
- `monorepo`
- `embedded-kernel`
- `multi-agent-config`

详见 ADR-0002。

### Repo-Types YAML

`config/repo-types.yaml` —— Repo 类型 → 切片模板映射表，versioning 与 skill 版本绑定。

详见 ADR-0002。

### Resume Token

`analysis/.resume-token` —— skill 中断后记录 checkpoint，下次 `--resume` 从中断点继续。

详见 ADR-0009。

### Round（grilling 轮次）

Round 1（战略层）/ Round 2（战术层）/ Round 3（SLA + 风险）/ Round 4（用户答 Q1-Q10）/ Round 5（用户答 Q1-Q5，落地为 ADR-0011~0015）。

---

## 新增 R5 词条（2026-07-06 同日追加）

### Acceptance Script（验收脚本）

`analysis/acceptance/check.sh` —— 阶段十 §10 验收脚本入口。共 5 个子脚本（`01-grep.sh` / `02-ast.sh` / `03-schema.sh` / `04-link.sh` / `05-mermaid-judge.sh`）。≥ 80% PASS 算通过。

详见 ADR-0011。

### AST Assertion

tree-sitter 解析 draft 抽出名词短语或 API 名做断言（跨章术语一致、关键 API 数量匹配）。第 4-5 条验收。

详见 ADR-0011。

### `extends:` Chain（继承链）

`~/.config/repo-analyzer/defaults.yaml` 中通过 `extends:` 数组递归加载父配置；dict 浅合并、scalar 覆盖、循环引用检测。

详见 ADR-0012。

### `env_var_override`（环境变量覆盖）

skill 启动时扫描 `REPO_ANALYZER_<UPPER_SNAKE_CASE>` 环境变量，覆盖 `defaults.yaml` 中对应字段。优先级最高 > CLI argv > 默认。

详见 ADR-0012。

### Chunked Tree-sitter

tree-sitter 解析按 5MB 切文件 + 单核串行 + 多语言按扩展名分发。`config/tree-sitter.yaml` 配置；3 仓库 benchmark 在 `docs/benchmarks/tree-sitter-baseline.md`。

详见 ADR-0014。

### Failed Module Section（§9 未完成模块明细）

报告末尾新增可选章节。`STATE_REPORT.md` 中 `failed_modules[]` 字段非空时才渲染；条件 block 由 `render_report.py` 处理。

详见 ADR-0015。

### Last-Session Pref（偏好持久化）

`~/.config/repo-analyzer/last-session.json` —— 记录上次会话使用的 flag（带 `--save-pref` 才保存）；30 天未用丢弃；启动加 `--use-last-pref` 时合并到 argv。

详见 ADR-0012。

### LLM-judge

第二 LLM（haiku-4.5 暂定）读 draft 后打 0-10 分，用于验收条目 11-13（内容准确度 / 受众匹配度 / 受众区分度）。详见 ADR-0011。

### Repo-Analyzer ↔ Graphify Decoupled（完全解耦）

repo-analyzer 不读不写 `graphify-out/`。`~/.config/repo-analyzer/defaults.yaml` 中 `graphify.compatible_mode` 字段当前为占位（不实现）。

详见 ADR-0013。

### STATE_REPORT.failed_modules[]

`analysis/STATE_REPORT.md` YAML frontmatter 中 `failed_modules[]` 字段，必填（即使 `[]`）。每个元素含 `id` / `tier` / `attempts` / `last_error` / `last_error_at` / `partial_output` / `suggested_recovery`。

详见 ADR-0009 / ADR-0015。

> **维护规约补充**：
> 5. R5 新词进入"新增 R5 词条"段独立列出，不混入字母段（避免破坏已有版本兼容性）
> 6. ADR-0011~0015 落地后本段即冻结，后续 Round 在段尾追加新"X 词条"段

---

## S

### SLA Budget（SLA 预算）

激进档：30 分钟 / 500K tokens / 3 次失败回退。详见 ADR-0007。

### STATE_REPORT.md

预算耗尽兜底产物，列出已完成阶段 + 失败模块 + 下次重试入口。详见 ADR-0009。

### Storyline Module

阶段四生成的模块顺序锚点（`05-module-ids.yaml` 中 `storyline_position` 字段），阶段五 sub-agent 必须按此顺序排列 draft。详见 ADR-0004。

### Sub-agent Mode

阶段五按模块清单并行起 N 个 sub-agent，每个只看自己的模块切片 + 自己上下文。

详见 ADR-0004。

---

## T

### Tier Coverage

模块分档与阈值映射：核心 ≥ 80% / 重要 ≥ 50% / 次要 ≥ 20%。详见 ADR-0005。

### TL;DR Hook（钩子句）

报告 §0 第一句，要求陌生读者 5 秒抓住项目是什么。详见 ADR-0010。

### Transition Block

模板中 `{{ transition_block }}` 占位，由阶段七 1 个 sub-agent 填过渡句。详见 ADR-0006。

### Tree-sitter Symbols

`tree-sitter parse` 产出的源码对外 API 名清单，用于覆盖率门控的「expected」侧。详见 ADR-0005。

### Trust Boundary（信任边界）

阶段一被砍后（ADR-0001），信号源单一：12 维精切 + tree-sitter 解析 = 真相源；不再有「low-confidence overview」。

---

## W

### Wikilink ID Map

`analysis/05-module-ids.yaml` —— 锁定 `[[module_xxx]]` 命名空间。详见 ADR-0004。

### Wikilink Cross-Check

阶段五自检时 `grep` 抓所有 `[[module_xxx]]`，与 ID map 对比。详见 ADR-0004。

---

## Y

### YAML Config Set

`config/repo-types.yaml` + `~/.config/repo-analyzer/defaults.yaml` 等等。详见 ADR-0002 / ADR-0008。

---

> **维护规约**：
> 1. 新词按字母顺序插入对应字母段；不允许多字母段混合
> 2. 每个术语引用至少 1 个 ADR 编号（`详见 ADR-XXXX`）
> 3. R4 决策新词在前，R1-3 残留词后续补全
> 4. 表格、缩写、定义统一中文、键名英文
