# 03 Plan: HTTPX Standard Analysis

## 规模估计

分析对象为生产 Python 代码，不计测试、文档、脚本和配置。有效代码总量为 8,827 行。

| 分组 | 文件/能力 | 行数 | standard 目标 | 计划 |
|---|---|---:|---:|---|
| 核心 | 请求 API 与 Client 编排 | 2,457 | 60% | 完整读取 `_api.py`、`_client.py` |
| 核心 | Request/Response/Headers/Cookies | 1,277 | 60% | 完整读取 `_models.py` |
| 核心 | URL、QueryParams、解析规范化 | 1,168 | 60% | 完整读取 `_urls.py`、`_urlparse.py` |
| 核心 | 内容、multipart、流 | 540 | 60% | 完整读取 `_content.py`、`_multipart.py` |
| 核心 | 配置、代理匹配、认证、解码 | 1,231 | 60% | 完整读取 `_config.py`、`_utils.py`、`_auth.py`、`_decoders.py` |
| 核心 | Transport 抽象与适配器 | 886 | 60% | 完整读取 `_transports/*.py` |
| 次要 | CLI | 506 | 30% | 完整读取 `_main.py` |
| 次要 | 异常、状态码、类型和公共导出 | 762 | 30% | 完整读取公共契约文件 |

核心合计 7,559 行，最低目标 4,536 行；次要合计 1,268 行，最低目标 381 行。

## 分析模式

使用 `standard`。本项目不是按文件逐一复述，而是按业务功能组织：

1. 用户请求如何被构造、配置合并、认证/重定向处理并交给 transport。
2. Request/Response 如何承载 headers、cookies、body、stream 和生命周期。
3. URL 与 QueryParams 如何形成规范化、可组合的请求地址。
4. transport 如何把同一请求契约映射到 httpcore、ASGI、WSGI 或 mock。
5. CLI 和异常/状态码/类型如何把内部能力暴露给开发者。

## 覆盖计划

- 核心模块完整读取，预计核心实际读取 7,559/7,559 行，即 100%。
- 次要模块完整读取，预计次要实际读取 1,268/1,268 行，即 100%。
- 测试目录不纳入源码覆盖率，但会读取测试文件清单和开发者文档中的测试命令作为验证背景。
- 不把外部依赖内部实现计入 httpx 覆盖率。
- 对可选依赖路径（HTTP/2、SOCKS、Brotli、Zstandard）只记录本地 gate 和限制，不声称运行验证。

## 关键探索问题

- HTTPX 如何让同步和异步路径共享同一套语义，而不把两套实现强行合并成一个运行时抽象？
- 为什么 Request/Response 要把流生命周期作为显式状态，而不是始终把 body 读入内存？
- transport 抽象如何同时支持网络、代理、ASGI、WSGI 和 mock？
- Requests 兼容性在哪些位置被主动让位于更清晰或更安全的行为？
