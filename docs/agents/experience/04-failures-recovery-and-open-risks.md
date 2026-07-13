# 失败、恢复与未完成事项

## 1. Ruff 语义提取失败必须保留为失败

**结论：** Ruff 的语义 Graphify 提取经历了有界重试和较长观察，但没有产生可验收的图谱与报告。因此它是中断/失败记录，不能由后续手写报告、参考材料或 code-only 结果改写为语义模式成功。

**等级：** 已核验。

**仓库证据：** [执行记录：Ruff 失败](../goal-execution-record.md#4-ruff-repeatedly-stalled-during-semantic-extraction)、[真实 UAT 规则](../../../dev-rules/real-uat-regression/README.md)。

## 2. 失败原因要停在证据能支持的粒度

**结论：** 已知失败发生在语义提取阶段，并出现无效 JSON、markdown 包裹 JSON、截断和路径解析异常等现象；没有完整请求级追踪时，不能归因到特定 HTTP 状态、供应商故障、OOM 或密钥问题。

**等级：** 已核验。

**仓库证据：** [执行记录：详细 stdout/stderr 缺口](../goal-execution-record.md#5-missing-detailed-graphify-stdoutstderr)。

## 3. 恢复路径需要保留原始证据链

**结论：** `resume` 或 post-graph 修复不能只保留标准化输出；raw Graphify 产物、命令、退出码、时间和失败分类必须可回溯，否则恢复结果不可审计。

**等级：** 已核验。

**仓库证据：** [执行记录：resume 证据链](../goal-execution-record.md#3-resume-needed-to-preserve-raw-graphify-evidence)。

## 4. 当前风险与“已完成”必须并列呈现

**结论：** 已完成的非 Ruff 运行、code-only 续跑、P4 尚未稳定的项目、目标隔离问题和 P5 范围外状态必须同时呈现。不能为了交付简洁而省略其中任一项。

**等级：** 已核验。

**仓库证据：** [V1 状态](../../goals/stark-repo-analyzer-v1-implementation.md#status)、[物理基线当前边界](../../baseline/physical-baseline.md#current-evidence-boundary)。

## 5. 真实 UAT 不能由静态证据替代

**结论：** 静态源码阅读、目录结构、测试/fixture 和中断运行都不能被称为真实 UAT 通过；真实 UAT 需要本项目规则要求的固定输入、调用、工具、产物和验证证据。

**等级：** 已核验。

**来源范围：** 多次追问“哪里跑了真实 UAT”“是否 ready”“为什么失败”的项目记忆。

**仓库证据：** [真实 UAT 回归规则](../../../dev-rules/real-uat-regression/README.md)。
