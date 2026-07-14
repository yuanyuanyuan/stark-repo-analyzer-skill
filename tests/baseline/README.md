# 历史 Baseline 外部归档入口

旧 V1 的完整 `physical-runs/`、`reference-runs/`、六仓库清单和过程报告已经退出 Git。
它们仍可从外部归档定位和核验，但不再作为当前 analyzer 的 acceptance 输入。

## 归档位置

- 仓库内索引：[`docs/archive/local-artifact-index.md`](../../docs/archive/local-artifact-index.md)
- 本机归档：`/Users/chuzu/repo-analyses/stark-repo-analyzer-skill-g4-artifacts-20260714/`
- 内容清单：外部目录中的 `ARCHIVE_MANIFEST.sha256`
- 清单 SHA-256：`25899571e64847607e533f866a61115e2d658273d3a784e3d0a0d5a890ece215`

完整副本包含归档时的 3,913 个常规文件、158 个目录和原始相对路径。恢复前先核对清单，
不要只凭目录存在判断证据完整。

## 当前验收边界

- 当前单元测试位于 `tests/test_graphify_gate.py`，只使用 `tests/fixtures/graphify/` 的小型确定性 fixture。
- 当前 Skill 静态合同由 `acceptance/skill-structure-check.sh` 和
  `acceptance/skill-contract-check.sh` 验证。
- 开发期聚焦 UAT 与发布级真实回归的触发条件、证据合同和声明上限，以
  [`docs/dev-rules/real-uat-regression/README.md`](../../docs/dev-rules/real-uat-regression/README.md) 为准。

旧 `physical-baseline-check.sh` 和 `physical-repeatability-check.sh` 与完整六仓库运行目录强耦合，
已随 G4-2 删除。它们验证的是旧 V1 证据形状，不能继续充当当前产品 gate。

## 维护边界

- 不在本目录重新提交完整运行目录、Graphify 输出、缓存、长转录或旧六仓库报告。
- 新的确定性测试证据进入 `tests/fixtures/`；新的真实 UAT 原始证据按 ADR-0019 保存在 Git 外。
- 外部归档位置、清单或校验值变化时，同步更新本入口和仓库内工件索引。
- 归档中的旧报告只能用于历史核验，不能覆盖当前 spec、ADR、roadmap 或 dev-rules。

## 主线总结

本目录现在是一张“取件单”，不是证据仓本体：Git 只保留定位和校验信息，完整历史材料位于外部归档。当前验收只读取活动测试、Skill 合同门和真实 UAT 规则，不再读取旧六仓库运行目录。
