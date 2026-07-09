你是一位资深架构师，请基于已生成的 repomix 切片和模块底稿，对所有模块做判断型深度分析。

## 输入
- 分析目录: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts
- 模块清单: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/05-module-ids.yaml
- 模块底稿目录: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts
- 主要证据切片: `slices/02-backend.xml`、`slices/04-docs.xml`、`slices/06-tests.xml`、`slices/09-dependencies.xml`、`slices/12-history-hotspot.txt`

## 模块任务
### MODULE module_001
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_001.md
- 模块分组: skills
- 模块层级: core
- 需在 repomix 切片中核对的源码路径:
- skills/watch/.skillignore
- skills/watch/SKILL.md
- skills/watch/scripts/build-skill.sh
- skills/watch/scripts/config.py
- skills/watch/scripts/download.py
- skills/watch/scripts/frames.py
- skills/watch/scripts/setup.py
- skills/watch/scripts/transcribe.py
- skills/watch/scripts/watch.py
- skills/watch/scripts/whisper.py

### MODULE module_002
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_002.md
- 模块分组: tests
- 模块层级: core
- 需在 repomix 切片中核对的源码路径:
- tests/conftest.py
- tests/test_config.py
- tests/test_dedup.py
- tests/test_download.py
- tests/test_fixtures.py
- tests/test_frames.py
- tests/test_setup.py
- tests/test_timestamps.py
- tests/test_watch.py
- tests/test_whisper.py

### MODULE module_003
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_003.md
- 模块分组: [root]
- 模块层级: core
- 需在 repomix 切片中核对的源码路径:
- .gitattributes
- .gitignore
- .skillignore
- AGENTS.md
- CHANGELOG.md
- CLAUDE.md
- LICENSE
- README.md
- dev-sync.sh

### MODULE module_004
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_004.md
- 模块分组: .claude-plugin
- 模块层级: minor
- 需在 repomix 切片中核对的源码路径:
- .claude-plugin/marketplace.json
- .claude-plugin/plugin.json

### MODULE module_005
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_005.md
- 模块分组: hooks
- 模块层级: minor
- 需在 repomix 切片中核对的源码路径:
- hooks/hooks.json
- hooks/scripts/check-setup.sh

### MODULE module_006
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_006.md
- 模块分组: .agents
- 模块层级: minor
- 需在 repomix 切片中核对的源码路径:
- .agents/plugins/marketplace.json

### MODULE module_007
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_007.md
- 模块分组: .codex-plugin
- 模块层级: minor
- 需在 repomix 切片中核对的源码路径:
- .codex-plugin/plugin.json

### MODULE module_008
- 模块底稿: /Users/chuzu/projests/stark-repo-analyzer-skill/uat-evidence/run-005/artifacts/drafts/06-module-module_008.md
- 模块分组: .github
- 模块层级: minor
- 需在 repomix 切片中核对的源码路径:
- .github/workflows/release.yml


## 要求
- 不要调用任何 skill，不要运行 repo_analyzer.py，不要重新生成 analysis；只读取上面列出的分析目录文件。
- 不要写入任何文件，不要修改 analysis 目录；只在最终回复中返回 Markdown。
- 不要在分析目录根部直接读取源码路径；源码内容来自 `slices/*.xml` 中的 `<file path="...">`。
- 只基于分析目录中的证据判断，不要编造源码事实。
- 补充业务角色、设计思路、关键数据流、模块协同、架构亮点和风险。
- 每个关键判断必须引用已有证据文件路径。
- 每个模块必须按下面格式输出，方便脚本拆分；不得省略任何模块：

<!-- MODULE_RESULT: module_xxx -->
## Agent 深度分析

...该模块分析...
<!-- END_MODULE_RESULT -->
