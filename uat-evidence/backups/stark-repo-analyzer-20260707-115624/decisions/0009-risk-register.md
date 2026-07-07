---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q9)
---

# ADR-0009 风险登记表：R1~R6 + 预算耗尽兜底

## Context

13 阶段工作流没列风险与失败模式。一个生产级 skill 至少需要：

- Token 爆炸 → 阶段五产物超主 agent 上下文
- Sub-agent 超时 → 阶段五并发时 1+ 个 agent 挂掉
- 阶段二切片失败 → 浅 clone / 无 lock 文件
- Target repo 拒绝访问 / 需登录 / 二进制占大头
- 用户中途切换 mode（interactive → autonomous）
- 阶段六门控失败时如何回退
- 预算耗尽统一兜底

## Decision

**风险登记表，6 类 + 统一兜底**：

### R1 — Token 爆炸

- **触发时机**：阶段五产物超主 agent 上下文窗口（默认 200K tokens），或单 sub-agent 单次响应 > 50K tokens
- **检测方法**：每次 API 调用后 `tokens_used += response.usage.total_tokens`
- **降级路径**：
  1. 主 sub-agent 在阶段五阶段接收 draft 时按 5K tokens / chunk 分批 ingest
  2. Chunk 之间用 wikilink 锚点（`[[module_001 §3]]`）维护上下文连贯
  3. 单 sub-agent 响应 > 50K 时强制 `stop_reason=length`，改用 next sub-agent 接力
- **重试预算**：共用 ADR-0004 / ADR-0007 的 3 次配额

### R2 — Sub-agent 超时（≥1 个挂掉）

- **触发时机**：阶段五并行 sub-agent 中 1+ 个 agent 在 10 分钟内无响应（默认 LLM API timeout 60 秒 × 10 次重试）
- **检测方法**：sub-agent 启动时记录 timestamp，每 60 秒 ping；超过 10 分钟未响 mark `TIMEOUT`
- **降级路径**：
  1. 单个 sub-agent TIMEOUT → retry 1 次（同一 prompt +1 token variance）
  2. 重试仍 TIMEOUT → 标 `skipped`，**不阻断**其他 sub-agent
  3. 跳过模块在阶段六覆盖率门控中按 0% 覆盖计算（**不会门控失败**，因为是"没数据"而非"覆盖不足"）
- **报告影响**：`STATE_REPORT.md`（详见 R-budget-exhaustion）列出 skipped 模块清单

### R3 — 阶段二切片失败（Phase-2a / 12 维精切）

- **触发时机**：
  - Target repo 是 shallow clone（`git clone --depth=1`）
  - 仓库无 lock 文件（项目没锁定依赖）
  - 二进制文件占大头（图像 / 视频 / 模型权重）
  - Phase-2a 识别 Repo 类型时所有 6 个类型都不匹配（corner case）
- **检测方法**：Phase-2a 结束后做 sanity check——`02a-repo-type.yaml` 必须有非空 `type` 字段
- **降级路径**：
  1. shallow clone 检测到 → 自动 `git fetch --unshallow` 后重试
  2. 无 lock 文件 → 跳过锁文件维度（不阻断）
  3. 二进制占大头（> 50%）→ 提示用户确认「轻量级分析」模式（只取 manifest + 顶层目录）
  4. 类型不匹配 → 默认按 `web-fullstack` 硬套 12 维 + 打 warning

### R4 — Target repo 不可达

- **触发时机**：
  - 私有 repo / 需登录
  - GitHub API 限速（403 / 429）
  - 404（仓库不存在 / 路径错）
  - 网络中断
- **检测时机**：阶段零「目标仓库元数据」阶段就做探活
- **降级路径**：
  1. 私有 repo → 检查 `~/.ssh/config` 或 `~/.config/gh/hosts.yml`，尝试 SSH/HTTPS 自动认证
  2. API 限速 → 退避 60 秒后重试，仍失败则切换到 `git clone` 直拉（不走 API）
  3. 404 → abort，输出友好提示「仓库不存在，请检查 URL / 权限」
  4. 网络中断 → 提示用户检查网络，5 分钟后重试

### R5 — 阶段六门控失败（覆盖率不达标）

- **触发时机**：覆盖率 < ADR-0005 / ADR-0008 阈值（80% / 50% / 20%）
- **检测方法**：阶段六脚本算出 `coverage_ratio` 后比对阈值
- **降级路径**：
  1. 不达标模块子集 → 写 `08-coverage-failure.md`，触发阶段五 sub-agent 部分回退（详见 ADR-0005）
  2. 单模块最多回退 3 次（共用配额）
  3. 3 次耗尽 → 标 `FAILED`，**不阻断**整个流程，进入 R-budget-exhaustion
- **报告影响**：失败模块在最终报告中以「⚠️ 模块未达到 80% 覆盖率标准」标注

### R6 — 用户中途切换 mode

- **触发时机**：用户在阶段三或阶段七期间切换 `interactive` → `autonomous`（或反向）
- **检测方法**：监听 `--mode` flag 的 mtime 或 argv 二次传入
- **降级路径**：
  1. 阶段三中途切：`ask_user()` 抽象重新评估 `mode`，已收集的 answer 缓存到 `03-question-answers.md`，新增问题按新 mode 提交
  2. 阶段七中途切：renderer 销毁当前进度，按新 `--mode` 重新渲染模板
  3. 阶段五中途切：**不支持**（并发 sub-agent 已启动，切换会浪费 token）→ 提示用户等待当前阶段完成

### 预算耗尽兜底（R-budget-exhaustion）

- **触发时机**：ADR-0007 三个预算任一耗尽（时间 / token / 失败重试）
- **降级路径**：
  1. 强制 `yield` 终止当前阶段
  2. 输出 `analysis/STATE_REPORT.md`：
     ```
     ## Skill Run State Report
     ## Status: ABORTED (reason: token_exhausted | timeout | retries_exhausted)
     ## Completed Phases:
     ## - Phase-2a: OK (产物文件列表)
     ## - Stage 3: OK
     ## - Stage 5: 8/10 modules completed
     ## - ...
     ## Failed / Skipped Modules:
     ## - module_007: TIMEOUT (skipped, retry budget exhausted)
     ## - module_009: COVERAGE FAILED (60% < 80% threshold)
     ## Next Steps:
     ## - Run with `--resume` to continue from last checkpoint
     ## - Or manually inspect analysis/drafts/06-module-008.md
     ```
  3. 写 `analysis/.resume-token` 文件，记录下一个可恢复阶段
  4. 用户可 `repo-analyzer --resume --from-stage=5 --module=module_007` 手动接力

## Alternatives

- **K1. 不做风险登记**——出问题时临时救火，可复现性差。
- **K2. 只列 3 类风险**——覆盖不全。
- **K3. 全 6 类 + 统一兜底（本 ADR）**——工程量 +30 分钟，但 production-ready。

## Consequences

- 阶段零增加「目标仓库探活」步骤（属 R4）。
- 阶段六增加 yield → 部分回退机制（属 R5，详见 ADR-0005）。
- 阶段八增加 `STATE_REPORT.md` 产物（属 R-budget-exhaustion）。
- skill 入口增加 `--resume --from-stage=N --module=ID` 调试 flag。
- §10 验收清单中「可在 budget 耗尽时优雅终止」成为可验证项。

## Open Questions

- [ ] R-budget-exhaustion 输出的 `.resume-token` 是否会过期？24 小时 vs 7 天 vs 永久。
- [ ] R2 sub-agent TIMEOUT 的阈值 10 分钟是否合理？需要按模型类型细分（haiku vs opus）。
- [ ] R5 的覆盖率不达标模块是否要在最终报告中保留 draft 还是仅标 `[INCOMPLETE]`？

## Linked

- ADR-0004（重试配额 +1 R-budget-exhaustion 触发）
- ADR-0005（覆盖率失败触发 R5）
- ADR-0007（三个预算耗尽定义）
- 阶段零 §0 / 阶段六 §8 / 阶段八 §8
