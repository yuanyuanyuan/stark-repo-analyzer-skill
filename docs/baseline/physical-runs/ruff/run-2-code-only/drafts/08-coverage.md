# 08 覆盖率汇总

覆盖率按 reference-skill 口径，只计实际读取的行范围；Graphify 节点/边不计入行覆盖率。

| 模块 | 总行数 | 已读行数 | 覆盖率 | 备注 |
|---|---:|---:|---:|---|
| CLI/config | 1524 | 520 | 34.1% estimated | 重点入口与参数模型；未声称达 standard 60% |
| lint/fix | 795 | 482 | 60.6% estimated | check 全读，diagnostics 局部 |
| formatter/printer | 1961 | 1156 | 58.9% estimated | printer 全读，format 局部 |
| parser/AST | not measured | bounded | estimated | 入口、token source、visitor |
| cache | 1098 | bounded core | estimated | 持久化、key、读写路径 |
| server | not measured | bounded | not measured | 目录与关键入口 |
| ty | not measured | navigation only | not measured | 不声称覆盖 |

结论：本报告是 bounded standard 分析，不是 Ruff 全仓库覆盖；未执行 build/test/P5，不能把静态结论升级为运行时保证。
