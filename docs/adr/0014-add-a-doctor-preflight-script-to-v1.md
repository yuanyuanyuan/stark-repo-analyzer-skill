# 为 V1 增加 doctor 预检脚本

V1 提供 `acceptance/doctor.sh preflight|post-graph --target <repo> --work-dir <dir> [--json]`。`preflight` 检查 Graphify CLI、Python import、版本、headless extract 能力、Graphify 自身 LLM 探测、目标可读性和工作区可写性；`post-graph` 检查图谱产物、来源和输出隔离边界。退出码 `0` 为 ready，`10` 为 Agent 可修复的 Bootstrap 条件，`20` 为需要用户提供敏感配置，`30` 为阻断错误。

## Consequences

- `--json` 输出供 Agent 编排消费；默认输出供用户和日志阅读，任何输出不得暴露密钥。
- doctor 不运行正式提取、不写目标仓库、不自行安装；Agent 根据 `10` 的结构化建议执行 Bootstrap 后重跑 doctor。
- 正式分析只能从 doctor 返回 `0` 后开始，避免把环境问题误写为分析失败。
