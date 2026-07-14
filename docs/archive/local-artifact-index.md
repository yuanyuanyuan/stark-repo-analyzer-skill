# 本机工件归档索引

本索引只负责定位已经移出或即将移出 Git 的大型历史工件。它像“仓库外材料的提货单”：
记录位置和校验值，但不把历史材料重新变成活动产品合同或验收结论。

## 2026-07-14：G4 历史 Baseline 归档

完整 `tests/baseline/` 已复制到：

`/Users/chuzu/repo-analyses/stark-repo-analyzer-skill-g4-artifacts-20260714/`

归档结果：

- 源 HEAD：`f9025a554ad14ece26d9145d095c350f7664f6ee`；归档来自包含已有 staged/dirty 迁移的物理工作树。
- 内容：完整 `tests/baseline/`，共 3,913 个常规文件、158 个目录、1,224,337,092 个逻辑字节。
- 源清单：`SOURCE_MANIFEST.sha256`；归档清单：`ARCHIVE_MANIFEST.sha256`。
- 两份清单逐字比较通过，SHA-256 均为 `25899571e64847607e533f866a61115e2d658273d3a784e3d0a0d5a890ece215`。
- 详细来源、时间、口径和恢复边界见外部目录中的 `README.md`。
- G4-1 先建立外部副本，没有在归档刀中删除源证据；G4-2 校验入口后已将完整运行目录移出 Git，仓库只保留 `tests/baseline/README.md` 定位文件。

## 2026-07-13：根目录清理归档

仓库根目录曾包含 Graphify 输出、Codex 转录、工具缓存和重复参考 zip。目录收敛时，这些内容被保留到 Git 外位置：

`/Users/chuzu/repo-analyses/stark-repo-analyzer-skill-repo-cleanup-20260713/`

归档结果：

- 原始文件：177 个，约 8.8 MB。
- 校验清单：`MANIFEST.sha256`。
- 清单 SHA-256：`a8a473941059fe72efa05cffa96f603b2c8986558164410742456ef1e80f4b5a`。
- 内容：旧根 Graphify 输出、Codex 转录、工具缓存、Python bytecode 和重复参考 zip。

该目录仅用于防止清理过程丢失本机材料，不是当前产品合同或真实 UAT 通过证据。根 Graphify 输出属于开发期生成物；doctor self-test 已改用 `tests/fixtures/graphify/` 的最小确定性 fixture。

## 主线总结

当前有两份可核验的 Git 外归档：2026-07-14 的完整 baseline 副本，以及 2026-07-13 的根目录清理材料。索引只证明材料可定位和内容可校验，不提高其中任何旧运行的验收等级。
