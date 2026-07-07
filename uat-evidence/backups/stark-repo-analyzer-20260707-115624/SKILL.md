---
name: stark-repo-analyzer
version: 0.1.0
description: 使用确定性脚本和必要的 agent 判断，对目标 git 仓库生成可复查的架构分析底料、动态切片和分析报告。
---

# Stark Repo Analyzer

本 skill 用于分析一个本地或远程 git 仓库，生成 `analysis/` 目录。确定性的步骤由 `scripts/repo_analyzer.py` 完成；需要业务判断、跨模块评价和最终评分的步骤再交给 subagent。

## 最小运行方式

```bash
python3 scripts/repo_analyzer.py <本地仓库路径或 git URL> --output analysis --no-question
```

生成三份受众报告：

```bash
python3 scripts/repo_analyzer.py <本地仓库路径或 git URL> --output analysis --mode all --no-question
```

## 主要产物

跑完后先看：

1. `analysis/README.md`：总索引，判断本次运行是否完整。
2. `analysis/02a-manifest-card.md`：5KB 项目名片，快速理解目标仓库。
3. `analysis/ANALYSIS_REPORT.md`：主报告入口。
4. `analysis/slices/`：需要继续深挖时交给 subagent 的底料。

- `analysis/00-meta.txt`：git 与文件元数据。
- `analysis/02a-repo-type.yaml`：Repo 类型与动态切片清单。
- `analysis/02a-manifest-card.md`：5KB 项目名片。
- `analysis/slices/`：按类型生成的 XML/TXT 切片。
- `analysis/05-module-ids.yaml`：模块候选清单。
- `analysis/08-coverage.md`：覆盖率门控基线。
- `analysis/ANALYSIS_REPORT*.md`：确定性分析报告。
- `analysis/README.md`：索引页。
- `analysis/acceptance/check.sh`：本地硬断言入口。

## 执行边界

- 不读取或写入 `graphify-out/`；如果需要串联 graphify，请在 shell 层执行。
- 不把确定性扫描交给 LLM 猜。
- 不新增依赖；当前 CLI 只使用 Python 标准库和 git。
- 深度模块分析、交叉验证、内容准确度和最终裁决分数需要后续 subagent 完成。

## 终验收

完成 PLAN.md 实现时，必须再运行两个代理场景：

1. 小白用户子代理：第一次使用该 skill，分析 `https://github.com/adminhuan/smart-search-mcp`。
2. 裁决代理：按 10 分制评价完整过程、agent 反应和分析结果。

只有裁决分数 `>= 9.5/10` 才能声明最终通过。
