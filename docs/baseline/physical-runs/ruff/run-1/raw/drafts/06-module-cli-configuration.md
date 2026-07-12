# 模块：CLI 意图与分层配置编排

## 来源、范围与限制

- **源码**：只读 `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/ruff`，固定 HEAD `c588a3f7f57461692652d339936222b4496c5953`。未使用 Git 历史，未修改源树。
- **本模块边界**：从 Clap 参数进入，到 `Configuration` 合并、`Settings` 编译、按路径解析，再到 `check` / `format` 取得设置。没有分析 `ruff_workspace::options`、`pyproject` 的 TOML 解析实现，也没有深入 lint/formatter 内核。
- **叙事位置**：Ruff 的入口先将“本次命令想做什么”与“哪些行为是可配置的”分开；本模块交付每个目标文件的 `Settings`，使后续高吞吐检查/格式化无需重新解释用户输入。

## 要解决的业务问题

同一 CLI 要服务一次性的 `ruff check --select ...`、团队仓库的 `pyproject.toml`、嵌套子项目以及 stdin。若命令层直接把参数传给 lint/format，优先级、相对路径和子目录规则会分散到消费者，既难保证一致，也会把配置发现放进并行热路径。Ruff 因而以“延迟合并的配置描述 -> 已验证运行设置 -> 按路径路由”三段式，将 Python 工具整合为一个 CLI 而不牺牲批量执行路径。

## 核心结构与职责边界

|结构|职责|关键证据|
|---|---|---|
|`CheckCommand` / `FormatCommand` + `ConfigArguments`|把一次命令拆为命令动作、文件/输出控制，与会进入项目设置的覆盖项；拒绝 `--isolated` 与配置文件、多个显式配置文件的矛盾组合。|`crates/ruff/src/args.rs:703-787,790-887`|
|`Configuration`|保留大量 `Option` 和可追加列表，表达“未指定”与“覆盖/扩展”的差别；包含全局、文件发现、lint、format、analyze 四个域。|`crates/ruff_workspace/src/configuration.rs:175-210,530-739`|
|`Settings`|最终、具体的执行形态：文件发现、linter、formatter、analysis 及少量顶层输出/修复选项；默认值和路径根被固化。|`crates/ruff_workspace/src/configuration.rs:213-400`; `settings.rs:16-170`|
|`PyprojectConfig` / `Resolver`|前者持有默认根设置和发现策略；后者持有追加的作用域设置，返回路径最长前缀匹配的 `Settings`。|`resolver.rs:32-46,103-199,269-283`|

这里最重要的边界是：`Configuration` 不是运行时设置。它故意允许空值和层叠；`into_settings` 才检查版本、编译文件模式/每文件 target version、推导默认值并构造不可变执行对象（`configuration.rs:213-400`）。这样 `check` 与 `format` 不需要理解 TOML、CLI 或优先级。

## 主流程

```mermaid
flowchart TD
  A[Clap: Check/Format + 全局参数] --> B[partition]
  B --> C[动作参数: files/diff/watch/stdin]
  B --> D[ConfigArguments: file/inline/专用 flag 覆盖]
  D --> E{resolve 优先级}
  E -->|isolated| F[默认 Configuration + CLI]
  E -->|显式 --config 文件| G[固定根 Settings]
  E -->|祖先配置| H[分层默认根 Settings]
  E -->|用户配置/默认| H
  F --> I[Configuration::into_settings]
  G --> I
  H --> I
  I --> J[project_files_in_path]
  J --> K[遍历中发现子目录配置并 Resolver::add]
  K --> L[Resolver::resolve(path)]
  L --> M[check: LinterSettings]
  L --> N[format: FormatterSettings]
```

1. `run` 做一次命令分发；check/format 均先 `partition`，再调用同一个 `resolve`（`crates/ruff/src/lib.rs:128-228,243-264`）。这保证 formatter 和 linter 的配置语义有同一入口，而非两个逐渐漂移的 parser。
2. `ConfigArguments::transform` 先将 `--config KEY=VALUE` 覆盖合入基础配置，再由专用 flag 覆盖它（`args.rs:703-787`）。Check 与 Format 分别只暴露本领域的 CLI 覆盖，命令行为（如 `--diff`、输出文件）则留在 `CheckArguments`/`FormatArguments`（`args.rs:790-916`）。
3. 根解析有明确优先级：isolated、用户指定文件、stdin/CWD 祖先、用户配置、内置默认；后面三类采用 hierarchical，后续遍历会为更近目录找设置（`crates/ruff/src/resolve.rs:20-145`）。fallback 还从 `requires-python` 推导 target version，避免无 Ruff 段时丢失 Python 约束（同文件:83-139）。
4. `resolve_configuration` 沿 `extend` 收集链，检测环，再按顺序合并、应用 origin fallback，最后调用 transformer（`resolver.rs:315-382`）。`Configuration::combine` 的 `self.or(base)` 和对 `extend-*` 的拼接把“覆盖”与“追加”区分开（`configuration.rs:654-695`；lint 域同一模式见:1240-1315）。
5. 文件走并行 walker；遇到目录先查配置并写入共享 `Resolver`，而普通文件根据当前路径解析的 include/exclude 决定是否纳入（`resolver.rs:434-510,515-690`）。这让嵌套项目只影响自己的子树，而不是重写全局默认。

## 与消费者的契约

`check` 先由 `project_files_in_path` 获得文件和 resolver，对每个并行任务调用 `resolver.resolve(path)`；随后按该设置过滤、找 package root、读缓存，并仅把 `LinterSettings` 交给诊断执行（`crates/ruff/src/commands/check.rs:37-193`）。`format` 走完全相同的路径路由，但消费 `FormatterSettings`、其扩展名映射和 format exclude（`commands/format.rs:70-190`）。二者的共享契约是“路径决定设置”，不是“本次命令只有一份设置”。

这同时解释 `Settings` 的组合形态：顶层 `fix`、`output_format` 等在 check 启动阶段一次读取；每文件差异留给 resolver（`crates/ruff/src/lib.rs:285-320`）。format 在实际文件工作前还遍历 resolver 的全部 settings 预警 lint/formatter 不兼容项（`commands/format.rs:95,1105-1200`），表明统一配置模型不仅复用输入，也能跨功能做一致性检查。

## 关键决策与权衡

### 1. 用显式优先级而非“最后发现的文件获胜”

显式配置文件被固定为所有路径的设置；祖先、用户和默认才允许层级解析（`resolve.rs:20-145`）。这牺牲了一点“传一个根配置仍自动继承子项目”的便利，却让 CI 的 `--config` 可复现，符合统一工具首先保证确定性的哲学。若始终层级合并，某个依赖或子仓库的 TOML 会悄然改变 CI 行为。

### 2. 先合并描述，再编译执行设置

`Configuration` 的 optional 字段可准确保留“不覆盖”；`Settings` 则将 glob、默认 include、预览模式、target version 编译为消费者可直接使用的形态（`configuration.rs:213-400`）。代价是配置域巨大、`combine` 需随新选项同步维护；收益是高频每文件路径不做 TOML 解析和默认推导。相较让各子命令自行 merge map，此处把复杂度集中到一个可验证边界。

### 3. 分层路由而非每文件独立完整发现

walker 发现目录配置后写入 resolver，读路径通过最长作用域选择设置（`resolver.rs:174-199,638-690`）。它适配 monorepo，同时避免每个文件重复向上搜索；代价是并行遍历期间需要 `RwLock` 协调 resolver，且配置错误会终止遍历。相较纯全局配置，正确性更强；相较无缓存的每文件搜索，吞吐更可控。

## 依赖、跨模块推断与评价

- `ruff_workspace::pyproject::load_options` 和 `settings_toml` 是本模块的配置文件边界；其 TOML schema/发现细节未在本任务允许范围内阅读。【待主 agent 验证】
- `ruff_linter`、`ruff_python_formatter` 和 `ruff_graph` 接收各自的 settings 子树，因此统一配置并非把 lint/format 算法混在一起，而是共享选择与生命周期、分离实际执行。【待主 agent 验证】
- `commands::check` / `commands::format` 是本模块下游消费者；接下来应由执行管线草稿解释缓存、并行和诊断/写回如何利用这份 per-file 设置。【待主 agent 验证】

**亮点。** 配置发现与路径解析被收敛到一个 resolver，check/format 的差异仅发生在取得设置之后。这是“一个 CLI、多种 Python 工具角色”的实质，而非只复用 flag 名称。

**风险。** `Configuration` 的宽大结构和手工 `combine` 是演进热点；新增选项若遗漏转换/合并，可能只在某一优先级层失效。建议用属性测试覆盖“CLI > inline > local extend > ancestor/default”的代表性字段组合，并为 `combine` 的覆盖与追加语义建立表驱动测试。另有代码内注释承认 extend 链目前可重复解析、缺少缓存（`resolver.rs:311-314`）；大型多配置仓库会放大该启动成本，但未在本次静态阅读中测量，不能断言其实际性能影响。

## 实际阅读覆盖（标准模式）

覆盖率按实际 `sed` 请求行区间的并集 / `wc -l`，不把 `rg` 结构搜索计入；命令及状态由主执行日志记录。源只读，无测试或构建要求由本子模块执行，故**未执行**。

|文件|总行数|实际读取区间|已读行数|覆盖率|未读原因|
|---|---:|---|---:|---:|---|
|`ruff/src/main.rs`|78|1-78|78|100.0%|无|
|`ruff/src/lib.rs`|693|120-540|421|60.8%|错误处理、边缘命令未纳入本编排叙事|
|`ruff/src/args.rs`|1,524|700-940；1040-1524|726|47.6%|前段 Clap 字段声明未逐行读取；本文件低于 60%，范围限制已披露|
|`ruff/src/resolve.rs`|145|1-145|145|100.0%|无|
|`ruff/src/commands/check.rs`|302|1-302|302|100.0%|无|
|`ruff/src/commands/format.rs`|1,425|1-700；1080-1200|821|57.6%|格式化算法/结果渲染不是本模块重点|
|`ruff/src/commands/mod.rs`|16|1-16|16|100.0%|无|
|`ruff_workspace/src/configuration.rs`|2,313|120-1600|1,481|64.0%|后段插件选项细节不影响编排主流程|
|`ruff_workspace/src/resolver.rs`|1,187|1-1187|1,187|100.0%|无|
|`ruff_workspace/src/settings.rs`|341|1-341|341|100.0%|无|
|`ruff_workspace/src/lib.rs`|17|1-17|17|100.0%|无|
|**合计**|**8,041**|—|**5,515**|**68.6% ✅**|模块总体达到标准模式核心覆盖目标；个别消费者/参数文件以边界说明处理|
