# module_001 skills

- 文件数: 10
- 分层: core

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`skills` 路径组，共 10 个文件。
- 分析优先级：核心模块，必须优先核对入口、测试和对外 API。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `skills/watch/.skillignore`
- `skills/watch/SKILL.md`
- `skills/watch/scripts/build-skill.sh`
- `skills/watch/scripts/config.py`
- `skills/watch/scripts/download.py`
- `skills/watch/scripts/frames.py`
- `skills/watch/scripts/setup.py`
- `skills/watch/scripts/transcribe.py`
- `skills/watch/scripts/watch.py`
- `skills/watch/scripts/whisper.py`

## 关键路径
- 从 `skills/watch/scripts/config.py:15` 的 `read_env_file` 开始核对调用链。
- 从 `skills/watch/scripts/config.py:46` 的 `get_config` 开始核对调用链。
- 从 `skills/watch/scripts/config.py:63` 的 `frame_cap` 开始核对调用链。
- 从 `skills/watch/scripts/download.py:18` 的 `is_url` 开始核对调用链。
- 从 `skills/watch/scripts/download.py:25` 的 `resolve_local` 开始核对调用链。
- 从 `skills/watch/scripts/download.py:42` 的 `_pick_subtitle` 开始核对调用链。
- 从 `skills/watch/scripts/download.py:53` 的 `_pick_video` 开始核对调用链。
- 从 `skills/watch/scripts/download.py:63` 的 `fetch_captions` 开始核对调用链。

## 关键符号
- `read_env_file` (skills/watch/scripts/config.py:15)
- `get_config` (skills/watch/scripts/config.py:46)
- `frame_cap` (skills/watch/scripts/config.py:63)
- `is_url` (skills/watch/scripts/download.py:18)
- `resolve_local` (skills/watch/scripts/download.py:25)
- `_pick_subtitle` (skills/watch/scripts/download.py:42)
- `_pick_video` (skills/watch/scripts/download.py:53)
- `fetch_captions` (skills/watch/scripts/download.py:63)
- `_read_info` (skills/watch/scripts/download.py:96)
- `download_url` (skills/watch/scripts/download.py:113)
- `download` (skills/watch/scripts/download.py:163)
- `_scale_filter` (skills/watch/scripts/frames.py:40)
- `_clamp_fps` (skills/watch/scripts/frames.py:47)
- `parse_time` (skills/watch/scripts/frames.py:53)
- `format_time` (skills/watch/scripts/frames.py:75)
- `get_metadata` (skills/watch/scripts/frames.py:84)
- `auto_fps` (skills/watch/scripts/frames.py:120)
- `auto_fps_focus` (skills/watch/scripts/frames.py:139)
- `extract` (skills/watch/scripts/frames.py:160)
- `extract_scene_candidates` (skills/watch/scripts/frames.py:215)
- `_even_indices` (skills/watch/scripts/frames.py:281)
- `parse_timestamps` (skills/watch/scripts/frames.py:293)
- `merge_frames` (skills/watch/scripts/frames.py:310)
- `extract_at_timestamps` (skills/watch/scripts/frames.py:322)
- `_even_sample` (skills/watch/scripts/frames.py:391)
- `_frame_delta` (skills/watch/scripts/frames.py:413)
- `_thumb_frames` (skills/watch/scripts/frames.py:422)
- `dedupe_perceptual` (skills/watch/scripts/frames.py:461)
- `_dedupe_by_deltas` (skills/watch/scripts/frames.py:477)
- `extract_scene_or_uniform` (skills/watch/scripts/frames.py:508)
- `extract_keyframes` (skills/watch/scripts/frames.py:574)
- `_which` (skills/watch/scripts/setup.py:60)
- `_check_binaries` (skills/watch/scripts/setup.py:64)
- `_check_file_permissions` (skills/watch/scripts/setup.py:71)
- `_read_env_key` (skills/watch/scripts/setup.py:90)
- `_have_api_key` (skills/watch/scripts/setup.py:114)
- `is_first_run` (skills/watch/scripts/setup.py:122)
- `_scaffold_env` (skills/watch/scripts/setup.py:127)
- `_write_setup_complete` (skills/watch/scripts/setup.py:140)
- `_brew_pkg` (skills/watch/scripts/setup.py:164)
- `_install_macos` (skills/watch/scripts/setup.py:178)
- `_install_hint_linux` (skills/watch/scripts/setup.py:195)
- `_install_hint_windows` (skills/watch/scripts/setup.py:205)
- `_status` (skills/watch/scripts/setup.py:215)
- `cmd_check` (skills/watch/scripts/setup.py:257)
- `cmd_json` (skills/watch/scripts/setup.py:292)
- `cmd_install` (skills/watch/scripts/setup.py:298)
- `main` (skills/watch/scripts/setup.py:351)
- `_to_seconds` (skills/watch/scripts/transcribe.py:18)
- `parse_vtt` (skills/watch/scripts/transcribe.py:22)
- `_dedupe` (skills/watch/scripts/transcribe.py:53)
- `filter_range` (skills/watch/scripts/transcribe.py:68)
- `format_transcript` (skills/watch/scripts/transcribe.py:81)
- `main` (skills/watch/scripts/watch.py:23)
- `plan_chunks` (skills/watch/scripts/whisper.py:38)
- `load_api_key` (skills/watch/scripts/whisper.py:63)
- `_from_env` (skills/watch/scripts/whisper.py:70)
- `_from_dotenv` (skills/watch/scripts/whisper.py:73)
- `extract_audio` (skills/watch/scripts/whisper.py:113)
- `audio_duration` (skills/watch/scripts/whisper.py:140)
- `split_audio` (skills/watch/scripts/whisper.py:162)
- `_build_multipart` (skills/watch/scripts/whisper.py:199)
- `_post_whisper` (skills/watch/scripts/whisper.py:235)
- `_read_error_body` (skills/watch/scripts/whisper.py:307)
- `_retry_after` (skills/watch/scripts/whisper.py:320)
- `shift_segments` (skills/watch/scripts/whisper.py:330)
- `_segments_from_response` (skills/watch/scripts/whisper.py:348)
- `transcribe_chunks` (skills/watch/scripts/whisper.py:369)
- `_transcribe_file` (skills/watch/scripts/whisper.py:401)
- `transcribe_video` (skills/watch/scripts/whisper.py:412)
- `transcribe_one` (skills/watch/scripts/whisper.py:440)

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 风险与缺口
- 缺少可见测试文件，变更该模块前应先补最小回归验证。
- 公开符号较多，后续人工深挖应优先确认职责边界是否过宽。

## 证据
- 模块 ID 来源：`05-module-ids.yaml`
- 代码切片：`slices/02-backend.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 历史热点：`slices/12-history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| skills | 10 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`skills/watch` 是产品核心模块，承担 `/watch <url-or-path>` 的真实执行能力：把视频 URL 或本地视频转成 agent 可消费的“帧路径 + 时间戳转录 + 元信息报告”。这一判断来自 `AGENTS.md` 对模块结构的说明，以及 README 中“paste a URL or local path → captions/download → frames/transcript → Claude reads frames”的工作流描述（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。

**设计思路**：模块采用“自包含 skill 文件夹”设计，`SKILL.md` 与 `scripts/` 同级，运行时通过 `SKILL_DIR/scripts/...` 定位脚本，避免绑定 Claude Code 专属环境变量。这是跨 Claude Code、Codex、Cursor、Copilot 等宿主安装的关键设计约束（证据：`slices/04-docs.xml`、`slices/05-agent-config.xml`）。实现层面拆成 `watch.py` 编排入口、`download.py` 处理 yt-dlp、本地文件与字幕、`frames.py` 处理 ffmpeg 抽帧、`transcribe.py` 处理 VTT、`whisper.py` 处理 Whisper fallback、`setup.py/config.py` 处理运行前置条件和用户配置（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。

**关键数据流**：主链路是 source → `download.download()` 判断 URL/本地路径 → URL 走 `yt-dlp` 下载视频与英文 VTT，本地路径直接 resolve → `frames.py` 生成 keyframe/scene/uniform/cue frames → `transcribe.py` 优先解析 VTT → 无字幕且允许时进入 Whisper fallback → `watch.py` 输出 Markdown 报告、帧路径和 transcript（证据：`slices/07-config-scripts.xml`、`slices/04-docs.xml`）。`config.py` 提供 `WATCH_DETAIL` 默认值与 frame cap 映射，`setup.py --check/--json/install` 提供运行前依赖和 API key 状态（证据：`slices/07-config-scripts.xml`）。

**模块协同**：它与测试模块形成强耦合回归关系：`tests/test_watch.py` 直接运行 `skills/watch/scripts/watch.py`，验证 detail 路由、timestamp cue、dedup 默认行为；`tests/test_whisper.py` 覆盖 chunk plan、split、timestamp shift 和部分失败容忍（证据：`slices/06-tests.xml`）。它也与发布/安装模块协同：`build-skill.sh` 只归档 `skills/watch`，GitHub release workflow 调用该脚本生成 `dist/watch.skill`（证据：`slices/07-config-scripts.xml`）。

**架构亮点**：亮点是把复杂视频理解拆成确定性工具链，而不是让模型直接猜：`yt-dlp` 负责获取素材，`ffmpeg` 负责抽帧，VTT/Whisper 负责转录，模型只消费结果。这符合“确定性环节用代码，判断环节交给模型”的项目原则（证据：`slices/04-docs.xml`、`slices/07-config-scripts.xml`）。另一个亮点是 token 成本意识很强：detail 模式、frame cap、dedup、focused range 都围绕“让帧预算花在有信息量的位置”设计（证据：`slices/04-docs.xml`、`slices/06-tests.xml`）。

**主要风险**：第一，核心源码的完整后端切片 `slices/02-backend.xml` 在当前目录缺失，模块底稿中大量函数符号只能通过 `slices/07-config-scripts.xml` 和测试切片交叉验证，不能宣称已核对全部源码细节（证据：当前可用切片列表、`slices/07-config-scripts.xml`）。第二，模块依赖外部二进制与网络服务，`ffmpeg`、`yt-dlp`、Groq/OpenAI API 的环境差异会成为主要运行风险；`setup.py` 和 hook 已做前置检测，但这仍是产品可靠性的外部边界（证据：`slices/07-config-scripts.xml`、`slices/04-docs.xml`）。第三，历史热点显示所有核心文件修改次数均为 1，说明当前历史信号不足，不能用热点判断成熟度或稳定性（证据：`slices/12-history-hotspot.txt`）。

