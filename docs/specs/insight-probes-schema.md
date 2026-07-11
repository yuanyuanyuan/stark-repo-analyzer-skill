# insight-probes.json 最小 Schema（T19-1）

> 机械合同 SSOT：Acceptance Auditor / Agent Consumer / Process Gate（`insight-probe-process`）共用。
> 本票**不**定义 LLM 判定逻辑；只定义产物形状与流程完整性。

## 文件位置

分析**工作目录**根：`{out}/insight-probes.json`（与 `quality-gate-report.json` 同级）。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | number | 是 | 固定为 `1` |
| `mode` | string | 是 | 分析模式，如 `standard` / `deep` / `quick` |
| `probes` | array | 是 | 探针结论列表；Catalog **每一类至少一条** |

## Probe 项

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 是 | Catalog id（见下） |
| `status` | string | 是 | 仅 `hit` \| `miss` \| `n_a` |
| `summary` | string | 是 | 非空结论摘要；`n_a` 时作为**形态/不适用理由** |
| `anchors` | string[] | 是 | 源码或文档锚点列表（可为空数组；`hit` 建议非空，由后续票加强） |
| `report_ref` | string | 是 | 终稿/草稿中的章节或锚点引用字符串（可空字符串；hit 进终稿由 T19-3 约束） |
| `candidates_considered` | number | 否 | 确定性候选枚举数量（审计辅助） |

### 示例

```json
{
  "version": 1,
  "mode": "standard",
  "probes": [
    {
      "category": "ui_promise_runtime_path",
      "status": "miss",
      "summary": "沿候选选项入口复核后未发现未挂接的用户可感知承诺。",
      "anchors": [],
      "report_ref": "",
      "candidates_considered": 2
    },
    {
      "category": "multi_source_rules",
      "status": "miss",
      "summary": "未发现同一业务规则在多处冲突定义。",
      "anchors": [],
      "report_ref": ""
    },
    {
      "category": "config_dual_write_dead_impl",
      "status": "n_a",
      "summary": "仓库无多配置源/平行 Manager 形态，类别不适用。",
      "anchors": [],
      "report_ref": ""
    }
  ]
}
```

## Insight Probe Catalog（稳定 id）

| id | 语义 |
|----|------|
| `ui_promise_runtime_path` | 用户可感知选项/行为是否进入真实执行路径 |
| `multi_source_rules` | 同一规则是否多处定义且冲突 |
| `config_dual_write_dead_impl` | 多配置源或未挂主路径的平行实现 |

类别 id **不得**绑定单一 demo 业务名词。

## Process Gate 语义（`insight-probe-process`）

写入 `quality-gate-report.json.checks[]`：

- **fail** 当：缺文件、JSON 非法、`version/mode/probes` 不合法、缺任一 Catalog 类别、非法 `status`、必填字段类型错误。
- **pass** 当：三类均有合法结论，字段合法——**不论** `status` 为 `hit` / `miss` / `n_a`。
- **`status=miss` 不导致 fail**（认真查过未发现硬伤 ≠ 流程失败）。
- `allowed_to_synthesize` 仍为全部 checks 的合取，表示是否允许 **Full** Delivery；本 schema 票不改变「gate 红是否写终稿」的 skill 行为（T19-4）。

## 非目标

- 不在本 schema 中实现候选枚举或 LLM 判定（T19-2）。
- 不强制 `hit` 与终稿正文对齐（T19-3）。
- 不定义 `delivery_status` / Degraded 横幅（T19-4）。
