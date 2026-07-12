# 次要模块：completion、测试与平台基础设施

## Shell completion

`ShellComplete` 把当前命令树、已输入参数和不完整 token 解析成 shell-specific 输出；Bash、Zsh、Fish 只负责协议差异，共享 completion 上下文和 `CompletionItem`（`src/click/shell_completion.py:67-468`）。`_resolve_context` 与 `_resolve_incomplete` 复用 Command/Group/Parameter 的结构，说明 completion 不是另一个 parser，而是命令模型的只读投影（`src/click/shell_completion.py:599-704`）。

边界是 resilient parsing：Context 在补全场景忽略副作用和默认值，避免为了生成候选项执行真实 callback（`src/click/core.py:480-500`、`src/click/core.py:1591-1623`）。亮点是类型也能提供文件/目录候选；问题是 shell 协议和命令解析状态存在双重边界，新增参数行为必须同时考虑正常执行和补全。

## 测试隔离与调用验证

`CliRunner` 提供 `invoke`、环境覆盖、stdin、stdout/stderr 捕获和临时文件系统；`Result` 封装输出、异常、退出码和 return value（`src/click/testing.py:231-316`、`src/click/testing.py:317-772`）。它把真实 CLI 的进程级交互压缩为可重复的函数调用，测试可以验证 help、错误、环境变量和多命令链路。

设计代价是隔离通过替换运行时流、环境和当前目录实现，不等价于真实子进程；涉及终端、信号或多进程的行为仍需更高层测试。`pyproject.toml:83-105` 可验证项目启用 pytest 和 branch coverage，但本次没有运行完整覆盖率报告，因此不把测试覆盖率写成事实。

## 平台、异常与基础设施

| 文件 | 作用 | 关键边界 |
|---|---|---|
| `_compat.py` | 终端宽度、ANSI、TTY、Windows/Unix 差异 | 平台检测和流属性必须被高层 UI 消费。 |
| `_termui_impl.py` | pager、progress bar、终端实现 | 非 TTY 只输出标签，避免控制序列污染。 |
| `_winconsole.py` | Windows 控制台 Unicode/流包装 | 仅在 Windows 路径启用，当前环境未执行 Windows 行为。 |
| `_textwrap.py` | 面向可见字符和 ANSI 的文本换行 | 被 formatter 间接使用。 |
| `_utils.py` | 内部 sentinel 和解析 flag | 为 core/types 提供实现细节，不是公共业务 API。 |
| `globals.py` | 当前 Context 栈和颜色默认值 | 线程/上下文边界由调用方维护。 |
| `exceptions.py` | Abort、Exit、UsageError 及参数错误层次 | 将 Python 异常映射到 CLI 退出和错误输出。 |
| `__init__.py` | 公共 API 聚合与兼容属性 | 维持用户从 `click` 顶层导入的稳定性。 |

这些文件共同形成“跨平台但保持上层模型不变”的支撑层。它们不单独决定 Click 的业务架构，但决定核心模块能否在终端、管道、Windows 和测试环境中保持一致。

## 覆盖率

| 文件 | 总行数 | 已读行数 | 覆盖率 | 未读原因 |
|---|---:|---:|---:|---|
| `_compat.py` | 590 | 240 | 40.7% | 后续平台分支未逐行深入，已超过次要门槛。 |
| `_termui_impl.py` | 945 | 380 | 40.2% | 进度条核心状态已读，余下渲染辅助分支未逐行深入。 |
| `_winconsole.py` | 297 | 297 | 100% | 无 |
| `_textwrap.py` | 188 | 188 | 100% | 无 |
| `_utils.py` | 36 | 36 | 100% | 无 |
| `globals.py` | 67 | 67 | 100% | 无 |
| `exceptions.py` | 378 | 378 | 100% | 无 |
| `__init__.py` | 127 | 127 | 100% | 无 |
| **合计** | **2628** | **1713** | **65.2%** | **达标 ✅** |
