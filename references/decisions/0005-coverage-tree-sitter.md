---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q5)
---

# ADR-0005 覆盖率门控 = `tree-sitter` API 名 + `grep` draft 符号名 交集比

## Context

PLAN.md §10 + §8 阶段六对模块覆盖率设了阈值：

- 核心模块 ≥ 80%
- 重要模块 ≥ 50%
- 次要模块 ≥ 20%

但「覆盖率」未定义度量。可能度量：

| 度量 | 实现 | 偏倚 |
|------|------|------|
| 文件覆盖率 | `grep -c "{{module_xxx}}" drafts/*` | monorepo 严重低估（8 个文件组成的 lib 可能只命中 3 个） |
| 行覆盖率 | 关键路径解释行数 / 源码关键函数行数 | 「高度抽象 helper 文件」爆 200% |
| API 表面覆盖率 | tree-sitter 解析所有 `export` / `def` | 动态语言（JS/Python）需要 tree-sitter |
| LLM self-report | 模块 sub-agent 自评 checklist | 等于没有门控（幻觉 100% 命中） |

## Decision

**C+E 双度量 + 强制门控 + 失败回退循环**：

1. **强制指标（脚本可断言）** —— **关键符号覆盖率**：
   ```bash
   # Step 1: tree-sitter 扫源码，得 expected-symbols.yaml
   tree-sitter parse src/ -f yaml > expected-symbols.yaml
   # 提取 export / pub / def 的名字
   grep -E 'definition.*(export|pub|def)\s+\w+' expected-symbols.yaml \
     | grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\b' \
     | sort -u > expected-symbols.txt

   # Step 2: grep 抓 draft 所有英文单词，得 covered-symbols.yaml
   grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\b' analysis/drafts/06-module-*.md \
     | sort -u > covered-symbols.txt

   # Step 3: 算交集比例
   coverage=$(comm -12 expected-symbols.txt covered-symbols.txt | wc -l)
   total=$(wc -l < expected-symbols.txt)
   ratio=$(echo "scale=4; $coverage / $total" | bc)
   ```

2. **辅助指标（LLM 主观，仅提示不门控）**：
   - 阶段六另起一个 sub-agent，**只读不写**，对每个 draft 打 0-10 分：
     - 「解释清晰度」（语句是否让陌生读者看懂）
     - 「边界条件覆盖度」（错误路径 / 异常流是否提到）
   - 评分仅写入 `analysis/08-coverage.md` 的「主观评估」段，不参与硬门控

3. **强制门控阈值**（与 ADR-0007 SLA 预算联动）：
   - 核心模块（tier=core）：阈值 ≥ 80%
   - 重要模块（tier=important）：阈值 ≥ 50%
   - 次要模块（tier=minor）：阈值 ≥ 20%

4. **失败回退循环**：
   - 若强制指标不达阈值，阶段六 `yield` 失败
   - 写 `analysis/08-coverage-failure.md`：
     - 不达标模块列表
     - 每个不达标模块缺失的 API 名清单（top 20）
     - 触发阶段五 sub-agent **部分回退**：只重启不达标模块，原已通过模块保留
   - 单模块最多回退 3 次（与 ADR-0004 共用配额）
   - 通过 cross-ref pass（详见 ADR-0004）后才进覆盖率门控，避免双重失败混淆

5. **tree-sitter 多语言支持**：
   - 必备：TypeScript / Python / Go / Rust / C++ / Java / Lua
   - 配置 `config/tree-sitter-langs.yaml`：
     ```yaml
     enabled_langs: [typescript, javascript, python, go, rust, cpp, java, lua]
     fallback_langs: [ruby, php, kotlin, swift]
     unsupported_strategy: skip_module  # 完全不支持的语言模块直接跳过
     ```
   - monorepo 按 package per-language 扫描，per-package 出独立覆盖率

## Alternatives

- **E1. 文件覆盖率**——简单但 monorepo 偏倚大。
- **E2. 行覆盖率**——在 mixed-paradigm 仓库偏倚严重。
- **E3. API 表面覆盖率**——对动态语言太重，没有 draft 端 grep 配合。
- **E4. LLM self-report**——零门控。
- **E5. C+E 双度量 + 回退循环（本 ADR）**——实现成本中等，断言可信。

## Consequences

- 阶段六必须能在目标仓库跑 `tree-sitter`，即使在 monorepo 下也要 per-package 跑。新增运行时依赖 `tree-sitter-cli`（约 5MB 二进制）。
- 阶段六增加 yield → 回退机制，§8.3 现有「产出 `08-coverage.md`」流程扩展为线性 + 循环两态。
- §10 验收标准里第 10 行「模块覆盖度」从主观题变客观题。
- 单次完整跑流程新增 2-5 秒 tree-sitter 扫描 + 1-2 秒 grep 交集计算。
- 阶段六失败产物从 `08-coverage.md` 1 个文件扩到 `08-coverage.md` + `08-coverage-failure.md` 2 个文件。

## Open Questions

- [ ] Tree-sitter 多语言解析并行度：是否能 6 核并发跑？还是单核顺序（语言之间不共享 AST）？需要 benchmark。
- [ ] 大仓库（100MB+）下 tree-sitter parse 是否会被 OOM？需要 chunked parse 策略。
- [ ] 失败回退 3 次耗尽时（与 ADR-0004 共用配额），是否触发 ADR-0007 SLA 预算耗尽兜底？

## Linked

- ADR-0004（cross-ref 通过后才进覆盖率门控）
- ADR-0007（回退受 SLA 约束）
- ADR-0009（运行风险：tree-sitter OOM 是 R1 候选风险之一）
- 阶段六 §8 / 阶段十 §10
