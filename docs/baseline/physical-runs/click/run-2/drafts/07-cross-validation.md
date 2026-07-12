# Click 阶段 7 交叉验证

## 验证范围

- 固定源码：`/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click`
- 固定 HEAD：`b67832c2167e5b0ff6764a8c04a0a9087e697b5a`
- 验证方式：读取五份模块草稿的结论与覆盖率表，回到源码按行抽查跨模块契约；补充不改变源码的运行时 smoke。
- 禁止项：未读取 Git 历史，未修改源码，未使用目标项目 `graphify-out`。

## 覆盖率门控

| 模块草稿 | 实现文件 | 有效行数 | 已读行数 | 覆盖率 | 标准门槛 | 结果 |
|---|---|---:|---:|---:|---:|---|
| 命令树与调用上下文 | `core.py`, `decorators.py` | 4,350 | 4,350 | 100% | 60% | 达标✅ |
| Parser 与参数类型 | `parser.py`, `types.py` | 1,908 | 1,908 | 100% | 60% | 达标✅ |
| 终端 UI 与格式化 | 4 个指定文件 | 2,413 | 2,413 | 100% | 60% | 达标✅ |
| Shell completion | `shell_completion.py` | 704 | 704 | 100% | 60% | 达标✅ |
| 支持、异常、测试与文件工具 | 8 个指定文件 | 2,913 | 2,913 | 100% | 30% | 达标✅ |
| **合计** | **全部 src/click 实现** | **12,288** | **12,288** | **100%** | **按模块门槛** | **达标✅** |

五份草稿末尾均存在覆盖率表；大文件按分段读取，未发现只读小片段却声称达标的模块。

## 抽查后的跨模块契约

### 1. Context → parser → Parameter → ParamType

`Command.make_context` 创建 Context 后在不清理 scope 中执行 `parse_args`（`src/click/core.py:1322-1357`）。`Command.parse_args` 接收 parser 的 `opts, args, param_order`，按 eager/命令行出现顺序调用参数的 `handle_parse_result`（`src/click/core.py:1359-1393`）。parser 本身只负责 token 归属、原始值和出现顺序；`Parameter.consume_value` 再按命令行、环境变量、`default_map`、默认值取值，`type_cast_value` 调用 `ParamType`（`src/click/core.py:2470-2572`）。

这验证了模块叙事中的主边界：Click 没有把所有语义塞进 parser，而是让 parser 保持窄状态机，把来源仲裁、组合类型和回调放在 Parameter/ParamType 层。`Option.consume_value` 还在该边界处理 `FLAG_NEEDS_VALUE`、prompt 和 flag value（`src/click/core.py:3507-3567`），因此 parser 草稿中对 sentinel 的“上层解释”判断准确。

### 2. Context → globals → cleanup

`Context.__enter__`/`__exit__` 调用 `push_context`/`pop_context`，最外层 depth 为零时 unwind `ExitStack`（`src/click/core.py:549-566`）。`globals.py` 使用 `threading.local()` 保存 stack（`src/click/globals.py:9-51`），所以“当前上下文”是线程局部而不是进程全局；但它不是异步任务局部，也不能把并发使用 Click runner 变成安全操作。异常显示时 `ClickException` 会在构造时缓存颜色配置，再由 `main` 在 Context 已准备的边界输出（`src/click/exceptions.py:44-65`, `src/click/core.py:1557-1589`）。

### 3. Command/Group → shell completion → ParamType

Shell completion 的 `_resolve_context` 设置 `resilient_parsing=True`，用 `make_context` 沿 Group 链建立 Context，不触发交互式 callback（`src/click/shell_completion.py:599-657`）。`ShellComplete.get_completions` 将当前目标委派给 `obj.shell_complete`（`src/click/shell_completion.py:292-304`）。源码抽查确认 Group 生成命令名候选（`src/click/core.py:2086-2103`），Path 类型返回 `CompletionItem(..., type="file")`（`src/click/types.py:971-985`），Choice 类型由 ParamType 处理归一化后的候选语义（`src/click/types.py:330-418`）。因此 completion 草稿的核心判断成立：shell 协议适配层不复制参数业务规则，而消费统一对象协议。

### 4. Terminal UI → support layer

`termui.prompt` 将完整 prompt 直接交给 input/getpass，转换通过 `convert_type` 或调用方传入的 `value_proc`（`src/click/termui.py:84-104`, `107-142`, `194-242`）。pager 的统一入口按 TTY/PAGER/平台选择 `_nullpager`、pipe 或临时文件；`get_pager_file` 只对暴露 `.buffer` 的文本流构造 `MaybeStripAnsi` wrapper（`src/click/_termui_impl.py:400-468`）。这验证了终端草稿对“门面 + 支持层 + 布局内核”的描述，同时暴露下方两个已验证缺陷。

## 已验证的真实风险

### A. 原子写异常路径会提交内容

`_AtomicFile.__exit__` 把异常状态传给 `close(delete=True)`，但 `close` 的 `delete` 参数没有分支，始终执行 `os.replace`（`src/click/_compat.py:455-485`）。在当前工作目录内执行的等价 smoke 结果为 `atomic_after_exception='new'`，即旧文件被新内容替换。该结果与次要模块草稿的风险判断一致，不能再写成仅凭静态代码的猜测。

### B. 临时文件 pager 的文本/二进制契约不闭合

`_tempfilepager` 创建 `NamedTemporaryFile(mode="wb")` 并把它直接 yield；`get_pager_file` 的 `.buffer` 检查无法把该 wrapper 变成文本 wrapper，`termui.echo_via_pager` 随后写入 `str`（`_termui_impl.py:580-633`, `432-467`; `termui.py:339-355`）。等价 smoke 结果为 `pager_status=error`、`TypeError: a bytes-like object is required, not 'str'`。当前环境未进行真实 Windows 控制台验证，因此 Windows 端到端状态记录为 `not performed`，但实现级缺陷已复现。

## 运行时与源码结论的对照

- 正常 CLI：通过 `CliRunner` 调用带 `Choice` option 的嵌套命令，`runner_exit=0`、输出为 `alice\n`。
- Shell completion：设置 Bash completion 所需的 `COMP_WORDS`/`COMP_CWORD` 后，输出 `plain,alice` 和 `plain,bob`，返回状态 0。
- 参数错误：整数 option 输入 `bad` 产生 `BadParameter: 'bad' is not a valid integer.`，验证统一类型错误路径。
- 无效的 completion 环境：未设置 `COMP_WORDS` 时直接调用 Bash completion 会抛 `KeyError`；这是调用方未提供 shell 协议环境的预期前置条件，已记录为失败 smoke，不作为 Click 在真实 shell 中的缺陷。

## 交叉验证结论

模块草稿之间没有发现命令树、参数来源、completion 委派或资源清理方向上的矛盾。整体设计可以归纳为：用对象化元数据建立单一语义源，用 Context 把局部状态和生命周期绑定在调用树上，再让终端、补全、文件工具和测试围绕这些协议做适配。代价是隐式线程局部状态、跨层调用链和平台边界较多；本次基线还实际暴露了两个支持层边界缺陷，说明“统一协议”在异常退出和临时文件路径上仍需要更强测试门禁。
