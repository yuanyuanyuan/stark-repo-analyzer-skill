# dev-rules · 开发与验收规则目录

本目录存放本仓库 **dev 侧** 可执行规则（agent/人共用的操作与验收口径），与产品 skill 正文、CLI 实现并列维护。

## 目录约定

| 路径 | 用途 |
|------|------|
| [`real-uat-regression/`](real-uat-regression/) | **真实UAT回归测试**（正式名称）规则：按 quick / standard / deep 分档 |
| （后续）其它 dev 规则 | 新增时在本 README 登记一行，保持「一类规则一个子目录」 |

## 权威与同步

1. **操作入口**：根目录 [`AGENTS.md`](../AGENTS.md) 必须指向本目录（至少指向真实UAT 子目录）。
2. **产品契约细节**：skill 工作流与质量门语义仍以 `skills/repo-analyzer/` 与（若存在）`docs/specs/` 为准；本目录写 **如何跑回归、分档期望、证据目录、禁止假通过**。
3. **变更联动（强制）**：当 **代码、skill、gate、需求/Issue/ticket** 发生会改变分析行为或验收语义的变更时，**必须同步更新**本目录对应规则（至少 `real-uat-regression/`），并在 PR 中写明规则 diff 或「规则无影响」理由。禁止只改实现不改回归规则，或只改规则不改实现却声称已验收。

## 命名

- 目录与文件使用英文 kebab-case；正文默认中文。
- 对外正式测试名：**真实UAT回归测试**（标签 `real-uat-regression`）。
