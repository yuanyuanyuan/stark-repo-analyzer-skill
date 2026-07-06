# Graph Report - stark-repo-analyzer-skill  (2026-07-06)

## Corpus Check
- 9 files · ~3,927 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 203 nodes · 194 edges · 17 communities (13 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]

## God Nodes (most connected - your core abstractions)
1. `video-use 仓库分析方案 v2（基于 repomix + repo-analyzer 框架）` - 15 edges
2. `stageRuntimeControl` - 9 edges
3. `stages` - 9 edges
4. `2.2 并行子代理提取策略` - 6 edges
5. `publicSurface` - 5 edges
6. `publicSurface` - 5 edges
7. `2.1 宏观认知建模的机制与原理` - 5 edges
8. `3. 阶段二：12 维精细切片（不压缩 + XML，**并行执行**）` - 5 edges
9. `7. 阶段五：业务模块并行深度分析（subagent 团队）` - 5 edges
10. `continuationBoundary` - 4 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (17 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (32): active, authorityMode, blockedOn, completed, currentStage, currentStageKey, deactivatedAt, deactivationReason (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (32): active, authorityMode, blockedOn, completed, currentStage, currentStageKey, deactivatedAt, deactivationReason (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (27): 0. 环境与目录约定, 10. 验收标准（核心 80% / 次要 20% 模式）, 11. 完整执行顺序, 12. 开关与默认值, 13. 反馈记录（供未来复用）, 1. 阶段零：克隆 + 元数据采集, 4.1 识别项, 4.2 自适应提问（AskUserQuestion） (+19 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (25): completedAt, status, completedAt, status, completedAt, status, completedAt, status (+17 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (23): active, choiceSurfaceState, controlState, criticalFetchLoopCount, criticalFetchLoopMax, currentStage, dispatchChain, dispatchedAgents (+15 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (12): 2.1.1 机制：repomix `--compress` 内部做了什么, 2.1.2 原理：为什么"宏观认知建模"能成立, 2.1.3 与 overview.md 14 项的对应关系, 2.1.4 失效边界：什么场景下压缩机制不够用, 2.1 宏观认知建模的机制与原理, 2.2.1 分组策略（按"信息源"切，不是按"项号"切）, 2.2.2 Subagent Prompt 模板, 2.2.3 执行流程 (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (9): stageRuntimeControl, activationMode, createdAt, driverMode, executionLeasePolicy, factGatePolicy, hookGateMode, promptFingerprint (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (5): mode, scriptMtimeMs, startedAt, status, updatedAt

### Community 8 - "Community 8"
Cohesion: 0.40
Nodes (5): 3.0 共享资源, 3.1 切片清单, 3.2 维度 12 的 git log 聚合脚本, 3.3 并行调度, 3. 阶段二：12 维精细切片（不压缩 + XML，**并行执行**）

### Community 9 - "Community 9"
Cohesion: 0.40
Nodes (5): publicSurface, hiddenInternalFields, nativeEnhancementAllowed, popupRequired, primaryDisplay

### Community 10 - "Community 10"
Cohesion: 0.40
Nodes (5): publicSurface, hiddenInternalFields, nativeEnhancementAllowed, popupRequired, primaryDisplay

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (4): continuationBoundary, mode, reason, status

### Community 12 - "Community 12"
Cohesion: 0.50
Nodes (4): continuationBoundary, mode, reason, status

## Knowledge Gaps
- **164 isolated node(s):** `PreToolUse`, `PreToolUse`, `schemaVersion`, `active`, `runId` (+159 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `stages` connect `Community 3` to `Community 4`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `video-use 仓库分析方案 v2（基于 repomix + repo-analyzer 框架）` connect `Community 2` to `Community 8`, `Community 5`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `stageRuntimeControl` connect `Community 6` to `Community 4`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `PreToolUse`, `PreToolUse`, `schemaVersion` to the rest of the system?**
  _164 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._