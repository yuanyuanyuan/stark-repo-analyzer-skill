# ADR-0005 覆盖率门控(80 / 50 / 20%)的度量算法缺位

## Status

Proposed (Round 2)

## Context

PLAN.md §10 + §8 阶段六对模块覆盖率设了阈值:
- 核心模块 ≥ 80%
- 重要模块 ≥ 50%
- 次要模块 ≥ 20%

但"覆盖率"的具体度量**未定义**。可能的度量:
1. **文件覆盖率**:`grep -c "{{ module_xxx }}" analysis/drafts/*` — 文字命中比例。
2. **行覆盖率**:draft 中关键路径解释行数 / 实际源码关键函数行数。
3. **API 表面覆盖率**:模块对外导出的 class / function 数量 / draft 中提到的数量。
4. **LLM self-report**:模块 sub-agent 自评 checklist。

每种定义对应不同 SLA:
- 文件覆盖对 monorepo 严重低估(8 个文件组成的 lib 模块可能只有 3 个被命名)。
- 行覆盖在"高度抽象的 helper 文件"中爆 200%(1 个 5 行 helper 占 200 行 budget)。
- API 表面对动态语言(JS / Python) 需要 tree-sitter,工具成本高。
- LLM self-report = 没有门控(幻觉 100% 命中)。

## Decision (提议)

**采用双度量**:

1. **强制指标(脚本可断言)**:**关键符号覆盖率**。
   - 用 `tree-sitter <lang>` 解析 src/ 下 export / pub / def,得到 `expected_symbols.yaml`(set A)。
   - 在 `analysis/drafts/06-module-*.md` 中 `grep -E` 抓所有 `\b[[:alnum:]_.]+\b`,得到 `covered_symbols.yaml`(set B)。
   - 覆盖率 = `|A ∩ B| / |A|`。
   - 阶段六 sub-agent 跑这个脚本,对**所有 tier 模块**强制 ≥ 阈值(80 / 50 / 20%)。失败则写 `08-coverage-failure.md` 触发回退到阶段五补做。

2. **辅助指标(LLM 主观)**:语义覆盖。
   - 阶段六另起一个 sub-agent,读 `06-module-*.md`,对每个模块打 0~10 的"解释清晰度"、"边界条件覆盖度"评分。
   - 评分只做提示,不做硬门控。

## Alternatives Considered

- **E1. 文件覆盖率**:简单但有 bias。
- **E2. 行覆盖率**:在 mixed-paradigm 仓库下偏倚严重。
- **E3. API 表面覆盖率**:对动态语言太重。
- **E4. LLM self-report**:无门控。
- **E5. 强制双度量(本 ADR)** :实现成本较高,但断言可信。

## Consequences

- 阶段六必须能在目标仓库跑 `tree-sitter`,即使在 monorepo 下也要 per-package 跑。这是个新的运行时依赖(`tree-sitter-cli` / `py-tree-sitter`)。
- 阶段六需要能 yield 失败并触发回退路径(阶段五 → 阶段六 循环),而非线性 §8.3 把结果写 `08-coverage.md` 就完事。
- §10 验收标准里第 10 行"模块覆盖度"从主观题变成客观题。

## Open Questions

- [ ] Tree-sitter 多语言覆盖(TS / Python / Go / Rust / C++ / Java)实现量是否会让 skill 启动延迟 5s+?
- [ ] 失败时回退成本:重跑一个 module sub-agent 是 O(分钟级)+ O(token-cost) 的,需要明确预算上限。

## Linked

- Q5(Round 2 第五问)
- 阶段五 §7
- 阶段六 §8
- 验收 §10
