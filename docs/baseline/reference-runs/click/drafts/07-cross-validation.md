# 交叉验证

## 验证范围

本阶段回到入口、Context、Command/Group、Parameter、parser、types、termui 和官方概念文档，对草稿中的跨模块结论做一致性检查。验证只针对当前固定 commit，不使用 Git 历史。

## 已验证结论

1. **声明到执行链路成立**：`decorators.command/group` 生成 Command/Group；Command 通过 `make_context`、`parse_args`、`invoke` 进入 callback（`src/click/decorators.py:144-314`、`src/click/core.py:1322-1395`）。
2. **Group 参数边界成立**：Group 单独解析自身参数，再通过 `resolve_command` 找到子命令并创建子 Context；文档对参数必须位于所属命令位置的说明与实现一致（`src/click/core.py:1978-2086`；`docs/commands-and-groups.md:162-204`）。
3. **参数来源闭环成立**：Parameter 处理命令行、环境变量、默认映射、默认值和 prompt，并写入 `Context._parameter_source`；文档列出的优先级与 `ParameterSource` 顺序一致（`src/click/core.py:169-206`、`src/click/core.py:2470-2740`）。
4. **类型元数据复用成立**：`ParamType` 同时提供转换、显示信息和 shell completion；`formatting` 通过 Parameter usage pieces 消费这些信息（`src/click/types.py:42-183`、`src/click/core.py:2823-2846`）。
5. **资源生命周期成立**：File 类型和应用扩展通过 `Context.call_on_close`/`with_resource` 注册清理，Context 退出时关闭 ExitStack（`src/click/types.py:857-970`、`src/click/core.py:648-712`）。
6. **补全隔离成立**：ShellComplete 解析命令树，Context 的 resilient parsing 用于避免补全过程触发正常副作用（`src/click/shell_completion.py:216-326`、`src/click/core.py:480-500`）。

## 交叉洞察

Click 的统一抽象不是“所有功能都调用同一个函数”，而是“所有入口都围绕可观察的命令/参数元数据和 Context 运行”。help、completion、测试和运行时分发都能读取这套结构；这解释了为何显式注册和受限定制会被选作默认路线。

## 未完全验证项

- Windows 控制台行为只读了实现和兼容层，未在 Windows 运行。
- pager、编辑器启动、真实 shell completion 只做静态分析和 smoke 级验证，未在各 shell 进程中执行。
- 本次未启用 Agent 并行分析，无法提供独立 subagent 之间的结论对照。
- 外部竞品只做定位级资料读取，未完成 Typer、Docopt、Fire 的固定 commit 实现级横向分析。
