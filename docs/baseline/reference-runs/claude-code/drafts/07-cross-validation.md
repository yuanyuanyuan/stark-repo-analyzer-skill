# 07 Cross Validation

## Method

从每个核心草稿抽取关键结论，回到固定 commit 的源码路径核对；跨模块推断只在两个以上模块都提供证据时成立。

## Validated Conclusions

| 结论 | 证据一 | 证据二 | 结果 |
|---|---|---|---|
| 查询循环负责继续条件，工具运行时负责调用级生命周期 | `query.ts:219-307` | `toolOrchestration.ts:19-82` | 通过 |
| 工具池会在模型看到工具前应用 deny 规则 | `tools.ts:253-327` | `Tool.ts:123-158` | 通过 |
| 工具结果会形成下一轮查询输入 | `query.ts:551-580`, `788-861` | `toolOrchestration.ts:118-176` | 通过 |
| 子代理复用查询循环但使用独立/子级上下文 | `runAgent.ts:697-756` | `Task.ts:38-57` | 通过 |
| 技能可以从路径条件进入动态技能集合 | `loadSkillsDir.ts:985-1058` | `commands.ts:476-505` | 通过 |
| 记忆写入使用受限工具策略 | `sessionMemory.ts:387-481` | `autoDream.ts:216-233` | 通过 |
| 远程桥接采用 allowlist，而不是开放全部本地命令 | `commands.ts:610-686` | `main.tsx:87-98` | 通过，具体传输未验证 |

## Cross-Module Design Pattern

源码呈现一个一致模式：先建立显式上下文/策略，再把能力转换为统一记录，最后由共享执行循环消费。工具、命令、技能、MCP 都趋向“注册/过滤/执行”三段式；任务和记忆则在此基础上增加持久化、取消和后台门控。

## Corrections and Unverified Items

- README 把 `main.tsx` 描述为核心 CLI 入口，这与源码导入和函数位置一致；但 README 提到的 40+ 工具只做了目录/注册层核对，未逐个统计发行构建可见工具。
- 官方文档的多表面定位与命令中的 remote/bridge allowlist 相容，但不能证明当前镜像包含官方所有客户端。
- `feature()` 和环境变量的大量分支只能证明“存在条件路径”，不能证明本 commit 的生产构建启用了哪些路径。
- 没有发现可运行的测试配置，因此未进行动态行为验证；所有结论是静态证据结论。
