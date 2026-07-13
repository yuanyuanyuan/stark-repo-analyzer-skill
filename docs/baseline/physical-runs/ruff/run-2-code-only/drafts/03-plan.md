# 03 规模与计划

Ruff 是大型 Rust 单仓工具链。本次 standard 分析采用 bounded scope：以用户可感知的 CLI/config、lint/fix、formatter/printer 为三条核心主线；以 parser/AST、cache、server、ty 为次要边界。原因是全仓库逐行深读会把“扫描”误写成“理解”，且不符合本次要求的诚实覆盖。

规模盘点：`find crates -path '*/src/*.rs' ... wc -l` 得到 664,970 行，包含测试与生成代码，未测量纯生产行数。重点文件：`crates/ruff/src/args.rs` 1524 行，`commands/check.rs` 302 行，`commands/format.rs` 1425 行，`cache.rs` 1098 行，`printer.rs` 536 行。

核心问题：Ruff 如何把“配置解析、文件发现、解析、规则执行/修复、稳定输出”组织成一条低摩擦 CLI 流程，并同时服务 formatter 与 LSP/server？

阶段计划：研究说明 → 模块叙事 → 核心深读 → 次要边界 → 交叉验证 → 洞察 → 覆盖率 → 融合。Graphify 只提供代码关系导航；源码和行号决定结论。
