# Issue: 修复 LLM-judge 默认模型不兼容导致的 Codex WARN

## 背景

在分析 `https://github.com/adminhuan/smart-search-mcp` 后运行 `analysis/acceptance/check.sh`，主体确定性验收通过：

```text
TOTAL:71 PASS:67 FAIL:0 WARN:2 SKIP:2
```

其中一项 WARN 为：

```text
WARN|llm-judge:执行|codex 退出码 1
```

进一步复现 `scripts/llm_judge.py` 构造的 Codex 命令：

```bash
printf '只输出 ok\n' | codex exec --model haiku-4.5 - --skip-git-repo-check
```

得到真实错误：

```text
unexpected status 404 Not Found: Model "haiku-4.5" is not supported by any configured account in this group
```

直接原因是 `scripts/llm_judge.py` 默认模型为 `haiku-4.5`：

```python
DEFAULT_MODEL = os.environ.get("REPO_ANALYZER_LLM_JUDGE_MODEL", "haiku-4.5")
```

当前环境的 Codex CLI 可用，但该模型不可用；不指定模型时默认 `gpt-5.5` 可正常执行。因此这不是报告内容评分失败，也不是主体 deterministic acceptance 失败，而是 LLM 裁判阶段的模型配置兼容性问题。

## Proposed breakdown

1. **Title**: 让 LLM-judge 使用环境可用的 Codex 默认模型并输出可诊断错误
   **Blocked by**: None - can start immediately
   **User stories covered**: 用户运行完整分析验收时，可选 LLM 裁判不应因为过期/不可用默认模型产生难以诊断的 WARN。

## What to build

让 `llm-judge` 的 Codex 调用不再硬依赖 `haiku-4.5`。当用户没有显式设置 `REPO_ANALYZER_LLM_JUDGE_MODEL` 时，应优先使用当前 Codex CLI 配置的默认模型；当用户显式设置模型且调用失败时，验收输出应包含足够定位的信息，例如模型名和 Codex stderr 的关键错误摘要。

这是一条端到端垂直切片：用户运行仓库分析后执行 `acceptance/check.sh`，如果 LLM-judge 可执行，应得到 PASS/评分结果；如果模型不可用，应得到可操作 WARN，而不是只有 `codex 退出码 1`。

## Acceptance criteria

- [ ] 未设置 `REPO_ANALYZER_LLM_JUDGE_MODEL` 时，`scripts/llm_judge.py` 不再默认传入 `--model haiku-4.5`，而是使用当前 Codex CLI 配置的默认模型，或使用项目明确支持的默认模型。
- [ ] 显式设置不可用模型时，例如 `REPO_ANALYZER_LLM_JUDGE_MODEL=haiku-4.5`，`analysis/acceptance/llm-judge.sh` 的 WARN 详情包含模型名和 Codex 返回的关键错误摘要。
- [ ] 新增或更新测试覆盖：Codex 返回非零退出码时，`llm_judge.py` 输出可诊断 WARN；非 strict 模式仍不让 deterministic acceptance 失败。
- [ ] 复跑最小验证命令能说明问题已修复：

```bash
REPO_ANALYZER_LLM_JUDGE_MODEL=gpt-5.5 sh analysis/acceptance/llm-judge.sh
REPO_ANALYZER_LLM_JUDGE_MODEL=haiku-4.5 sh analysis/acceptance/llm-judge.sh
```

## Blocked by

None - can start immediately

## Notes

- 不要把这个 WARN 表述为主体分析失败；本次主体结果为 `FAIL:0`。
- 不要通过手改生成产物掩盖 WARN。
- 需要保留用户显式指定模型的能力；问题在于默认值和错误可诊断性。
