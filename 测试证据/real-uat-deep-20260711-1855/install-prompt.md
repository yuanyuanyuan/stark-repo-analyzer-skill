# AI Installation Agent Prompt

目标模式: deep
规则版本: 2.2.0

## 任务
为 Repo Analyzer 配置可选增强工具，使目标模式可用。

## 范围约束（强制）
1. **不得**修改被分析仓库的源码或依赖清单（package.json / Cargo.toml / go.mod / pyproject.toml 等），除非用户对本次安装显式授权且与分析证据隔离。
2. 只安装或配置满足缺失能力所需的最小工具集；禁止为凑齐工具包盲目安装。
3. 安装后回报：命令路径、版本号、以及 doctor 能力矩阵是否放行目标模式。
4. 不要在分析 run 内把 deep 静默降级为 standard。

## 当前能力矩阵摘要
- available_modes: standard, deep
- blocked_modes: (none)
- deep missing: (none)

## 安装焦点
deep 能力已满足；若用户仍要安装，仅做版本确认并回报，不要重复安装。

## 官方来源
- ast-grep: https://ast-grep.github.io/ (verified 2026-07-11)
- graphify: https://github.com/safishamsi/graphify (verified 2026-07-11)
- universal-ctags: https://docs.ctags.io/ (verified 2026-07-11)

## 验收
重新运行:
`repo-analyzer doctor --repo <REPO> --out <OUT>`
确认 capability matrix 中目标模式 available，且未污染被分析仓库。
