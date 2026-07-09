# {{ project_name }} 业务分析报告

> 目标 `{{ source }}`；Repo 类型 `{{ repo_type }}`；报告由 repo-analyzer 模板渲染器生成。

## 0. 管理摘要
- 项目识别名：{{ readme_title }}
- 对外能力数量：{{ tool_count }}
- 运行命令候选：{{ command_count }}
- 最大维护单元：`{{ largest_root }}`（{{ largest_count }} 个文件）

## 1. 用户价值
README 摘要显示该项目的主要卖点是：
{{ readme_points }}

当前扫描到的能力清单：
{{ tool_summary }}

## 2. 采用成本
- 主要语言：{{ language_line }}
- 依赖 manifest：{{ manifest_names }}
- 推荐先验证的命令：
{{ commands }}

## 3. 业务风险
- 能力集中在 `{{ largest_root }}`，如果该模块缺少测试或错误处理，发布风险会集中放大。
- {{ business_risk_line }}
- 验收入口是 `acceptance/check.sh`，适合在交付前做快速门禁。

{{ agent_business_insights }}

{{ audience_section }}

## 7. 证据索引
- 项目名片：`02a-manifest-card.md`
- 主技术报告：`ANALYSIS_REPORT.tech-lead.md`
- 文档切片：`slices/04-docs.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 状态报告：`STATE_REPORT.md`
{{ failed_section }}

{{ research_section }}
