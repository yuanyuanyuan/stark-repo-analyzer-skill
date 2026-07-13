# 交叉验证与质量门控

## 验证范围

阶段 6 的四个独立 subagent 草稿均已完成。本阶段回到固定源码 HEAD
`b67832c2167e5b0ff6764a8c04a0a9087e697b5a`，核对模块之间的关键连接、Graphify
导航证据和覆盖率边界。源码仓库在验证前后均保持 clean。

## 源码裁决

1. **声明到执行链路成立。** `decorators.command/group` 将函数和装饰器参数物化为
   `Command/Group`，`Command.main -> make_context -> parse_args -> invoke` 负责
   上下文、解析和 callback 生命周期（`src/click/decorators.py:144-378`；
   `src/click/core.py:1220-1457`）。
2. **Group 的参数归属成立。** Group 先解析自己的参数，再由 `resolve_command`
   找到子命令并创建子 Context；文档关于参数必须位于所属命令位置的说明与实现一致
   （`src/click/core.py:1978-2086`；`docs/commands-and-groups.md:162-204`）。
3. **参数来源闭环成立。** `Parameter` 统一处理命令行、环境变量、`default_map`、
   默认值和 prompt，并将来源写入 `Context._parameter_source`；`ParameterSource`
   是运行时枚举而非报告层推断（`src/click/core.py:169-206,2470-2740`）。
4. **类型协议复用成立。** `ParamType` 同时提供转换、错误消息、metavar、环境变量
   拆分和 completion 元数据；help/usage 通过 Parameter 消费同一协议
   （`src/click/types.py:42-183`；`src/click/core.py:2823-2846`）。
5. **资源生命周期成立。** 文件类型和扩展能力通过 `Context.with_resource` 或
   `call_on_close` 注册清理，Context 退出时关闭 `ExitStack`
   （`src/click/core.py:648-712`；`src/click/types.py:857-970`）。
6. **completion/test 隔离成立。** shell completion 读取命令树并启用 resilient
   parsing，`CliRunner` 则替换输入、输出、环境和文件系统再调用真实 command 入口
   （`src/click/shell_completion.py:216-326`；`src/click/testing.py:231-316`；
   `src/click/core.py:480-500`）。

## Graphify 与源码边界

- Graphify `0.9.13` 的 code-only raw graph 为 1910 nodes / 3916 edges，normalized
  graph 为 1907 nodes / 3916 edges；post-graph doctor 报告 1813 个节点和 3916 条边
  有 source references。它适合定位入口和关系候选，不替代源码阅读。
- 对 `cli()`、`Command`、`Context` 等高连接节点，Graphify 生成了大量 inferred/community
  关系；本轮没有把这些关系直接写成架构事实。最终结论均回到源码和项目文档核对。
- 发现 94 个 normalized 节点没有可定位 symbol source reference；这属于图谱质量边界，
  不影响已由源码确认的核心结论，已保留在 Graphify health 中。

## 覆盖率与限制裁决

- 三个核心模块均达到 standard 的 60% 门槛；次要模块达到 30% 门槛，但 `_compat.py`
  和 `_termui_impl.py` 的部分平台实现只做了关键区段阅读，不能写成全平台行为已验证。
- Windows 控制台、真实 Bash/Zsh/Fish completion、pager/editor 和多进程终端行为没有
  在本轮执行；它们在报告中标为静态证据或待验证。
- 外部资料仅用于 Click 官方定位和设计文档背景；Typer、Docopt、Python Fire 等未固定
  commit 做实现级横向分析，因此竞品部分保持定位级比较。
- `06-module-tasks.json` 的初始状态曾滞留为 pending，但 `subagent-dispatch.json` 和
  四个草稿均显示 subagent 已完成；本阶段已将任务 manifest 回写为 completed，避免
  控制面状态与实际产物不一致。

## 跨模块结论

Click 的统一抽象不是“所有功能调用一个函数”，而是所有入口围绕可观察的
`Command/Parameter/Context` 元数据协作：执行负责消费它，help/completion/test 负责投影
它，Context 负责隔离状态和资源。这解释了 Click 为什么能在较短声明 API 下支持嵌套命令，
也解释了 `core.py` 和 Context 状态面为何持续较大。
