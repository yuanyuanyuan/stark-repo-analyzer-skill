# 05 Modules Plan: HTTPX

## 报告叙事线

用户入口/API →[入口需要一个稳定的请求对象承载配置与 body]→ 请求/响应模型 →[模型必须把 URL、headers、cookies 和 body 变成可传输的规范表示]→ URL 与配置 →[规范化后的请求需要被送入不同执行环境]→ Transport 适配层 →[执行结果回到响应模型后，还要处理认证重试和内容解码]→ 认证与解码 →[最后才把同一套能力暴露给命令行和公共异常/状态码契约]→ CLI 与公共契约。

这条线按一次请求的生命周期组织，不按目录顺序复述文件。

## 模块清单

| 顺序 | 模块 | 类型 | 主要证据 |
|---:|---|---|---|
| 1 | 请求入口与 Client 编排 | 核心 | `httpx/_api.py`, `httpx/_client.py` |
| 2 | Request/Response 与 body 模型 | 核心 | `httpx/_models.py`, `_content.py`, `_multipart.py` |
| 3 | URL、QueryParams 与运行时配置 | 核心 | `httpx/_urls.py`, `_urlparse.py`, `_config.py`, `_utils.py` |
| 4 | Transport 抽象与执行适配器 | 核心 | `httpx/_transports/*.py` |
| 5 | 认证、内容解码与错误传播 | 核心 | `httpx/_auth.py`, `_decoders.py`, `_exceptions.py` |
| 6 | CLI 与公共 API 契约 | 次要 | `httpx/_main.py`, `_status_codes.py`, `_types.py`, `__init__.py` |

## 章节大纲

1. 场景与定位：兼容 Requests 的高层 HTTP 客户端为何需要 sync/async、显式流和 transport 注入。
2. 项目全景：公共 API、模型、client、transport、可选能力之间的关系。
3. 一次请求的主路径：配置合并 → Request → auth/redirect → transport → Response。
4. 深入设计：同步/异步镜像、流生命周期、URL 规范化、transport 边界和错误层级。
5. 兼容性与主动差异：默认不跟随重定向、严格 timeout、streaming 和 cookie 约束。
6. 评价与启发：设计亮点、代价、外部依赖边界和可改进处。

## Mermaid 主图设计

最终报告至少包含：

- client 请求生命周期图；
- transport 适配器关系图；
- Response streaming/decoding 状态图。

## 过渡逻辑

- API 只负责 ergonomic 入口，因此必须把真正的合并规则集中到 `BaseClient`。
- Request/Response 解决数据承载，但不应该知道 TCP/ASGI/WSGI，所以需要 transport contract。
- URL/config 把用户输入变成确定的请求语义，transport 才能按 URL pattern、代理和 SSL 设置选择执行路径。
- transport 返回原始 stream 后，Response 才能负责解码、读取、关闭、elapsed 和错误上下文。
- CLI 复用 `Client.stream()`，证明公共能力可以不复制一套网络逻辑。
