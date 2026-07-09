---
Status: Accepted
Date: 2026-07-06
Round: 5 (R5-Q3)
---

# ADR-0013 `repo-analyzer` 与 `graphify` 完全解耦

## Context

项目根目录中已有 `graphify-out/` 子项目，配套 CLI：

- `graphify query "<question>"` —— 语义查询
- `graphify path "<A>" "<B>"` —— 关系路径
- `graphify update .` —— 重建索引（AST-only，无 API 成本）
- `graphify-out/graph.json` —— 图数据
- `graphify-out/wiki/index.md` —— 知识库索引
- `graphify-out/GRAPH_REPORT.md` —— 架构报告

`repo-analyzer` 是 PLAN.md 在设计的另一个分析 skill，产出：

- `analysis/README.md` —— 阶段八 README 索引
- `analysis/drafts/06-module-*.md` × N —— 模块分析
- `analysis/02a-repo-type.yaml` —— Repo 类型识别
- `analysis/02a-manifest-card.md` —— 5KB 名片

两个 skill **扫描的仓库存量有大量重叠**——graphify 已经扫过了一遍仓库，repo-analyzer 还要再扫一遍。是否复用？

## Decision

**A 完全解耦**：repo-analyzer 与 graphify 互不读对方产物。

具体规则：

1. **不读取**：
   - `repo-analyzer` 不读 `graphify-out/graph.json`
   - `repo-analyzer` 不读 `graphify-out/wiki/index.md`
   - `repo-analyzer` 不读 `graphify-out/GRAPH_REPORT.md`

2. **不写入**：
   - `repo-analyzer` 不写 `graphify-out/`
   - `repo-analyzer` 不修改 `.claude/skills/graphify/`

3. **配置层可选显式声明**：
   - `~/.config/repo-analyzer/defaults.yaml` 可设 `graphify.compatible_mode: true` —— **当前 ADR 暂不实现此 flag**，仅保留 YAML 字段占位，避免后续锁定冲突

4. **错误处理**：
   - 若用户提示"请同时跑 graphify 与 repo-analyzer 互补"—— skill 不报错，但也不自动调用 graphify；由用户在 shell 层做：
     ```bash
     graphify update . && repo-analyzer /path/to/repo
     ```

5. **README 提及但不依赖**：
   - `analysis/README.md` 顶部加一行提示：
     > 提示：本 skill 与 `graphify` 子项目解耦，索引不共享。如需共享请在 shell 层串联。

## Alternatives

- **G1. B 单向读取** —— repo-analyzer 读 graph.json 作为 Phase-2a 补充输入。优点省扫描。
- **G2. C 双向耦合** —— 互相喂数据，索引一致。工程量大。
- **G3. A 完全解耦（本 ADR）** —— 简单、各自演化独立、互不锁定。

## Consequences

- repo-analyzer 独立扫描，Phase-2a 不享受 graphify 的索引**优势**——但也避免**依赖耦合**。
- 两个 skill 各自演化路径独立，可独立升级、独立替换。
- 用户串联两个 tool 时需在 shell 层手动编排（如 `repo-analyzer.sh` 包装脚本同时调两边）。
- 性能开销：repo-analyzer 全程自扫，预计 Phase-2a 多花 10-15 秒（100MB 仓库级别）。
- 后续若发现 graphify 索引质量对 repo-analyzer 有显著优势，可另开 ADR 重新设计耦合模式（此 ADR 留 `graphify.compatible_mode` 占位即可）。

## Open Questions

- [ ] 完全解耦后，能否在 `analysis/README.md` 末尾链接到 `graphify-out/GRAPH_REPORT.md` 作为"另请参阅"？纯 markdown 链接不算耦合。
- [ ] 若用户希望两个 skill 共享 token 预算（slb_budget 联合），需不需要 `~/.config/graphify/defaults.yaml` 配 `repo_analyzer.shared_sla`？跨工具配置——目前未设计。

## Linked

- ADR-0001（Phase-2a 不依赖 graphify）
- ADR-0008（defaults.yaml 留 `graphify.compatible_mode` 占位字段）
- 阶段八 §8（README 顶部提示）
