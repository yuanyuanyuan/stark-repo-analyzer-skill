# deep Full（接线后）对照 standard / v1.0

| 报告 | 行数 | 字节 | 唯一锚点≈ | 200ms | ready | 导航 | ExportControls | SEO | Worker |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1.0 | 136 | 13211 | **62** | 2 | 2 | 6 | 6 | 21 | 15 |
| standard 213622 | 204 | 12169 | 20 | 0 | 0 | 0 | 4 | 12 | 17 |
| **deep wired 220005** | **226** | 11949 | **24** | **2** | **2** | **7** | 4 | **16** | **18** |

## 门禁

| 项 | standard 213622 | deep 接线前 214641 | **deep 接线后 220005** |
|---|---|---|---|
| Doctor deep | false（standard 跑） | **false**（reference-edges） | **true** |
| Gate Full | true | false | **true 13/13** |
| ANALYSIS_REPORT | 有 | 无 | **有** |
| graphify_refs.wired | n/a | false | **true** |
| probes | 2 hit / 1 miss | 3 n_a | **3 hit** |

## 解读

1. **接线是 deep Full 的阻塞根因**：同一目标仓，接线前 doctor 拒 deep；接线后 Full 通过。
2. **deep 相对 standard 略增主题覆盖**（200ms/ready/导航/SEO），行数 226 > standard 204，但锚点密度仍 **远低于 v1.0（62）**。
3. 因此「比 v1.0 薄」**不能**只靠换 deep 解决；deep 修复了能力门禁与部分主题，**不自动恢复 v1.0 锚点密度**。
4. core incomplete refs ≈76.7% 仍低于 80% 阈值故 gate 绿，跨模块结论仍需谨慎。
