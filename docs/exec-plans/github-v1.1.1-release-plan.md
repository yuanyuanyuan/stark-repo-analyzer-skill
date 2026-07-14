# GitHub v1.1.1 发布执行计划

状态：`active`

- 质量门：完整门
- 独立Judge：必须
- Roadmap：[github-v1.1.1-release-roadmap.md](../roadmap/github-v1.1.1-release-roadmap.md)
- 进度：[github-v1.1.1-release-progress.md](github-v1.1.1-release-progress.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | `v1.1.1` 发布顺序与验证 |
| 当前状态 | `active` |
| 何时读取 | 执行本发布任一步前 |
| 关联真源 | roadmap；VERSION；progress；pre-release-security-scan |

## 目标关

### 目标

发布 `v1.1.1` 源码 Release，覆盖发布前安全扫描 dev-rule 与路由，且本发布先通过安全扫描。

### 非目标

不改产品分析合同；不伪造 UAT/marketplace 通过；不把 gitleaks PASS 说成真实回归 UAT。

### 完成条件

1. 元数据 `1.1.1` 一致。
2. 测试与校验通过。
3. 发布前安全扫描（工作树 + 全历史 + 跟踪面）PASS 并记入 progress。
4. 标签与 GitHub Release 指向发布提交。
5. 独立 Judge `Verdict: pass` 或用户书面豁免后控制面 `completed`（CLOSE-J1/CLOSE-J2）。

## 启动关

### Blindspot Pass

- 暂存变更已含 pre-release-security-scan 规则；发布提交应叠加版本投影与本控制面。
- 发布自身必须先跑 gitleaks，不能“规则写了但首次发版跳过”。
- Release Notes 不得把协作/安全基建写成 analyzer 用户行为变更。
- 标签/Release 不可逆；先本地校验再 push tag。
- 完整门收口路径：`awaiting-judge` → 独立 Judge → `validate-control-plane.py --mode audit` → `completed`；Worker 不得自审自过。

### 工作区基线

- 基线时间：2026-07-14 18:10 CST
- 分支：`main` @ `ff861bd`（与 `origin/main` 同步）
- 已暂存用户/本轮范围：`.gitignore`、`AGENTS.md`、`docs/dev-rules/README.md`、`docs/dev-rules/pre-release-security-scan/README.md`、`docs/dev-rules/real-uat-regression/README.md`
- 本任务额外拥有：`VERSION`、`CHANGELOG.md`、adapter/`package.json` 版本投影、本发布 roadmap/plan/progress、目录索引更新
- 排除：其它分支、无关本地缓存

## 执行计划

| ID | 动作 | 验证 |
|---|---|---|
| S0 | 升版本与 CHANGELOG、控制面 | validate-release-metadata |
| S1 | 安全扫描 + 测试 + control-plane bootstrap | gitleaks；pytest；validate |
| S2 | 提交、推送、tag、gh release | 远端一致 |
| S3 | awaiting-judge → 独立 Judge → audit → completed | Judge pass；CLOSE-J1/CLOSE-J2 |

## 验证合同

- `gitleaks dir --no-banner --redact .`
- `gitleaks git --no-banner --redact --log-opts="--all" .`
- 跟踪面：`git ls-files` 无真实密钥类文件；`.gitignore` 覆盖 `.env`
- `python -m pytest tests/unit -q`
- `python tools/release/validate-release-metadata.py`
- `python tools/release/validate-control-plane.py --mode bootstrap` 与收口 `audit`
- `git diff --check`
- `gh release view v1.1.1`

## 收口路径

- CLOSE-J1：Worker 自验结束将 plan 标为 `awaiting-judge`，生成审查包
- CLOSE-J2：独立 Judge `Verdict: pass` 后 audit，再 `completed`
