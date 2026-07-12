# 阶段 7：跨模块交叉验证

## 覆盖率门控

全部 5 个模块草稿均有文件级覆盖率表，合计行标注达标。主 agent 读取了这些表，并回到固定源码对关键边界做抽查；不需要补读，所有模块均为 100% 行覆盖。

| 模块 | 类型 | 有效行 | 已读行 | 覆盖率 | 门槛 | 结果 |
|---|---|---:|---:|---:|---:|---|
| command-model | 核心 | 4,795 | 4,795 | 100% | 60% | 达标✅ |
| parse-types | 核心 | 1,908 | 1,908 | 100% | 60% | 达标✅ |
| terminal-io | 核心 | 3,982 | 3,982 | 100% | 60% | 达标✅ |
| shell-completion | 核心 | 704 | 704 | 100% | 60% | 达标✅ |
| secondary | 次要 | 899 | 899 | 100% | 30% | 达标✅ |
| **合计** | - | **12,288** | **12,288** | **100%** | - | **达标✅** |

## 关键结论抽查

### 1. Context、解析和 callback 的边界

已验证：`Command.make_context` 创建 Context、调用 `parse_args`，明确不调用 callback（`src/click/core.py:1322-1357`）。`Command.parse_args` 调用 `_OptionParser.parse_args`，再按 `param_order` 调用 Parameter 的 `handle_parse_result`（`src/click/core.py:1359-1393`）。这支持“对象描述结构、Context 承载调用、参数管线提供值”的主结论。

### 2. Group 的父子调用顺序

已验证：普通 Group 和 chain Group 的 dispatch、父 callback、子 Context、结果回调和返回值聚合位于 `src/click/core.py:1886-1929,1992-2058`；Context 初始化对 `obj`、meta、terminal width、default map 和 parser flags 的继承位于 `src/click/core.py:378-503`。草稿的 Context 链叙事和 Group 顺序没有事实偏差。

### 3. Parser 与 ParamType 的契约

已验证：`_OptionParser` 的文档明确它只负责 options/arguments，不负责 types/defaults（`src/click/parser.py:224-239`）；其输出包含 values、leftovers 和 order（`298-314`），`allow_interspersed_args` 与 `ignore_unknown_options` 由 Context 控制（`245-258,327-341`）。`ParamType.__call__` 转入 `convert` 并通过 `fail` 产生 `BadParameter`（`src/click/types.py:101-165`），而 Parameter 的来源、类型、required、callback和 feature-switch 仲裁位于 `src/click/core.py:2470-2656,2719-2805`。因此 parse-types 草稿关于“两阶段管线”的结论成立。

### 4. 类型与终端资源

已验证：`File.convert` 根据 lazy/atomic 选用 `LazyFile` 或 `open_stream`，并通过 `ctx.call_on_close` 注册关闭（`src/click/types.py:857-969`）；`utils.open_file` 对 `-`、lazy 和借用标准流提供 `KeepOpenFile`（`src/click/utils.py:375-421`）。这闭合了 parse-types 与 terminal-io 之间的资源协作，不再把它当作未验证推断。

### 5. 终端能力与非交互降级

已验证：`utils.echo` 统一处理流、bytes、ANSI 剥离和 flush（`src/click/utils.py:245-340`）；pager 在非 TTY 时走 null pager，在 TTY 时按平台和 PAGER 选择后端（`src/click/_termui_impl.py:400-428`）。terminal-io 草稿关于“能力判定而不是环境假设”的结论成立。Unicode cell 宽度和额外终端控制序列仍是静态分析提出的风险，不是已运行验证的缺陷。

### 6. Completion 与正式命令模型

已验证：`Command.main` 检测 completion 环境变量后导入 `shell_completion` 并提前退出（`src/click/core.py:1591-1621`）；`_resolve_context` 使用 `make_context(..., resilient_parsing=True)`，沿 Group 链创建子 Context 而不触发 callback（`src/click/shell_completion.py:599-657`）。Command、Choice、Path/File 可返回 `CompletionItem`（`src/click/core.py:1411-1456`；`src/click/types.py:437-457,971-985,1173-1189`）。因此“completion 是正式 runtime 的受控投影”已由跨文件证据支持。

### 7. Testing runner 与运行时 hook

已验证：`CliRunner.isolation` 替换 stdin/stdout/stderr、prompt/getchar、ANSI hook、环境变量并在 finally 恢复（`src/click/testing.py:435-595`）；`invoke` 执行 `cli.main`，区分 SystemExit/普通异常并在 finally flush、停止 fd 捕获、构造 Result（`src/click/testing.py:596-739`）。`__init__.py` 的公共重导出和兼容动态属性位于 `src/click/__init__.py:10-127`。secondary 草稿的测试协议和公共边界判断成立。

## 结论与修正

- 未发现需要修正的核心事实性结论。
- 将 subagent 共享文件中“未使用 Agent”“只覆盖单模块”的陈旧表述改为本次实际执行情况；根目录汇总文件由主 agent 重写，不使用 subagent 早期生成的单模块 metadata/report。
- 保留模块草稿中的【待主 agent 验证】作为模块局部证据边界；凡属于跨模块主线的内容已在本文件给出源码行号验证。

## 残余限制

本轮没有运行行为测试、真实 shell、Windows console 或并发 runner；因此不能把静态证据表述为运行时通过。外部竞品定位来自官方文档，不包含 GitHub issue/社区讨论或历史演进证据。
