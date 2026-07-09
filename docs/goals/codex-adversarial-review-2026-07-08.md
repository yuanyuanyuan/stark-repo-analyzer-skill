# Codex 对抗性审查报告 — T01-T12 重构

**审查时间**：2026-07-08 13:34  
**审查引擎**：codex exec (gpt-5.5, xhigh reasoning)  
**审查范围**：`scripts/` 下 T01-T12 全部重构改动  
**判定**：❌ **FAIL** — 发现 8 个重大问题

---

## 问题清单

### 1. 模块拆分是物理分离，非真正解耦
- **严重度**：高
- **位置**：`analyzer_modules.py:6`、`analyzer_coverage.py:24`、`analyzer_agent.py:6`、`analyzer_reports.py:19`
- **问题**：存在通过 lazy import 刻意回避的隐藏循环依赖：
  - `analyzer_modules` → (lazy) → `analyzer_coverage` → `module_rows`（反向依赖）
  - `analyzer_agent` → (lazy) → `analyzer_reports` → `agent_insights`（反向依赖）
- **共享可变单例**仍在 `analyzer_common.py:30`（`_LOADER` / `_TOKEN_COLLECTOR`）
- **违反声明**：工程师报告称"no circular dependencies"，实际是用 lazy import 掩盖

### 2. Codex 自动降级只处理"二进制不存在"，未覆盖真实失败
- **严重度**：高
- **位置**：`analyzer_preflight.py:52`、`analyzer_agent.py:51`
- **问题**：
  - 预检只查 `shutil.which("codex")`，不覆盖：auth 失败 / 模型不支持 / config 损坏 / codex 崩溃
  - `run_agent_task()` 只 catch timeout，不 catch `OSError`
  - codex 存在但不可用时，重试后记录失败但**永不降级**到 deterministic
- **影响**：默认 codex 模式是**可靠性倒退**

### 3. `--resume` 可能删除用户文件
- **严重度**：高
- **位置**：`analyzer_common.py:274`
- **问题**：`prepare_output(resume=True)` 先列特定生成文件，然后**整目录删除** `reports/data/diagnostics/logs/acceptance/agent-runs`
- **影响**：用户放在这些子目录下的手写笔记、之前的运行日志被静默删除

### 4. 进度/日志不可靠
- **严重度**：中高
- **位置**：`analyzer_common.py:190`、`repo_analyzer.py:124`、`analyzer_preflight.py:93`
- **问题**：
  - `LogWriter` 用秒级文件名，并发运行会互相覆盖
  - `LogWriter` 全部 buffer 到 `summary()`，但 `summary()` 只在成功路径调用 → **失败运行丢失日志**
  - `count_stages()` 在 agent 模式开启时**高估**可选修复 stage 数（即使不跑修复也计入），进度可能停在 `[19/27]`

### 5. 输出结构仍有隐藏假设和静默跳过
- **严重度**：中
- **位置**：`analyzer_acceptance.py:17`、`acceptance/llm-judge.sh:6`、`analyzer_acceptance.py:240`
- **问题**：
  - 许多 writer 假设编排器已创建父目录，拆分后的模块不独立健壮
  - `write_acceptance()` 复制 `llm-judge.sh` 但**不替换 `__SKILL_ROOT__` 占位符**
  - `llm-judge.sh` 忽略 root 参数，从 `$0` 重新计算路径
  - 生成的 executor runner **忽略执行器退出码**，只解析 stdout 状态行 → 崩溃的执行器会静默消失

### 6. 名片扩容是更大的盲截断，非更好优先级
- **严重度**：中
- **位置**：`analyzer_metadata.py:220`
- **问题**：`card[:10_000]` 仍可能在段落中间截断，不保证 README 或高信号字段存活
- **影响**：增加了内容量，但没有有意义的截断策略

### 7. 旧 `analysis` 引用残留（PRD 明确要求移除）
- **严重度**：中
- **位置**：`analyzer_common.py:58`、`repo_analyzer.py:131`
- **问题**：
  - `IGNORE_DIRS` 仍含 `analysis`、`analysis-final`、`analysis-judge` 等
  - CLI 描述仍写"analysis 产物"
  - agent prompt 仍告诉 codex 不要修改 "analysis" 目录

### 8. REQ-01 不完整
- **严重度**：中
- **问题**：默认输出改了 `.stark-repo-analyzer`，但**没找到 gitignore 追加逻辑**和**最终 stdout 提示**
- **PRD 要求**：两者都必须有

---

## 审查验证说明

- graphify query 过时（指向旧单文件），审查从源码直接验证
- `py_compile` 和 import 检查通过
- 未跑完整 pytest 套件
- 未编辑任何文件（只读审查）
