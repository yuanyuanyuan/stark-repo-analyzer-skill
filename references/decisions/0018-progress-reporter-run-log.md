---
Status: Accepted
Date: 2026-07-08
Round: 6 (T10)
---

# ADR-0018 进度输出与运行日志

## Context

T10 之前，`repo_analyzer.py` 使用 `timed_stage` 上下文管理器记录阶段耗时到 `performance` dict，但：

1. 运行时没有进度输出——用户看不到当前执行到哪个阶段、总共多少阶段。
2. agent 调用没有实时反馈——用户不知道 agent 是否在运行、运行了多久。
3. 没有独立的运行日志文件——只有 `PERFORMANCE_REPORT.md` 事后报告，没有运行时日志。

## Decision

**新增 `ProgressReporter` 和 `LogWriter` 类，替换 `timed_stage`，提供 `[N/M]` 进度输出和结构化运行日志。**

### ProgressReporter

```python
class ProgressReporter:
    def __init__(self, performance: dict, total: int, log_writer: LogWriter = None)
    def stage(self, name: str) -> ContextManager  # 替换 timed_stage
    def agent_progress(self, run_id: str, attempt: int, status: str, elapsed: float)
    def summary(self, total_elapsed: float)
```

- `stage()` 打印 `[N/M] stage_name ...` 到 stderr，完成后打印 `[N/M] stage_name -> PASS (0.123s)`。
- `agent_progress()` 打印 agent 调用结果到 stderr。
- `summary()` 打印最终汇总行并 flush 日志。
- 内部仍然写入 `performance["stages"]`，与 `PERFORMANCE_REPORT.md` 兼容。

### LogWriter

```python
class LogWriter:
    def __init__(self, output_dir: Path)  # 创建 logs/run-YYYYMMDD-HHMMSS.md
    def stage_entry(self, name: str, elapsed: float, status: str)
    def agent_entry(self, run_id: str, attempt: int, status: str, elapsed: float)
    def flush(self, total_elapsed: float, stage_count: int, agent_count: int)
```

- 日志文件包含阶段耗时表、agent 调用表和汇总信息。
- 每次运行生成独立日志文件，文件名含时间戳。

### count_stages

`count_stages(args)` 根据 `agent_mode`、`research`、`save_pref` 等参数预计算总阶段数，用于进度显示。

### 集成

- `repo_analyzer.py` 创建 `ProgressReporter` 和 `LogWriter`，所有 `timed_stage` 替换为 `progress.stage()`。
- `analyzer_agent.py` 的 `run_agent_task`、`run_module_agent_loop`、`run_cross_ref_agent`、`repair_failed_coverage_modules`、`repair_cross_ref_modules` 新增 `progress=None` 可选参数。
- `progress` 为 `None` 时，行为与之前完全一致（向后兼容）。

## Alternatives

- **M1. 仅加 print 语句** —— 没有结构化日志，无法事后分析。
- **M2. 仅写日志文件** —— 运行时看不到进度。
- **M3. ProgressReporter + LogWriter（本 ADR）** —— 运行时有进度，事后有日志。

## Consequences

- `timed_stage` 保留在 `analyzer_common.py` 但不再被 `repo_analyzer.py` 使用。
- `analyzer_agent.py` 函数签名新增 `progress=None` 可选参数，向后兼容。
- 每次运行生成 `logs/run-YYYYMMDD-HHMMSS.md` 日志文件。
- stderr 输出 `[N/M]` 格式进度，不影响 stdout 的 `分析完成:` 消息。

## Linked

- ADR-0016（日志写入 `logs/` 子目录）
- T10 任务说明
