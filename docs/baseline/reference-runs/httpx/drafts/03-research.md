# 03 Research: HTTPX

## 项目解决的核心问题

HTTPX 面向需要在 Python 中发起真实 HTTP 请求的开发者，提供一个同时覆盖同步、异步、HTTP/1.1、HTTP/2、流式响应和命令行访问的客户端层。README 将其定位为“下一代 HTTP client”，并明确列出 sync/async API、HTTP/1.1/2、WSGI/ASGI transport、严格 timeout 和类型标注（`README.md:5-16`, `59-70`）。

具体场景包括：

1. 应用代码既需要传统同步调用，又需要在 asyncio/Trio 中复用同一套请求模型。`Client` 与 `AsyncClient` 共享 `BaseClient` 的配置、请求构造和重定向/认证语义，而在发送阶段分别调用同步或异步 transport（`httpx/_client.py:188-473`, `594-1034`, `1307-1749`）。
2. 服务或测试代码需要把 HTTP 请求送入 ASGI/WSGI 应用，而不是通过真实网络。HTTPX 把应用适配成 transport，使上层 client 流程不需要知道目标是网络服务还是进程内应用（`httpx/_transports/asgi.py:63-187`, `httpx/_transports/wsgi.py:44-149`）。
3. 兼容 Requests 使用习惯，同时修正长期使用中容易隐藏成本的默认行为，例如默认不自动跟随重定向、所有网络操作有 timeout、流式响应显式关闭。官方 compatibility 文档明确记录这些有意差异（public docs, unpinned; local docs link at `README.md:106-116`）。

## 定位

HTTPX 不是底层 HTTP 协议实现本身，而是建立在 `httpcore` 之上的高层客户端。项目配置把 `httpcore==1.*` 声明为依赖（`pyproject.toml:30-35`），README 也把 httpcore 描述为 underlying transport implementation（`README.md:122-129`）。因此其主要价值在于：稳定的公共请求模型、配置合并、同步/异步双接口、可插拔 transport 和用户体验，而不是重新实现连接池或 HTTP/2 协议。

## 同类对比

| 项目 | 可验证定位 | 技术路线差异 | 本基线的使用方式 |
|---|---|---|---|
| Requests | 官方仓库描述为 simple/elegant HTTP library；同步优先、生态成熟 | HTTPX 明确提供 async、HTTP/2、transport 适配和更严格默认值 | 作为兼容性与设计取舍参照；本 commit 未读取 Requests 源码 |
| httpcore | 官方仓库描述为 minimal HTTP client | 更低层，负责连接池/协议适配；HTTPX 在其上提供高层请求 API | 只以 HTTPX 依赖声明和 adapter 调用为证据 |
| aiohttp | 常见异步 HTTP 客户端/服务器方案 | 异步模型与服务器能力更强，API 不以 Requests 兼容为主 | 未在本轮获取固定版本源码，具体差异待验证 |
| urllib3 | HTTP 连接池和底层网络库 | HTTPX 选择 httpcore 作为底层，并在 API 层提供 sync/async 双路径 | README 仅说明其设计受到 urllib3 启发（`README.md:141-143`） |

## 为什么需要单独做这个项目

仅组合 Requests、async 库和底层连接池，会把同步/异步语义、请求模型、cookie、重定向、流式生命周期和 transport 注入分散到多个 API。HTTPX 的代码显示它把这些行为集中在 `Request`/`Response`、`BaseClient` 和 transport contract 上，再把协议实现下沉到 httpcore（`httpx/_models.py:382-494`, `515-1077`; `httpx/_client.py:188-473`, `964-1034`）。

独特价值主张不是“功能最多”，而是一个高层客户端同时提供：

- Requests 风格的低门槛入口；
- async 作为一等路径，而不是另一个不相容 API；
- 通过 transport 统一真实网络、ASGI、WSGI、mock；
- 显式流式资源管理和严格 timeout。

## 项目背后的组织动机

本 commit 的 README、贡献指南和配置文件没有给出完整组织战略。可以确认的是：项目采用 BSD-3-Clause，作者字段为 Tom Christie（`pyproject.toml:5-12`），并通过独立文档、第三方包目录和贡献流程组织生态（`mkdocs.yml:25-52`, `docs/contributing.md:1-102`）。更具体的商业动机、团队路线或历史决策未找到，不能据此推断。

## 研究边界

- Jina Reader 读取的官网与 compatibility 页面当前未绑定到 `b5addb6`，所以只作为“公开定位/兼容性意图”证据。
- 未配置 Exa，未完成语义搜索建议的 3-5 次查询。
- 未读取 httpcore、Requests、aiohttp、urllib3 的固定版本实现；跨项目实现差异仅在报告中使用已声明或明确标注为待验证的层面。
