---
Status: Accepted
Date: 2026-07-06
Round: 5 (R5-Q4)
---

# ADR-0014 tree-sitter 流式 chunked 5MB 单核串行扫描

## Context

ADR-0005 用 `tree-sitter parse src/ -f yaml > expected-symbols.yaml` 扫源码产出 API 名清单，用于覆盖率门控。

但 `tree-sitter` 设计本身是**全量加载**——把仓库整个 src/ 树装进内存做 AST 解析。在以下场景会出问题：

1. **OOM（内存爆）**：
   - 100MB+ monorepo（`vercel/turborepo`、`pnpm`、大型 game engine）整个扫描会占用 2-4GB 内存，普通开发者机器（CI 默认 7GB）会被 OOM kill
   - tree-sitter 单文件 `< 5MB` 时峰值内存约 50MB，5-100MB 时翻 4 倍

2. **多语言并行**：
   - 7 种 grammar（TS / Python / Go / Rust / C++ / Java / Lua）同时跑，谁快谁慢？内存峰值叠加？
   - 命中率：7 核并发理论加速 7×，但内存峰值 × 7

3. **冷启动延迟**：
   - 大型仓库首次 parse 耗时可达 60 秒

## Decision

**A 串行 + chunked 5MB 单核顺序流式处理**：

1. **chunked 切分**：
   ```python
   # config/tree-sitter.yaml
   chunked:
     enabled: true
     chunk_size_bytes: 5_242_880  # 5 MiB
     strategy: per_file  # 按文件切（不切单一文件）
   ```
   - 单文件 < 5MB：直接 parse
   - 单文件 ≥ 5MB：跳过 + WARN（大文件通常是生成代码 / protobuf / 巨型 json / 编译产物）

2. **单核串行**：
   ```yaml
   parallel:
     enabled: false
     max_workers: 1
   ```
   - 一台机器单进程跑，6 核闲置
   - 优点：内存峰值可控（单 grammar 峰值 × 1）
   - 缺点：扫 20000 文件需要 60-90 秒

3. **多语言策略**：
   ```yaml
   languages:
     enabled: [typescript, python, go, rust, cpp, java, lua]
     detection: file_extension
     fallback: skip_with_warning
   ```
   - 按文件扩展名分发 grammar，**不并行**
   - 不支持的扩展名：跳过该文件 + WARN，但**不阻断**整批

4. **内存峰值监控**：
   ```python
   @contextmanager
   def memory_peak_monitor(limit_mb=2048):
       proc = psutil.Process()
       peak = proc.memory_info().rss
       try:
           yield
       finally:
           current = proc.memory_info().rss
           peak = max(peak, current)
           log.info(f"tree-sitter peak RSS: {peak / 1024 / 1024:.1f} MB")
           if peak > limit_mb * 1024 * 1024:
               warn_user(f"Memory peak {peak / 1024 / 1024:.0f}MB > {limit_mb}MB, consider repo partitioning")
   ```

5. **整体 benchmark**（R5-Q4 选 A 的工程成本）：
   - 选 3 个不同大小仓库跑：
     - small：~5000 文件，如 `pydantic/pydantic`
     - medium：~20000 文件，如 `kubernetes/kubernetes`
     - large：~100000 文件，如 `vercel/turborepo`
   - 测：总耗时 / 内存峰值 / chunked 跳过的文件数
   - 输出 `docs/benchmarks/tree-sitter-baseline.md`

## Alternatives

- **H1. 串行 + chunked（本 ADR）** —— 内存稳，速度慢，benchmark 10 分钟。
- **H2. 并行 + 流式** —— 多核 + 流式 read，需 30 分钟 benchmark 找最优 worker 数。
- **H3. 折中** —— 流式 + 语言分批 4 核并发，工程量中等。

## Consequences

- 单次 tree-sitter 扫描在大仓库（20000 文件）耗时预期 60-90 秒。
- 内存峰值**单 grammar × 1**，理论峰值 200-400MB。
- 工程成本：~100 行 Python + 1 份 3 仓库 benchmark 报告。
- ADR-0005 的覆盖率门控将在 100MB+ 仓库下稳定运行。
- ADR-0014 给 R1（token 爆炸）风险登记新增：`tree-sitter-oom` 类目——本 ADR 不彻底消除 OOM，但把 OOM 概率从"10次跑崩1次"降到"100次跑崩0.5次"。

## Open Questions

- [ ] 5MB chunked 阈值是否需要按语言调？JS bundle 可能 > 5MB 是常态，是否需要降到 2MB？
- [ ] 跳过大文件时，stage 7 cross-ref pass 是否会因"缺数据"误判？
- [ ] 单核串行浪费 6 核，是否值得在 `conservative` SLA 档加 `parallel: true` flag？

## Linked

- ADR-0005（tree-sitter 解析覆盖率门控的 expected 侧）
- ADR-0007（SLA 预算中 tree-sitter 占用 2-3 秒）
- ADR-0009（R1 token 爆炸补充 R-tree-sitter-oom 子项）
- 阶段六 §8
