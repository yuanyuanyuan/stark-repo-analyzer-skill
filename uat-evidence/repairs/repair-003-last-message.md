主裁判接管完成最小修复。

改动文件：
- scripts/repo_analyzer.py
- tests/test_repo_analyzer_cli.py

根因：
- 外部 README/manifest 片段中的 Markdown fence、锚点链接和 wiki-link/shell 条件语法会被生成产物或验收脚本误判为产物自身结构。

测试结果：
- python -m unittest tests.test_repo_analyzer_cli.RepoAnalyzerCliTest.test_external_markdown_syntax_does_not_break_acceptance: PASS
- python -m unittest tests.test_repo_analyzer_cli: PASS
- claude-video 修复验证遇到 GitHub 443 连接失败，属于外部网络阻塞，进入后续 UAT 轮次重试。

剩余风险：
- 需要 run-002 独立 UAT 用真实目标仓库复验。
