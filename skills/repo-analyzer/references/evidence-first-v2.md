# Evidence-First v2 工件模板

## Evidence Plan

```markdown
# Evidence Plan

## 架构问题
- 问题、为什么值得回答、回答会影响哪项架构判断。

## 候选证据
- 问题 -> `文件:行号` / 关键单元 ID / 项目文档。

## 模块分级
- core / secondary / excluded，附理由和来源。

## 分工
- 运行时无 subagent 时可写 `parallelism: degraded` 与串行顺序。
- standard/deep 完整通过必须写明：
  - `parallelism: active`
  - 实际子代理分工
  - 每个子代理产物，例如 `module-evidence/{module}.json`
  - 主 Agent 融合过程
- standard/deep 若写 `parallelism: degraded`，只能判为 CLI/gate 机械链路通过，不能判为多子代理验收通过。

## 预算
- mode、time、token、subagent 上限、单 agent 证据预算、报告长度。

## 风险抽样
- 每个核心模块的风险类别、候选路径和停止条件。

## Unparsed File Read Pass
- 触发：core 模块存在 unparsed 文件时 **强制**；不得仅列 Unsupported 路径后结束。
- `unparsed_read_pass.parallelism`: `active` | `degraded`（与模块分析 parallelism 分字段）。
- 工具白名单：`rg`/`grep`、`find`、`wc`、文件读取、`git` 只读。
- 选样与预算：入口/主路径 UI / Matrix 跨模块 unparsed / 风险路径优先；quick≤5；standard 覆盖 core 主路径相关子集；deep 提高比例并允许预算内 skip_reason。
- 产物：`unparsed-file-reviews/*` 或 `unparsed-file-reviews.json`，和/或 Matrix `unparsed_manual_reads[]`。
- 语义：confidence=`manual-read`；**不**清除 unparsed、**不**抬高 parse_rate、**不**计为 analyzed unit。
```

## Module Evidence Matrix

每个核心模块保存为 `module-evidence/{module}.json`：

```json
{
  "module": "模块名",
  "module_role": "模块在系统中的角色",
  "entry_points": ["src/x.ts:10"],
  "core_data_structures": ["结构及其设计意义"],
  "main_flow": ["带锚点的主流程"],
  "cross_module_dependencies": ["依赖两端及协同方式"],
  "key_design_decisions": ["动机、权衡、替代方案"],
  "risk_areas": [
    {
      "category": "error-handling",
      "evidence": "src/x.ts:42",
      "finding": "抽样发现",
      "impact": "对架构评价的影响"
    }
  ],
  "semantic_reviews": [
    {
      "unit_id": "src/x.ts#handler",
      "anchor": "src/x.ts:10",
      "judgment": "该入口通过队列隔离请求接收与后台处理，以延迟换取突发流量下的稳定性。",
      "source_observation": "源码 span 显示 handler 只入队请求并立即返回，由后台 worker 执行实际处理。",
      "verdict": "supported"
    }
  ],
  "source_evidence": ["src/x.ts:10"],
  "open_questions": ["尚未验证的问题"],
  "narrative": "与机器字段一致的 Why > What 模块叙事",
  "unparsed_manual_reads": [
    {
      "path": "src/legacy/ui.tsx",
      "tools_used": ["rg", "read"],
      "anchors": ["src/legacy/ui.tsx:12"],
      "observation": "该 unparsed 文件编排上传入口，但仍无枚举单元。",
      "confidence": "manual-read",
      "residual_gap": "无稳定 unit 分母；跨模块类型细节未验证"
    }
  ]
}
```

`unparsed_manual_reads` 为可选数组：仅当本模块 path 下存在 core unparsed 且本 pass 补读过时填写。字段含义：`path` 为 unparsed 文件路径；`tools_used` 为基线只读工具；`anchors` 为 `文件:行号`；`observation` 为可审计观察；`confidence` 固定 `manual-read`；`residual_gap` 为补读后仍未知。该字段 **不** 把文件变为 analyzed unit。

`cross_module_dependencies` 和 `open_questions` 可以是空数组，其余字段不可为空。`source_evidence` 必须使用 `文件:行号` 锚点。每条有效 `semantic_reviews` 都要求：`unit_id` 引用当前 analyzed unit，`anchor` 与 `judgment` 逐值匹配 coverage 当前字段，`source_observation` 非空，`verdict` 为 `supported`。

语义抽查预算按模式变化：

- standard：每个 core 模块至少 1 条。
- deep：每个 core 模块最多 3 条代表性 analyzed unit；不足 3 条时全抽。

选样优先跨模块关系、`refs_status` 不完整、风险路径和影响最终批判性评价的判断。语义抽查降低锚点掺水风险，但不构成真实性证明。

## Coverage 回填

只能修改 `coverage-units.json` 中每个 unit 的以下字段：

```json
{
  "status": "analyzed",
  "anchor": "src/x.ts:10",
  "judgment": "该入口通过队列隔离请求接收与后台处理，以延迟换取突发流量下的稳定性。",
  "skip_reason": null
}
```

未分析时保持 `status: unanalyzed`，填写一行 `skip_reason`，不得删除单元。

## Unsupported Area

报告必须逐路径声明未解析 core 区域，并明确不对该区域做覆盖充分声明。**Unsupported ≠ 禁止分析**：出现 core unparsed 时必须先执行 **Unparsed File Read Pass**，再声明 residual。

```markdown
## Unsupported Area

- `src/legacy/parser.ts`：符号枚举失败；已执行 manual-read 补读（见 `unparsed-file-reviews/parser.md`），观察见 `src/legacy/parser.ts:12`（confidence=`manual-read`，非枚举单元）。本报告仍不对该文件声明覆盖充分 / analyzed unit。
- `src/debug/seo.ts`：预算内 skip（优先级低于主路径 UI）；未补读，残留盲区。
```

只有包含路径和 `Unsupported Area` 标识的明确声明，质量门才允许未解析 core 区域继续合成；它不豁免解析质量阈值。core unparsed 非空时，质量门 `unparsed-manual-review` 还要求存在补读记录（Evidence Plan「Unparsed File Read Pass」、`unparsed-file-reviews*` 或 Matrix `unparsed_manual_reads`）；**有补读记录仍不豁免** `parse-quality`。`coverage-units.json` 的 `parse_health` 必须显示全仓和主语言源码解析率至少 80%，核心未解析文件占比不超过 20%。核心单元中 `refs_status: partial/missing` 的占比超过 80% 时同样阻断合成。
