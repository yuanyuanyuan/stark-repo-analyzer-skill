# Agent 主导 Graphify Bootstrap 并保留密钥边界

Graphify 不可用、版本不兼容或缺少非敏感运行依赖时，Agent 可自行执行官方安装/升级命令、安装所需 extras 并复检 CLI、Python import 与 Graphify 后端探测。API key、企业代理、私有 provider 地址及其授权始终由用户提供；Agent 不生成、读取、输出或绕过这些配置。

## Consequences

- Bootstrap 是 skill 的可执行前置阶段，失败日志必须指明缺失条件和下一步用户操作。
- 安装命令按 Graphify 实际诊断选择，不把某个 extra 或供应商写死为唯一配置。
- Bootstrap 成功不等同于分析成功，仍须通过 LLM、图谱健康和证据质量闸门。
