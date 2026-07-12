# 阶段 7：交叉验证

## 覆盖率门控

| 模块草稿 | 声明覆盖 | 门槛 | 结论 |
|---|---:|---:|---|
| CLI 与配置编排 | 5,515 / 8,041 = 68.6% | 60% | ✅ 达标；`args.rs`、`format.rs` 个别覆盖较低但模块合计达标且原因披露 |
| Lint 执行、规则选择与安全修复 | 2,862 / 2,862 = 100.0% | 60% | ✅ 达标 |
| Python 格式化管线 | 6,881 / 10,800 = 63.7% | 60% | ✅ 达标 |

三个表均存在，均披露了分母、已读行数和未读原因。覆盖率是代理实际 `sed`/读取
范围的自报，并非由独立工具重新统计；主 agent 只验证其表格结构与若干关键证据。

## 主 agent 抽查

| 草稿结论 | 复核源码 | 结果 |
|---|---|---|
| CLI `run` 按子命令调度，并在 check/format 路径交给共同设置解析 | `crates/ruff/src/lib.rs:128-264`; `crates/ruff/src/commands/check.rs:37-193`; `commands/format.rs:70-150` | ✅ 支持 |
| lint 修复按安全适用性筛选、跳过隔离组和位置重叠编辑，并构造 source map | `crates/ruff_linter/src/fix/mod.rs:29-124` | ✅ 支持 |
| formatter 的公开入口依次 parse、收集 trivia/comments、格式化并 print | `crates/ruff_python_formatter/src/lib.rs:136-178`; `crates/ruff_formatter/src/printer/mod.rs:44-92` | ✅ 支持 |

## 跨模块结论

1. **已验证：路径化的设置是共享边界。** CLI 草稿与 `check.rs`/`format.rs` 的抽查均
   显示：前端不把所有设置静态塞给某个算法，而是先构造 resolver，再按文件取得
   `LinterSettings` 或 `FormatterSettings`。这使 monorepo 差异进入同一个入口，却不
   把 lint 与 format 算法耦合。
2. **已验证：两个执行引擎的“安全”含义不同但互补。** Linter 的安全来自 fix
   applicability、隔离与重叠处理；formatter 的安全来自可解析输入、注释归属和
   document printer。二者都由 CLI 选择路径，但没有共享“改写算法”。
3. **部分验证：统一工具链依赖共享 Python 基础设施。** `AGENTS.md` 明确 Ruff/ty
   共享 parser/AST，formatter 与 linter 草稿也引用 parser/AST；但本次没有阅读
   parser/AST 实现或所有 CLI 消费代码，因此不对完整依赖图作更强结论。

## 未验证与限制

- 没有执行 CLI、测试、基准或 Clippy；无法确认静态路径在该环境构建、性能或端到端
  行为。
- 未审阅单条 lint rule、缓存、notebook、LSP、WASM、ty 或 parser/AST 内部。
- 没有 Git 历史或网络资料，故不声称设计演进原因或外部竞争格局已独立验证。
