# Evidence Plan · v2.1 · standard · multi-agent

## 架构问题

- 长截图切割如何把上传 → Worker 切图 → 按 index 落库 → 导出串成主链？
- src 与 shared-components / config / tools 的职责边界在哪里？
- parse_rate≈48% 时，哪些结论可从 hooks/utils 成立，哪些必须 Unsupported？

## 候选证据

- Repo Map / coverage-units（本目录已从同 commit 确定性扫描继承并 doctor 绑定）
- 主链：`src/main.tsx`、`src/App.tsx`、`src/hooks/useAppState.ts`、`useImageProcessor.ts`、`useWorker.ts`
- 导出：`src/utils/pdfExporter.ts`、`zipExporter.ts`、`ExportControls.tsx`、`FileUploader.tsx`
- 次要：`config/*`、`shared-components/*`、`tools/*` 抽样

## 模块分级

- core: `src`
- secondary: `config`、`shared-components`、`tools`、`scripts`
- excluded: `test-setup`、`.`（无单元分母根杂项）

## 分工（parallelism: active）

本轮在支持并发工具调用的 Codex 会话中**真实并行**启动 3 个分析 worker（子代理角色），各自独立读写产物，再由主 agent 融合。

| 子代理 ID | 职责 / scope | 产物路径 |
|---|---|---|
| `subagent-src-state` | 会话状态 + Worker 切图主链（useAppState / useImageProcessor / useWorker / main） | `subagent-artifacts/subagent-src-state.json` |
| `subagent-src-export` | 上传 UI + PDF/ZIP 导出边界 | `subagent-artifacts/subagent-src-export.json` |
| `subagent-secondary` | config / shared-components / tools / scripts 抽样 | `subagent-artifacts/subagent-secondary.json` |

主 agent 融合过程：

1. 校验三份 subagent JSON 的 unit_id / anchor / judgment 非空  
2. 合并写入 `coverage-units.json` 回填  
3. 合成 `module-evidence/src.json`（吸收 state+export 子代理发现；secondary 进入跨模块依赖与次要叙事）  
4. 写 `report.md` 叙事线：问题 → 全景 → 主链（state 子代理）→ 导出（export 子代理）→ 次要模块（secondary 子代理）→ 风险/建议  
5. 跑 `gate --mode standard`  
6. 记录预算与并行摘要  

## 预算

- mode: standard  
- subagent 上限: 6；**本轮实际并行 3**  
- 覆盖目标: core 60% / secondary 30%  
- Semantic Source Review: 每 core ≥1（融合阶段由主 agent 对跨模块高影响单元复核）

## 风险抽样

- 切片乱序 / Object URL 泄漏 / 导出空选择 / 未解析 components

## 报告结构

场景 → 全景 → 设计哲学 → 主流程 Mermaid → 模块协作 → src 深度（双源子代理）→ 次要模块 → 风险与 Unsupported → 改进建议 → 并行执行摘要


## 预算（gate 字段）

- mode: standard
- time: 90 分钟
- token: 90000
- subagent 上限: 6（本轮实际 3）
- 报告长度: 中等

## 实际子代理执行记录（gate）

- parallelism: active
- 子代理分工：subagent-src-state 负责 src 会话状态与 Worker 切图主链。
- 子代理分工：subagent-src-export 负责上传 UI 与 PDF/ZIP 导出边界。
- 子代理分工：subagent-secondary 负责 config/shared-components/tools/scripts 次要模块抽样。
- 子代理产物：subagent-src-state 写入 subagent-artifacts/subagent-src-state.json 与贡献 module-evidence/src.json。
- 子代理产物：subagent-src-export 写入 subagent-artifacts/subagent-src-export.json。
- 子代理产物：subagent-secondary 写入 subagent-artifacts/subagent-secondary.json。
- 主 agent 融合过程：主 agent merge 三份子代理产物后回填 coverage-units.json、合成 module-evidence/src.json 与 report.md，再运行 gate。
