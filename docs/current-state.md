# Fleet Current State — 2026-03-27

## What's Working (End-to-End Verified)

- OpenClaw 2026.3.24 running (gateway on ws://0.0.0.0:18789)
- Mission Control running (Docker: Postgres, Redis, backend, frontend)
- 7 fleet agents + gateway agent registered and provisioned in MC
- **TOOLS.md pushed to all agents** (AUTH_TOKEN, BASE_URL, BOARD_ID, OpenAPI discovery)
- **SOUL.md with MC Workflow instructions** pushed to all agent workspaces
- **Full MC → OpenClaw → Agent → MC loop verified:**
  1. Task created in MC, assigned to architect
  2. Dispatched via `chat.send` (deliver=false) through OpenClaw gateway
  3. Agent received task, read TOOLS.md, got credentials
  4. Agent called MC REST API: updated task to in_progress, posted comment
  5. Activity visible in MC dashboard
- Fleet self-bootstraps via setup.sh

## Configuration Required

### OpenClaw exec approval: `tools.exec.ask=off`
Without this, agents get blocked on interactive approval for every shell command.
Set in `~/.openclaw/openclaw.json`:
```json
"tools": {
  "exec": {
    "host": "gateway",
    "security": "full",
    "ask": "off"
  }
}
```

### Claude Code permissions in agent workspaces
Each agent workspace needs `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)"],
    "deny": []
  }
}
```

### MC template sync after agent registration
Call `POST /api/v1/gateways/{id}/templates/sync?rotate_tokens=true&force_bootstrap=true`
to push TOOLS.md and mint agent tokens. Added to setup.py.

## Architecture (Confirmed by E2E Test)

```
Task Dispatch:  MC → chat.send(deliver=false) → Gateway(INTERNAL_MESSAGE_CHANNEL) → Agent
Response:       Agent reads TOOLS.md → calls MC REST API (task update, comments, memory)
Observation:    Human → MC dashboard (activity events, SSE streams, board memory)
```

No external channels needed for basic operation.

## Next Steps (M39+)

- M39: Full autonomous task execution (agent does real work, not just API test)
- M40: Observation & interaction (SSE, board memory chat, approval gates)
- M41: Coordination features (nudge/ask-user with deliver=true paths)
- M42: AICP skills for fleet management
- M43: NNRT autonomous contribution