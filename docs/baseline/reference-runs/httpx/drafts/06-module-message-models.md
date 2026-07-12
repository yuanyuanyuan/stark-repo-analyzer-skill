# 06 Module: Request, Response, Content and Multipart Models

## 读者问题

请求和响应如何成为 transport 与用户 API 之间稳定的“消息协议”，同时支持 eager body、streaming body、同步和异步？

## 核心模型

`Headers` 用三元组保存原始 key、规范化 key 和 value，提供大小写不敏感、多值 header、raw bytes 和敏感字段脱敏 repr（`httpx/_models.py:139-379`）。这不是普通 dict：HTTP header 的重复字段、字节编码和传输格式都必须保留。

`Request` 在构造时完成 method 大写、URL/params 合并、cookie header 注入、body 编码和自动 Host/Content-Length 头（`_models.py:382-460`）。`Response` 保存 status、headers、request、history、next_request、extensions 和 stream；非流内容立即读入，外部 stream 则保持延迟读取（`_models.py:515-569`）。

## 数据流

```mermaid
flowchart LR
  A[content/data/files/json] --> B[encode_request]
  B --> C[ByteStream or IteratorByteStream]
  C --> D[Request auto headers]
  D --> E[Transport]
  E --> F[Response raw stream]
  F --> G[content decoder]
  G --> H[ByteChunker/TextChunker]
  H --> I[bytes/text/lines/json]
```

`_content.py` 将 bytes、str、同步/异步迭代器、urlencoded、multipart、JSON 等输入统一为 headers + stream（`_content.py:107-218`）。`MultipartStream` 按字段逐块生成，能够估算长度时使用 Content-Length，否则使用 chunked（`_multipart.py:224-300`）。这让大文件上传可以避免一次性加载到内存。

## Why > What

- `Request(content=...)` 会自动补齐 Host 与 body headers，而显式 `stream=...` 不自动补齐（`_models.py:406-439`）。这是在“方便构造”和“允许 transport/server 侧精确控制”之间划边界。
- `Response.read()`、`iter_bytes()`、`close()` 和 async 对应方法通过 `is_stream_consumed`/`is_closed` 防止重复或关闭后读取（`_models.py:876-1077`）。代价是调用方必须理解流生命周期，但收益是连接可以及时归还池。
- `Response.encoding` 的优先级为显式设置、Content-Type charset、default_encoding，再回退 UTF-8（`_models.py:653-672`）。解码不是简单的 `bytes.decode()`，而是把协议 metadata 和用户配置纳入模型。
- multipart 文件上传拒绝 `StringIO` 与文本文件（`_multipart.py:158-165`），主动牺牲部分 Requests 宽松兼容，换取避免隐式字符编码问题。

## 亮点与问题

亮点是消息模型把 headers、body、stream、cookies 和错误上下文集中在稳定对象中；CLI、mock、ASGI/WSGI 都可以复用。问题是 `_models.py` 达 1,277 行，Headers、Request、Response、Cookies 四类职责较多；重新设计时可以保持公开对象不变，内部拆分 codec、stream state 和 cookie jar。

## 覆盖率明细

| 文件 | 有效代码行 | 已读行数 | 覆盖率 |
|---|---:|---:|---:|
| `httpx/_models.py` | 1,277 | 1,277 | 100% |
| `httpx/_content.py` | 240 | 240 | 100% |
| `httpx/_multipart.py` | 300 | 300 | 100% |
| **合计** | **1,817** | **1,817** | **100% / 达标** |
