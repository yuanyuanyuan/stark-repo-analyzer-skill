# 06 Module: Authentication, Decoding and Error Propagation

## 读者问题

请求发送后，认证挑战、压缩内容、字符编码和异常如何沿同一条生命周期返回给调用者？

## Authentication

`Auth` 把认证表达为 generator flow：先 yield request，收到 response 后可以继续 yield 下一请求；同步和异步 flow 由默认适配器包装（`httpx/_auth.py:22-111`）。Basic、NetRC、Digest 和 FunctionAuth 共享这个边界（`_auth.py:113-348`）。Client 在 `_send_handling_auth()` 中驱动 flow，并在每次二次请求前读取旧 response、维护 history、捕获并关闭异常响应（`_client.py:930-962`, `1645-1677`）。

这比在 Client 里写死 Basic/Digest 分支更可扩展，但认证插件必须遵守 stream 可重放和 response 生命周期约束。

## Decoding

`_decoders.py` 将 gzip、deflate、Brotli、zstd 和 identity 统一为 `ContentDecoder`，`MultiDecoder` 按 response header 的编码列表组合解码；`TextDecoder` 处理字符编码和分块边界，`LineDecoder` 处理换行（`httpx/_decoders.py:1-393`）。Response 在 `iter_bytes()` 中先解压、再按 chunk size 输出，在 `iter_text()` 中继续做字符解码（`httpx/_models.py:699-722`, `884-924`）。

## 错误传播

异常层级把 HTTPError、RequestError、TransportError、Timeout、Network、Protocol、Decoding、Redirect 和 HTTPStatusError 分开；`request_context()` 将当前 request 附着到 RequestError（`httpx/_exceptions.py:74-120`, `243-377`）。这样调用者可以按网络超时、协议错误或业务 HTTP 状态分别处理，而不暴露 httpcore 异常类型。

## Why > What

- generator auth flow 同时容纳无认证、一次性 header 认证和挑战-响应认证；代价是 control flow 比直接返回 header 更难理解。
- decoder 与 Response stream 解耦，允许压缩解码、文本解码和行切分在不同阶段组合；如果先把 body 全部 decode，会失去大响应的流式能力。
- RequestError 通过上下文附着 request，避免 transport 层每次都显式包装错误；边界是只有被 `request_context()` 包住的路径才能自动保留上下文。

## 亮点与问题

亮点是把“重试/二次请求”和“分块内容处理”都建模为可推进的 flow，而不是在公共 API 层做特殊情况。问题是 DigestAuth、压缩解码和 async/sync 双路径都增加了状态空间；重新设计时可以保留 flow contract，并为每个 flow 提供可观测的状态事件。

## 覆盖率明细

| 文件 | 有效代码行 | 已读行数 | 覆盖率 |
|---|---:|---:|---:|
| `httpx/_auth.py` | 348 | 348 | 100% |
| `httpx/_decoders.py` | 393 | 393 | 100% |
| **合计** | **741** | **741** | **100% / 达标** |
