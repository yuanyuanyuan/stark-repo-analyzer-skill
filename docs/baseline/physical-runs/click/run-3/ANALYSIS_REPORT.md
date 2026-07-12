# Click command-model 架构分析

## 范围与结论

固定源码 HEAD 为 b67832c2167e5b0ff6764a8c04a0a9087e697b5a。本报告只分析 core.py、decorators.py、globals.py、exceptions.py，共 4795 行，实际读取覆盖率 100.0%，超过 standard 核心模块 60% 门槛。其他源码没有读取，跨模块推断标记为【待主 agent 验证】。

Click 解决的不是把 argv 切成字符串，而是让多级 CLI 在长期演进中保持统一的调用、帮助、错误和状态语义。Command 描述可复用命令，Context 描述一次调用，Group 规定 dispatch，异常类型规定用户可见出口。

## 业务问题

当 tool run 增长到 tool admin user create，系统需要每层只消费自己的参数，父层能发布共享对象，子命令能懒加载，帮助和错误能显示完整命令路径，callback 和资源清理顺序可预测。单一 parser 能解析部分语法，却不能自然提供这些组合协议。

## 对象模型

装饰器先把 option/argument 参数保存到函数的 __click_params__，command 再取出参数、按函数名推导命令名并实例化 Command；group 选择 Group 作为命令类，Group.command/group shortcut 会创建后立即注册。证据：decorators.py:217-250、293-377；core.py:1793-1884。

Command 对象保存 name、callback、params 和 context_settings；Context 是一次调用的 activation record，保存 parent、command、params、args、obj、default_map、invoked_subcommand、parameter source 和 ExitStack。证据：core.py:312-338、960-1079。

Mermaid 主流程：decorators.py:217-250 的 callback/参数声明 → core.py:960-1079 的 Command/Group → core.py:1322-1357 的 make_context → core.py:1359-1393 的 parse_args/Parameter → core.py:1992-2084 的 Group dispatch → core.py:841-911 的 child Context/Context.invoke → core.py:1543-1589 的 main 错误出口。完整 Mermaid 图见 drafts/06-module-command-model.md。

## Context 链

子 Context 默认继承父 Context 的 obj、共享 meta、终端宽度、颜色、帮助选项和环境变量前缀，但拥有自己的 params、args 和资源清理。find_object 沿 parent 链搜索，ensure_object 可创建缺失对象；pass_context、pass_obj 和 make_pass_decorator 将这些能力包装成 callback 注入器。证据：core.py:378-514、733-759；decorators.py:28-130。

进入 Context 会推入线程局部 current-context 栈，最外层退出时关闭 ExitStack 并弹栈。证据：core.py:549-712；globals.py:20-67。这样资源生命周期跟随命令调用，而不是散落在 callback 的异常分支中。风险是 obj、meta 和隐式 current context 可能隐藏依赖，大型插件系统需要额外的类型化约束。

## Group dispatch

make_context 只创建并解析 Context，不调用 callback；Command.invoke 再将 ctx.params 作为关键字参数传入 callback。证据：core.py:1322-1409。

普通 Group 的顺序是：解析父参数，resolve_command 找子命令，设置 invoked_subcommand，执行父 callback，创建子 Context，执行子 callback，执行 result callback。chain 模式逐个创建子 Context，按序执行并收集返回值列表。证据：core.py:1886-1929、1992-2058。

get_command/list_commands 是懒加载边界。自定义 Group 可以在需要时发现命令；CommandCollection 还把多个 Group 的命令展平，本地命令优先，source Group callback 不执行。证据：core.py:1931-1939、2113-2168。动态发现的完整跨模块语义为【待主 agent 验证】。

## 参数来源和 callback

parse_args 获取 parser 的 opts、剩余 args 和实际调用顺序，按 eager 优先、随后按调用顺序处理参数。参数来源按 command line、environment、default_map、本地 default 仲裁，并以 ParameterSource 记录。证据：core.py:142-166、1359-1393、169-206、2470-2516。

随后进行类型转换、required 检查和参数 callback；callback 统一收到 ctx、param、value，prompt 的结果也经过同一管线。UNSET/FLAG_NEEDS_VALUE、同名参数仲裁和 resilient parsing 让 completion/help 可以避免副作用，但也构成自定义 Parameter 必须遵守的隐式协议。证据：core.py:2592-2805、3507-3584。

## 统一错误出口

augment_usage_errors 为 UsageError 补 Context，为 BadParameter 补 Parameter。UsageError.show 根据 Context 输出 command path、usage 和 help hint；BadParameter、MissingParameter、NoSuchOption、NoSuchCommand 将故障映射到参数/命令语义。证据：core.py:123-140；exceptions.py:35-111、114-301。

Command.main 将 ClickException 转为错误输出和退出码，并单独处理 EPIPE、Exit、Abort、EOFError 和 KeyboardInterrupt。证据：core.py:1543-1589。callback 不需要重复实现 CLI 错误格式，代价是必须遵循 Click 异常协议。

## 设计决策与权衡

1. 独立 Context 而不是全局 Namespace：换取参数隔离、父子状态和资源生命周期，代价是 Context 链和注入器增加学习成本。
2. Group 负责 dispatch 而不是只做 subparser 容器：换取稳定的父/子/结果 callback 顺序，代价是 chain 限制和 Group 多职责。
3. 显式元数据和受约束行为：换取统一帮助、错误、来源追踪和懒加载，代价是帮助格式与解析行为不能无限定制。

## 业界对比与重设计

argparse 以 ArgumentParser/Namespace 为中心，偏通用 parser 配置；docopt 以帮助文本驱动解析，偏手工界面控制；Typer 以类型提示和函数签名降低样板。Click 选择 Command/Group/Context 对象，牺牲部分自由度换取组合和稳定体验。

如果重新设计，我会保留 Context.parent/obj 兼容层，增加类型化 state provider；把动态命令发现抽成轻量 CommandDescriptor；为 Parameter 暴露 consume、cast、required、callback、arbitration 的明确协议；把 standalone 异常策略抽成可注入 policy。

主要扩展点是 context_class、command_class/group_class、Group.get_command/list_commands、shell_complete、result_callback 和 make_pass_decorator。主要问题是 obj/meta/current context 的隐式共享，以及 Group 同时承担注册、发现、帮助、解析、dispatch 和结果处理。

## 限制

Exa 三次搜索因 MCP 未配置失败，docopt 官方页因证书错误失败；Click Why、Commands and Groups、Python argparse、Typer 官方页面已读取。没有 Agent 工具，因此未执行参考 skill 要求的 Agent 并行阶段；没有运行测试或 CLI。详细命令、退出状态、覆盖率和源码完整性见 execution-log.md、checks.md、drafts/08-coverage.md。
