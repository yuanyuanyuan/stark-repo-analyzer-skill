# Issue Tracker：GitHub

本仓库的工作项与 PRD 使用 GitHub Issues，通过 `gh` CLI 读写。仓库由当前目录的 Git remote 推断。

## 约定

- 创建：`gh issue create --title "..." --body-file <file> --label "..."`
- 读取：`gh issue view <number> --comments`
- 列表：`gh issue list --state open --json number,title,body,labels,comments`
- 评论：`gh issue comment <number> --body "..."`
- 标签：`gh issue edit <number> --add-label "..."` 或 `--remove-label "..."`
- 关闭：`gh issue close <number> --comment "..."`

技能要求“发布到 issue tracker”时，创建 GitHub Issue；要求“读取 ticket”时，读取 issue 正文、评论与 labels。

## Pull Request 请求入口

外部 PR 不作为 triage 请求入口。Issues 与 PR 共用编号空间，裸 `#42` 有歧义时先尝试 `gh pr view 42`，失败后再读取 Issue。

## 依赖与顺序

优先使用 GitHub 原生 issue dependencies。不可用时，在正文顶部写 `Blocked by: #<number>`。阻塞项全部关闭后，ticket 才进入可领取 frontier。

发布一组依赖 tickets 时，按 blocker 在前的顺序创建，以便后续 issue 引用真实编号。
