# ADR 0001: Bounded Standard Scope for a Leaked Source Mirror

## Status

Accepted for this baseline run.

## Context

固定 commit 包含 1,884 个 TypeScript/TSX 文件和 512,664 行代码，但没有构建配置、依赖清单或测试入口。参考 skill 的 standard 要求核心模块至少 60%、次要模块至少 30%，并要求不虚报覆盖率。

## Decision

按“用户请求进入 CLI 后如何形成模型请求、工具调用、子任务、上下文和扩展能力”的数据流建立核心模块；MCP、插件、权限、UI、远程和平台适配作为次要/外围模块。对大型文件只把实际读取的行范围计入覆盖率，无法达到门槛就明确记录失败原因。

## Alternatives Considered

- 把全部 `src` 当作一个模块：无法解释业务边界，也会把 512k 行的未读代码错误地包装成全局结论。
- 只分析 README 和目录名：速度快，但无法满足 Why > What、跨模块和源码行号证据要求。
- 依赖 Git 历史恢复设计动机：违反本次固定 commit 证据边界，因此不采用。

## Consequences

报告能复核关键主链路，但不是全仓库逐文件审计。覆盖率表会把纳入范围、实际读行和未读外围代码分开，后续重实现可以先对比主链路，再补齐外围模块。
