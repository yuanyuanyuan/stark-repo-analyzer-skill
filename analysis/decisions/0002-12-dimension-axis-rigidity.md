# ADR-0002 12 维切片轴线的刚性问题

## Status

Proposed (grilling 进行中,Round 1)

## Context

PLAN.md §3 阶段二定义 12 维切片:`01-frontend.xml / 02-backend.xml / 03-database.xml / 04-tests.xml / 05-agent-config.xml / 06-dependencies.xml / 07-... / 12-history-hotspot.txt`。

这些维度是**按 Web 全栈应用隐式建模的**:前端、后端、数据库、依赖、测试、历史 hot-spot。这种切法在面对以下 repo 类型时立刻出问题:

1. **单语言 CLI / 库**:Go CLI、Python SDK、Rust crate——`01-frontend.xml` 与 `02-backend.xml` 严重重叠或其中一个完全空。
2. **Monorepo**:`vercel/turborepo`、`pnpm` 仓库——`frontend` 命中范围过宽、跨包通信成为第 13 维(缺失)。
3. **嵌入式 / 内核**:c/c++ 仓库——`database` 几乎不存在,缺失"中断处理 / 驱动 / IPC"维度。
4. **AI agent 配置**:仓库内有 `.claude/**` 同时又有 `.cursor/**` 又有 `.codex/**`,5 维度不足以装得下。

更关键:阶段三"项目特征识别"是在切片**之后**跑的,识别的结果**无法反馈**到切片策略——这是一个**有向无环、超时 hardcoded**的设计。

## Decision (提议)

**改为自适应切片模式:阶段三先识别 Repo 类型,阶段二动态生成切片清单。**

具体规则:
1. 阶段二(新版本)先执行一次**轻量级 Phase-2a**:基于 `package.json` / `Cargo.toml` / `go.mod` / `pyproject.toml` / 顶层 `README.md` 识别 Repo 主类型(monorepo / single-lang-CLI / single-lang-lib / web-fullstack / embedded / kernel)。
2. 根据类型 mapping 到**切片模板**:
   - web-fullstack → 12 维(原模板)
   - single-lang-CLI → 7 维(outer / type / API 表面 / 配置 / 错误处理 / 依赖 / 测试)
   - monorepo → 8 维(顶层 / 包列表 / 包间依赖图 / 各包模块定义 / 公共代码 / 构建脚本 / 测试 / 变更热点)
   - embedded / kernel → 7 维(子系统划分 / 启动流程 / IPC / 关键数据结构 / 错误处理 / 测试 / 提交热点)
3. 阶段三再以该切片清单作为输入,做"项目特征识别"。

## Alternatives Considered

- **B1. 12 维固定**:对所有 repo 跑同一套切片,空维度写"n/a"。简单但浪费 token、阶段三无法纠错。
- **B2. 自适应切片模式(本 ADR)** :多一个 Phase-2a 阶段,但下游更准确。
- **B3. 完全 free-form**:不预设维度,让阶段二自由生成。风险:不同 agent 输出维度不一,阶段六"交叉验证"算法失效。

## Consequences

- 阶段二从 1 步变 2 步,额外加一次 repomix 调用(轻量级,只取 manifest)。
- 阶段六交叉验证脚本需要参数化:按 repo 类型选择不同"必含字段集合"。
- 报告 §9 阶段七需要先取"识别类型"再选模板渲染。
- 切片数量从 12 变为 7-12,**数量不再稳定**,验收标准 §10 中"12 维切片索引"需要改成"N 维切片索引 + 类型 tag"。

## Open Questions

- [ ] 单次会话内是否允许"先识别 → 再切片"还是必须用分两次会话(避免上下文污染)?
- [ ] monorepo 类型下,12 维模板的 `06-dependencies.xml` 还需要吗?还是会与新维度"包间依赖图"重叠?

## Linked

- Q2(Round 1 第二问)
- 阶段二 §3
- 阶段六 §8 交叉验证清单
- 阶段七 §9 报告骨架 §9.1
