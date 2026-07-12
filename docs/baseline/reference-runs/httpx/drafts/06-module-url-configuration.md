# 06 Module: URL, Query Parameters and Runtime Configuration

## 读者问题

用户传入的字符串、相对 URL、代理、环境变量和 timeout，如何变成确定且可组合的请求语义？

## 规范化层

`urlparse()` 先做长度和控制字符校验，再拆分 scheme/authority/path/query/fragment，随后完成 host 编码、端口归一化、路径校验和 percent-encoding（`httpx/_urlparse.py:213-345`）。IPv4、IPv6、ASCII host 和 IDNA host 分别处理（`_urlparse.py:348-392`）。URL 对外提供 raw 与 str 属性、copy_with 和 QueryParams 视图（`_urls.py:15-418`）。

`QueryParams` 以不可变风格提供 set/add/remove/merge，保留多值 key 的编码结果（`_urls.py:420-641`）。`BaseClient._merge_url()` 强制 base URL 末尾 `/`，并对相对路径去除前导 `/` 后拼接（`_client.py:391-411`）。这使 base URL 语义可预测，但与普通 filesystem join 不同，必须在文档中明确。

## 配置与路由

`Timeout` 支持单值或 connect/read/write/pool 分项，`Limits` 管理连接池上限，`Proxy` 保存 proxy URL、认证和 SSL context（`_config.py:72-248`）。`get_environment_proxies()` 读取 HTTP(S)_PROXY、ALL_PROXY 和 NO_PROXY，并用 `URLPattern` 做匹配/优先级排序（`_utils.py:30-237`）。Client 将这些 pattern 排序后在 `_transport_for_url()` 中选择 transport（`_client.py:685-769`）。

## Why > What

- URL 采用 canonical parsed representation，所有属性从同一 `ParseResult` 推导，减少“字符串表现”和“传输字段”不一致的可能（`_urlparse.py:315-345`）。
- 默认端口被省略、路径 `.`/`..` 被规范化、IDNA 被编码，减少代理匹配和 origin 判断中的等价 URL 分歧（`_urlparse.py:395-475`）。
- 代理不是 Client 中的一组 if/else，而是 URLPattern → transport 的通用 mount 机制。这样 mounts 不只支持 proxy，也能支持按 scheme/domain 路由自定义 transport（`_client.py:697-716`, `760-769`）。
- timeout 默认覆盖网络操作，且可以显式传 `None` 禁用。官方 compatibility 文档将这与 Requests 的无默认 timeout 区分开来；动机是避免网络调用无限等待，但具体生产事故背景未找到。

## 亮点与问题

亮点是把 URL 标准化、配置对象和 transport 路由连成单一语义链。问题是 URL parser 自定义实现复杂，且 `_urls.py` 与 `_urlparse.py` 合计 1,168 行；维护 RFC/WHATWG 边界需要较高测试投入。另一个边界是环境代理行为依赖运行环境，当前分析只验证代码路径，没有运行外部代理。

## 覆盖率明细

| 文件 | 有效代码行 | 已读行数 | 覆盖率 |
|---|---:|---:|---:|
| `httpx/_urls.py` | 641 | 641 | 100% |
| `httpx/_urlparse.py` | 527 | 527 | 100% |
| `httpx/_config.py` | 248 | 248 | 100% |
| `httpx/_utils.py` | 242 | 242 | 100% |
| **合计** | **1,658** | **1,658** | **100% / 达标** |
