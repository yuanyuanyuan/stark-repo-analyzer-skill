你是新的修复代理。只做一个小修复。

工作目录：`/Users/chuzu/projests/stark-repo-analyzer-skill`

只允许修改：
- `scripts/repo_analyzer.py`
- `tests/test_repo_analyzer_cli.py`

不要修改：
- `uat-evidence/run-001`
- UAT 评分标准
- 目标仓库

失败来自 run-001 的 `acceptance/check.sh`：
- `FAIL|wikilinks valid`
- `FAIL|anchors:02a-manifest-card.md`
- `FAIL|markdown fences balanced`

请直接修复通用根因：
1. 外部 README 片段嵌入 Markdown 时，不能让目标 README 内的 ``` 破坏生成报告的 fence 平衡。
2. 外部 README 片段中的 `(#install)` 这类锚点链接，不能被生成产物的锚点验收当作产物自身锚点失败。
3. shell 代码里的 `[[ ... ]]` 不能被验收脚本当作 wiki link。

推荐最小方案：
- 增加一个小 helper，只用于把外部 README 摘要行安全嵌入 Markdown：把行内 ``` 替换成不会触发 fence 的文本，或者对整段做最小转义。
- 在 `report_body()` 的 README 摘要处使用该 helper。
- 在 `write_manifest_card()` 的 fenced README 片段处使用该 helper，避免内层 ```。
- 在生成的验收脚本里，让 wiki link 检查只扫描 markdown 文件，并忽略代码围栏内文本；锚点检查也忽略代码围栏内文本。
- 增加一个最小测试：构造 README 含 fenced code、`(#install)` 和 shell `[[ -z "$DEST" ]]`，运行 analyzer + acceptance，断言通过，并断言主报告 fence 平衡。

运行相关测试。最终回复只写：改动文件、根因、测试结果、剩余风险。
