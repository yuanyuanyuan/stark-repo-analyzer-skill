你是 repair 子代理。当前裁判 UAT run-005 未满分，原因不是 acceptance，而是最终交付报告质量：`agent-runs/modules-batch/result.md` 和 `drafts/06-module-*.md` 里已有 `## Agent 深度分析`，但 `ANALYSIS_REPORT*.md` 仍偏底料索引，没有把 agent 深度分析汇入最终报告，tech report 还写着“需要后续 subagent 深化”。

目标：修复 stark-repo-analyzer skill，使 agent 模式下最终报告是真正完整交付物。

要求：
1. 只改必要文件，优先 `scripts/repo_analyzer.py`、`templates/*.tmpl.md`、`tests/test_repo_analyzer_cli.py`，必要时更新 `SKILL.md` 和 `references/PLAN_COMPLIANCE.md`。
2. 在 `REPORT_DATA.json` 中加入 agent 模式/状态和模块深度分析摘要数据。
3. `ANALYSIS_REPORT.md` 和 `ANALYSIS_REPORT.tech-lead.md` 至少必须包含 `Agent 深度分析摘要`，并展示每个模块的 agent 结论摘要/证据；business 和 learning 报告也应有面向受众的 agent insight 摘要。
4. 当 `AGENT_SUMMARY.mode != deterministic` 且 status PASS 时，报告不能再写“需要后续 subagent 深化”这类过时措辞。
5. acceptance 增加硬断言：agent 模式下最终报告必须包含 agent insights。
6. 补/改单元测试，运行 `python -m unittest tests.test_repo_analyzer_cli`、`python -m py_compile scripts/repo_analyzer.py scripts/render_report.py tests/test_repo_analyzer_cli.py`、`git diff --check`。
7. 不要修改 UAT evidence 旧产物，不要提交 commit。

完成后返回：改了哪些文件、测试结果、仍然存在的风险。
