# Pre-Release Security Scan · 发布前安全扫描

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 规定公开发版前必须执行的敏感资料/密钥泄漏扫描；不替代真实回归 UAT，也不定义产品分析合同 |
| 当前状态 | `active` |
| 当前结论/入口 | **Release 阻断门**：打 tag / 创建 GitHub Release / 声明版本已公开就绪前，必须完成本规则规定的扫描且无真实泄漏 |
| 何时读取 | 准备升 `VERSION`、写发布 CHANGELOG、推送发布提交、打 tag、`gh release create` 或公开“可安装发布”前 |
| 何时更新 | 扫描工具、必扫范围、通过标准或证据落点变化时 |
| 关联真源 | 产品发布级行为验收 → [real-uat-regression](../real-uat-regression/README.md)；控制面收口 → [document-control](../document-control/README.md) / [dual-agent-review](../dual-agent-review/README.md) |

## 一、要解决什么

公开仓库一旦推送密钥，历史几乎不可逆。本规则要求：**发布前先证明当前工作树与 git 历史没有敏感资料泄漏**，再进入 tag / GitHub Release。

直觉：真实回归 UAT 像“功能路考”；本扫描像“出站安检，先查有没有把钥匙和证件带出去”。类比边界：安检通过不代表功能合格；功能路考通过也不能代替安检。

## 二、触发条件（必须执行）

满足任一即触发，且 **阻塞** 后续发布动作，直至通过或书面阻塞说明：

1. 创建或更新 **GitHub Release**（含 source / 安装说明指向的正式版本）。
2. 创建或推送 **版本 tag**（如 `v1.2.0`）。
3. 将 `VERSION` / adapter 清单 / 公开 README 声明为 **新的可安装发布版本** 并准备推送到默认公开分支。
4. 活动 roadmap/plan 将目标定义为“公开 release / 发版 / ship 到 GitHub”。

不触发（但推荐择机跑）：纯内部文档整理、未触达公开身份的本地实验、不升版本的小修。

## 三、最低扫描包（刚需）

发布前 **同一次收口会话** 内至少执行：

### 1. 工作树密钥扫描

```bash
gitleaks dir --no-banner --redact .
```

### 2. 全 git 历史密钥扫描

```bash
gitleaks git --no-banner --redact --log-opts="--all" .
```

### 3. 跟踪面快速核对

```bash
git ls-files | rg -i '(^|/)\.env($|\.)|\.pem$|id_rsa|\.p12$|credentials|\.key$' || true
rg -n '^\.env($|\.|$)' .gitignore
```

要求：

- 无真实 `.env` / 私钥类文件被 git 跟踪（`.env.example` / `.env.template` 除外）。
- `.gitignore` 仍覆盖 `.env` 与 `.env.*`（可对 example/template 做例外）。

### 4. 可选加深（推荐，不替代 1–3）

- gstack **`cso`** daily 或 secrets archaeology（Phase 2），对依赖、CI、Skill 供应链做补充。
- 自定义高价值前缀扫历史：`AKIA`、`ghp_`、`github_pat_`、`sk_live_`、`sk-ant-`、`xoxb-`、`-----BEGIN … PRIVATE KEY-----` 等。

工具缺失时：必须先安装（如 `brew install gitleaks`）再扫；**禁止**用“没装工具”当通过理由。

## 四、通过 / 失败标准

| 结果 | 条件 | 能否发版 |
|---|---|---|
| **PASS** | gitleaks 工作树与全历史均为 `no leaks found`（或仅确认后的已知假阳性并已 allowlist）；跟踪面无真实密钥文件 | 可以继续 tag / Release（仍须满足其它发布门） |
| **FAIL** | 任一真实密钥、token、私钥、带口令连接串出现在工作树或历史；或扫描未实际跑完 | **禁止** tag / Release / 声称发布就绪 |
| **BLOCKED** | 环境无法跑扫描且无法在合理时间内修复 | 保持未发布；progress 写阻塞原因，不得标 `completed` 为“已发布” |

假阳性处理：

- 允许对 **确认的** 测试夹具 / 文档占位符使用 gitleaks allowlist（路径或规则级），并在 progress 写明理由。
- 本仓库历史中的超大 baseline/`graph.json`、UAT 证据包路径应通过根目录 `.gitleaks.toml` 路径 allowlist 处理，**不要**用 `--max-target-megabytes` 冒充“已扫全历史密钥面”。
- **禁止**为通过而全局关闭规则、跳过 `--log-opts="--all"`，或只扫最近一次 commit 冒充全历史。

泄漏处置顺序（一旦 FAIL）：

1. **先在提供商侧 rotate / 吊销**；
2. 停止跟踪并清理工作树；
3. 必要时 scrub 历史并通知所有已克隆方；
4. 复扫 PASS 后才能重新进入发版流程。

## 五、证据与落点

每次发布扫描须留下可核验记录（至少一项）：

1. 发布 plan 对应的 `*-progress.md` 追加一节 **「发布前安全扫描」**，写明：
   - 时间、扫描人/Agent、gitleaks 版本；
   - 两条命令的退出码与关键日志行（commits scanned / no leaks found 或 findings 摘要）；
   - 跟踪面核对结果；
   - 最终 verdict：`PASS` / `FAIL` / `BLOCKED`。
2. 可选：本地 JSON 报告写入 `.gstack/security-reports/`（目录须 gitignore，**不得**把含真实密钥的全文报告提交进公开仓）。

收口声明：

- 可以说「发布前安全扫描 PASS」。
- **不能**把本扫描 PASS 说成「真实回归 UAT 通过」或「产品行为已验收」。
- **不能**把真实回归 UAT 通过说成「已做过密钥安检」。

## 六、与其它门的关系

| 门 | 职责 | 与本规则关系 |
|---|---|---|
| [real-uat-regression](../real-uat-regression/README.md) | 用户等价入口到报告的产品行为 | 并列发布门；互不替代 |
| [task-quality-gates](../task-quality-gates/README.md) / [dual-agent-review](../dual-agent-review/README.md) | 交付思考关口与独立 Judge | 发布任务仍走完整门/Judge 时，本扫描是 Worker 验证证据之一 |
| `validate-release-metadata.py` / `validate-control-plane.py` | 版本投影与控制面状态 | 元数据/状态正确 ≠ 无密钥泄漏 |

建议发布顺序：

1. 实现与文档就绪  
2. **本规则安全扫描 PASS**  
3. 版本元数据校验  
4. 发布级真实回归 UAT（若本版本要求）  
5. 控制面 audit / Judge（若适用）  
6. tag + GitHub Release  

第 2 步可与第 3–5 步并行准备，但 **第 6 步前必须已有本规则 PASS 证据**。

## 七、禁止事项

1. 未跑全历史扫描就打公开 tag。  
2. 只扫当前 diff / 暂存区，却声称“历史已安检”。  
3. 将真实密钥写入 progress、Issue、Release notes 或提交 allowlist 样本。  
4. 用单元测试、fixture、或“代码里没有 password 字符串”代替 gitleaks。  
5. 因本规则未机械挂进 CI 而跳过：在 CI 补齐前，**Agent/人类发布操作者仍须手动执行**。

## 八、最小操作清单（复制用）

```bash
# 0) 工具
command -v gitleaks || brew install gitleaks
gitleaks version

# 1) 工作树
gitleaks dir --no-banner --redact .

# 2) 全历史
gitleaks git --no-banner --redact --log-opts="--all" .

# 3) 跟踪面
git ls-files | rg -i '(^|/)\.env($|\.)|\.pem$|id_rsa|\.p12$|credentials|\.key$' || true
rg -n '^\.env' .gitignore
```

全部通过后，再执行 `validate-release-metadata`、tag 与 `gh release`。
