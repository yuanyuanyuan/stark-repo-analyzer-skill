# Click Shell completion：把命令模型变成终端的下一步提示

前一个模块解释了 Click 如何把终端交互与输出组织起来；Shell completion 继续解决执行前的同一个问题：用户尚未提交命令时，终端如何知道当前输入可能是什么。这个文件的核心判断是，补全不是业务回调的另一条执行路径，而是把已有命令、参数和类型对象投影成不同 shell 能理解的协议。Click 因此把“识别当前上下文”和“让 shell 呈现候选项”拆开，业务命令仍由统一命令模型描述，shell 差异收敛在适配类中（`src/click/shell_completion.py:19-55,216-324`）。

## 1. 模块角色与业务问题

### 角色

模块承担三层转换：

1. 把环境变量中的 `shell_instruction` 解码为 `source` 或 `complete` 请求，并选择注册的 shell 实现（`src/click/shell_completion.py:19-44`）。
2. 把 Bash、Zsh、Fish 注入的当前命令行状态解析为 `args` 与 `incomplete`，再沿 Click 命令树定位补全对象（`src/click/shell_completion.py:285-304,370-440,599-704`）。
3. 把统一的 `CompletionItem` 转成目标 shell 的行协议和脚本片段（`src/click/shell_completion.py:67-102,104-207,306-324,382-456`）。

去掉它，命令仍可能执行，但每个应用都要重复编写 shell 脚本、参数上下文解析和候选项序列化；更严重的是，补全逻辑会和命令定义分叉。该模块把“执行前发现”纳入 Click 的组合模型，同时不调用命令业务回调。后一点由 `_resolve_context` 的文档和 `resilient_parsing=True` 直接支持；其对所有回调的最终抑制效果仍依赖上下文实现，属于【待主 agent 验证】（`src/click/shell_completion.py:599-657`）。

### 业务问题

补全请求是一个低延迟、频繁触发、输入可能不完整的特殊请求：

- shell 可能只提供半个引号字符串或末尾反斜杠；普通 `shlex.split` 会因为语法未闭合而失败，因此模块提供容错切分（`src/click/shell_completion.py:506-539`）。
- 当前词可能是选项名、选项值、位置参数，或子命令名；同一个字符串在不同位置必须交给不同对象处理（`src/click/shell_completion.py:660-704`）。
- Bash、Zsh、Fish 对环境变量、数组、描述文本和文件路径候选的协议不同；通用补全算法不能直接把一份文本原样交给三者（`src/click/shell_completion.py:104-207,327-456`）。
- 请求来自外部 shell，输入状态不完整且不能依赖成功执行，因此解析必须尽量可恢复，并将未知 shell 或未知指令变成失败状态（`src/click/shell_completion.py:38-55`）。

## 2. 设计思路：统一语义，末端适配

模块的中心抽象是 `ShellComplete`。它持有统一的 `cli`、`ctx_args`、`prog_name` 和 `complete_var`，规定四个变化点：如何生成安装脚本、如何从 shell 环境取得输入、如何调用命令模型产生候选、如何把候选格式化回 shell 协议（`src/click/shell_completion.py:216-324`）。

这形成一个窄适配层：

- 语义层：`get_completions` 统一执行 `_resolve_context`、`_resolve_incomplete`，然后调用当前 `Command | Parameter` 的 `shell_complete`（`src/click/shell_completion.py:292-304`）。
- 协议层：子类只实现 shell 的 `source_template`、`get_completion_args` 和 `format_completion`；Bash、Zsh、Fish 的脚本都留在本文件（`src/click/shell_completion.py:104-207,327-456`）。
- 扩展层：`_available_shells` 保存名称到类的映射，`add_completion_class` 用注册表增加新 shell，而不需要修改分派函数（`src/click/shell_completion.py:459-503`）。

关键的架构选择是“动态请求 + 预生成脚本”并存：`source` 只生成 shell 函数，之后每次按键触发函数再回到 CLI 进程执行 `complete`；候选项不被永久静态化。这保持了命令定义和补全行为的组合性，代价是每次补全都有进程启动、上下文构造和参数解析开销。这个性能代价是否在 Click 的命令模型中可接受，以及 `shell_complete` 是否会触发昂贵的外部查询，需结合参数类型和命令实现验证，属于【待主 agent 验证】。

## 3. 核心结构

### 3.1 环境变量入口

`shell_complete` 接收调用方传入的 `complete_var` 和 `instruction`。它以第一个下划线拆分，例如 `bash_complete` 得到 shell=`bash`、操作=`complete`；找不到注册类或操作不是 `source` / `complete` 时返回状态码 `1`。`source` 输出无额外换行，`complete` 输出带换行，二者都先编码为 bytes，以避免 Windows 文本 stdout 把 LF 转成 CRLF（`src/click/shell_completion.py:19-55`）。

因此协议不是“shell 直接调用 Python API”，而是：

```text
安装阶段：环境变量=<shell>_source  -> Python 输出 shell 函数
交互阶段：环境变量=<shell>_complete -> shell 函数输出当前候选项
```

这里的 `complete_var` 是可配置的变量名，shell 名称和操作名是变量值的一部分；这允许不同 CLI 使用不同环境变量，避免固定全局变量冲突（`src/click/shell_completion.py:23-35,44-53`）。

### 3.2 CompletionItem：候选值与显示策略

`CompletionItem` 用一个小对象承载候选值及其 shell 相关元数据：

| 字段 | 作用 | 本文件中的消费者 |
|---|---|---|
| `value` | 建议插入命令行的值 | 三个 shell 的格式化器 |
| `type` | 当前内建值为 `plain`、`dir`、`file`，指示 shell 使用普通、目录或文件行为 | 三个 source 脚本 |
| `help` | 候选旁的描述文本，可选 | Zsh、Fish；Bash 不消费 |
| `**kwargs` | 扩展元数据，缺失属性返回 `None` | 自定义类型和自定义 shell 可消费 |

它使用 `__slots__` 固定核心字段，同时保留 `_info` 存放任意元数据；`__getattr__` 将未定义属性变成 `None`，因此扩展消费者不必为每个元数据字段修改核心类（`src/click/shell_completion.py:67-102`）。这是一种有意的开放数据边界：短期降低扩展成本，长期则把元数据命名和类型约束交给约定，错误可能延迟到某个自定义 shell 的运行时。

### 3.3 解析上下文与目标对象

补全语义的主干是 `get_completions`：先用完整参数建立 Context 层级，再根据当前不完整词选择对象，最后把请求委派给对象的 `shell_complete`（`src/click/shell_completion.py:292-304`）。本文件能确认委派接口的形状；`Command`、`Parameter` 和具体 `ParamType` 如何实现候选生成，超出允许读取范围，相关结论均应标记【待主 agent 验证】。

```mermaid
flowchart TD
    A[Shell 按键触发 completion function\nsrc/click/shell_completion.py:104-207] --> B[环境变量携带 shell_complete\nsrc/click/shell_completion.py:19-44]
    B --> C[选择 ShellComplete 子类\nsrc/click/shell_completion.py:459-503]
    C --> D[get_completion_args\nBash/Zsh/Fish:370-440]
    D --> E[_resolve_context\n构造命令树上下文:599-657]
    E --> F[_resolve_incomplete\n选 Command 或 Parameter:660-704]
    F --> G[shell_complete(ctx, incomplete)\n调用方对象接口:292-304]
    G --> H[CompletionItem 列表\nsrc/click/shell_completion.py:67-102]
    H --> I[format_completion\n各 shell 行协议:382-456]
    I --> A
```

图中 `shell_complete(ctx, incomplete)` 是模块与统一命令模型的关键契约：Shell 层不关心候选值是由选项、参数类型还是命令组产生的，只负责选择正确对象和编码结果。这正是“共享命令元数据、隔离 shell 协议”的组合点；对象侧的具体组合规则需【待主 agent 验证】。

## 4. 端到端流程

### 4.1 `source`：安装 shell 适配器

调用 `source()` 时，基类以 `%` 模板填充三个变量：函数名、环境变量名和程序名（`src/click/shell_completion.py:257-283`）。函数名由程序名转换而来：先把连字符替换成下划线，再移除非 ASCII 单词字符，最后加上 `_completion` 前缀（`src/click/shell_completion.py:257-263`）。

- Bash 模板注册 `complete -o nosort -F ...`，按 `plain`、`dir`、`file` 分别追加候选、启用目录名或默认文件补全（`src/click/shell_completion.py:104-135`）。
- Zsh 模板通过 `compdef` 注册函数；候选用三行表示 `type`、`key`、`descr`，有描述时走 `_describe`，无描述时走 `compadd`，目录和文件交给 `_path_files`（`src/click/shell_completion.py:143-185`）。
- Fish 模板用 `complete --no-files --command ... --arguments "(function)"`，把动态结果作为命令替换返回；类型为目录或文件时分别调用 Fish 的路径 helper（`src/click/shell_completion.py:187-207`）。

Bash 在生成脚本前检查版本；模块只输出错误信息，随后仍返回父类生成的脚本，因为 `_check_version` 没有抛出异常或返回失败状态（`src/click/shell_completion.py:333-368`）。这是兼容性提示而不是强制门禁：调用者可能拿到一个旧 Bash 无法完整支持的脚本。是否由更上层捕获此提示或决定终止，超出本文件范围，标记【待主 agent 验证】。

### 4.2 `complete`：每次请求重新解析

基类 `complete()` 依次执行 `get_completion_args()`、`get_completions()`，再对每个 `CompletionItem` 调用 `format_completion()`，最终用换行拼接（`src/click/shell_completion.py:314-324`）。这个顺序保证了候选生成不需要知道目标 shell；只有最后一步才做协议编码。

各 shell 的输入取法体现“协议适配”边界：

- Bash/Zsh 都通过 `COMP_WORDS` 和 `COMP_CWORD` 得到完整词列表与光标索引，跳过程序名取 `args`，索引越界时把 `incomplete` 视为空串（`src/click/shell_completion.py:370-402`）。
- Fish 的 `COMP_WORDS` 来自当前光标前文本，`COMP_CWORD` 单独提供当前词；它会先切分当前词，再从 `args` 移除重复的最后词（`src/click/shell_completion.py:428-440`）。

这种差异没有泄漏到后续上下文解析：从 `get_completion_args` 返回开始，所有 shell 都进入同一条 `get_completions` 流程。

## 5. 解析判定：把“不完整”归属给正确对象

### 5.1 命令树上下文

`_resolve_context` 不把完整参数重新执行一遍，而是以 `resilient_parsing=True` 创建 Context，并沿 Group 层级消费已经完成的参数（`src/click/shell_completion.py:599-657`）。普通 Group 通过 `resolve_command` 进入一个子命令；chain Group 则循环解析多个子命令，并为子上下文设置 `allow_extra_args=True`、`allow_interspersed_args=False`。这让补全可以停在已知的命令层级，而不是要求输入已经足够完整。

它还合并 `ctx._protected_args` 与 `ctx.args` 再继续遍历，说明解析器产生的“尚未归属但不能丢失”的参数也必须参与后续命令解析（`src/click/shell_completion.py:613-653`）。如果命令名无法解析，函数返回当前 Context，让上层仍有机会对当前层产生候选，而不是直接把不完整输入当成异常（`src/click/shell_completion.py:621-626,635-640`）。

### 5.2 当前词的优先级

`_resolve_incomplete` 按以下优先级选择补全对象（`src/click/shell_completion.py:660-704`）：

1. 先规整长选项的 `=` 形式。独立的 `=` 变为空值；`--name=value` 被拆成选项名和待补全值，以吸收不同 shell 对等号的不同切分方式（`src/click/shell_completion.py:671-679`）。
2. 未出现 `--` 且当前词像选项时，直接交给当前 `Command`，得到选项名候选（`src/click/shell_completion.py:681-687`）。`_start_of_option` 使用当前 Context 的 `_opt_prefixes`，所以不会把前缀字符硬编码为只有短横线（`src/click/shell_completion.py:565-572`）。
3. 反向检查已完成参数，若最后一个选项名仍需要值，则把当前不完整值交给该 `Option`；flag 和 count 选项被排除，`nargs` 决定回溯范围（`src/click/shell_completion.py:574-597`）。
4. 若不是选项值，寻找仍未填满的 `Argument`。可变参数、尚未来自命令行的参数，以及多值参数尚未达到 `nargs`，都视为可继续补全（`src/click/shell_completion.py:542-562`）。
5. 没有待填位置参数时，回到当前 `Command`，由命令组产生子命令或由命令自身产生候选（`src/click/shell_completion.py:696-704`）。

这组顺序的价值在于把“文本匹配”提升成“语义位置匹配”：`--`、多值参数和 `=` 都在文本进入候选生成前被消解。代价是该文件直接依赖 Context 的内部状态 `_protected_args`、`_opt_prefixes` 和参数来源信息；这些内部字段一旦改变，completion 可能静默错配。字段的稳定性和版本兼容策略需【待主 agent 验证】。

### 5.3 命令、参数与 ParamType 的协作边界

本文件能确认的调用链只有：

```text
ShellComplete.get_completions
  -> _resolve_context
  -> _resolve_incomplete
  -> Command.shell_complete(ctx, incomplete)
     或 Parameter.shell_complete(ctx, incomplete)
  -> list[CompletionItem]
```

`Command`、`Parameter`、`Option`、`Argument` 和 `Context` 是从 `.core` 导入的接口类型（`src/click/shell_completion.py:9-15`）；文件没有定义它们，也没有直接导入或调用 `ParamType`。因此可以确定 Shell 层为命令或参数提供统一委派点，但“参数如何再委托给 ParamType”“Choice、Path 等类型如何生成 `dir` / `file` 元数据”只能作为【待主 agent 验证】。这条边界很重要：如果把类型生成逻辑搬进本文件，shell 适配层就会开始了解业务参数语义，核心组合性会下降。

## 6. 基类与 Bash/Zsh/Fish 的边界

| 层 | 负责什么 | 不负责什么 |
|---|---|---|
| `ShellComplete` | 保存 CLI 请求上下文；生成函数名和 source；统一解析、候选委派、结果遍历 | 不知道具体 shell 的环境变量形状、转义规则和文件 helper |
| `BashComplete` | 版本探测；解析 `COMP_WORDS` / `COMP_CWORD`；编码 `type,value` | 不决定命令树中哪个对象产生候选 |
| `ZshComplete` | 读取同名环境变量协议；编码三行记录；处理带描述项的冒号转义 | 不实现 `_describe` 的语义，只生成其所需格式 |
| `FishComplete` | 处理 Fish 的当前词重复表示；把帮助文本变成 tab 描述格式并逃逸换行、tab | 不把所有值都当作路径，类型交给 source 脚本处理 |
| 注册表 | 通过名称把外部 instruction 路由到实现 | 不验证自定义类是否完整或名称是否冲突 |

基类边界清晰的原因是候选生成与 shell 展示的变化速度不同：命令树解析规则应共享，shell 的安装脚本和 wire format 应隔离。新增 shell 的最小路径是继承 `ShellComplete`，提供 `name`、`source_template`、`get_completion_args`、`format_completion`，再调用 `add_completion_class` 注册（`src/click/shell_completion.py:216-324,468-485`）。核心分派函数不需要新增 `if` 分支，这是对扩展性最直接的收益。

但该扩展点是“约定式插件”而非强约束接口：抽象方法依靠 `NotImplementedError`，模板变量也只由 `%` 格式化检查。一个自定义类可以注册成功，却在首次 source 或 complete 时才失败；注册名重复还会覆盖旧类（`src/click/shell_completion.py:283-312,468-485`）。

## 7. 外部协议、错误与性能取舍

### 协议的优点与脆弱点

模块直接复用 shell 的原生机制：Bash 的 `complete` / `compopt`、Zsh 的 `compdef` / `_describe` / `_path_files`、Fish 的 `complete` / 路径 helper。这样 `dir` 和 `file` 不必由 Python 自己实现路径扫描，候选可以获得 shell 原生行为（`src/click/shell_completion.py:104-207`）。

不过返回值是轻量文本协议，不是带长度和字段编码的结构化协议：Bash 使用逗号，Zsh 使用三行和冒号，Fish 使用逗号加 tab。模块只在 Zsh value 有描述时逃逸冒号，在 Fish help 中逃逸换行并替换 tab；没有看到对所有字段进行统一的 delimiter、换行、空值和编码处理（`src/click/shell_completion.py:382-456`）。这降低了实现成本，却把“候选值不能包含什么”变成隐含协议。Zsh 模板注释明确要求冻结已广泛部署的脚本，再由 formatter 处理冒号，说明向后兼容已经反过来约束了编码设计（`src/click/shell_completion.py:137-143,404-419`）。

### 错误路径

- 未注册 shell 或未知操作返回 `1`，适合让外部 shell 知道请求未被处理（`src/click/shell_completion.py:38-55`）。
- `COMP_WORDS`、`COMP_CWORD` 缺失或不可转整数时，Bash/Zsh 实现没有本地捕获；`complete()` 及对象侧 `shell_complete` 的异常也没有统一边界（`src/click/shell_completion.py:370-402,314-324`）。从本文件看，坏环境可能直接中断 Python 进程并污染 completion 体验。
- `split_arg_string` 只捕获 `shlex` 在输入未闭合时的 `ValueError`，保留部分 token；它不是完整 shell 解析器，也不会尝试恢复所有 shell 语法（`src/click/shell_completion.py:506-539`）。
- `prog_name` 被直接插入 shell source 模板，`func_name` 只做字符删除和连字符替换，没有看到针对模板上下文的 shell escaping；特殊程序名可能导致函数名碰撞、非法脚本或注入风险。这是源码可见的安全与兼容性检查缺口（`src/click/shell_completion.py:257-283`）。

### 性能取舍

每次交互请求都会重新启动 CLI 子进程、切分输入、构造 Context，并可能沿 Group chain 创建多个子 Context；本文件没有候选缓存或常驻服务（`src/click/shell_completion.py:110-111,152-153,189-190,314-324,613-657`）。这是以延迟换新鲜度：动态候选可以反映当前文件系统和运行时状态，且不必维护静态 spec；代价是按键级触发的进程启动成本，以及自定义补全访问网络或数据库时的放大效应【待主 agent 验证】。

## 8. 关键权衡与业界对比

### 关键权衡

1. **统一命令语义 vs shell 特化**：所有 shell 共享 Context 定位和对象委派，避免三份命令解析器；代价是必须维护三种外部协议和每个 shell 的边界行为。
2. **动态准确性 vs 交互延迟**：每次回到 Python 得到最新候选，优于生成一次后长期过期的静态列表；代价是进程和解析开销，且没有内建超时、缓存或取消机制。
3. **开放元数据 vs 可验证性**：`CompletionItem` 的 `**kwargs` 让自定义 shell/type 可以扩展；代价是缺乏 schema、编码约束和能力协商，错误更晚暴露（`src/click/shell_completion.py:73-83,88-102`）。

### 业界对比

从设计路线看，常见 CLI completion 有两种极端：完全静态生成 shell 脚本，或每次请求由运行时动态计算。Click 选择中间形态：脚本注册逻辑，候选动态回调。这保留了命令模型的单一来源，又能使用 Bash/Zsh/Fish 的原生目录和文件完成器；代价是运行时进程开销和协议兼容维护。

与 JSON 等结构化跨 shell 协议相比，这里的文本协议更容易被 shell 原生命令消费，部署面小，但字段转义明显更脆弱。与把文件路径候选全部交给 Python 的实现相比，`dir` / `file` 类型让 shell 做最终呈现，减少重复实现；但 `CompletionItem.type` 的能力集合是软约定，扩展 shell 需要自己定义新类型的解释（`src/click/shell_completion.py:77-83,382-456`）。以上是基于本文件协议形状的架构对比；其他 CLI 的具体性能和兼容性数据不在本次读取范围内。

## 9. 如果重做：保持组合点，强化协议边界

1. **引入内部结构化响应，再为每个 shell 编码。** 保留 `CompletionItem` 的开放元数据，但由 `BashEncoder`、`ZshEncoder`、`FishEncoder` 统一处理 delimiter、换行、空值和 shell 特殊字符。这样不会让命令或 ParamType 关心 shell，核心组合性提升；代价是增加一层 encoder，并需要兼容已有 source 脚本和旧候选格式。
2. **把请求状态建模成不可变 `CompletionRequest`。** 当前 `_resolve_context` 直接把 `resilient_parsing=True` 写入 `ctx_args`（`src/click/shell_completion.py:613-614`）；改为复制并显式传递 `args`、`incomplete`、shell 能力，可减少调用方状态被修改的隐患。组合性会更稳定，迁移成本在于自定义 `ShellComplete` 需要适配新接口。
3. **建立明确的错误边界。** 对缺失/非法环境变量、未知 shell、候选生成异常分别定义可诊断的 stderr 和退出码，确保 stdout 永远只含协议数据。这样 shell 失败更可控，但若吞掉对象侧异常，调试信息会减少，因此应提供可选 debug 模式；不应把诊断写入 stdout。
4. **增加能力协商与注册校验。** 注册时检查 `name`、模板变量和必需方法，拒绝重名或显式允许覆盖；`CompletionItem.type` 可由 shell 声明支持集合。这样插件失败更早、演进更可见，代价是弱约定扩展的自由度下降。
5. **只缓存稳定部分。** 可以缓存函数名、source 脚本以及命令元数据索引，但不要默认缓存动态候选；若增加候选缓存，应以 `args + incomplete + 参数来源 + 外部状态版本` 为键，并提供失效策略。这样降低常规补全延迟，同时不破坏动态 completion 的语义；缓存设计复杂度和内存成本会上升。
6. **为每个协议建立 golden tests 和属性测试。** 重点覆盖引号未闭合、反斜杠、`--name=value`、`--`、多值参数、冒号/逗号/tab/换行、旧 Bash 和异常环境。测试应固定 source 脚本兼容性，因为 Zsh 注释已经说明脚本可能被长期部署（`src/click/shell_completion.py:137-143`）。具体测试文件和测试层不在本次范围内，需后续支持/测试模块验证【待主 agent 验证】。

这些建议共同维护一个核心原则：命令、参数和类型只产出语义候选，shell 层负责把语义翻译成外部协议。若把缓存、shell 分支或 escape 规则下沉到命令对象，短期看似方便，长期会让新增 shell 和新增参数类型互相耦合，损害 Click 最有价值的组合性。

## 10. 小结：从核心算法进入支持层

`shell_completion.py` 的核心贡献不是某个 shell 脚本，而是一条稳定的适配流水线：环境变量选协议，shell 子类还原输入，Context 沿命令树恢复语义，Command 或 Parameter 产生 `CompletionItem`，最后由 shell formatter 完成展示。它把业务命令定义与终端协议隔开，同时承认一个现实：补全发生在不完整输入和严格外部协议之间，转义、版本、错误隔离和延迟都不能被抽象层隐藏掉。

下一步应进入支持层、测试层和平台兼容性分析：验证命令/参数/ParamType 的真实候选委派，确认 `resilient_parsing` 对回调和提示的影响，覆盖三种 shell 的 source 与 complete golden 输出，并在 Windows、旧 Bash、不同 Zsh/Fish 版本上检查换行、路径和编码行为【待主 agent 验证】。

## 覆盖率

| 文件名 | 总行数 | 已读行数 | 覆盖率% | 未读原因 |
|---|---:|---:|---:|---|
| `src/click/shell_completion.py` | 704 | 704 | 100% | 无 |
| 合计 | 704 | 704 | 100% | 标准核心最低 60%，达标✅ |
