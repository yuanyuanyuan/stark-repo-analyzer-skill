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
- available_modes: standard
- blocked_modes: deep
- deep missing: reference-edges

## 安装焦点
只补齐 deep 缺失能力：reference-edges。优先使 reference-edges 在目标仓可验证：Universal Ctags 须能产出 roles=reference；Graphify 图边在接入 units 前不能单独冒充 complete refs。symbol-enumeration 可再补 ast-grep。

## 官方来源
- ast-grep: https://ast-grep.github.io/ (verified 2026-07-11)
- git: https://git-scm.com/doc (verified 2026-07-11)
- graphify: https://github.com/safishamsi/graphify (verified 2026-07-11)
- grep: https://www.gnu.org/software/grep/manual/ (verified 2026-07-11)
- jq: https://jqlang.github.io/jq/ (verified 2026-07-11)
- ripgrep: https://github.com/BurntSushi/ripgrep (verified 2026-07-11)
- universal-ctags: https://docs.ctags.io/ (verified 2026-07-11)

## 验收
重新运行:
`repo-analyzer doctor --repo <REPO> --out <OUT>`
确认 capability matrix 中目标模式 available，且未污染被分析仓库。
