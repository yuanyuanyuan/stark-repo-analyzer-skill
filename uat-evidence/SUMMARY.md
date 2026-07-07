# stark-repo-analyzer v1 UAT 总结

## 安装

- 安装方式：软链接，不复制文件。
- 当前链接：`~/.codex/skills/stark-repo-analyzer -> /Users/chuzu/projests/stark-repo-analyzer-skill`
- 旧版本处理：原有 `~/.codex/skills/stark-repo-analyzer` 已备份到 `uat-evidence/backups/` 后清理。
- 测试调用方式：`$stark-repo-analyzer`

## UAT 规则

- 目标仓库：`https://github.com/bradautomates/claude-video`
- 证据根目录：`/Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence`
- 每轮测试使用新的独立 `codex -exec` 会话。
- 评分维度共 6 项：用户使用友好度、使用简易度、结果契合度、结果完整性、执行稳定程度、证据完整性与可复查性。
- 判定标准：6 项都必须 `5/5` 才通过；任一维度非满分则打回修复并重新测试。

## run-001

- 目录：`uat-evidence/run-001/`
- 结果：不通过。
- 证据：测试会话完成并生成产物，但验收脚本返回失败。
- 失败项：
  - `FAIL|wikilinks valid`
  - `FAIL|anchors:02a-manifest-card.md`
  - `FAIL|markdown fences balanced`
- 裁判报告：`uat-evidence/run-001/JUDGE.md`

## 修复

- 修复目录：`uat-evidence/repairs/`
- 修复摘要：
  - 对外部 README、manifest 摘录做 Markdown 中性化，避免目标仓库内容中的 fenced code、`[[...]]` 和本地 anchor 干扰交付物结构。
  - 验收脚本在检查 wikilink 和 anchor 前剥离 fenced code，避免把代码示例误判为文档结构。
  - 新增回归测试覆盖外部 Markdown 语法不应破坏验收流程。
- 验证：
  - `python -m unittest tests.test_repo_analyzer_cli.RepoAnalyzerCliTest.test_external_markdown_syntax_does_not_break_acceptance` 通过。
  - `python -m unittest tests.test_repo_analyzer_cli` 通过。
  - `graphify update .` 已运行并通过，维护日志在 `uat-evidence/repairs/graphify-update-after-repair-003.log`。

## run-002

- 目录：`uat-evidence/run-002/`
- 结果：通过。
- 测试代理退出码：`0`
- 裁判侧二次验收退出码：`0`
- 产物目录：`uat-evidence/run-002/artifacts/`
- 关键证据：
  - `uat-evidence/run-002/prompt.md`
  - `uat-evidence/run-002/environment.txt`
  - `uat-evidence/run-002/codex-session.log`
  - `uat-evidence/run-002/codex-last-message.md`
  - `uat-evidence/run-002/acceptance-recheck.log`
  - `uat-evidence/run-002/JUDGE.md`

## run-003

- 目录：`uat-evidence/run-003/`
- 触发原因：用户发现 `ANALYSIS_REPORT.md` 与 `ANALYSIS_REPORT.tech-lead.md` 字节级完全相同，run-002 裁判漏判。
- 修复摘要：
  - `ANALYSIS_REPORT.md` 在 `all` 模式下改为总览/导航报告。
  - `ANALYSIS_REPORT.tech-lead.md` 保持技术负责人报告。
  - 验收脚本新增 `main report distinct`，防止主报告再次等于任一受众报告。
- 结果：通过。
- 测试代理退出码：`0`
- 裁判侧二次验收退出码：`0`
- 报告比对：`REPORT_COMPARE=DIFFERENT`
- 关键证据：
  - `uat-evidence/run-003/prompt.md`
  - `uat-evidence/run-003/codex-session.log`
  - `uat-evidence/run-003/codex-last-message.md`
  - `uat-evidence/run-003/acceptance-recheck.log`
  - `uat-evidence/run-003/report-compare.log`
  - `uat-evidence/run-003/JUDGE.md`

## 最终结论

`stark-repo-analyzer` v1 已完成软链接安装、独立 Codex 使用测试、失败修复、重新测试和裁判评估。run-003 修复了主报告与技术报告重复的问题，6 个评分维度全部为 `5/5`，最终判定为 UAT 通过。
