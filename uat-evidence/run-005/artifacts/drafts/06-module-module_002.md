# module_002 tests

- 文件数: 10
- 分层: core

## 角色
该模块由确定性扫描按路径、公开符号和对外工具/API 生成，是后续 agent 判断业务价值与架构风险的分析底稿。

## 深度分析
- 模块边界：`tests` 路径组，共 10 个文件。
- 分析优先级：核心模块，必须优先核对入口、测试和对外 API。
- 业务假设：若该模块包含运行入口或对外 API，它就是报告后续判断的主要证据来源；否则先按支撑模块处理。

## 关键文件
- `tests/conftest.py`
- `tests/test_config.py`
- `tests/test_dedup.py`
- `tests/test_download.py`
- `tests/test_fixtures.py`
- `tests/test_frames.py`
- `tests/test_setup.py`
- `tests/test_timestamps.py`
- `tests/test_watch.py`
- `tests/test_whisper.py`

## 关键路径
- 从 `tests/conftest.py:19` 的 `_run` 开始核对调用链。
- 从 `tests/conftest.py:25` 的 `build_cut_clip` 开始核对调用链。
- 从 `tests/conftest.py:55` 的 `build_static_clip` 开始核对调用链。
- 从 `tests/conftest.py:73` 的 `cut_clip` 开始核对调用链。
- 从 `tests/conftest.py:80` 的 `static_clip` 开始核对调用链。
- 从 `tests/test_config.py:5` 的 `test_default_detail_is_balanced` 开始核对调用链。
- 从 `tests/test_config.py:11` 的 `test_env_overrides_detail` 开始核对调用链。
- 从 `tests/test_config.py:17` 的 `test_invalid_detail_falls_back_to_default` 开始核对调用链。

## 关键符号
- `_run` (tests/conftest.py:19)
- `build_cut_clip` (tests/conftest.py:25)
- `build_static_clip` (tests/conftest.py:55)
- `cut_clip` (tests/conftest.py:73)
- `static_clip` (tests/conftest.py:80)
- `test_default_detail_is_balanced` (tests/test_config.py:5)
- `test_env_overrides_detail` (tests/test_config.py:11)
- `test_invalid_detail_falls_back_to_default` (tests/test_config.py:17)
- `test_get_config_keys` (tests/test_config.py:23)
- `test_frame_cap_mapping` (tests/test_config.py:30)
- `test_frame_delta_identical_is_zero` (tests/test_dedup.py:10)
- `test_frame_delta_is_mean_absolute_difference` (tests/test_dedup.py:14)
- `test_frame_delta_mismatched_length_is_infinite` (tests/test_dedup.py:20)
- `_touch` (tests/test_dedup.py:27)
- `test_dedupe_collapses_identical_run` (tests/test_dedup.py:40)
- `test_dedupe_keeps_all_distinct` (tests/test_dedup.py:50)
- `test_dedupe_compares_against_last_kept_not_previous` (tests/test_dedup.py:59)
- `test_dedupe_threshold_is_inclusive` (tests/test_dedup.py:69)
- `test_dedupe_empty_and_single_are_noops` (tests/test_dedup.py:79)
- `test_dedupe_mismatched_thumb_count_is_noop` (tests/test_dedup.py:87)
- `test_thumb_frames_match_candidate_count` (tests/test_dedup.py:98)
- `test_dedupe_perceptual_collapses_static_clip` (tests/test_dedup.py:104)
- `test_dedupe_perceptual_keeps_distinct_cuts` (tests/test_dedup.py:114)
- `test_scene_engine_reports_zero_dedup_on_distinct` (tests/test_dedup.py:126)
- `test_uniform_fallback_dedupes_static` (tests/test_dedup.py:134)
- `test_keyframe_uniform_fallback_dedupes_static` (tests/test_dedup.py:146)
- `test_dedup_false_disables_collapse` (tests/test_dedup.py:153)
- `_capture_argv` (tests/test_download.py:22)
- `fake_run` (tests/test_download.py:32)
- `_sub_langs` (tests/test_download.py:39)
- `_assert_english_only` (tests/test_download.py:44)
- `test_fetch_captions_requests_english_only` (tests/test_download.py:50)
- `test_download_url_requests_english_only` (tests/test_download.py:56)
- `_Result` (tests/test_download.py:27)
- `_duration` (tests/test_fixtures.py:7)
- `test_cut_clip_builds` (tests/test_fixtures.py:15)
- `test_static_clip_builds` (tests/test_fixtures.py:20)
- `test_keyframe_engine_on_cut_clip` (tests/test_frames.py:7)
- `test_keyframe_even_sampling_caps_and_spans` (tests/test_frames.py:16)
- `test_keyframe_fallback_on_static_clip` (tests/test_frames.py:28)
- `test_scene_engine_on_cut_clip` (tests/test_frames.py:36)
- `test_scene_even_sampling_caps_and_spans` (tests/test_frames.py:45)
- `test_scene_fallback_on_static_clip` (tests/test_frames.py:63)
- `_run` (tests/test_setup.py:11)
- `_write_env` (tests/test_setup.py:29)
- `test_json_reports_watch_detail` (tests/test_setup.py:37)
- `test_keyless_completed_setup_proceeds_silently` (tests/test_setup.py:44)
- `test_keyless_first_run_is_encouraged` (tests/test_setup.py:59)
- `test_key_present_is_ready` (tests/test_setup.py:70)
- `test_parse_timestamps_mixed_formats` (tests/test_timestamps.py:9)
- `test_parse_timestamps_strips_and_dedupes` (tests/test_timestamps.py:13)
- `test_parse_timestamps_empty` (tests/test_timestamps.py:17)
- `test_parse_timestamps_rejects_garbage` (tests/test_timestamps.py:22)
- `test_merge_frames_sorts_and_reindexes` (tests/test_timestamps.py:27)
- `test_merge_frames_keeps_all_pinned` (tests/test_timestamps.py:41)
- `test_extract_at_timestamps_one_frame_per_point` (tests/test_timestamps.py:47)
- `test_extract_at_timestamps_drops_out_of_window` (tests/test_timestamps.py:58)
- `test_extract_at_timestamps_caps_and_spans` (tests/test_timestamps.py:67)
- `test_extract_at_timestamps_does_not_clobber_detail_frames` (tests/test_timestamps.py:77)
- `_run` (tests/test_watch.py:10)
- `test_efficient_uses_keyframe_engine` (tests/test_watch.py:23)
- `test_balanced_uses_scene_engine` (tests/test_watch.py:29)
- `test_token_burner_uses_scene_engine` (tests/test_watch.py:35)
- `test_transcript_skips_frames` (tests/test_watch.py:40)
- `test_flag_overrides_env` (tests/test_watch.py:46)
- `test_default_is_balanced` (tests/test_watch.py:51)
- `test_timestamps_add_cue_frames_to_detail` (tests/test_watch.py:57)
- `test_timestamps_with_transcript_detail_is_cue_only` (tests/test_watch.py:63)
- `_frame_lines` (tests/test_watch.py:70)
- `test_dedup_collapses_static_by_default` (tests/test_watch.py:74)
- `test_no_dedup_preserves_static_frames` (tests/test_watch.py:80)
- `test_under_limit_is_single_chunk` (tests/test_whisper.py:17)
- `test_at_limit_is_single_chunk` (tests/test_whisper.py:20)
- `test_over_limit_splits_into_enough_chunks` (tests/test_whisper.py:24)
- `test_chunks_are_contiguous_and_cover_full_duration` (tests/test_whisper.py:29)
- `test_each_chunk_estimated_under_limit` (tests/test_whisper.py:39)
- `test_zero_duration_is_single_chunk` (tests/test_whisper.py:46)
- `test_adds_offset_to_start_and_end` (tests/test_whisper.py:53)
- `test_zero_offset_is_identity` (tests/test_whisper.py:60)
- `test_does_not_mutate_input` (tests/test_whisper.py:64)
- `_make_mp3` (tests/test_whisper.py:69)
- `test_creates_one_file_per_plan_entry` (tests/test_whisper.py:85)
- `test_returns_plan_offsets` (tests/test_whisper.py:95)
- `test_chunks_are_smaller_than_full` (tests/test_whisper.py:104)
- `test_reads_duration_of_synthesized_clip` (tests/test_whisper.py:118)
- `test_shifts_and_concatenates_each_chunk` (tests/test_whisper.py:125)
- `fake_transcribe` (tests/test_whisper.py:127)
- `test_keeps_successful_chunks_when_one_fails` (tests/test_whisper.py:137)
- `flaky` (tests/test_whisper.py:140)
- `test_raises_when_every_chunk_fails` (tests/test_whisper.py:149)
- `always_fail` (tests/test_whisper.py:152)
- `TestPlanChunks` (tests/test_whisper.py:14)
- `TestShiftSegments` (tests/test_whisper.py:50)
- `TestSplitAudio` (tests/test_whisper.py:82)
- `TestAudioDuration` (tests/test_whisper.py:115)
- `TestTranscribeChunks` (tests/test_whisper.py:122)

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 风险与缺口
- 公开符号较多，后续人工深挖应优先确认职责边界是否过宽。

## 证据
- 模块 ID 来源：`05-module-ids.yaml`
- 代码切片：`slices/02-backend.xml`
- 依赖切片：`slices/09-dependencies.xml`
- 历史热点：`slices/12-history-hotspot.txt`

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| tests | 10 | deterministic deep scan |

## Agent 深度分析

- attempts: 1
- 证据: `agent-runs/modules-batch/result.md`

**业务角色**：`tests` 是核心质量闸门，不是普通附属测试。它覆盖配置解析、下载参数、抽帧策略、去重、timestamp cue、setup 状态、watch 端到端路由和 Whisper 分块，是保障 `/watch` 跨宿主可用性的主要确定性验证层（证据：`drafts/06-module-module_002.md`、`slices/06-tests.xml`）。

**设计思路**：测试设计明显偏“无网络、可重复、工具链模拟”。`conftest.py` 使用 ffmpeg 合成测试视频，`test_download.py` 捕获 yt-dlp argv 而不是访问真实网络，`test_watch.py` 对本地 clip 跑 `watch.py --no-whisper`，`test_whisper.py` 用合成 mp3 验证分块与时间戳拼接（证据：`slices/06-tests.xml`）。这使测试关注确定性逻辑，而不是被外部网站、API 或网络状态污染。

**关键数据流**：测试数据流从 fixture 合成视频开始，进入 `watch.py` 或底层函数，再断言输出报告中的 detail、engine、frame path、dedup、cue frame 等可观察结果（证据：`slices/06-tests.xml`）。Whisper 测试则从音频大小与时长推导 chunk plan，再验证 split 后 chunk 文件、offset 保留、segment shift 和部分 chunk 失败策略（证据：`slices/06-tests.xml`）。

**模块协同**：该模块直接绑定 `skills/watch/scripts` 的公开行为。`test_config.py` 保护 `WATCH_DETAIL` 和 `frame_cap`；`test_frames.py/test_dedup.py/test_timestamps.py` 保护 frame selection 与 cue merge；`test_setup.py` 保护 `setup.py --json` 的结构化状态；`test_watch.py` 保护入口脚本的用户可见输出（证据：`slices/06-tests.xml`、`drafts/06-module-module_002.md`）。

**架构亮点**：测试覆盖的是产品行为，而不只是函数返回值。例如 `test_default_is_balanced`、`test_transcript_skips_frames`、`test_timestamps_add_cue_frames_to_detail` 直接验证用户会看到的报告语义；这对 agent skill 很重要，因为最终契约是“模型读到什么输出”，不是内部函数如何命名（证据：`slices/06-tests.xml`）。另外，下载测试验证 `--sub-langs en.*`，能防止字幕语言策略回退成不确定行为（证据：`slices/06-tests.xml`）。

**主要风险**：第一，测试 suite 仍依赖本机 ffmpeg，环境缺失会导致测试不可跑；README 也明确测试需要 ffmpeg（证据：`slices/04-docs.xml`、`slices/06-tests.xml`）。第二，网络真实行为、yt-dlp 网站兼容性、Groq/OpenAI API 错误体等并未从当前测试切片看到完整集成覆盖；这是合理取舍，但发布前不能把它等同于端到端线上验证（证据：`slices/06-tests.xml`、`slices/07-config-scripts.xml`）。第三，历史热点只有一次提交记录，无法从历史数据判断哪些测试长期稳定或经常失败（证据：`slices/12-history-hotspot.txt`）。

