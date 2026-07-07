# module_001 skills

- 文件数: 10
- 分层: core

## 角色
该模块由确定性扫描按路径分组生成，用于给后续 subagent 提供分析入口。

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

## MCP 工具/API 表面
- 未识别到 MCP 工具

## 覆盖率明细
| 文件组 | 文件数 | 已读方式 |
|---|---:|---|
| skills | 10 | deterministic scan |
