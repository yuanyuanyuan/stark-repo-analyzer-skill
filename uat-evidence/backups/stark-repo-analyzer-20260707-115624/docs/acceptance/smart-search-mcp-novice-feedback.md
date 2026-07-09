# smart-search-mcp 小白验收反馈追踪

## 场景

- 角色：第一次使用 `stark-repo-analyzer` skill 的小白用户子代理。
- 目标仓库：`https://github.com/adminhuan/smart-search-mcp`。
- 验收命令：

```bash
python3 scripts/repo_analyzer.py https://github.com/adminhuan/smart-search-mcp --output analysis --mode all --no-question
analysis/acceptance/check.sh
```

## 反馈与处理

| 反馈 | 处理方式 | 回归证据 |
|---|---|---|
| 不清楚跑完后先看哪个文件。 | `SKILL.md` 增加“跑完后先看”顺序。 | `analysis/README.md` 和 `SKILL.md` 都列出主入口。 |
| 报告里切片引用不完整。 | 报告按 repo 类型动态列出实际生成的 `slices/` 文件。 | `acceptance/check.sh` 断言主报告中的 `slices/*` 引用都存在。 |
| git 历史热点会混入 `node_modules`。 | 历史统计过滤全局忽略目录。 | `test_report_only_links_existing_artifacts_and_history_ignores_dependencies` 覆盖。 |
| 三份受众报告过于相似。 | `tech-lead`、`business`、`learning` 增加各自关注段落。 | `acceptance/check.sh` 断言受众标记和两两差异度。 |
| 报告自称“骨架/待补全”，影响可交付感。 | 覆盖与状态报告改为确定性验收完成状态，只保留主观复核边界。 | `test_coverage_and_state_are_final_deterministic_outputs` 覆盖。 |
| MCP 工具名没有显式抽取。 | 从 JS/TS 源码抽取 `ai_*` 工具名并写入报告和模块草稿。 | `test_reports_mcp_tool_names_from_source` 覆盖。 |

## 当前结论

小白用户路径已收敛为：运行一条 CLI 命令，先看 `analysis/README.md`，再看项目名片、主报告和切片；本地验收脚本会检查核心产物、引用链、API 表面、受众差异和门控状态。
