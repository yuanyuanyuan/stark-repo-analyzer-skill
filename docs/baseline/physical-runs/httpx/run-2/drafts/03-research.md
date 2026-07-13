# Research Draft

## 项目解决的核心问题

HTTPX 面向需要可靠 HTTP 调用的 Python 应用：既要保持 requests 风格的易用性，又要覆盖 HTTP/2、严格超时、连接池、流式传输和 async 场景。README 将其定位为“next-generation HTTP client”，并明确提供同步与异步 API、命令行客户端以及 WSGI/ASGI 直连能力。

## 竞品定位

本地源码确认的比较基准是 requests（兼容的高层 API）、urllib3（底层网络设计灵感）和 httpcore（HTTPX 的底层 transport 实现）。外部项目的当前实现与性能数据未调研，标记为未找到。HTTPX 的差异不在于重新实现全部协议，而在于把稳定的 Request/Response 模型与可替换 transport 边界组合起来，并对 sync/async 提供平行接口。

## 为什么需要单独做这个项目

requests 的同步体验无法直接覆盖 async 与 HTTP/2；直接让业务依赖底层协议库又会暴露连接池、编码、重定向和生命周期细节。HTTPX 在高层保留熟悉的调用方式，同时将网络实现下沉到 `httpcore`，使测试替身、ASGI/WSGI 调用和真实网络共享同一客户端契约。

## 组织动机

源码与 README 显示其属于 Encode 生态，强调类型标注、严格超时、测试覆盖和与 requests 的兼容迁移。社区与商业背景未通过外部资料验证。
