# 模块计划与报告叙事

## 模块清单

### 核心模块

1. **命令模型与上下文执行**：`core.py`、`decorators.py`。负责把 Python 函数变成命令树，创建父子 Context，解析后分发回调，并管理资源清理。
2. **参数解析与类型转换**：`parser.py`、`types.py`，并消费 `core.py` 中的 `Parameter`、`Option`、`Argument`。负责把 argv、环境变量、默认值和 prompt 汇聚为已校验的 Python 值。
3. **终端交互与帮助输出**：`termui.py`、`formatting.py`、`utils.py`。负责可见输出、提示、确认、进度条、文件流、ANSI 和帮助文本布局。

### 次要模块

4. **Shell completion**：`shell_completion.py`，把命令树和参数类型投影为 Bash/Zsh/Fish 的补全协议。
5. **测试隔离与调用验证**：`testing.py`，为 CLI 提供输入、输出、环境、文件系统隔离和结果封装。
6. **平台、异常与基础设施**：`_compat.py`、`_termui_impl.py`、`_winconsole.py`、`_textwrap.py`、`_utils.py`、`globals.py`、`exceptions.py`、`__init__.py`。

## 报告大纲

1. 场景与定位：为什么“可组合 CLI”需要完整运行时，而不只是 parser。
2. 项目全景：声明 API、命令树、上下文、解析器、交互和测试之间的边界。
3. 主流程：装饰器声明 → 命令树 → Context → parser/types → callback → cleanup。
4. 核心设计一：Context 如何把父子命令、参数来源和资源生命周期统一起来。
5. 核心设计二：显式参数模型如何让解析、类型、help、completion 共用元数据。
6. 核心设计三：CLI 的可组合性如何约束帮助格式、参数交错和扩展方式。
7. 次要能力：终端、completion、测试、平台兼容和异常边界。
8. 评价与启发：亮点、真实代价、重新设计建议和待验证项。

## 叙事线

装饰器声明 API →[需要一个可执行的命令树]→ 命令模型与上下文 →[命令执行前必须把文本变成可靠值]→ 参数解析与类型转换 →[错误、help 和交互必须对用户可见]→ 终端交互与帮助输出 →[同一元数据可以投影给 shell]→ completion →[同一执行模型需要可重复验证]→ 测试隔离。

这条线按用户输入的数据流组织，不按源码目录顺序组织。平台兼容、异常和导出 API 作为支撑层收尾，以免把读者注意力从主执行模型带走。

## 关键探索问题

- 为什么 Click 选择显式 Command/Group/Context，而不是仅暴露 parse 函数？
- 参数来源优先级如何影响可预测性和脚本化使用？
- `Context` 的共享状态、退出栈和线程边界如何限制扩展方式？
- 类型元数据如何同时服务转换、错误、help 和 completion？
- Click 对可定制性的主动限制换来了什么，又牺牲了什么？
