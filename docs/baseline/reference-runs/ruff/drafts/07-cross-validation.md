# 交叉验证

## 验证规则

交叉验证只检查本地 commit 可见的实现，公开资料不作为实现证据。每个结论至少对照一个调用方和一个被调用方；跨模块推断若无法完整读完则保留限制。

## 已验证链路

1. `ruff/src/lib.rs:243-248` 调用 `resolve::resolve`，随后 `commands::check::check` 在 `ruff/src/commands/check.rs:1-120` 调用 `project_files_in_path`。因此“CLI 先得到项目配置，再发现文件”有直接调用链证据。
2. `commands/check.rs:80-120` 为每个 resolved path 调用 `resolver.resolve(path)` 并传入 `settings.linter`；`ruff_linter/src/linter.rs:119-238` 再以文件为并行单位执行。配置到 linter 的契约成立。
3. `ruff/src/lib.rs:296-319` 选择 `FixMode`，`ruff_linter/src/fix/mod.rs:54-165` 合并 edits，说明修复模式由 CLI 策略控制、由 linter 负责执行，而不是规则直接写盘。
4. `ruff_python_parser/src/lib.rs:281-387` 提供 `Parsed<Mod>`，formatter 的 `format_module_source`/`format_module_ast`（`ruff_python_formatter/src/lib.rs:136-180`）和 semantic `check_file`（`ty_python_semantic/src/lib.rs:181-215`）都把 parser 产物作为下游输入。共享 frontend 是已验证的架构事实。
5. `ruff_formatter/src/lib.rs:596-705,859-940` 的 Format traits、write/format API 与 `ruff_python_formatter` 的 node formatting API 相连，验证了“Python 后端生成通用 document、通用 printer 负责输出”的边界。
6. `ruff/src/lib.rs:385-442` 仅在 TOML 变更时重新 resolve，普通 Python 变更直接重新执行检查；watch 的配置/源文件分流由代码直接支持。

## 未完成验证

- 规则 registry 到每个规则实现的完整映射未遍历；不能验证全部 900+ 规则或每条 fix 的安全标记。
- parser 到所有语法节点的覆盖不足；只验证公共 API、控制模块和 lexer 主体。
- LSP 是否对所有请求路径复用完全相同的 CLI settings 未逐请求验证。
- ty 与 Ruff linter 的配置共享程度只验证了 workspace/DB 入口，未验证所有配置转换。

## 交叉结论

Ruff 的稳定核心不是某个单独的规则，而是多个边界的组合：`Settings/Resolver` 决定输入，parser/AST 提供共享结构，linter 和 formatter 分别消费它们，CLI/Printer 将结果转换为人类或 CI 可消费的契约。这个结论有调用链证据；更深的性能原因（如每阶段具体 benchmark）在本次未运行基准测试，标记为待验证。
