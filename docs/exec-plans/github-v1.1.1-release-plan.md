# GitHub v1.1.1/v1.1.2 发布执行计划

状态：`completed`

- 质量门：完整门
- 独立Judge：必须
- Roadmap：[github-v1.1.1-release-roadmap.md](../roadmap/github-v1.1.1-release-roadmap.md)
- 进度：[github-v1.1.1-release-progress.md](github-v1.1.1-release-progress.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | pre-release security scan 发布顺序与验证（完成口径 `v1.1.2`） |
| 当前状态 | `completed`；v1.1.2 纠正发布 + 独立 Judge pass |
| 何时读取 | 执行本发布任一步前 |
| 关联真源 | roadmap；VERSION；progress；pre-release-security-scan |

## 目标关

### 目标

发布含 pre-release security scan 的源码 Release；因 `v1.1.1` 时序缺口，以 **`v1.1.2` 纠正发布** 作为完成口径（先扫后 tag；main/tag/Release 同提交）。

### 非目标

不改产品分析合同；不伪造 UAT/marketplace 通过；不把 gitleaks PASS 说成真实回归 UAT。

### 完成条件

1. 纠正发布元数据 `1.1.2` 一致。
2. 测试与校验通过。
3. **打 `v1.1.2` tag 前**安全扫描（工作树 + 全历史原命令 + 跟踪面）PASS 并记入 progress。
4. **打 tag 当刻** 远端 `main`、标签 `v1.1.2` 与 GitHub Release 指向同一提交；收口文档提交可之后推进 `main`（标签仍钉在发布提交）。
5. `v1.1.1` 时序缺口已披露；未声称 marketplace/G5 UAT。
6. 独立 Judge `Verdict: pass` 或用户书面豁免后控制面 `completed`（CLOSE-J1/CLOSE-J2）。

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
| S0 | 升版本与 CHANGELOG、控制面（含 1.1.2 纠正） | validate-release-metadata |
| S1 | **先**安全扫描 + 测试 + control-plane bootstrap | gitleaks 原命令；pytest；validate |
| S2 | 提交、推送、tag `v1.1.2`、gh release | 发布提交上 main/tag/Release 同提交 |
| S3 | awaiting-judge → 独立 Judge → audit → completed | Judge pass；CLOSE-J1/CLOSE-J2 |

## 验证合同

- `gitleaks dir --no-banner --redact .`
- `gitleaks git --no-banner --redact --log-opts="--all" .`
- 跟踪面：`git ls-files` 无真实密钥类文件；`.gitignore` 覆盖 `.env`
- `python -m pytest tests/unit -q`
- `python tools/release/validate-release-metadata.py`
- `python tools/release/validate-control-plane.py --mode bootstrap` 与收口 `audit`
- `git diff --check`
- `gh release view v1.1.2`

## 收口路径

- CLOSE-J1：Worker 自验结束将 plan 标为 `awaiting-judge`，生成审查包
- CLOSE-J2：独立 Judge `Verdict: pass` 后 audit，再 `completed`（已完成）
