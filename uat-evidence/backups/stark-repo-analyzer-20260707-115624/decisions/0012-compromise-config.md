---
Status: Accepted
Date: 2026-07-06
Round: 5 (R5-Q2)
---

# ADR-0012 妥协性配置三件套：env 覆盖 + `extends:` 继承 + 偏好持久化

## Context

ADR-0008 已经把开关分成：

- **5 真开关**：runtime argv 透传
- **5 内部变量**：`~/.config/repo-analyzer/defaults.yaml`

但还有一类**中间地带**"妥协性配置"——既不是用户显式 CLI 开关，也不是 skill 默认常量，而是**根据使用场景动态调整的边界配置**：

1. **环境变量覆盖**（CI 必须）：CI 跑时不能传 argv，但能用 `REPO_ANALYZER_SLA_BUDGET_MINUTES=60 env` 临时覆盖
2. **`extends:` 继承**：本地 `defaults.yaml` 继承团队共享 `defaults.team.yaml`，避免团队规范重复传
3. **会话间偏好持久化**：用户上次跑选了 `--mode business`、选了 `--no-question`，下次启动要不要默认沿用

## Decision

**三件齐做，分别落地**：

### 1. 环境变量覆盖（`env_var_override`）

读取规则：skill 启动时按 `REPO_ANALYZER_<UPPER_SNAKE_CASE>` 读取环境变量，覆盖 `defaults.yaml` 中对应字段：

```bash
# CI 配置示例
export REPO_ANALYZER_SLA_BUDGET_MINUTES=90
export REPO_ANALYZER_SLA_BUDGET_TOKENS=1500000
export REPO_ANALYZER_TARGET_COVERAGE_CORE=0.85
export REPO_ANALYZER_MODE=business
export REPO_ANALYZER_OFFLINE=true
repo-analyzer /path/to/repo
```

落地：
- skill 入口 `cli.py` 中 `os.environ` 扫描 `REPO_ANALYZER_` 前缀的所有 key
- 命名映射：`SLA_BUDGET_MINUTES` ↔ `sla_budget.minutes`，`TARGET_COVERAGE_CORE` ↔ `target_coverage.core`
- env 覆盖 **优先级最高** > CLI argv > `defaults.yaml`
- 覆盖日志：skill 启动 banner 中打印 `[ENV OVERRIDE] sla_budget.minutes=90 (was 30)`

### 2. `extends:` 字段继承（`yaml_extends_chain`）

`defaults.yaml` 支持 `extends:` 字段，指向父配置：

```yaml
# ~/.config/repo-analyzer/defaults.yaml（用户本地）
extends:
  - ~/work/team-configs/repo-analyzer.defaults.team.yaml

# 用户自定义覆盖
sla_budget:
  minutes: 60  # 团队配 30，我重写为 60

target_coverage:
  core: 0.85    # 团队配 0.80，我调到 0.85
```

加载规则：
1. 解析 `~/.config/repo-analyzer/defaults.yaml`
2. 递归解析 `extends:` 列表中的每个文件
3. 深度合并（dict 浅覆盖，scalar 直接覆盖）
4. 当前文件最后，覆盖父文件字段
5. 循环引用检测（path-based graph cycle detection）

落地：
- `config_loader.py` 中 `load_with_extends(path: Path) -> dict`
- 错误处理：父文件不存在 → WARN 但不阻断；循环引用 → ERROR 阻断

### 3. 会话间偏好持久化（`last_session_prefs`）

skill 启动时检查 `~/.config/repo-analyzer/last-session.json`：

```json
{
  "timestamp": "2026-07-06T17:00:00+08:00",
  "flags_used": {
    "--mode": "business",
    "--no-question": true
  },
  "qa_path": "/tmp/repo-analyzer/repo-x/questions-answered.json"
}
```

行为：
- 加 `--save-pref` flag 时**自动保存**本次会话的全部 flag 到 `last-session.json`
- 默认行为：**不**自动保存，避免污染用户环境
- 用户加 `--use-last-pref` 时读取 `last-session.json` 中的 flag（合并到 argv）

落地：
- `~/.config/repo-analyzer/last-session.json` 文件 ownership 是用户本人（`mode 0600`）
- 30 天未使用则丢弃（mtime > 30d → 删除）
- 不持久化的内容：内部 `--target-coverage-core` 等敏感阈值（仅 env / CLI 控制）

## Alternatives

- **E1. 仅 env 覆盖** —— 仅满足 CI 场景，约 50 行。
- **E2. 仅 `extends:` 继承** —— 团队共享，约 80 行。CI 覆盖靠用户脚本。
- **E3. 三件齐做（本 ADR）** —— env + extends + 偏好，约 150 行 + 配置文档。

## Consequences

- 总计约 150 行 Python + 1 份 config loader 单测。
- `~/.config/repo-analyzer/` 成为配置根目录，新增 `defaults.yaml` + `last-session.json` 两个文件。
- 配置文件 YAML/JSON schema 校验（用 pydantic / jsonschema）。
- skill 启动 banner 增加 `[CONFIG]` 段落显示当前生效配置（含 env 覆盖高亮）。
- 文档：新增 `docs/configuration.md` 描述优先级链、env 命名约定、extends 用法。

## Open Questions

- [ ] env 变量命名用 `REPO_ANALYZER_SLA_BUDGET_MINUTES` 还是 `REPO_ANALYZER_SLA.BUDGET.MINUTES`？前者标准，后者更结构化。
- [ ] `last-session.json` 是否应该跟随用户当前位置（project-local `analyzer-prefs.json`）而不是全局？两种策略各有优势。
- [ ] `extends:` 是否支持远端 URL（`https://team-configs/repo-analyzer.defaults.yaml`）？涉及鉴权问题。

## Linked

- ADR-0008（5 真 + 5 内部变量基础）
- ADR-0007（SLA 预算受 env 覆盖影响）
- 阶段十二 §12
