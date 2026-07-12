已完成物理基线分析。固定 HEAD 为 `b67832c2167e5b0ff6764a8c04a0a9087e697b5a`，源码树未修改，所有产物均在当前工作目录。

[最终报告](</private/tmp/stark-repo-analyzer-click-run-c1LVKL/ANALYSIS_REPORT.md>) · [元数据](</private/tmp/stark-repo-analyzer-click-run-c1LVKL/metadata.json>) · [执行日志](</private/tmp/stark-repo-analyzer-click-run-c1LVKL/execution-log.md>) · [检查清单](</private/tmp/stark-repo-analyzer-click-run-c1LVKL/checks.md>)

静态实现覆盖率为 `100%`（12,288/12,288）。测试结果：`1901 passed, 25 skipped, 31000 deselected, 1 xfailed`。

已明确记录限制：外部调研、官网遍历、原生 Windows 验证、多 shell 版本矩阵和 coverage.py 百分比未执行。另复现并记录了原子写异常提交、临时 pager 二进制/文本边界两个缺陷。