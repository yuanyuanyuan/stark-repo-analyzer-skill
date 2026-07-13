# 03 研究说明

## 研究边界

没有外部网络调研、Git history 或项目 build/test，均按输入约束标记 not performed。研究材料是固定 HEAD 源码、参考规范、`input.md` 与预生成 Graphify code-only 证据。

## 问题与定位

Ruff 面向需要在大量 Python 文件上快速、可自动修复、可持续集成的开发者。源码把它实现为同时拥有 linter、formatter、配置解析、缓存和语言服务器入口的 Rust workspace，而不是单一规则集合。CLI 在 `crates/ruff/src/args.rs:116-198` 把 check、format、server、config、analyze 等能力统一成命令模型。

## 竞品定位

本次不做外部事实对比。仅能从源码推断设计方向：Ruff 把 lint 与 format 放在同一个 CLI 和共享 workspace/settings 体系内；这一点区别于只提供单一职责的 formatter 或只提供诊断的 linter。具体竞品性能、历史动机和用户评价均未调研，不作断言。

## 独特价值假设

源码证据支持的保守表述是：统一配置、共享缓存、统一诊断输出和 Rust 实现共同服务“低延迟批处理工具”目标；不能仅凭本次 bounded reading 证明全部性能结论。
