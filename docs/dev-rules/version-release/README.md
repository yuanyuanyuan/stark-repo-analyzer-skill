# Version Release · 版本发布规则 / SOP / Checklist

| 固定字段 | 内容 |
|---|---|
| 文档角色 | 本仓库公开版本发布的总规则、标准操作顺序（SOP）与可勾选检查清单；编排安全扫描、元数据、控制面与 Judge，不替代任一子门细则 |
| 当前状态 | `active` |
| 当前结论/入口 | **先扫 → 再提交/推送 → 再 tag/Release → 再 Judge 收口**；完成口径以「纠正后可安装版本」为准；tag 钉发布提交，收口文档可后推 `main` |
| 何时读取 | 升 `VERSION`、写 CHANGELOG、打 tag、`gh release create`、开发布 roadmap/plan 时 |
| 何时更新 | 发布顺序、检查项、元数据投影路径或失败模式变化时 |
| 关联真源 | 密钥门 → [pre-release-security-scan](../pre-release-security-scan/README.md)；产品 UAT → [real-uat-regression](../real-uat-regression/README.md)；完整门/Judge → [task-quality-gates](../task-quality-gates/README.md) / [dual-agent-review](../dual-agent-review/README.md)；控制面 → [document-control](../document-control/README.md) |

## 一、要解决什么

发版不是“改个版本号推上去”，而是一次**不可逆的公开声明**：tag 与 GitHub Release 会把某个提交钉成可安装身份。若安全扫描、元数据、控制面完成口径或 Judge 证据在 tag 之后才补齐，就会出现“版本已公开但证据追溯不上”的空洞。

直觉：发版像机场登机——安检（密钥）、登机牌（VERSION/tag）、舱单（Release notes）、登机口复核（Judge）各有一门，**不能先起飞再补安检条**。类比边界：安检通过不等于飞行合格（真实回归 UAT）；登机口复核通过也不等于已经飞过完整航线。

## 二、本仓库发布身份

| 真源 | 路径 / 约定 |
|---|---|
| 产品版本号 | 根 `VERSION`（单行，无 `v` 前缀） |
| 投影 | `package.json`、`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`、`.codex-plugin/plugin.json` |
| 变更说明 | `CHANGELOG.md`（版本节与 `VERSION` 一致） |
| 校验 | `python tools/release/validate-release-metadata.py` |
| Git 标签 | `v` + `VERSION`，如 `1.1.2` → `v1.1.2`（推荐注释标签） |
| 公开 Release | `gh release create`，非 draft；notes 不得越级宣称 UAT/marketplace |
| 控制面 | 发布类任务开 `docs/roadmap/*-release-roadmap.md` + `docs/exec-plans/*-release-plan.md` + `*-progress.md` |

Skill 核心交付清单见 `tools/release/core-package-files.txt`；协作基建（code-map、dev-rules）默认**不**进入 Skill 安装包，除非计划明确写入。

## 三、强制顺序（SOP）

复制执行时**禁止跳步**。时间线必须可在 progress 中核验。

### Phase 0 — 控制面与范围

1. `git status --short`；记录工作区基线与本任务拥有文件。
2. 若无活动发布控制面：成对创建 roadmap（目标/非目标/阶段）与 plan/progress（完整门、`独立Judge：必须`、CLOSE-J1/CLOSE-J2）。
3. 更新 `docs/roadmap/README.md`、`docs/exec-plans/README.md`、`docs/README.md` 活动入口（唯一 `active`）。
4. 写清**完成口径版本号**（若中途纠正发版，以纠正版本为完成口径，旧 tag 只作历史披露）。

### Phase 1 — 元数据（未 tag）

1. 升 `VERSION`。
2. 同步全部 adapter / `package.json` 投影。
3. 写 `CHANGELOG.md` 新版本节：做了什么、**没**改产品合同什么。
4. `python tools/release/validate-release-metadata.py` → PASS。

### Phase 2 — 发布前安全扫描（未 tag，同会话）

权威细则：[pre-release-security-scan](../pre-release-security-scan/README.md)。

```bash
command -v gitleaks || brew install gitleaks
gitleaks version
gitleaks dir --no-banner --redact .
gitleaks git --no-banner --redact --log-opts="--all" .
git ls-files | rg -i '(^|/)\.env($|\.)|\.pem$|id_rsa|\.p12$|credentials|\.key$' || true
rg -n '^\.env' .gitignore
```

要求：

- 两条 gitleaks **均为** `no leaks found` 且退出码 0。
- 使用根目录 `.gitleaks.toml` 时：仅允许对**已确认**的大体积分析夹具路径 allowlist；progress 写明理由。
- **禁止**用 `--max-target-megabytes` 冒充“已扫全历史密钥面”。
- 证据写入 progress 的 **「发布前安全扫描」** 节（时间、版本、命令、退出码、verdict）。

### Phase 3 — 功能/控制面验证（未 tag）

```bash
python -m pytest tests/unit -q
python tools/release/validate-control-plane.py --mode bootstrap
python tools/release/validate-control-plane.py --mode audit   # 已有 completed 门时
git diff --check
```

若本版本**宣称**产品行为或 G5 就绪：另按 [real-uat-regression](../real-uat-regression/README.md) 跑真实回归；否则 notes/progress 明确 **未执行**。

### Phase 4 — 提交与推送（仍未 tag）

1. 仅 stage 本任务范围。
2. 提交信息建议：`release: prepare vX.Y.Z …`。
3. `git push origin <default-branch>`。
4. **再次**（或确认仍有效）Phase 2 扫描结果属于**即将被 tag 的提交**；若 push 后又改了提交内容，必须复扫。

### Phase 5 — Tag 与 GitHub Release（不可逆）

仅在 Phase 2–4 通过后：

```bash
git tag -a "vX.Y.Z" -m "vX.Y.Z: <one-line summary>"
git push origin "vX.Y.Z"
gh release create "vX.Y.Z" --title "vX.Y.Z" --target <default-branch> --notes-file - <<'NOTES'
## 包含 / 不包含
## 验证边界（marketplace / G5 UAT 未声称则写明）
NOTES
```

对齐核验（**打 tag 当刻**）：

```bash
git rev-parse HEAD
git rev-list -n 1 "vX.Y.Z"
git rev-parse "origin/$(git rev-parse --abbrev-ref HEAD)"
gh release view "vX.Y.Z" --json tagName,isDraft,targetCommitish,url
```

要求：`HEAD` == `vX.Y.Z^{}` == 当时远端默认分支 tip；Release **非 draft**。

### Phase 6 — 控制面收口（完整门）

1. plan → `awaiting-judge`；progress 记 S0–S2 证据。
2. 生成审查包：`python tools/release/judge_review_package.py --plan <plan> …`
3. 独立 Judge（禁止 Worker 自过）：优先子代理，否则  
   `python tools/release/run-independent-judge.py --plan <plan>`
4. **原样**追加 `### Judge Review`；仅 `Verdict: pass` 或结构化用户豁免可继续。
5. `python tools/release/validate-control-plane.py --mode audit`
6. plan/roadmap → `completed`；更新目录索引为无活动 / 最近完成。
7. 收口文档提交**可以**推高 `main`；**版本 tag 仍钉在发布提交**（与 v1.0.0 / v1.1.0 模式一致）。  
   验收表述写「打 tag 当刻对齐」，不要写「收口后永远 main==tag」。

### Phase 7 — 纠正发版（仅当已公开版本有证据缺口）

若 tag 已公开但发现安全扫描/元数据/说明有硬缺口：

1. **不要**把“事后扫过了”改写成“发布前已扫过”。
2. 升补丁或次要版本（如 `1.1.1` → `1.1.2`），**重新从 Phase 1 走完整 SOP**。
3. 旧 tag 保留；Release notes 与 progress **披露**旧版本时序/证据缺口。
4. 控制面完成口径改写为**纠正版本**，避免 plan 仍写旧版本号导致 Judge revise。

## 四、验收项模板（写入审查包）

建议固定四条，避免漂移：

1. `VERSION` 与全部 adapter 投影一致。
2. 打 tag **前** gitleaks 工作树 + 全历史原命令 PASS，且 progress 有时间戳证据。
3. 打 tag **当刻** 默认分支 tip、`vX.Y.Z^{}`、GitHub Release 指向同一发布提交；之后允许收口文档推进 `main`。
4. Release notes / progress 披露未执行的 marketplace / G5；安全扫描 PASS ≠ 真实回归 UAT。

## 五、发布 Checklist（每次勾选）

### A. 范围与控制面

- [ ] 工作区基线已记录；用户无关改动已排除
- [ ] 发布 roadmap + plan + progress 已建或已激活；唯一 `active`
- [ ] plan 声明：`质量门：完整门`、`独立Judge：必须`、CLOSE-J1/CLOSE-J2
- [ ] 完成口径版本号写死（含是否纠正发版）

### B. 元数据

- [ ] `VERSION` 已升
- [ ] `package.json` / Claude / Codex adapter 版本一致
- [ ] `CHANGELOG.md` 有对应节
- [ ] `validate-release-metadata.py` PASS

### C. 安全扫描（tag 前）

- [ ] `gitleaks dir` PASS
- [ ] `gitleaks git --log-opts="--all"` PASS（无 max-target 冒充）
- [ ] 跟踪面无真实 `.env`/私钥类文件；`.gitignore` 覆盖 `.env`
- [ ] progress 有「发布前安全扫描」节，verdict=`PASS`

### D. 测试与其它门

- [ ] `pytest tests/unit`（或约定套件）PASS
- [ ] `validate-control-plane.py --mode bootstrap` PASS（活动完整门）
- [ ] `git diff --check` 干净
- [ ] 若宣称产品就绪：真实回归 UAT 已跑；否则明确未执行

### E. 提交 / tag / Release

- [ ] 发布内容已 commit 并 push
- [ ] 扫描针对**即将 tag 的提交**仍有效
- [ ] 注释标签 `vX.Y.Z` 已 push
- [ ] GitHub Release 非 draft，notes 边界正确
- [ ] 打 tag 当刻：main tip == `vX.Y.Z^{}` == Release 目标提交

### F. Judge 收口

- [ ] plan = `awaiting-judge`；审查包字段完整
- [ ] 独立 Judge 已跑；progress 有原样 `### Judge Review`
- [ ] `Verdict: pass` 或合格书面豁免（豁免人/豁免项/剩余风险）
- [ ] `validate-control-plane.py --mode audit` PASS 后才 `completed`
- [ ] 目录索引已更新；未把 Judge pass 说成 UAT 通过

## 六、常见失败模式（本仓库实证）

| 失败 | 后果 | 正确做法 |
|---|---|---|
| tag 前用 `--max-target-megabytes` 跳过大 blob 却记 PASS | Judge revise；不能声称全历史安检 | 原命令 + `.gitleaks.toml` 夹具 allowlist |
| 先 `gh release create` 再补完整扫描 | 证据无法追溯为 pre-release | 纠正版本重走 SOP；旧版披露缺口 |
| plan 完成条件仍写旧版本号，实际发纠正版 | 控制面与事实冲突 → Judge revise | 完成口径同步改为纠正版本 |
| 验收写「永远 main==tag」 | 收口文档一提交就“失败” | 验收写「打 tag 当刻对齐」 |
| 审查包验收项与 plan 不一致 | Judge 按包验收判 revise | 包与 plan 同一套验收句 |
| 超过 3 轮 revise 仍纠缠 | 协议要求交用户 | 停自动循环，列出选项请维护者决策 |
| 把 gitleaks PASS 写成产品 UAT | 证据等级越权 | 两门并列，互不替代 |

## 七、命令速查（最短路径）

```bash
# 元数据
python tools/release/validate-release-metadata.py

# 安全（tag 前）
gitleaks dir --no-banner --redact .
gitleaks git --no-banner --redact --log-opts="--all" .

# 测试与控制面
python -m pytest tests/unit -q
python tools/release/validate-control-plane.py --mode bootstrap

# 发布（示例版本）
git push origin main
git tag -a vX.Y.Z -m "vX.Y.Z: summary"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z" --target main --notes "..."

# 收口
python tools/release/judge_review_package.py --plan docs/exec-plans/<name>-plan.md ...
python tools/release/run-independent-judge.py --plan docs/exec-plans/<name>-plan.md
python tools/release/validate-control-plane.py --mode audit
```

## 八、与其它规则的分工

| 规则 | 管什么 | 不管什么 |
|---|---|---|
| **本文件** | 发版总顺序、checklist、tag/main 语义、纠正发版 | 密钥规则细节、UAT 矩阵、Judge 协议正文 |
| pre-release-security-scan | gitleaks 怎么跑、PASS/FAIL | 版本号投影、Release notes 文案 |
| real-uat-regression | 产品行为是否验过 | 密钥是否泄漏 |
| dual-agent-review | Worker/Judge 分权与 awaiting-judge | 具体 gitleaks 命令 |
| document-control | roadmap/plan 生命周期与索引 | GitHub Release API |

## 主线总结

公开发版 = 安全扫描通过的**同一提交**被 tag 并写成 GitHub Release，再经独立 Judge 收口。先扫后标；纠正版另开版本号；tag 钉死发布提交，收口文档可以随后推进 `main`。Checklist 每条都应对应 progress 或命令输出，禁止用口头“应该没问题”代替。
