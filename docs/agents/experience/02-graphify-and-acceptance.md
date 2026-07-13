# 结构证据与验收经验

## 1. doctor 是强制侧车，不是可选诊断

**结论：** `doctor.sh preflight` 必须在提取前通过，`doctor.sh post-graph` 必须在图谱产物生成后通过；doctor 的非零结果阻止正式分析继续。

**等级：** 已核验。

**来源范围：** 所有 Graphify/doctor 相关 observation，包含对版本、产物、manifest 和 code-only 标识的审计任务。

**仓库证据：** [doctor](../../../acceptance/doctor.sh)、[真实 UAT 规则](../../../dev-rules/real-uat-regression/README.md)。

## 2. 图谱输出必须与目标源码隔离

**结论：** Graphify 原始和标准化产物写入 `$WORK_DIR/graphify-out/`；目标仓库只读。运行前后均要检查目标树是否被写入，残留物必须清理并记录。

**等级：** 已核验。

**来源范围：** 物理运行、目标树残留和隔离失败的项目记忆。

**仓库证据：** [任务执行记录：输出越界问题](../goal-execution-record.md#1-graphify-output-could-cross-the-source-boundary)。

## 3. 图谱只能导航，源码才裁决

**结论：** `EXTRACTED` 关系要在核心路径回到源码核实；`INFERRED` 只能待验证；`AMBIGUOUS` 只能进入风险或问题。这条规则避免将图谱推断直接写成架构事实。

**等级：** 已核验。

**仓库证据：** [V1 Graphify 边界](../../goals/stark-repo-analyzer-v1-implementation.md#graphify-and-doctor-boundaries)、[UAT 禁止假通过](../../../dev-rules/real-uat-regression/README.md)。

## 4. code-only 必须显式标识，不能伪装成语义图谱

**结论：** code-only 运行取消 LLM/provider 语义提取，能够提供 AST/代码关系证据，但不应继承语义模式的成功或可重复性结论。doctor、metadata、manifest 和报告需要携带该模式。

**等级：** 已核验原则；当前迁移实现状态待验证。

**来源范围：** 关于 `graphify 0.9.13 --code-only --no-cluster`、现有控制面假设和新增测试需求的记忆。

**仓库证据：** [执行记录：Ruff code-only continuation](../goal-execution-record.md#7-ruff-code-only-continuation)、[doctor 的 extraction mode](../../../acceptance/doctor.sh)。

## 5. 对工具版本与安装失败要记录事实，不要猜测环境

**结论：** 版本升级和 CLI 可用性必须由实际二进制路径、`--version`、`extract --help` 与 preflight 证明。命令拼写或安装目标错误只能说明本次升级没有发生，不能推导工具本身不支持功能。

**等级：** 记忆支持。

**来源范围：** 2026-07-13 关于 `uv tool upgrade graphifyy` 失败而现有 `/Users/chuzu/anaconda3/bin/graphify` 仍为 `0.9.8` 的记录。

**边界：** 该观察是当时的机器状态；后续升级应重新执行 doctor，不能依赖此记录。
