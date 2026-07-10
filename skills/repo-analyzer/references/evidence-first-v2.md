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
- subagent scope，或 `parallelism: degraded` 与串行顺序。

## 预算
- mode、time、token、subagent 上限、单 agent 证据预算、报告长度。

## 风险抽样
- 每个核心模块的风险类别、候选路径和停止条件。
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
  "source_evidence": ["src/x.ts:10"],
  "open_questions": ["尚未验证的问题"],
  "narrative": "与机器字段一致的 Why > What 模块叙事"
}
```

`cross_module_dependencies` 和 `open_questions` 可以是空数组，其余字段不可为空。`source_evidence` 必须使用 `文件:行号` 锚点。

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

报告必须逐路径声明未解析 core 区域，并明确不对该区域做覆盖充分声明：

```markdown
## Unsupported Area

- `src/legacy/parser.ts`：符号枚举失败，本报告不对该文件及其跨模块关系声明覆盖充分。
```

只有包含路径和 `Unsupported Area` 标识的明确声明，质量门才允许未解析 core 区域继续合成。
