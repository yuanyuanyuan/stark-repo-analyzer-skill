# Module Narrative Plan

请求入口/Client →[把用户意图合并成可发送的 Request]→ Request/Response 模型 →[将稳定模型交给不同运行环境]→ Transport 边界 →[返回字节流后交给解码与生命周期管理]→ Content/Decoder →[把结果暴露为同步或异步用户体验]→ API/CLI。

核心模块：

1. Client lifecycle and request pipeline: `httpx/_client.py`, `httpx/_api.py`
2. Request/response models: `httpx/_models.py`, `httpx/_urls.py`
3. Transport boundary and adapters: `httpx/_transports/base.py`, `default.py`, `asgi.py`, `wsgi.py`, `mock.py`
4. Content and decoding: `httpx/_content.py`, `httpx/_decoders.py`, `httpx/_multipart.py`

次要模块：config/auth/exceptions/utils/status codes/types/CLI。
