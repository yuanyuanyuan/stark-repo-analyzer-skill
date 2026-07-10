# Evidence-First v2 最小基准

## 目的

本基准只验证 v2 的核心因果链，不构建重型 benchmark harness：确定性 Repo Map 与关键单元锚点是否能减少后续模型需要接收的源码输入，同时不遗漏已知核心模块，并让质量状态可机械检查。

## Fixture

- JavaScript 入口与服务模块
- 8000 行 legacy 兼容区，用于模拟大仓库中的低价值长文件
- README、架构文档、测试、generated、vendor 和 package manifest
- Universal Ctags 可复现测试替身
- graphify 明确不可用

## 对比口径

| 指标 | v1 近似路径 | v2 路径 |
|---|---|---|
| elapsed | 读取全部源码文件的本地 I/O 时间 | Doctor、scan、summarize、units、回填工件和 gate 的完整时间 |
| approximate token | 全部源码字节 / 4 | `repo-map.md` + 已分析关键单元锚点行字节 / 4 |
| 核心模块遗漏 | 已知核心模块是否缺失 | Repo Map 是否识别 `src` 候选 |
| 质量指标 | v1 无机器 gate | v2 gate pass rate |

elapsed 的工作内容不同，只用于记录成本边界，不宣称 CLI 墙钟时间必然小于一次文件读取。核心比较指标是近似模型输入、核心模块遗漏和质量可审计性。

## 复现

```bash
node --test test/e2e.test.js
```

测试会在输出中打印 `benchmark={...}`，并断言：

- v2 近似模型输入小于旧流程全量源码输入
- v2 不遗漏已知核心模块
- graphify 缺失时仍完成全链路
- v2 质量门逐项通过
- 同一 fixture 的 quick、standard、deep 三档均通过各自质量门，且已分析单元、风险样本、报告长度与 token 预算逐档增加

具体 elapsed 与字节换算结果受机器性能影响，不写死到仓库；测试每次运行都会生成当前机器的可复现结果。
