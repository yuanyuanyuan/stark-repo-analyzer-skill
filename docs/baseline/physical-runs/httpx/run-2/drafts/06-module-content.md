# Content and Decoding

`_content.py` 将 bytes、str、JSON、表单、multipart 和同步/异步迭代器统一为 ByteStream；`_decoders.py` 用可组合 decoder 处理 gzip/deflate/brotli/zstd、文本编码、分块和按行迭代。这样 Request 的发送格式与 Response 的消费格式都能以流为中心工作。

关键权衡是“流式优先但提供便利属性”：`.content`/`.text`/`.json()` 适合常规调用，`iter_*` 适合大响应；Response 明确要求调用方在手动 streaming 时关闭，换取连接复用和低内存占用。

## 覆盖率明细

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| httpx/_content.py | 240 | 180 | 75.0% | 采样读取 |
| httpx/_decoders.py | 393 | 300 | 76.3% | 采样读取 |
| httpx/_multipart.py | 300 | 180 | 60.0% | 采样读取 |
| 合计 | 933 | 660 | 70.7% | 达标✅ |
