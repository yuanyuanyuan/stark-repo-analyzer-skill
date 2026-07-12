# 格式化流水线：从 Python 源码到稳定文本

> 来源：只读 `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/ruff`，固定 HEAD `c588a3f7f57461692652d339936222b4496c5953`。范围仅含任务指定的 `ruff_python_formatter` 与 `ruff_formatter` 文件；未读取 Git 历史，未修改源树。分析时间：2026-07-12。
>
> 限制：这是大仓库的有界模块分析；未审阅 AST 各语法节点的具体规则、CLI 配置解析、visitor/format 子模块与打印器尾部测试。因此“Black 兼容性”在本草稿中只作为任务给定定位，不从本范围证明；对 CLI 契约的结论均标记待验证。

前一层的 CLI/配置需要把“用户选择与文件文本”变成一次格式化请求；本模块接住已解析的选项和源码，保证输出不是简单的空白替换，而是以 AST、原始 trivia 与可回溯文档 IR 为依据重排。它的存在是 Ruff 格式化器能够既统一版式又尽量不丢注释、保留抑制区语义的原因：若直接 token 级重写，注释的归属和 Python 缩进敏感性会成为高风险漏洞。

## 业务问题与系统角色

格式化的真实约束是三件事同时成立：语法可解析、注释仍紧贴其意图、在给定宽度下输出稳定。Python 注释可以出现在大量位置，模块选择“按 AST 节点归属、再分 leading/dangling/trailing”而非逐 token 建模，以少量可打印位置压低组合复杂度；源码注释也坦承这会受 AST 粒度限制（`comments/mod.rs:15-27,67-86`）。这正体现 Ruff 的全局取向：共享 Rust 引擎承载通用布局搜索，语言层保留 Python 语义和源码信息。

## 核心结构与边界

|结构|职责|边界含义|
|---|---|---|
|`PyFormatOptions`|语言偏好，如引号、magic trailing comma、preview、docstring code（`options.rs:258-446`）|配置值在进入规则前冻结，规则读取而非自行解析配置。|
|`PyFormatContext`|持有 options、源码、trivia、tokens、`Comments`，并保存节点层级、缩进、docstring/f-string 状态（`context.rs:15-54,89-140`）|把 Python 特有可变状态隔离在 context，不污染通用引擎。|
|`Comments` / `SourceComment`|节点键到三类注释的多映射；每条带源码 slice、行位置、已消费标志（`comments/mod.rs:116-189,191-257,348-385`）|规则只取“属于该节点”的注释；debug 下强制无遗漏。|
|`Document` / `FormatElement`|通用格式 IR 和元素序列；先传播必须展开的组（`ruff_formatter/.../document.rs:17-152`）|语言规则描述候选布局，不直接拼字符串。|
|`Printer`|队列、调用栈、缩进、group mode、source/verbatim marker 的解释器（`printer/mod.rs:35-88,94-180`）|只消费 IR 和打印选项，不认识 Python AST。|

`Comments` 用 `Rc`，不是为了共享所有权的抽象偏好，而是规避“迭代 context 中注释”与“可变写 formatter”同时借用的 Rust 冲突；格式规则可廉价 clone 后遍历（`comments/mod.rs:191-218`）。`WithNodeLevel` 的 RAII 恢复（`context.rs:237-292`）也把嵌套格式化状态的清理从调用约定提升为析构保证；若用手工 save/restore，错误路径漏恢复会让后续节点产生隐蔽版式串扰。

## 主流程

```mermaid
flowchart LR
  A[源码 + 已解析选项] --> B[parse + TriviaRanges]
  B --> C[Comments::from_ast\n节点/三类注释]
  C --> D[PyFormatContext]
  D --> E[Python AST Format 规则]
  E --> F[FormatElement Document]
  F --> G[propagate_expand]
  G --> H[Printer: fits/group/indent]
  H --> I[Printed 代码 + source markers]
  I --> J[调用方比较或返回文本]
```

1. `format_module_source` 按 `source_type` 解析、从 tokens 建 `TriviaRanges`，再格式化并打印（`ruff_python_formatter/src/lib.rs:135-145`）。`format_node` 建注释表和 context，调用泛型 `format!`，debug 下验证所有注释已消费（`lib.rs:156-177`）。这让“格式失败/打印失败/解析失败”保留不同错误通道（`lib.rs:98-132`），而不是把不可信输出当成功。
2. 每个 Python 节点规则先写 leading comments，必要时写 source positions，再写字段，最后写 trailing comments；dangling 必须由相应字段规则显式处理（`lib.rs:51-95`）。这种强制责任分配的代价是新增 AST 形态必须补特殊规则，收益是遗漏在 debug 断言中被及早发现。
3. 通用 `format` 以源码长度估算 buffer，收集 IR 后调用 `Document::propagate_expand`（`ruff_formatter/src/lib.rs:899-920`）。传播把硬换行、多行文本和 `ExpandParent` 向包围 group 上推，但把 `BestFitting` 作为边界（`document.rs:23-33,57-152`）：局部候选不会意外迫使外层布局展开。
4. `Printer` 用队列逐元素解释；软换行在 flat 模式消失或变空格，expanded 模式才换行并延迟缩进（`printer/mod.rs:69-160`）。group 根据模式或 `flat_group_print_mode` 决策，并记录 `GroupId` 的结果（`printer/mod.rs:170-180`）；测量状态区分首行、全部行与允许文本溢出（`printer/mod.rs:1617-1655`）。这是经典 document-printer 的“先表达选择、后全局决定”，比规则层边写边量宽更可组合，代价是 IR、回溯队列和 tag 配对校验都增加实现复杂度。
5. `formatted_file` 从数据库取得 options、解析模块和源码；输出与原文相同返回 `None`，否则返回新字符串（`ruff_python_formatter/src/lib.rs:180-200`）。【待主 agent 验证】CLI 将该 `Option<String>` 作为 check/write/diff 的输入，因本任务未读 CLI 调用点。

## 注释与范围格式化：两个语义护栏

注释归属器先用 visitor 构造 node-key map，空注释时不建遍历（`comments/mod.rs:234-257`），输出阶段按节点查询三段切片（`comments/mod.rs:279-359`）。这以“最接近意图”为启发式，不承诺 token 级精确；例如 AST 中不存在的位置只能靠具体规则挂到父节点（`comments/mod.rs:67-86`）。优点是通用规则可保持简洁，缺点是新语法或罕见注释形态的正确性依赖专用 placement/格式规则与测试，当前范围未逐行审阅 `placement.rs` 全部规则。

范围格式化不是截取文本后单独 format：它开启 source map、寻找完全覆盖选区的最深“逻辑行”节点，遇到 `fmt: off` 直接空结果，并用基准缩进打印后再切片（`range.rs:52-120,122-167`）。搜索排除子表达式、可疑 docstring、简单语句体和非标准缩进（`range.rs:127-153,191-237`）；因为孤立格式子表达式会改变可分割点，而在未格式化兄弟之间注入配置缩进会令 Python 词法失效（`range.rs:127-146,294-322`）。这是一项保守但正确性优先的取舍：可选区域较少，却保持“范围结果等于整文件相同行的结果”。

## 协作、取舍与评价

**依赖方向。** Python 层依赖 parser/AST/trivia、数据库和 `ruff_formatter`；通用层只知道 `FormatContext`、`FormatElement`、打印选项（`ruff_formatter/src/lib.rs:1-55,899-974`）。`FormatState` 令 context 和唯一 group-id 跨多个短生命周期 `Formatter` 持续存在（`lib.rs:922-974`），避免各规则各自命名或碰撞。该单向依赖是复用格式引擎的关键。【待主 agent 验证】上游 CLI/config 应只在构造 `PyFormatOptions` 时跨入本边界。

**亮点。**

- 注释“消费完毕”断言（`comments/mod.rs:361-385`）把最容易静默丢失的用户信息转为开发期失败，和格式器的保守语义目标一致。
- source position 只为逻辑行/模块且 source-map 启用时发射（`lib.rs:65-73`），将 range 功能的精度成本限定在需要它的模式。
- `Document::propagate_expand` 处理 interned 内容时缓存结果（`document.rs:93-101`），表明共享 IR 片段不会重复递归判断。

**问题与可行改进。**

- 节点级注释模型已承认 AST 缺口；把特例散落到各语法 formatter 会随着 Python 语法增长变难维护。可考虑把 placement 规则注册成可测试的“syntax shape -> anchor”表，但不能消除无节点锚点这个根本限制，且会增加 DSL/调试成本。
- range formatter 为正确性拒绝子表达式和非标准缩进，编辑器用户会感到能力边界。若重新设计，应先保留当前保守默认，再以明确 opt-in 尝试更宽的选区，并用整文件对照测试来约束；不能为覆盖率牺牲 Python 语义。

下一模块应沿着 `Printed` 的结果继续验证调用方如何以 CLI 的 check、diff 或写回策略消费它；本草稿只证明该模块最终返回 `Printed` 或“未变化/新字符串”。

## 实际读取覆盖率

覆盖率按本次实际发出的逐行读取命令的行区间并集计算，不把 `rg` 目录扫描计入；所列大文件的未读部分未用于上述结论。总计 `6,881 / 10,800 = 63.7%`，达到 standard 核心模块的 60% 下限 ✅。

|文件|总行数|已读行区间/行数|覆盖率|未读原因|
|---|---:|---:|---:|---|
|`ruff_python_formatter/src/lib.rs`|407|1-225 / 225|55.3%|主要入口已读；未读测试与尾部。|
|`context.rs`|467|1-467 / 467|100%|—|
|`comments/mod.rs`|1059|1-536 / 536|50.6%|未读后半 helper/测试。|
|`comments/map.rs`|838|1-590 / 590|70.4%|未读主要是测试。|
|`comments/placement.rs`|2462|1-390 / 390|15.8%|大型语法特例表未逐行审阅。|
|`range.rs`|776|1-500 / 500|64.4%|未读 visitor 后段和测试。|
|`options.rs`|513|1-513 / 513|100%|—|
|`ruff_formatter/src/lib.rs`|974|1-180、840-974 / 315|32.3%|未读通用 trait/类型细节。|
|`formatter.rs`|250|1-250 / 250|100%|—|
|`printer/mod.rs`|2109|1-1668 / 1668|79.1%|未读测试。|
|`format_element/document.rs`|945|1-260、650-816 / 427|45.2%|未读 IR display 中段与测试。|
|**合计**|**10,800**|**6,881**|**63.7% ✅**|有界读取；未读段落均已声明。|
