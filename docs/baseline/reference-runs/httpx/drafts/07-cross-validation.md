# 07 Cross-Validation

## 交叉验证方法

对每条跨模块结论至少检查一个上游和一个下游证据；关键路径回到固定 HEAD 的行号。测试目录只作为行为背景，不替代生产代码证据。

## 验证结果

| 结论 | 上游证据 | 下游证据 | 结果 |
|---|---|---|---|
| 函数式 API 复用 Client | `_api.py:39-120` 创建并关闭 Client | `_client.py:771-825` 构造并发送 Request | 通过 |
| Client 配置进入 Request extensions | `_client.py:340-389` 合并 timeout/headers/cookies/params | `_models.py:382-460` 保存 extensions 并编码 body | 通过 |
| transport 不承载 redirect/auth policy | `_client.py:930-1001` 先驱动 flow 再调用 transport | `_transports/base.py:26-86` 只有 request/close contract | 通过 |
| response stream 由 Client 绑定计时和 request | `_client.py:1001-1023` 包装 BoundSyncStream | `_models.py:935-976` 读取后 close | 通过 |
| sync/async 共享行为而分离 I/O | `_client.py:188-473` BaseClient 公共合并 | `_client.py:930-1034` 与 `1645-1749` 分别执行 sync/async | 通过 |
| URL pattern 支持代理和自定义 mount | `_client.py:685-716` 生成并排序 mounts | `_utils.py:120-227` pattern priority/matches | 通过 |
| ASGI/WSGI 是同一 transport contract 的适配器 | `_transports/base.py:26-86` contract | `_transports/asgi.py:99-187`, `wsgi.py:91-149` | 通过 |
| 解码发生在 Response streaming 层 | `_models.py:699-722` 选择 decoder | `_models.py:884-924` iter_bytes/iter_text | 通过 |
| CLI 复用核心 stream 能力 | `_main.py:478-499` 使用 `Client.stream()` | `_client.py:827-877` stream 上下文保证 close | 通过 |
| HTTPX 依赖 httpcore 而非内置连接池 | `pyproject.toml:30-35` 声明依赖 | `_transports/default.py:230-249`, `374-403` 调用 httpcore | 通过 |

## 关键结论抽查

1. “默认不自动跟随重定向”由 `BaseClient` 初始化的 `follow_redirects=False`（`_client.py:196-198`）和 `_send_handling_redirects()` 的分支（`_client.py:985-995`）共同支持，非只来自 README。
2. “流式 body 可复用”不能泛化为所有 stream。`Request.read()` 仅在读完后替换为 `ByteStream`（`_models.py:468-494`）；generator 二次消费仍会触发 `StreamConsumed`，因此报告使用“边界”而不是“任意可重放”。
3. “100% 覆盖”是 README/开发者文档的项目声明（`README.md:69-70`, `docs/contributing.md:142-151`），不是本次架构分析的代码执行覆盖率；本次 coverage 指源码读取覆盖率，二者已区分。

## 未通过或待验证

- 未验证 httpcore 内部连接池、协议、HTTP/2 和 proxy 的实际运行行为。
- 未验证 optional extra 的安装组合。
- 未验证官网当前内容是否与 `b5addb6` 完全一致。
- 未找到足以证明组织战略的固定版本一手资料。
