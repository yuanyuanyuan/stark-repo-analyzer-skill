# 复制参考文件并限制 Graphify 修改范围

V1 将保真复制参考仓库的 `skills/repo-analyzer/`、`README.md` 和 `README.zh.md`；插件元数据继续保持与参考一致。只允许在 `SKILL.md`、`module-analysis-guide.md` 和 README 中加入已确认的 Graphify 流程与文档，并新增 `references/graphify-integration-guide.md`；不得以改造名义重写原有流程或引入独立应用。

## Consequences

- 文件级 diff 必须能归类为“参考保真复制”“Graphify 增强”或“本项目验收支持”。
- 参考 `analysis-guide.md` 保持原样，防止 Why > What 的方法论在改造中漂移。
- 复制动作属于后续实现任务；当前 ADR 只锁定范围，不提前声称文件已落地。
