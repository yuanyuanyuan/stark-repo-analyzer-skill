# Quality Checks

| Check | Status | Evidence |
|---|---|---|
| 输出目录独立 | 通过 | 所有本次文件位于 `docs/baseline/reference-runs/claude-code` |
| 源码目录和 HEAD 已确认 | 通过 | `metadata.json`、`execution-log.md`：HEAD=`a371abbe75ffa0d0a3c92290e2bbf56a7ef54367` |
| 未使用 Git 历史推断实现 | 通过 | 日志声明只使用固定 commit、当前 README 和公开文档 |
| README/配置/入口已读取 | 部分通过 | README、main、setup、entrypoint 已读；配置文件不存在 |
| 按业务功能识别模块 | 通过 | `05-modules-plan.md` 使用 query/tool/task/skill/context 数据流划分 |
| Why > What | 通过 | 每个核心草稿含动机、替代方案代价、边界和问题 |
| Mermaid 核心流程 | 通过 | query、tool、task、skill、context 草稿及最终报告均含图 |
| 关键结论含源码行号 | 通过 | 草稿、交叉验证和报告均使用 `path:line` |
| 外部定位和同类对比 | 部分通过 | GitHub、镜像 README、官方文档已读；竞品源码未固定读取 |
| 核心模块覆盖率 >=60% | 部分通过 | 4/5 达标；task-agent=59.1%，见 `08-coverage.md` |
| 次要模块覆盖率 >=30% | 部分通过 | mcp-plugin、permission-security 达标；entry-ui 未达标；remote-platform 未评估 |
| 未虚报全仓库覆盖 | 通过 | 全仓库 512,664 行与未评估目录明确记录 |
| 交叉验证完成 | 通过 | `07-cross-validation.md` 有 7 条跨模块核验 |
| 缺失/失败/待验证事项记录 | 通过 | `execution-log.md`、`08-coverage.md`、本表均有明确限制 |
| 每个输出文件 <=300 行 | 通过 | 生成后由验证命令检查 |
| 每个输出文件 <=15KB | 通过 | 生成后由验证命令检查 |

## Overall Result

**部分通过。** 主链路基线可用于重实现对比，但不是全仓库 standard 达标报告；任务/代理和入口/UI 仍需后续补读。
