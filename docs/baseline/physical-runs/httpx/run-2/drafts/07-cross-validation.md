# Cross Validation

1. Client 与 transport 的边界在代码和文档中一致：Client 处理重定向、hooks、配置和生命周期，transport 处理单次请求；`advanced/transports.md` 明确要求 transport 使用 Request/Response。
2. 流式语义贯穿模型、client 和 async 文档：Response 流关闭时记录 elapsed，手动 streaming 由调用方负责关闭，说明资源生命周期不是 transport 的隐式副作用。
3. sync/async 并非两个不同产品：`Client`/`AsyncClient`、`BaseTransport`/`AsyncBaseTransport`、同步/异步 stream 形成结构对称，减少用户迁移成本；代价是双路径维护。
4. README 的“requests-compatible + HTTP/2 + async + ASGI/WSGI”定位均能在源码边界找到对应实现，未发现仅文档宣称而无本地代码支撑的核心能力。

未执行：跨模块抽查的完整逐行覆盖门控、外部竞品核验、Git 历史演进核验。
