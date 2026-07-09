---
Status: Accepted
Date: 2026-07-08
Round: 6 (T09)
---

# ADR-0017 运行时预检与 Agent 模式自动降级

## Context

T09 之前，`--agent-mode` 默认为 `deterministic`，用户需要显式指定 `--agent-mode codex` 才能启用 agent 模式。这导致：

1. 用户不知道有 agent 模式可用，默认跑 deterministic 就结束了。
2. 指定 `--agent-mode codex` 但本机未安装 `codex` CLI 时，在 agent 阶段才发现失败，浪费时间。
3. 没有统一的运行时预检，缺少 `git`/`npx`/`codex` 等工具时到中途才报错。

## Decision

**`--agent-mode` 默认改为 `codex`，新增 5 项运行时预检，codex 不可用时自动降级到 `deterministic`。**

### 预检 5 项

1. **git 可用** — `shutil.which("git")`，不可用直接 `SystemExit`。
2. **repomix (npx) 可用** — `shutil.which("npx")`，不可用直接 `SystemExit`。
3. **target 有效** — 本地路径存在或 git URL 格式合法，不可用直接 `SystemExit`。
4. **codex 可用**（仅当 `agent_mode == "codex"`）— 不可用时自动降级到 `deterministic`，设置 `args._agent_mode_degraded = True`。
5. **agent_command 已设置**（仅当 `agent_mode == "command"`）— 未设置直接 `SystemExit`。

### 自动降级

当预检发现 `codex` 不在 PATH 中时：
- `args.agent_mode` 从 `"codex"` 改为 `"deterministic"`
- `args._agent_mode_degraded` 设为 `True`
- `write_config_effective` 在 `config-effective.json` 中记录 `agent_mode_degraded` 字段
- 预检结果打印到 stderr，用户可见

### 默认值同步

`build_parser()` 和 `set_if_default()` 的 `agent_mode` 默认值同步改为 `"codex"`。

## Alternatives

- **M1. 保持 deterministic 默认** —— 用户不知道有 agent 模式可用。
- **M2. codex 默认但不降级** —— codex 不可用时直接报错，用户体验差。
- **M3. codex 默认 + 自动降级（本 ADR）** —— 用户默认得到最佳模式，不可用时静默降级。

## Consequences

- `preflight_check()` 函数从 `repo_analyzer.py` 提取到 `analyzer_preflight.py`，保持入口文件 < 200 行。
- `config-effective.json` 新增 `agent_mode_degraded` 字段。
- 测试环境需要安装 `fake_codex` 以 shadow 系统真实 codex，否则降级到 deterministic。
- SLA 报告和性能报告中的 `agent_mode` 字段反映降级后的实际值。

## Linked

- ADR-0016（输出目录结构变更，`config-effective.json` 路径更新）
- T09 任务说明
