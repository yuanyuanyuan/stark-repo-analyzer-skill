# 修复计划：019f3787 会话 Review 问题

目标：修复 `stark-repo-analyzer v0.1.0` 在小白用户验收中暴露的问题，让下一次对 `https://github.com/adminhuan/smart-search-mcp` 的验收能真实覆盖完整分析、多受众报告、双代理终验收和裁决评分。

来源问题记录：

- `/Users/chuzu/projests/video-know-it/analysis-review-019f3787.md`

## 总体策略

先修会导致“假通过”的问题，再修报告可信度和使用体验。

最小修复面：

1. `scripts/repo_analyzer.py`：报告生成、验收脚本生成、状态语义、复现命令、风险提示。
2. `tests/test_repo_analyzer_cli.py`：用公共 CLI 行为覆盖每个非平凡修复。
3. `SKILL.md`：把小白用户完整分析路径写成默认可执行路径，并明确终验收要求。
4. `docs/acceptance/`：记录小白用户验收和裁决评分。

非目标：

- 不引入新依赖。
- 不做通用 agent 编排框架。
- 不把 `smart-search-mcp` 的人工评价塞进确定性 CLI。
- 不修复无关工作区改动。

## 阶段 1：关闭 P0 假通过

### 1.1 完整模式强制三份受众报告

问题覆盖：

- P0：未生成三份受众报告。
- P0：验收脚本把缺失受众报告当 optional。

改动点：

- 保留 CLI 当前 `--mode tech-lead|business|learning|all` 能力。
- 修改 `write_acceptance`：只要 `README.md` 或 `03-question-answers.md` 显示 `报告受众: all` / `报告模式: all`，就强制要求：
  - `ANALYSIS_REPORT.tech-lead.md`
  - `ANALYSIS_REPORT.business.md`
  - `ANALYSIS_REPORT.learning.md`
- 完整模式下删除 `PASS|audience reports optional` 的通过语义，改为缺失即 `FAIL|audience reports required`。
- 单受众模式仍允许只生成一份报告，但输出必须明确 `single audience mode`，避免误认为完整验收。

TDD 切片：

1. 新增测试：`--mode all` 后删除 `ANALYSIS_REPORT.business.md`，`acceptance/check.sh` 必须失败。
2. 新增测试：默认 `tech-lead` 模式下验收通过，但输出含 `audience reports skipped:single-mode`，不再出现 `optional`。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli.RepoAnalyzerCliTest.test_mode_all_writes_three_reports_and_acceptance_entrypoint
```

验收标准：

- `--mode all` 缺任一受众报告必失败。
- 验收输出不再包含 `PASS|audience reports optional`。

### 1.2 小白用户验收默认使用 `--mode all`

问题覆盖：

- P0：未生成三份受众报告。
- P1：最终答复误导。

改动点：

- 更新 `SKILL.md` 的“最小运行方式”命名：
  - `快速基线扫描`：允许单受众。
  - `完整分析 / 验收路径`：必须 `--mode all --no-question`。
- 在 `SKILL.md` 终验收中明确：小白用户子代理必须运行完整分析路径。

验证命令：

```bash
python3 scripts/repo_analyzer.py https://github.com/adminhuan/smart-search-mcp --output analysis-novice-final --mode all --no-question
analysis-novice-final/acceptance/check.sh
```

验收标准：

- `analysis-novice-final/README.md` 显示 `报告模式: all`。
- 三份受众报告存在。
- 验收脚本 exit 0。

## 阶段 2：状态语义和报告可信度

### 2.1 区分确定性基线通过和完整分析通过

问题覆盖：

- P1：`PASS_DETERMINISTIC_ACCEPTANCE` 语义过强。
- P1：最终答复把基线通过说成完整验收通过。

改动点：

- `STATE_REPORT.md` 改为：
  - `deterministic_status: PASS`
  - `judgement_status: PENDING`
  - `final_acceptance_status: PENDING`
- 如果只是 CLI 产物通过，不写 `final`。
- 最终通过只能出现在裁决代理评分记录中。

TDD 切片：

1. 更新 `test_coverage_and_state_are_final_deterministic_outputs`，断言状态文件不含 `final`，且含 `judgement_status: PENDING`。
2. 验收脚本检查 deterministic 状态，不把 judgement pending 当失败。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli.RepoAnalyzerCliTest.test_coverage_and_state_are_final_deterministic_outputs
```

验收标准：

- CLI 自动验收只声明确定性基线通过。
- 完整终验收由裁决记录单独声明。

### 2.2 修正报告里的验收能力描述和架构图

问题覆盖：

- P1：报告声称验收会检查“报告差异”，但缺失报告时不检查。
- P2：架构图显示“多受众报告”，但单模式不是多受众。

改动点：

- `report_body` 根据 `mode` 生成不同描述：
  - `all`：图示 `多受众报告`，验收说明含受众差异检查。
  - 单受众：图示 `单受众报告`，验收说明不声称多报告差异。
- 技术负责人段落里的验收说明从固定文本改成基于模式的文本。

TDD 切片：

1. 默认模式报告不包含 `多受众报告`。
2. `--mode all` 主报告包含三份报告链接和多受众差异说明。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli
```

验收标准：

- 单模式报告不再暗示多受众已完成。
- 完整模式报告和验收脚本语义一致。

### 2.3 修正复现命令

问题覆盖：

- P2：报告中的复现命令不可直接运行。

改动点：

- 报告复现命令使用本次实际脚本路径：
  - 如果脚本位于当前仓库：写 `python3 /abs/path/to/scripts/repo_analyzer.py ...`
  - 同时保留可移植说明：`或在 skill 源码目录运行 scripts/repo_analyzer.py`。
- 复现命令包含实际 `--mode`。

TDD 切片：

1. 用临时输出目录运行 CLI，断言报告中包含 `str(CLI)` 和当前 mode。
2. `--mode all` 报告复现命令必须包含 `--mode all`。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli
```

验收标准：

- 用户复制报告命令可复现同类输出。
- 不再出现错误的 `python3 scripts/repo_analyzer.py ... --no-question` 单一路径。

## 阶段 3：分析质量风险提示

### 3.1 空测试/示例切片显式进入主报告

问题覆盖：

- P2：测试和示例切片为空，但主报告未提示风险。

改动点：

- 在 `工程成熟度` 下新增 `风险提示` 小节。
- 当 `slices/06-tests.xml` 为空或没有测试文件时，写：
  - `未识别到真实测试文件`
  - 如果 `package.json` 的 test 是 `echo`，写 `test 脚本疑似占位`
- 当 `slices/10-examples.xml` 为空时，写：
  - `未识别到示例或 demo 文件`

TDD 切片：

1. fixture 中 `package.json` 写 `"test":"echo 'ready'"`，报告必须提示占位测试。
2. fixture 增加真实 `test_*.py` 或 `*.test.js` 时，不应提示无测试文件。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli
```

验收标准：

- 主报告能让只读报告的用户看到测试风险。

### 3.2 单模块扫描限制写明

问题覆盖：

- P2：模块划分过粗。

改动点：

- 如果 `module_rows` 只返回 `[root]` 且文件数大于 1，在模块清单后增加提示：
  - `当前为路径分组得到的单模块，不等同于真实架构边界。`
- 不在本轮重写模块划分算法；这是更大改动，先用报告诚实表达限制。

TDD 切片：

1. 小仓库只有 `[root]` 模块时，报告包含限制说明。

验证命令：

```bash
python -m unittest tests.test_repo_analyzer_cli
```

验收标准：

- 后续 subagent 不会把 `[root]` 误当成真实架构边界。

## 阶段 4：终验收记录

### 4.1 小白用户子代理记录

问题覆盖：

- P0：未执行小白用户子代理。
- P3：开头长篇 prompt 噪音。

改动点：

- 新建或更新 `docs/acceptance/smart-search-mcp-novice-feedback.md`。
- 记录：
  - 小白用户目标。
  - 实际命令。
  - 产物路径。
  - 关键困惑点。
  - 是否能独立找到 README、主报告、三份受众报告和验收脚本。
- 要求 agent 输出简短执行进度，不再生成长篇“优化后的完整提示词”作为验收的一部分。

验收命令：

```bash
python3 scripts/repo_analyzer.py https://github.com/adminhuan/smart-search-mcp --output analysis-novice-final --mode all --no-question
analysis-novice-final/acceptance/check.sh
```

验收标准：

- 小白用户记录中有 action summary。
- 记录显示三份受众报告均被找到并打开。
- 无 `PASS|audience reports optional`。

### 4.2 裁决代理评分记录

问题覆盖：

- P0：未执行裁决代理。

改动点：

- 新建 `docs/acceptance/smart-search-mcp-judge-report.md`。
- 裁决 rubric 固定为 10 分：
  - 任务完成度 2 分。
  - 小白用户易用性 1.5 分。
  - 仓库分析正确性 2 分。
  - 证据质量 1.5 分。
  - 克制和简单性 1 分。
  - 失败处理和诚实边界 2 分。
- 分数低于 9.5 时，不能标记通过；列出最高影响扣分项，回到阶段 1-3 修复。

验收标准：

- 裁决报告包含分项评分、总分、扣分理由。
- 总分 `>= 9.5/10` 才能写 `final_acceptance_status: PASS`。

## 阶段 5：权限和发布前清理

### 5.1 避免 root-owned 产物

问题覆盖：

- P2：产物归属为 root。

改动点：

- 不在 CLI 里写 `chown`，因为权限归属应由运行用户决定。
- 在验收流程中增加检查命令：

```bash
find analysis-novice-final ! -user "$(id -un)" -maxdepth 3 -print
```

- 如果有输出，本次验收失败，先修运行方式。

验收标准：

- 新产物归属当前用户。
- 文档提醒不要用 `sudo` 跑 skill。

### 5.2 发布前安装版回归

改动点：

- 把修复后的 skill 复制到 `~/.codex/skills/stark-repo-analyzer/`。
- 用安装版路径跑一次真实验收，而不是只跑源码仓库脚本。

验证命令：

```bash
python3 /Users/chuzu/.codex/skills/stark-repo-analyzer/scripts/repo_analyzer.py https://github.com/adminhuan/smart-search-mcp --output analysis-final --mode all --no-question
analysis-final/acceptance/check.sh
```

验收标准：

- 安装版和源码版行为一致。
- 三份报告存在。
- 验收脚本通过。
- 产物不是 root-owned。

## 验收矩阵

| Review 问题 | 修复阶段 | 自动验证 | 人工/代理验证 |
|---|---:|---|---|
| 未执行双代理终验收 | 4 | 无 | 小白用户记录 + 裁决报告 |
| 未生成三份受众报告 | 1 | `test_mode_all...` | 小白用户检查三份报告 |
| audience optional 假通过 | 1 | 删除报告后验收失败 | 裁决检查验收输出 |
| 最终答复误导 | 1,2,4 | 状态语义测试 | 裁决检查最终报告 |
| 报告差异描述不实 | 2 | 报告文本断言 | 裁决抽查 |
| deterministic final 语义过强 | 2 | 状态文件断言 | 裁决抽查 |
| 复现命令错误 | 2 | 报告命令断言 | 小白用户复制执行 |
| root-owned 产物 | 5 | `find ! -user` | 发布前检查 |
| 架构图误导 | 2 | 报告文本断言 | 裁决抽查 |
| 空测试/示例未提示 | 3 | 风险提示断言 | 裁决抽查 |
| 模块划分过粗 | 3 | 单模块限制断言 | 裁决抽查 |
| graphify path 用法错误 | 4 | 无 | 小白用户流程说明 |
| 开头长 prompt 噪音 | 4 | 无 | 小白用户体验评分 |

## 建议执行顺序

1. 先做阶段 1：它直接决定验收是否会假通过。
2. 再做阶段 2：修正报告可信度和状态语义。
3. 然后做阶段 3：补齐分析质量风险提示，避免报告过度乐观。
4. 最后做阶段 4-5：跑真实小白用户验收、裁决评分和安装版回归。

## 最小通过定义

只有同时满足以下条件，才能声明本轮修复完成：

```text
python -m unittest tests.test_repo_analyzer_cli
python3 scripts/repo_analyzer.py https://github.com/adminhuan/smart-search-mcp --output analysis-novice-final --mode all --no-question
analysis-novice-final/acceptance/check.sh
find analysis-novice-final ! -user "$(id -un)" -maxdepth 3 -print
```

并且：

- 三份受众报告存在。
- 验收输出没有 `audience reports optional`。
- 小白用户子代理记录已写入。
- 裁决代理总分 `>= 9.5/10`。
- 安装版 skill 路径回归通过。
