# 06 Module: CLI and Public API Contract

## 角色

这是次要模块：它把核心 Client 能力包装成终端用户入口，并维护稳定的导出名、类型别名、状态码和异常分类；不重新实现网络流程。

## CLI

`_main.py` 使用 Click 解析 URL、method、params、content、data、files、json、headers、cookies、auth、proxy、timeout、redirect、verify、HTTP/2、download 和 verbose 参数（`_main.py:313-470`）。`main()` 创建 Client，再调用 `client.stream()`；响应可以下载到文件或根据 Content-Type 用 Pygments/Rich 输出，网络错误转为终端错误码（`_main.py:452-506`）。

这条实现路径很重要：CLI 不维护第二套请求/stream 逻辑，而是复用核心 public client。代价是 CLI 的可用性依赖 Click、Rich、Pygments optional extras（`pyproject.toml:43-47`）。

## 公共契约

`__init__.py` 聚合 `_api`、`_client`、`_models`、`_transports` 等模块并列出 `__all__`，还对缺少 CLI extra 的情况提供可执行的失败提示（`httpx/__init__.py:1-26`, `29-106`）。`_types.py` 用类型别名描述 Header、Cookie、RequestContent、Sync/AsyncByteStream 等边界，支撑 strict mypy 配置（`pyproject.toml:108-115`）。

`codes` 用 IntEnum 保存状态码和 reason phrase，并提供按 1xx-5xx 分类的方法，同时生成小写别名以兼容 Requests（`_status_codes.py:8-162`）。异常树则为调用者提供按层级捕获的稳定契约（`_exceptions.py:1-71`）。

## 评价

亮点是公共面集中导出、CLI 复用核心路径、状态码和异常具有语义层级。问题是 `__init__.py` 的星号导入让导出依赖隐式，CLI 的 rich/pygments 也会让“安装基础包后执行 `httpx`”出现额外依赖分支；当前代码通过 ImportError fallback 处理，但体验仍然依赖安装选项。

## 覆盖率明细

| 文件 | 有效代码行 | 已读行数 | 覆盖率 |
|---|---:|---:|---:|
| `httpx/_main.py` | 506 | 506 | 100% |
| `httpx/_exceptions.py` | 377 | 377 | 100% |
| `httpx/_status_codes.py` | 162 | 162 | 100% |
| `httpx/_types.py` | 114 | 114 | 100% |
| `httpx/__init__.py` | 106 | 106 | 100% |
| `httpx/__version__.py` | 3 | 3 | 100% |
| **合计** | **1,268** | **1,268** | **100% / 达标** |
