# Glossary — repo-analyzer skill

> 在 grilling 过程中沉淀的术语表。新词进入时按字母顺序插入。

| 术语 | 定义 | 出处 |
|------|------|------|
| **12 维切片** | repomix 阶段二按维度切分仓库的产物:`01-frontend.xml` ~ `12-history-hotspot.txt`。 | PLAN §3 |
| **Compression Ratio** | repomix 输出体积 / 仓库原始体积。比率越低,信息密度越低、信号越稀疏。 | 经验值,目标 > 0.2 视为有效。 |
| **Coverage Gate** | 阶段六"覆盖率门控":核心模块 80% / 次要 20% 必须覆盖,否则回到阶段五补做。 | PLAN §10 |
| **Diff-as-Input** | 阶段七 `7-summary` 输入为各 draft diff(增量),非完整模块文档。 | PLAN §7.3 |
| **IGNORE_GLOB** | repomix `--ignore` 模式,过滤掉 `*.lock`、`.claude/**`、二进制等。可在阶段二中以 `--include` 例外放行。 | PLAN §2.1 |
| **Manifest** | 阶段二开始前的 `01-pragmatic.md` / `02-slices-manifest.md`,列出本次切片维度的实际清单与对应文件数。 | PLAN §3 |
| **Phase-2a** | (拟定)阶段二前的一次轻量级探测,仅扫描 manifest 文件以推断 Repo 类型。 | ADR-0002 |
| **Pragmatic Summary** | 阶段一输出的 `01-pragmatic.md`:一句话项目定位、价值主张、目标用户。 | PLAN §2.1.3 |
| **README Index** | 阶段八产出的 `analysis/README.md`,作为目录索引。 | PLAN §8 |
| **Repo Type Tagger** | 阶段三识别的仓库类型(`web-fullstack` / `single-lang-CLI` / `monorepo` / `embedded` / `kernel`)。 | ADR-0002 |
| **Sign-off Checklist** | 阶段九最终验收清单,13 条目逐一勾选。 | PLAN §10 |
| **Sub-agent Mode** | 阶段一与阶段五使用 sub-agent 并行:阶段一为 4+1 宏观,阶段五为按业务模块并行。 | PLAN §2.2.4 / §7 |
| **Storyline** | 阶段四 §6.2"叙事线":模块按业务场景而非按文件夹聚合,3~5 章。 | PLAN §6.2 |
| **Tier Coverage** | 核心 / 重要 / 次要 三档模块覆盖度阈值(80% / 50% / 20% 目标)。 | PLAN §6 / §10 |
| **TL;DR Hook** | 报告 §0 TL;DR 的第一句,要求让陌生读者 5 秒抓住项目是什么。 | PLAN §9.2 |
| **Trust Boundary** | (ADR-0001)在阶段一/阶段二信号冲突点上,显式声明"以哪边为准"的边界。 | ADR-0001 |
| **Acronym** | (后续补) | |
