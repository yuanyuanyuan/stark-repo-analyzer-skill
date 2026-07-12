# 08 Coverage

## Calculation

覆盖率 = 通过实际读取命令请求的行范围并集 / 纳入该模块的文件总行数。重复读取不重复计数；未读区段、目录盘点和导入列表不计入已读。

## Core Modules

| Module | Files/lines | Read lines | Coverage | Target | Status |
|---|---:|---:|---:|---:|---|
| query-loop | 3,024 | 3,024 | 100.0% | 60% | 通过 |
| tool-runtime | 3,644 | 3,374 | 92.6% | 60% | 通过 |
| task-agent | 5,137 | 3,035 | 59.1% | 60% | 部分通过/未达标 |
| command-skill | 2,948 | 2,948 | 100.0% | 60% | 通过 |
| context-memory | 1,577 | 1,577 | 100.0% | 60% | 通过 |
| **核心合计** | **16,330** | **13,958** | **85.5%** | **60%/模块** | **4/5 模块达标** |

## Secondary Modules

| Module | Files/lines | Read lines | Coverage | Target | Status |
|---|---:|---:|---:|---:|---|
| mcp-plugin sampled scope | 8,228 | 2,824 | 34.3% | 30% | 通过，但仅限声明范围 |
| permission-security sampled scope | 4,161 | 1,506 | 36.2% | 30% | 通过，但仅限声明范围 |
| entry-ui sampled scope | 5,442 | 1,284 | 23.6% | 30% | 未达标 |
| remote-platform | 未完整枚举 | 未计算 | 不可计算 | 30% | 未评估 |

## Why the Gaps Exist

- `task-agent` 只差 0.9 个百分点；未读的 `src/utils/swarm/inProcessRunner.ts` 是主要缺口。
- `entry-ui` 的 `main.tsx` 和 `screens/REPL.tsx` 是数千行集成文件，当前只读取启动、信任、迁移和边界区段。
- MCP/plugin 和 permission 的“通过”不能推广到其全部目录；它们是按本文件声明的代表性文件范围计算。
- 全仓库 512,664 行不应被核心加权平均覆盖率替代；本基线采用模块门槛 + 明确未评估清单。
