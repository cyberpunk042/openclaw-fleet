# SessionEnd

**Type:** Claude Code Hook (lifecycle event)
**Category:** Session Lifecycle (fires when session terminates)
**Handler types:** command, http, prompt, agent
**Can block:** NO — session ends regardless
**Matcher:** `clear`, `resume` (switching), `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`

## What It Actually Does

Fires when a Claude Code session terminates — whether by user action (/clear, /exit), system action (logout, permission change), or session switch (/resume to different session). The handler can perform cleanup, persist final state, and notify the orchestrator.

## Fleet Use Case: Clean Shutdown

```
SessionEnd fires (session closing)
├── Persist final state:
│   ├── Save current task progress to .claude/memory/
│   ├── Save uncommitted decisions/rationale
│   └── Record trail event: "session ended"
├── Notify orchestrator (optional):
│   ├── Write signal file: state/session_ended/{agent}.json
│   └── Orchestrator detects at next cycle
├── claude-mem: SessionEnd hook captures final observations
└── Return: {} (acknowledged)
```

## Trigger Types

| Trigger | What Happened | Agent Impact |
|---------|--------------|-------------|
| `clear` | User called /clear | Session history cleared. New session starts. |
| `resume` | Switching to different session | Current session paused, other resumed. |
| `logout` | Auth changed | Session terminated. Full restart needed. |
| `prompt_input_exit` | User exited the prompt | Session ends normally. |
| `bypass_permissions_disabled` | Permission mode changed | Session can't continue with new permissions. |
| `other` | Various other terminations | Catch-all. |

## Relationships

- FIRES ON: every session termination
- CANNOT BLOCK: session ends regardless
- PAIRED WITH: SessionStart (end saves, start re-injects)
- CONNECTS TO: claude-mem (SessionEnd hook captures final observations)
- CONNECTS TO: .claude/memory/ (persist state before loss)
- CONNECTS TO: agent_lifecycle.py (session end affects lifecycle — agent may go IDLE)
- CONNECTS TO: orchestrator (detects session ended → may reassign work)
- CONNECTS TO: trail system (trail.session.ended event)
