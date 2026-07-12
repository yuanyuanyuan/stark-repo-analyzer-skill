# 阶段 5：模块识别与叙事线

## 整体设计哲学

Click 的贯穿性设计哲学是：**显式的命令组合 + 稳定的调用上下文 + 受约束的一致体验**。它把 CLI 从一次性字符串解析提升为可嵌套的命令对象图；同时限制某些“过度灵活”的行为，以保护帮助、错误、参数来源和扩展命令之间的一致性。

## 业务功能模块

| 模块 | 类型 | 文件范围 | 标准覆盖目标 | 责任假设 |
|---|---|---|---:|---|
| 命令模型与调用上下文 | 核心 | `src/click/core.py`, `src/click/decorators.py`, `src/click/globals.py`, `src/click/exceptions.py` | >=60% | 构建 Command/Group/Context，处理父子上下文、参数注入、命令 dispatch、错误出口和 decorator API。 |
| 参数解析与类型管线 | 核心 | `src/click/parser.py`, `src/click/types.py` | >=60% | 将 argv token 解析成选项/参数值，完成声明解析、类型转换、复合类型、Choice/Path/File 等校验。 |
| 终端 I/O 与跨平台适配 | 核心 | `src/click/termui.py`, `src/click/utils.py`, `src/click/formatting.py`, `src/click/_termui_impl.py`, `src/click/_compat.py`, `src/click/_textwrap.py`, `src/click/_winconsole.py`, `src/click/_utils.py` | >=60% | 提供 echo、颜色、prompt、pager、progress、文件和流处理，并隔离平台差异、编码和帮助排版。 |
| Shell completion 与命令发现 | 核心 | `src/click/shell_completion.py` | >=60% | 从当前 Context/Parameter 状态生成 Bash/Zsh/Fish completion，并与 Group 命令枚举、懒加载契约协作。 |
| 测试运行时与公共导出 | 次要 | `src/click/testing.py`, `src/click/__init__.py`, `src/click/py.typed` | >=30% | 通过 CliRunner 提供隔离输入输出/文件系统测试，并维护稳定的公共 API 导出面。 |

## 叙事主线

采用**数据流驱动**，从用户写下命令到 callback 返回值跟踪：

`装饰器声明` →[创建公开 Command/Group 与 Parameter 对象]→ `命令模型与 Context` →[为本次调用建立父子状态并确定待运行命令]→ `参数解析与类型管线` →[将 argv/envvar/default/prompt 合并为已转换值]→ `命令调用与错误出口` →[输出和资源生命周期交给终端层]→ `终端 I/O 与跨平台适配` →[将命令元数据暴露给交互式 shell]→ `Shell completion 与命令发现`。

测试运行时横切这条链：它通过 CliRunner 构造 argv、stdin、隔离目录和捕获策略，验证上述行为而不改变业务 callback。

## 相邻模块过渡

- 命令模型与 Context → 参数解析：Context 知道当前 Command 和参数容器，但需要 parser 把 token 变成参数来源可追踪的值。
- 参数解析与类型 → 终端 I/O：解析不只是转换字符串；prompt、文件、错误和帮助都要求终端层提供可移植的输入输出语义。
- 终端 I/O → Shell completion：终端交互不仅发生在执行时，completion 还需要复用命令/参数元数据，在“不执行 callback”的 resilient parsing 模式下推断用户意图。
- Shell completion → 测试运行时/公共导出：completion 和命令模型的契约必须可被测试 runner 验证，公共导出则把稳定边界交给应用作者。

## 阶段 6 调度

参考指南要求每个核心模块一个独立 Agent、次要模块合并一个 Agent。每个 Agent 只读取分配文件，并将草稿写入当前工作目录 `drafts/`；草稿必须包含全局角色、数据结构、Mermaid 流程、设计权衡、协作关系和覆盖率表。

由于 `core.py` 包含多个相互依赖的业务能力，将其整体分配给“命令模型与调用上下文”，避免两个 Agent 对同一文件产生覆盖率和结论冲突；parser/types、终端层、completion 各自保持文件边界清晰。

## secondary 模块实际收束重点

本次物理基线把最后一个模块收束为两条稳定性边界：`testing.py` 将全局解释器状态暂时替换为可观察、可恢复的 CLI 测试环境；`__init__.py` 则将跨模块实现压缩成稳定的 `click.*` 公共入口，并用 PEP 562 的惰性兼容分支承接旧名字。`py.typed` 是包级类型分发标记，但固定树中实际为 0 行空文件。

`testing.py` 对其他模块的调用（`formatting.FORCED_WIDTH`、`termui` prompt hook、`utils`/`_compat` 的 ANSI 判定、`Command.main`）全部来自分配文件中的导入和调用点；由于本次禁止阅读这些实现，交叉结论统一标注【待主 agent 验证】。
