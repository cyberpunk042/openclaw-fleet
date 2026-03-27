# Skills Inventory

Generated: 2026-03-27

## OpenClaw Built-in Skills (10/50 ready)

### Ready (usable now)

| Skill | Description | Fleet Relevance |
|-------|-------------|-----------------|
| coding-agent | Delegate coding tasks to sub-agents | **High** — software-engineer, qa-engineer |
| gh-issues | Fetch GitHub issues, spawn fix agents, open PRs | **High** — all project work |
| github | GitHub ops via `gh` CLI (PRs, issues, CI) | **High** — all agents |
| healthcheck | Host security hardening, risk config | **Medium** — devops |
| node-connect | Diagnose OpenClaw node connection issues | **Low** — admin only |
| openai-whisper-api | Transcribe audio via OpenAI API | **Low** — not fleet-relevant |
| skill-creator | Create/edit/audit SKILL.md files | **High** — creating fleet skills |
| tmux | Remote-control tmux sessions | **Medium** — devops, qa-engineer |
| video-frames | Extract frames from video via ffmpeg | **Low** — not fleet-relevant |
| weather | Weather forecasts | **None** |

### Needs Setup (relevant to fleet)

| Skill | What's Needed | Fleet Relevance |
|-------|--------------|-----------------|
| discord | Discord bot token + server | **High** — channel observation |
| slack | Slack workspace + app | **Medium** — team communication |
| session-logs | jq installed | **Medium** — debugging agent sessions |
| clawhub | clawhub CLI installed | **Medium** — install more skills |
| summarize | youtube-dl or similar | **Low** — content analysis |

### Not Relevant to Fleet

1password, apple-notes, apple-reminders, bear-notes, blogwatcher, blucli,
bluebubbles, camsnap, eightctl, gemini, gifgrep, gog, goplaces, himalaya,
imsg, mcporter, model-usage, nano-pdf, notion, obsidian, openai-whisper,
openhue, oracle, ordercli, peekaboo, sag, sherpa-onnx-tts, songsee,
sonoscli, spotify-player, things-mac, trello, voice-call, wacli, xurl

## OCMC Skills Marketplace

**Status:** Empty — no packs registered.

### Packs to Register

| Pack | URL | Skills Expected |
|------|-----|-----------------|
| Anthropic Official | https://github.com/anthropics/skills | Claude Code skills |
| Awesome Claude Skills | https://github.com/ComposioHQ/awesome-claude-skills | Community collection |

### Fleet-Specific Skills (to create)

| Skill | Purpose | Agent |
|-------|---------|-------|
| fleet-commit | Conventional commit with task reference | All |
| fleet-report | Post structured report to MC board memory | All |
| fleet-task-update | Standardized MC task status workflow | All |

## Agent → Skill Mapping (Recommended)

| Agent | Priority Skills |
|-------|----------------|
| architect | github, coding-agent |
| software-engineer | github, gh-issues, coding-agent, tmux |
| qa-engineer | github, tmux, coding-agent |
| devops | github, tmux, healthcheck |
| technical-writer | github |
| ux-designer | github |
| accountability-generator | github |