# {{ project_name }} 学习报告

> 目标 `{{ source }}`；Repo 类型 `{{ repo_type }}`；报告由 repo-analyzer 模板渲染器生成。

## 0. 先建立心智模型
- 这是一个 `{{ repo_type }}` 仓库。
- 主要语言是：{{ language_line }}。
- 你先把它理解成“文档说明能力、manifest 说明安装方式、源码说明真实入口”的三层结构。

## 1. 阅读顺序
1. 打开 `02a-manifest-card.md`，只看项目名、文件数、README 前 30 行。
2. 打开 `05-module-ids.yaml`，找到第一个模块 `{{ first_module }}`。
3. 打开 `drafts/06-module-{{ first_module }}.md`，看关键符号和工具/API 表面。
4. 打开 `slices/02-backend.xml`，对照源码里的入口。
5. 最后看 `ANALYSIS_REPORT.tech-lead.md`，把技术判断补齐。

## 2. 本仓库的第一批观察
- README 标题：{{ readme_title }}
- 第一个关键符号：`{{ first_symbol }}`
- 第一个对外工具/API：`{{ first_tool }}`
- 运行命令候选：
{{ commands }}

## 3. 练习题
- 解释 `{{ first_module }}` 为什么被排在模块清单第一位。
- 找到 `{{ first_tool }}` 在源码中的文件和行号。
- 说明 `slices/04-docs.xml` 和 `slices/02-backend.xml` 分别适合回答什么问题。

{{ audience_section }}

## 7. 证据索引
- 学习入口：`02a-manifest-card.md`
- 模块清单：`05-module-ids.yaml`
- 模块草稿：`drafts/06-module-{{ first_module }}.md`
- 代码切片：`slices/02-backend.xml`
- 文档切片：`slices/04-docs.xml`
{{ failed_section }}
