# GitHub v1.0.0 发布执行计划

- 状态：`blocked`
- 质量门：完整门
- 独立Judge：必须
- 日期：2026-07-14
- 对应 roadmap：[github-v1-release-roadmap.md](../roadmap/github-v1-release-roadmap.md)
- 协调入口：无

进度记录：
[github-v1-release-progress.md](github-v1-release-progress.md)

| 固定字段 | 当前内容 |
|---|---|
| 文档角色 | 定义首次 GitHub 源码 Release 的操作顺序、验证合同与发布边界 |
| 当前状态 | `blocked`；GitHub 已禁用目标仓库，等待维护者恢复后再继续 |
| 当前结论/入口 | 候选版本为 `v1.0.0`；唯一分发地址为 `yuanyuanyuan/stark-repo-analyzer-skill`，稳定 Skill 名为 `repo-analyzer` |
| 何时读取 | 执行本次发布的任何正式修改或 GitHub 写操作前 |
| 何时更新 | 任务顺序、验证、阻塞、实际结果或发布范围变化时 |
| 关联真源 | 方向见 roadmap；版本见 `VERSION`；实际事实见 progress；验收上限见 real-uat-regression |

## 当前主线

发布当前 `main` 候选为 GitHub `v1.0.0` 源码 Release。公开入口必须统一为当前远端分发地址，并以“独立维护、MIT 参考语料、无官方关联”方式致谢 `yzddmr6/repo-analyzer`；稳定 Skill 名保持 `repo-analyzer`。

## 目标关

### 目标

- 统一 README、manifest 与安装命令中的公开 identity。
- 在中英文 README 中增加准确的参考项目来源说明。
- 验证发布候选并创建 `v1.0.0` 源码型 GitHub Release。

### 非目标

- 不发布二进制、npm/PyPI 工件或 marketplace 条目。
- 不声称尚未执行的真实 marketplace 安装或 G5 真实回归 UAT 已通过。

### 完成条件

- `VERSION`、发布标签、Release 标题均为 `v1.0.0` / `1.0.0` 的一致投影。
- 远端 `main`、`v1.0.0` 标签和 GitHub Release 解析到同一提交。
- README 的身份、安装命令、支持范围与来源致谢一致。
- Worker 验证、独立 Judge verdict 与未验证边界均追加至 progress。

## 启动关

### Blindspot Pass

- 当前暂存改动来自既有 Skill 核心包迁移，必须保留并作为候选的一部分，不能 reset 或覆盖。
- 公开 identity 当前在远端与 README/manifest 之间冲突，所有公开入口须同步，不得只改 README。
- 真实外部安装、GitHub Release 写入与 G5 UAT 的证据等级不同，不能以仓库内 smoke 互相替代。
- 标签、推送和创建 Release 为外部不可逆动作；必须在全部本地验证和用户确认的候选提交后执行。

### 关键假设

| 假设 | 置信度 | 验证方式 |
|---|---:|---|
| 当前 `origin` 是本次目标仓库 | 高 | `git remote -v` 与 GitHub 只读查询 |
| 目标仓库允许当前凭据推送并创建 Release | 中 | GitHub CLI 身份/权限检查；失败即停止 |
| 当前暂存变更是维护者确认的 `v1.0.0` 候选 | 高 | 用户已书面确认；提交前再次展示 diff 摘要 |

### 工作区基线

- 基线日期：2026-07-14。
- 用户已有暂存改动：44 个文件，Skill 核心包、adapter、测试、控制面和版本 metadata；本任务将其作为候选保留。
- Worker 新增的未暂存范围：`CONTEXT.md` 发布词汇与本 roadmap/plan/progress；后续 README/metadata 仅限统一 identity、来源致谢和发布说明。

## 执行计划

| ID | 动作 | 输出 | 验证 |
|---|---|---|---|
| R0 | 激活控制面并盘点公开 identity | 活动 roadmap/plan、路径清单 | control-plane bootstrap 校验 |
| R1 | 统一 metadata 与中英文 README | 可复制的正确安装说明、来源致谢 | release metadata 校验、README 对照 |
| R2 | 运行候选验证 | 单元/合同/安装测试与发布元数据结果 | 实际退出码与证据摘要 |
| R3 | 执行可用的真实外部安装 smoke | 实际宿主/adapter 结果 | 仅报告已实际执行的路径 |
| R4 | 提交、推送、标签与 GitHub Release | `v1.0.0` Release | 远端标签与 Release 指向候选提交 |
| R5 | 独立 Judge 与收口 | Judge Review、Boundary Check | Judge `pass`、control-plane audit |

## 验证合同

- 必跑：`python -m unittest discover -s tests -v`、`python tools/release/validate-release-metadata.py`、`python tools/release/validate-control-plane.py --mode bootstrap`，以及 `git diff --check`。
- 发布前真实安装：尽力在可用的 Claude、Codex、`npx skills add` 与手动安装路径执行；缺少宿主、权限或网络时停止该路径并如实记录，不伪造通过。
- G5 真实回归 UAT 按 `docs/dev-rules/real-uat-regression/README.md` 另行执行；本次未跑不得称发布级真实回归通过。
- Judge 必须只读审查并至少独立执行一项核心风险验证；任何 `revise` 结果先修复再复审。

## 主线总结

本 plan 以真实证据发布 `v1.0.0`，并严格区分源码 Release、外部安装与产品真实回归。激活前不得执行 GitHub 写操作。
