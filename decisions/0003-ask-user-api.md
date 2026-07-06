---
Status: Accepted
Date: 2026-07-06
Round: 4 (R4-Q3)
---

# ADR-0003 Skill 内 `ask_user()` 抽象 + 运行时适配器

## Context

PLAN.md §4「阶段三：项目特征识别 + 自适应提问」使用「自适应提问 1~4」共 4 道题目：

1. 用户优先关心的方向（架构 / 性能 / 安全 / 业务模块 / 全栈）
2. 报告主要受众（技术负责人 / 业务方 / 个人学习）
3. 用法假设
4. 未来扩展

但以下契约信息全部缺失：

- **谁来识别项目特征**？（子 agent / 主 agent / repomix 自动推断？）
- **向谁提问**？（Skill 输入参数 / `AskUserQuestion` hook / 配置文件 / 推断？）
- **提问交互形态**：多轮对话 / 单次问答 / 自动跳过？
- **答案如何 feed 到阶段四**？阶段三产出是什么文件？
- **降级路径**：用户说「别问直接跑」怎么办？

更关键：skill 需在 Claude Code / Codex CLI / Cursor 三种 runtime 下运行，三者对交互 API 的支持度参差：

| Runtime | 原生交互 API | 备注 |
|---------|-------------|------|
| Claude Code | `AskUserQuestion` | 完整支持 2-4 选项 + multiSelect |
| Codex CLI | `codex ask` / 内置 prompt | 选项支持有限 |
| Cursor | Composer / Manual | 仅文本输入，无结构化 |

## Decision

**Skill 内部定义 `ask_user()` 抽象层 + 运行时适配器**：

1. **抽象签名**（伪代码）：
   ```python
   class AskUserAPI(Protocol):
       def ask(
           self,
           questions: list[Question],
           timeout_sec: int = 60,
       ) -> list[Answer]: ...

   @dataclass
   class Question:
       key: str                       # 内部语义 key
       header: str                    # 显示 chip（≤ 12 字符）
       prompt: str                    # 完整问题
       options: list[Option]          # 2-4 个选项
       multi_select: bool = False

   @dataclass
   class Answer:
       key: str
       selected: list[str]            # 选项 label 列表（multi 时可能 > 1）
       notes: str = ""                # 用户补充说明（可选）
   ```

2. **运行时适配器**（落地 3 个）：
   - `ClaudeCodeAskAdapter` → 调用 `AskUserQuestion`
   - `CodexAskAdapter` → 调用 `codex ask`（选项受限时退化为纯文本 prompt）
   - `CursorAskAdapter` → 退化为写入 `~/.config/repo-analyzer/questions.json`，等用户手工填写后 resumed

3. **降级链**（自动）：
   ```
   运行时支持的原生交互
       ↓ 不支持
   写入 questions.json + 暂停 skill
       ↓ 还不支持
   使用 `~/.config/repo-analyzer/defaults.yaml` 中的默认值
   ```

4. **skip 路径**（用户显式 `--no-question`）：
   - `--no-question` 标志被解析后，`ask_user()` 直接读 `defaults.yaml`，不再发起交互。
   - 默认值：
     - Q1 优先方向 = `architecture`
     - Q2 受众 = `tech-lead`
     - Q3 用法假设 = `[]`（空数组）
     - Q4 未来扩展 = `[]`（空数组）

5. **产出契约**：无论何种路径，阶段三**必须输出** `analysis/03-question-answers.md`，包含 4 道题的答案或默认值——这是阶段四的输入。

6. **互校验**：阶段三开始时做一次 sanity check——若 `03-question-answers.md` 已存在且非空，跳过提问直接进阶段四。

## Alternatives

- **C1. 全交互**——永远 `AskUserQuestion`，在 non-interactive runtime 下挂掉。
- **C2. 全默认**——零定制化，报告千人一面。
- **C3. 双向契约 + fallback（本 ADR）**——双轨，运行时自选降级链。
- **C4. InquirerPy 自实现**——不依赖运行时，但用户侧 UI 不一致。

## Consequences

- 阶段三新增 `analysis/03-question-answers.md` 输出契约，与 `00-context.md` / `01-pragmatic.md` / `02a-repo-type.yaml` / `02a-manifest-card.md` 一起成为输入目录的「自描述」层。
- 阶段四读取 `03-question-answers.md` 后，按答案选模板映射：`architecture` → 标准 8 章；`security` → 加 §6 安全态势章；`tech-lead` → 用 `tech-lead.tmpl.md`；`business` → 用 `business.tmpl.md`。
- Skill 入口需要支持 `--mode interactive|autonomous` 与 `--no-question` 两种 flag（详见 ADR-0008）。
- `~/.config/repo-analyzer/defaults.yaml` 成为必须配置项，首次运行自动生成模板。
- 三个适配器约 300 行 Python，新增单元测试覆盖默认/单选/多选/超时/skip 5 个分支。

## Open Questions

- [ ] 三个适配器用 Python 实现还是 Node？因为 skill 主语言未定——需先确认 skill 的 implementation stack。
- [ ] Cursor 适配器降级到 `questions.json` 后，skill 如何 resume？是 require 显式 `--resume` 还是自动检测文件 mtime？
- [ ] 用户在交互过程中途修改答案（撤回）如何处理？需不需要 versioned answers？

## Linked

- ADR-0001（阶段三读取 `02a-manifest-card.md` 作为「已知事实」）
- ADR-0006（按受众选模板）
- ADR-0008（`--no-question` 开关归属本 ADR）
- 阶段三 §4 / 阶段四 §6 / 阶段十二 §12
