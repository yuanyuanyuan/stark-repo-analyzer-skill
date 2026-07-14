---
status: superseded
superseded_by: ADR-0016
---

# 区分 Graphify 深度提取和分析档位

> 此决定已被 [ADR-0016](0016-graphify-code-only-v1.md) 取代。以下正文保留历史原貌。

V1 每次都以 `graphify extract <target> --mode deep` 构建结构证据图谱，但 repo-analyzer 仅交付 `standard` 分析档位；产品级 `deep` 分析档位延后到 V2。这两个概念必须在规格、metadata、日志和用户文档中使用不同的名称。

## 影响

- V1 不暴露或验收产品级 `deep` 分析流程，避免承诺未实现的高覆盖率语义。
- Graphify 命令中的 `--mode deep` 不得被解读为用户选择了更深的源码阅读范围。
- 后续引入产品级 `deep` 时必须新增独立输入契约、覆盖率门槛和回归样本。
