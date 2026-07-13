# 检查结果

| 检查 | 结果 | 证据 |
|---|---|---|
| 输出文件存在 | PASS | `report.md`、`metadata.json`、`execution-log.md`、`drafts/` 均已生成 |
| 源 HEAD | PASS | `a371abbe75ffa0d0a3c92290e2bbf56a7ef54367` |
| 源树未显示修改 | PASS | 执行期间 `git status --short` 无输出 |
| Git history 未使用 | PASS | 执行日志无 history 命令 |
| 外部调研 | not performed | 当前环境未提供 WebSearch/WebFetch |
| subagent 并行分析 | not performed | 当前工具面未提供 Agent 调度接口 |
| build/test | not performed | 未安装/确认项目依赖，避免改变源树 |
| 覆盖率门控 | PARTIAL | 代表性文件有明细；完整标准覆盖率未达成 |

结论：产物完整性通过；分析覆盖限制已公开记录。

| Graphify extraction | PASS | `graphify 0.9.8`, 16,226 raw nodes / 61,639 raw edges |
| Graphify normalization | PASS | 16,205 source-locatable nodes / 61,615 edges; `doctor post-graph` exit 0 |
| Graphify target isolation | BLOCKED | Graphify created transient target `graphify-out/`; cleaned and source rechecked clean |
