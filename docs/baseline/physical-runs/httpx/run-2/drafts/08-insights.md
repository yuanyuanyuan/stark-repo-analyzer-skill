# Insights

## 系统性设计哲学

HTTPX 的核心哲学是：高层 API 保持熟悉，底层能力通过明确 transport 边界替换；默认路径简单，复杂路径通过显式 Client、Request、Transport 和 stream API 暴露。类型标注、严格 timeout 和状态异常把网络不确定性尽量转成可见契约。

## 亮点

最值得借鉴的是 transport 不是“插件系统”式的全局扩展，而是一个处理单请求的窄接口。它同时支持真实网络、测试 mock 和 ASGI/WSGI，使测试替换与生产实现共享模型。其次，`USE_CLIENT_DEFAULT` 解决了 Python API 中默认值与显式禁用的经典歧义。

## 风险与重设计

`_client.py` 与 `_models.py` 较大，sync/async 对称逻辑扩大维护面；未来可用共享的请求策略对象减少重复，但要保留清晰的同步/异步栈。其次，手动 streaming 的关闭责任虽文档明确，却仍容易造成连接泄漏；可考虑增加更强的上下文封装或诊断告警，但不能牺牲底层 streaming 的可组合性。
