# 代码地图导航进度

文档类型：progress-log
关联 plan：[code-map-navigation-plan.md](code-map-navigation-plan.md)
继承状态：`completed`

## 当前快照

| 字段 | 内容 |
|---|---|
| 阶段 | 规则/沙箱纠错完成；重审 Judge 已独立重跑 pytest 并 pass；completed |
| 已完成 | M0–M3；hooks trust 验证；独立验证规则与 fallback 沙箱修正；合规 Judge 重审 pass |
| 进行中 | 无 |
| 阻塞 | 无 |
| 下一刀 | 无 |

## 记录

### 2026-07-14 — 控制面创建（proposed）

**实际完成**

- grill-with-docs 锁定设计：YAML 语义真源、Graphify 只读协助、PostToolUse+Stop 提醒 hook、五职责层、档 B 初版 feature、任务导向加载、不进 skill 包。
- `CONTEXT.md` 新增领域词「代码地图」。
- 新建 roadmap / plan / progress 控制面（当时 `proposed`）。
- 更新 roadmap / exec-plans / docs 目录索引（拟议入口）。

**实际验证**

- `git status --short`、`git diff --check`（控制面落盘时）。

### 2026-07-14 — M0–M3 实施（Worker）

**授权**

- 用户请求「实施」roadmap，作为维护者确认：roadmap/plan 改为 `active` 后实施。

**实际改动**

1. **M0**
   - `docs/adr/0027-repo-code-map-with-graphify-assist-and-reminder-hooks.md`（`accepted`）
   - `docs/dev-rules/code-map/README.md`
   - 更新 `docs/dev-rules/README.md`、`docs/adr/README.md`、`docs/README.md`、roadmap/exec-plans 索引
   - roadmap/plan 状态：`proposed` → `active`
2. **M1**
   - `docs/code-map/map.yaml`：5 layers + 12 active features + entrypoints/watch_paths/task_hints
   - `docs/code-map/README.md` 阅读入口
3. **M2**
   - `AGENTS.md`：权威表 + 启动顺序任务导向 code-map 步骤
   - `.codex/hooks/code_map_gate.py`：PostToolUse/Stop 提醒，不 deny
   - `.codex/hooks.json`：与 control_plane_gate **并列**挂载
4. **M3**
   - `tests/unit/test_code_map_gate.py`
   - 本 progress 收口；plan → `awaiting-judge`
   - 审查包：`docs/exec-plans/artifacts/code-map-navigation-review-package.json`

**未改（边界）**

- 未改 `skills/repo-analyzer` 用户分析行为代码合同。
- 未把 code-map 写入 `tools/release/core-package-files.txt`。
- 未实现 graph→map 自动生成。

**Worker 验证**

- `python -m pytest tests/unit/test_code_map_gate.py -q` → 8 passed
- `python tools/release/validate-control-plane.py --mode bootstrap` → PASS
- `python tools/release/validate-control-plane.py --mode audit` → PASS
- `git diff --check` → 无报错
- `map.yaml` entrypoints 全量存在性检查：72 paths，missing 0；active features = 12（档 B）
- hook 冒烟：对 `skills/repo-analyzer/SKILL.md` 的 apply_patch 载荷输出 `systemMessage` 提醒；无 `permissionDecision: deny` / `continue: false`
- 确认 core-package-files 不含 code-map

**未执行**

- 真实回归 UAT（产品行为未变，不在完成口径）
- Graphify 全量重建（仅约定只读协助；本刀未强制重建）
- 宿主 `/hooks` trust 点击（需用户侧；未信任时提醒降级）
- 独立 Judge（本记录之后由 Orchestrator 调度）

**Deviations**

- 无方向性偏离。hook 路径解析对 macOS `/var` vs `/private/var` 与 JSON 转义做了加固，仍保持「仅提醒」合同。

**Boundary Check**

- 结果适用范围：本仓库 Agent/维护者导航与协作 hook；不改变 analyzer 对目标仓的分析合同。
- 失效条件：未 trust hooks 时仅丢失提醒；map 长期不维护时导航过期（规则要求边界变更同步或无影响声明）。
- 回退：移除 hooks.json 中 code_map 条目并还原 AGENTS/code-map 文档即可；不涉及数据迁移。

**Judge Review**

### Judge Review
- Verdict: pass
- 刚性约束违规：无。
- 问题（按严重级别）：无阻塞问题。
- 缺失验证：无阻塞缺失；独立重跑 `pytest` 受只读沙箱无临时目录限制，已审查 Worker 的 `8 passed` 证据。
- 建议复查范围：宿主侧 `/hooks` trust 后，可手动确认生命周期提醒实际显示。
- 独立执行的验证及结果：`python tools/release/validate-control-plane.py --mode audit` → PASS；无写入入口检查 → 72 entrypoints、missing 0、12 active features；实际 hook 对受监控路径输出提醒，且不含 deny / `continue: false`。
- 实际模型 / 推理等级：`gpt-5.6-terra` / `medium`


**阻塞与下一刀**

- 阻塞：无。
- 下一刀：无。宿主侧可选：在 Codex `/hooks` 信任后确认 code_map 提醒可见。

### 2026-07-14 — 独立 Judge 与收口

**实际完成**

- Orchestrator 运行 `python tools/release/run-independent-judge.py --plan docs/exec-plans/code-map-navigation-plan.md`（gpt-5.6-terra / medium）。
- 将 Judge Review 原样追加；plan/roadmap 标 `completed`。
- `python tools/release/validate-control-plane.py --mode audit`。

**实际验证**

- 见上方 Judge Review 与 Worker 验证。

**Deviations**

- 无。

### 2026-07-14 — hooks trust 后验证（非 UAT）

**实际完成**

- 用户确认 Codex hooks 已 trust；按计划做提醒 hook 实机 stdin 冒烟与回归单测，**不做**真实回归 UAT。

**实际验证**

- `python -m pytest tests/unit/test_code_map_gate.py -q` → 8 passed
- `python tools/release/validate-control-plane.py --mode audit` → PASS
- `code_map_gate` PostToolUse：
  - 仅改 `skills/repo-analyzer/SKILL.md` → 输出 Code-map reminder systemMessage
  - 同时改 `map.yaml` → 无输出
  - 改未监控路径 `README.md` → 无输出
- `code_map_gate` Stop：当前工作区同时含 `docs/code-map/` 脏文件时静默（`map_updated` 判定为已同步）；用 mock `git status` 仅含 skill 路径时仍提醒
- 源码与输出均无 `permissionDecision: deny` / `continue: false`
- `.codex/hooks.json` PostToolUse + Stop 均挂载 `code_map_gate.py`，与 `control_plane_gate` 并列

**未执行**

- 真实回归 UAT（用户明确暂不做）
- 宿主 GUI 内一次真实 apply_patch 回合的可见气泡（stdin 合同已覆盖；若需 UI 侧确认可另做）

**Deviations**

- 无

**code-map 无影响**：本记录仅追加 progress 验证证据，不改变功能入口或职责分层。

## 重审 Judge Review

### Judge Review
- Verdict: pass
- 刚性约束违规：无。
- 问题（按严重级别）：无阻塞问题；此前未重跑 pytest 的 Judge pass 已作废，不作为本次结论依据。
- 缺失验证：无。真实回归 UAT 属明确未执行的非本次验收项。
- 建议复查范围：宿主侧持续确认已 trust 的 hook 在真实编辑回合中显示提醒。
- 独立执行的验证及结果：`python -m pytest tests/unit/test_judge_review_package.py tests/unit/test_code_map_gate.py -q -p no:cacheprovider --basetemp /tmp/judge-pytest` → `22 passed`；`python tools/release/validate-control-plane.py --mode audit` → `PASS`；`python tools/release/run-independent-judge.py --plan docs/exec-plans/code-map-navigation-plan.md --dry-run` 确认 fallback 使用 `workspace-write`，prompt 明确要求重跑廉价检查且禁止采信 Worker pytest 替代。
- 实际模型 / 推理等级：`gpt-5.6-terra` / `medium`

### 2026-07-14 — 合规重审收口

**实际完成**

- 独立 Judge 以 `workspace-write` fallback 重审；**亲自**重跑 `pytest`（22 passed）与 control-plane audit。
- 原样追加重审 Judge Review；plan/roadmap 恢复 `completed`。

**实际验证**

- 见重审 Judge Review。

**Deviations**

- 无。
