# 08 Insights

## 系统性设计哲学

HTTPX 的主线不是“把所有 HTTP 功能放在一个 Client 里”，而是把请求生命周期分成四个稳定边界：

1. `BaseClient` 负责用户配置和策略合并；
2. `Request`/`Response` 负责可观察的消息状态与 stream 生命周期；
3. transport 负责把消息交给具体执行环境；
4. auth/decoder/exception flow 负责把协议过程翻译成可组合的高层结果。

这解释了为什么 CLI、mock、ASGI 和 WSGI 不需要复制一套 HTTP 业务流程：它们都消费相同的消息和 transport contract。

## 设计亮点

### 1. 双 API 共享语义，分离 I/O

`BaseClient` 集中配置合并，`Client`/`AsyncClient` 保持对应的 send、auth、redirect 和 close 结构。这降低了使用者的迁移成本，也避免把异步能力做成独立产品。代价是实现镜像明显，未来需要严格的同步/异步行为对照测试。

### 2. 显式生命周期比隐式读取更可控

Response 的 `read/iter/close` 与 `is_stream_consumed/is_closed` 让连接归还、内存占用和错误状态可见。对于大响应和长连接，这是比“所有 response 自动 bytes 化”更可控的默认模型；代价是 API 学习成本更高。

### 3. Transport 是扩展点而不是底层细节泄漏点

默认 transport 通过 httpcore，进程内 transport 通过 ASGI/WSGI，测试 transport 通过 Mock。上层不依赖这些实现的异常类型，而是由 adapter 映射到 HTTPX exceptions。这个边界是项目最适合被重用和测试的部分。

### 4. 兼容性是经过筛选的兼容

README 和 compatibility 文档承认 Requests 是 API 参考，但本地实现主动采用严格 timeout、显式 streaming、client-level cookie 和更窄的 multipart 文件输入。它不是“逐项兼容”，而是保留熟悉形状，同时修正容易导致隐性网络调用或编码问题的行为。

## 真实问题

- `_client.py` 把配置、proxy mounts、redirect、auth、stream 和多个 HTTP verbs 集中到单文件，扩展时容易产生局部修改影响全局行为。
- URL parser 自定义规范化逻辑具有较高正确性负担；任何 RFC/WHATWG 边界变化都需要大量回归测试。
- httpcore 是关键外部依赖，本报告无法从 httpx commit 解释连接池和协议细节。
- CLI optional dependencies 的错误路径清晰，但基础安装与 CLI 安装之间仍有额外心智分支。

## 如果重新设计

不建议改变 public API。可以在内部引入三个显式策略对象：`ConfigMerger`（base/request merge）、`RedirectPolicy`（history/next request）和 `TransportRouter`（URLPattern/mount）。这样可降低 `_client.py` 的聚合度，同时保留现有同步/异步镜像和 transport contract。

## 可迁移启发

- 先定义消息对象和生命周期，再选择执行环境；
- 用 adapter 隔离外部依赖异常和协议类型；
- 兼容性应记录主动不兼容的理由，而不是只列功能相同点；
- 对 streaming API，关闭时机和重复消费错误是核心设计，不是边缘情况。
