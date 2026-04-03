# /resume

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents
**Alias:** /continue

## What It Actually Does

Resumes a previous conversation by session ID or name. Claude Code persists sessions — every conversation is saved and can be continued later. /resume loads the full conversation history, context, and state from a previous session.

This is how agents continue interrupted work. If a session was pruned by the doctor, compacted by the brain, or interrupted by a gateway restart, /resume brings the agent back to where they were (minus what was lost in compaction/pruning).

## When Fleet Agents Should Use It

**After gateway restart:** Gateway process restarted → agent sessions may disconnect. /resume reconnects to the previous session with its context intact.

**After brief interruption:** Network issue, brief outage → session still exists on server → /resume continues.

**Continuing multi-cycle work:** Agent works on a task across multiple heartbeat cycles. Between cycles, the session persists. Next heartbeat → gateway may create new session OR resume existing. /resume explicitly continues.

## What Survives vs What's New

After /resume:
- Previous conversation history is LOADED (from session persistence)
- CLAUDE.md and agent files are RE-READ from disk (may have changed)
- fleet-context.md is FRESH (brain wrote new data since last cycle)
- task-context.md is FRESH (brain may have updated task state)
- claude-mem observations from the previous session are SEARCHABLE

So the agent gets: old conversation + new context files. The new context may contain changes (new directives, new messages, task state changes) that happened while the session was idle.

## Relationships

- TRIGGERS: SessionStart hook (trigger="resume" — can inject updated context)
- LOADS: previous conversation history from session persistence
- RE-READS: all agent files from disk (IDENTITY, SOUL, CLAUDE, etc.)
- CONNECTS TO: gateway session management (session_key → persistent session)
- CONNECTS TO: agent_lifecycle.py (resume may reset agent from SLEEPING to ACTIVE)
- CONNECTS TO: /clear command (alternative — fresh start instead of resume)
- CONNECTS TO: /compact command (if resumed session has too much old context)
- CONNECTS TO: fleet-context.md Layer 6 (brain wrote fresh data — agent sees current state)
- CONNECTS TO: claude-mem (observations from previous session still searchable)
