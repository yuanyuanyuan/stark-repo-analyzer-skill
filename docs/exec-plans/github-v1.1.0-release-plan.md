# GitHub v1.1.0 发布执行计划

状态：`completed`

- 质量门：完整门
- 独立Judge：必须
- Roadmap：[github-v1.1.0-release-roadmap.md](../roadmap/github-v1.1.0-release-roadmap.md)
- 进度：[github-v1.1.0-release-progress.md](github-v1.1.0-release-progress.md)

| 固定字段 | 内容 |
|---|---|
| 文档角色 | `v1.1.0` 发布顺序与验证 |
| 当前状态 | `completed`；`v1.1.0` Release 已公开，独立 Judge pass |
| 何时读取 | 执行本发布任一步前 |
| 关联真源 | roadmap；VERSION；progress |

## 目标关

### 目标

发布 `v1.1.0` 源码 Release，覆盖默认 Judge 与代码地图协作基建。

### 非目标

不改产品分析合同；不伪造 UAT/marketplace 通过。

### 完成条件

1. 元数据 `1.1.0` 一致。
2. 测试与校验通过。
3. 标签与 GitHub Release 指向发布提交。
4. Judge pass 或书面豁免后控制面 `completed`。

## 启动关

### Blindspot Pass

- code-map 提交 `0d157b6` 已在 `main`；发布提交只应叠加版本与控制面。
- Release Notes 不得把协作基建写成 analyzer 行为变更。
- 标签/Release 不可逆；先本地校验再 push tag。

### 工作区基线

- 基线：`main` @ code-map 提交已推送；本任务拥有 VERSION/CHANGELOG/adapter 版本与本发布控制面。

## 执行计划

| ID | 动作 | 验证 |
|---|---|---|
| S0 | 升版本与 CHANGELOG、控制面 | validate-release-metadata |
| S1 | 跑测试与 control-plane | pytest / validate |
| S2 | 提交、推送、tag、gh release | 远端一致 |
| S3 | Judge 与 completed | audit + Judge |

## 验证合同

- `python -m pytest tests/unit -q`（或全量 unit）
- `python tools/release/validate-release-metadata.py`
- `python tools/release/validate-control-plane.py --mode bootstrap` 与收口 `audit`
- `git diff --check`
- `gh release view v1.1.0`

## 收口说明

独立 Judge `Verdict: pass`。S0–S3 完成；marketplace/G5 未执行已披露。
