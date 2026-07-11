# Local Rules（执行策略 SSOT）

本目录是 Repo Analyzer 的可分发执行合同。SKILL 工作流与 CLI 门禁应引用此处规则，而不是仅依赖散文描述。

- `modes.json`：模式定义、默认值、允许/禁止工具
- `capabilities.json`：deep 能力合同与提供方映射
- `tools/*.json`：单工具分类、官方源、verified date、fallback/reject

规则版本见 `modes.json` 的 `rules_version`。
