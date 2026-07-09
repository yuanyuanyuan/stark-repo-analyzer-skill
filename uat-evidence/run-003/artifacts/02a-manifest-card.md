# 5KB 项目名片

- 项目名: /watch
- 目标: https://github.com/bradautomates/claude-video
- Repo 类型: multi-agent-config
- 主要语言: Python(17)
- 文件数: 36

## 顶层文件快照
- .agents/plugins/marketplace.json
- .claude-plugin/marketplace.json
- .claude-plugin/plugin.json
- .codex-plugin/plugin.json
- .gitattributes
- .github/workflows/release.yml
- .gitignore
- .skillignore
- AGENTS.md
- CHANGELOG.md
- CLAUDE.md
- LICENSE
- README.md
- dev-sync.sh
- hooks/hooks.json
- hooks/scripts/check-setup.sh
- skills/watch/.skillignore
- skills/watch/SKILL.md
- skills/watch/scripts/build-skill.sh
- skills/watch/scripts/config.py
- skills/watch/scripts/download.py
- skills/watch/scripts/frames.py
- skills/watch/scripts/setup.py
- skills/watch/scripts/transcribe.py
- skills/watch/scripts/watch.py
- skills/watch/scripts/whisper.py
- tests/conftest.py
- tests/test_config.py
- tests/test_dedup.py
- tests/test_download.py
- tests/test_fixtures.py
- tests/test_frames.py
- tests/test_setup.py
- tests/test_timestamps.py
- tests/test_watch.py
- tests/test_whisper.py

## README 前 30 行
```text
# /watch

**Give Claude the ability to watch any video.**

Claude Code (recommended — auto-updates via marketplace):
'''
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
'''

Codex, Cursor, Copilot, Gemini CLI, or any of 50+ [Agent Skills](https://agentskills.io) hosts:
'''bash
npx skills add bradautomates/claude-video -g
'''
(`-g` installs globally for your user, available across all projects. Drop it to scope per-project.)

More install options (claude.ai web, manual) in the [Install](\#install) section below.

Zero config to start — `yt-dlp` and `ffmpeg` install on first run via `brew` on macOS (Linux/Windows print exact commands). Captions cover most public videos for free. Whisper API key is only needed when a video has no captions.

---

Claude can read a webpage, run a script, browse a repo. What it can't do, out of the box, is *watch a video*. You paste a YouTube link and it has to either guess from the title or pull a transcript that's missing 90% of what's on screen.

With Claude Video `/watch` you can paste a URL or a local path, ask a question, and Claude fetches captions first, downloads only what it needs, extracts frames (scene-aware, or fast keyframes at `efficient` detail), pulls a timestamped transcript (free captions when available, Whisper API as fallback), and `Read`s every frame as an image. By the time it answers, it has *seen* the video and *heard* the audio.

'''
/watch https://youtu.be/dQw4w9WgXcQ what happens at the 30 second mark?
'''

```

