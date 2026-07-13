# Analysis Plan

- Analysis mode: `standard`
- Effective source: 18 files / 12,295 lines
- Bounded scope required: `False`
- Core threshold: 60%; secondary threshold: 30%

## Size by Candidate Area

- `.devcontainer`: 7 effective lines
- `src`: 12,288 effective lines

## Required Sequence

Input -> Graphify code-only/doctor -> sizing -> local research -> adaptive questions -> module plan -> Agent module drafts -> source adjudication -> coverage gate -> report fusion.

## Research Boundary

- Local documents inspected: 21
- URL candidates: 30
- External research status: `not-performed` in this pilot

## Adaptive Questions

- `configuration-execution` (pyproject.toml and Python source): 配置、入口和核心执行路径之间的约束是显式声明还是运行时推导？为什么？
